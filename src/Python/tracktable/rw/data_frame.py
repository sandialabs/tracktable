# Copyright (c) 2014-2025, National Technology & Engineering Solutions of
# Sandia, LLC (NTESS). All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Adapters to read and write TrajectoryPoints to and from DataFrames.

We're starting with Pandas DataFrame objects.  We also intend to test
against DataFrame objects created by Polars.

Functions:
    points_from_data_frame
    data_frame_from_points
"""

from __future__ import annotations

import logging
import typing

import lazy_import

from typing import Generator, Optional, Sequence

from tracktable import domain as tt_domain
from tracktable.core import exceptions as tt_exceptions
from tracktable.domain import terrestrial, cartesian2d, cartesian3d

if typing.TYPE_CHECKING:
    from tracktable.domain.domain_types import TrajectoryPoint
    import pandas as pd
    import numpy as np
else:
    # Pandas is a fairly heavy-weight dependency that may not
    # always be installed.  Don't actually import it until
    # we use it.
    pd = lazy_import.lazy_module("pandas")
    np = lazy_import.lazy_module("numpy")


__all__ = ["read_points_from_data_frame", "write_points_to_data_frame"]


LOG = logging.getLogger(__name__)



def read_points_from_data_frame(
        input: pd.DataFrame,
        object_id_column: str,
        timestamp_column: str,
        coordinate_columns: list[str],
        property_columns: Optional[list[str]]=None,
        domain: str="terrestrial",
        warn_on_null_values: bool=False
    ) -> Generator[TrajectoryPoint, None, None]:

    """Turn a DataFrame into a sequence of points

    Your data frame must have columns for object ID, timestamp, and
    coordinates.  You can also add arbitrary other fields to the
    points.  The timestamp column must contain timestamps.  The
    coordinate columns must contain numbers.

    The data frame must be sorted by increasing order of timestamp.

    NOTE: The reader will skip any rows that have NA/None values in
    the object ID, timestamp, or coordinate columns.

    NOTE: Since this function returns a generator, input validation
    will not happen (and exceptions will not be raised) until you
    attempt to iterate over the returned points.

    Arguments:
        input (pd.DataFrame): Data frame containing point data
        object_id_column (str): Label of column containing object ID
        timestamp_column (str): Label of column containing timestamp
        coordinate_columns (list of str): List of column names containing coordinates

    Keyword Arguments:
        property_columns (list of str): Columns to include in point properties.
            Defaults to None.
        domain (str): Point domain for points to create.  Defaults to
            "terrestrial".  Can also be "cartesian2d" or "cartesian3d".
        warn_on_null_values (bool): If True, a warning will be printed
            for each row in the input that contains null values in an
            important column.  Defaults to False.
    Raises:
        MissingColumnError: One or more requested columns are not
            present in the input data frame.
        TypeError: Timestamp column must contain timezone-aware timestamp
            objects.

    """

    if property_columns is None:
        property_columns = []

    # Validation first - raise exceptions if anything's seriously
    # amiss
    _validate_domain_and_coordinate_columns(domain, coordinate_columns)
    _validate_column_names(input,
                           object_id_column,
                           timestamp_column,
                           *coordinate_columns,
                           *property_columns)
    _validate_timestamp_dtype(input[timestamp_column])

    # This function is going to be relatively slow because we are doing
    # the thing all the Pandas guides say not to do: iterating over a
    # DataFrame row by row.
    #
    # Start by pulling out exactly the columns we need so we can at least
    # have it quickly do the checks for nulls.

    necessary_columns = input[[
        object_id_column,
        timestamp_column,
        *coordinate_columns
    ]]
    any_null = necessary_columns.isnull().any(axis=1).to_list()

    column_name_to_index = {
        name: i
        for (i, name) in enumerate(input.columns)
    }

    if property_columns is not None:
        property_name_to_column = {
            name: column_name_to_index[name]
            for name in property_columns
        }
    else:
        property_name_to_column = {}

    if domain == "cartesian3d":
        num_coordinates = 3
    else:
        num_coordinates = 2
    point_class = tt_domain.domain_class(domain, "TrajectoryPoint")

    ##
    ##
    ## Here's the main loop: iterate over rows and create points
    ##
    ##
    num_nulls = 0
    num_points = 0
    for row in range(len(input)):
        if any_null[row]:
            num_nulls += 1
            if warn_on_null_values:
                LOG.warning(
                    "Null value in required column (object_id, timestamp, coordinate) at row %s",
                    row)

            continue

        # Set all the basic properties
        new_point = point_class()
        new_point.object_id = necessary_columns.iat[row, 0]
        new_point.timestamp = necessary_columns.iat[row, 1]
        new_point[0] = necessary_columns.iat[row, 2]
        new_point[1] = necessary_columns.iat[row, 3]
        if num_coordinates == 3:
            new_point[2] = necessary_columns.iat[row, 4]

        # Set all the metadata properties
        for (property_name, column_index) in property_name_to_column.items():
            value = input.iat[row, column_index]
            # Here we have to be careful about types.  I'm not yet sure why,
            # but if we try to set a property value to an np.int64, the Python
            # interpreter will throw a segfault.
            #
            # Values of type np.float64 and string go through fine.
            if np.issubdtype(type(value), np.integer):
                value = int(value)
            # Passing pd.NA to the interface also segfaults the interpreter.
            if pd.isna(value):
                value = None
            new_point.properties[property_name] = value

        # Point complete
        num_points += 1
        yield new_point

    LOG.info((
        "Generated %s point(s) from data frame and discarded %s due "
        "to null values."),
        num_points, num_nulls)


def write_points_to_data_frame(
        points: Sequence[TrajectoryPoint]
    ) -> pd.DataFrame:
    """Create a data frame from one or more trajectories

    The data frame will have columns for the object ID, timestamp,
    coordinates, and all user metadata properties for the points in
    the input trajectories.

    Rows will be sorted by increasing timestamp.

    Coordinate columns will be named "longitude" and "latitude" for
    terrestrial points and "x", "y", and possibly "z" for Cartesian
    points.  Point property columns will have the same names that
    they do in the per-point metadata.

    Object ID and timestamp columns will be named "object_id" and
    "timestamp".

    Arguments:
        input (list of TrajectoryPoint): Trajectory points to save

    Returns:
        New Pandas DataFrame
    """

    # It is most efficient to construct a Pandas DataFrame if we have
    # all the data available at once.  This will mean temporarily
    # keeping an additional copy in memory.
    if len(points) == 0:
        LOG.warning("write_points_to_data_frame: Input point list is empty.")

    data_lists: dict[str, list] = _build_data_lists(points)

    df = pd.DataFrame(data_lists)
    df.sort_values("timestamp")
    return df


def _build_data_lists(points: Sequence[TrajectoryPoint]) -> dict[str, list]:
    """Build the dict of lists that will become a DataFrame

    Helper function.

    Arguments:
        all_points (list of TrajectoryPoint)"""


    coordinate_names = _guess_coordinate_names(points)
    data_lists: dict[str, list] = {
        "object_id": [],
        "timestamp": []
    }
    data_lists.update({
        name: []
        for name in coordinate_names
    })
    if len(points) > 0:
        data_lists.update({
            name: []
            for name in points[0].properties.keys()
        })

    for point in points:
        data_lists["object_id"].append(point.object_id)
        data_lists["timestamp"].append(point.timestamp)
        for (i, name) in enumerate(coordinate_names):
            data_lists[name].append(point[i])
        for name in point.properties.keys():
            data_lists[name].append(point.properties[name])

    return data_lists


def _guess_coordinate_names(points: Sequence[TrajectoryPoint]) -> tuple[str, ...]:
    """Guess the names for coordinate columns

    Deduce the point domain and return ("longitude", "latitude") for
    terrestrial, ("x", "y") for cartesian2d, and ("x", "y", "z")
    for cartesian3d.

    If there are no points, assume terrestrial.

    Arguments:
        points (sequence of TrajectoryPoint): List of all available points

    Returns:
        One of the above tuples of names
    """

    if len(points) == 0:
        return ("longitude", "latitude")

    first_point = points[0]
    if isinstance(first_point, terrestrial.TrajectoryPoint):
        return ("longitude", "latitude")
    if isinstance(first_point, cartesian2d.TrajectoryPoint):
        return ("x", "y")
    if isinstance(first_point, cartesian3d.TrajectoryPoint):
        return ("x", "y", "z")
    raise NotImplementedError("Unknown point domain in _guess_coordinate_names")


def _validate_domain_and_coordinate_columns(
        domain: str,
        coordinate_columns: list[str]
    ) -> None:
    """Helper function: check domain against number of coordinate columns

    This function makes sure the domain is valid and that the number of
    coordinate columns matches (3 for cartesian3d, 2 otherwise).

    Arguments:
        domain (str): Requested point domain
        coordinate_columns (list[str]): Names of coordinate columns

    Returns:
        None

    Raises:
        IndexError: Wrong number of coordinate columns specified for
            selected coordinate domain.
        NoSuchDomainError: You asked for a nonexistent point domain.

    """

    if domain in ["terrestrial", "cartesian2d"]:
        if len(coordinate_columns) != 2:
            raise tt_exceptions.WrongCoordinatesError(
                domain, 2, len(coordinate_columns)
                )
    elif domain == "cartesian3d":
        if len(coordinate_columns) != 3:
            raise tt_exceptions.WrongCoordinatesError(
                domain, 3, len(coordinate_columns)
                )
    else:
        raise tt_exceptions.NoSuchDomainError(domain)


def _validate_column_names(input_df: pd.DataFrame,
                           *requested_column_names):
    """Make sure all columns are present in the data frame

    Check all columns to make sure they're in the data frame.
    If not, raise KeyError.

    Arguments:
        input (Pandas DataFrame): DataFrame for checking
        *column_names (str): Column names to check

    Returns:
        None.

    Raises:
        KeyError: A column is missing
    """

    names_as_set = set(input_df.columns)

    for name in requested_column_names:
        if name not in names_as_set:
            raise tt_exceptions.MissingColumnError(name)


def _validate_timestamp_dtype(timestamp_column: pd.Series):
    """Make sure the supplied column contains timestamps

    Arguments:
        timestamp_column (pandas.Series): Column to check

    Returns:
        None

    Raises:
        TypeError: Column does not contain TZ-aware timestamps
        according to Pandas.
    """

    if not isinstance(timestamp_column.dtype, pd.DatetimeTZDtype):
        raise TypeError((
            f"Timestamp column {timestamp_column.name} must contain "
            "timezone-aware timestamps.  Found data type "
            f"{timestamp_column.dtype} instead."
        ))

