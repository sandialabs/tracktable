# Copyright (c) 2014-2025 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
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


"""Tests for data_frame_from_points and points_from_data_frame
"""

import datetime
import pathlib
import zoneinfo

import pandas as pd
import pytest

from tracktable.domain import terrestrial, cartesian2d, cartesian3d
from tracktable.rw import data_frame as tt_data_frame
from tracktable.core import test_utilities
from tracktable.core import exceptions as tt_exceptions


@pytest.fixture
def test_data_path(tracktable_data_path: pathlib.Path) -> pathlib.Path:
    return tracktable_data_path / "internal_test_data"


@pytest.fixture
def sample_csv_df(test_data_path: pathlib.Path) -> pd.DataFrame:
    sample_csv = test_data_path / "Points" / "SampleFlightsUS.csv"
    sample_df = pd.read_csv(sample_csv)
    sample_df["string_property"] = sample_df["object_id"]
    sample_df["timestamp_property"] = sample_df["timestamp"]
    sample_df["float_property"] = sample_df["longitude"]

    return sample_df


@pytest.fixture
def sample_csv_df_with_timestamps(sample_csv_df) -> pd.DataFrame:
    my_df = sample_csv_df.copy()
    my_df["timestamp_as_string"] = my_df["timestamp"]
    my_df["timestamp"] = pd.to_datetime(
        my_df["timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        utc=True
        )
    my_df["timestamp_property"] = my_df["timestamp"]
    return my_df


@pytest.fixture
def sample_csv_points(test_data_path: pathlib.Path) -> list[terrestrial.TrajectoryPoint]:
    """Make TrajectoryPoints from SampleUSFlights.csv."""

    with open(test_data_path / "Points" / "SampleFlightsUS.csv") as infile:
        reader = terrestrial.TrajectoryPointReader()
        reader.input = infile
        reader.object_id_column = 0
        reader.timestamp_column = 1
        reader.coordinates[0] = 2
        reader.coordinates[1] = 3
        reader.set_real_field_column("heading", 4)
        reader.set_real_field_column("altitude", 5)
        reader.set_real_field_column("speed", 6)

        all_points = list(reader)

    # Add properties of each type to better exercise the converter
    for point in all_points:
        point.properties["string_property"] = point.object_id
        point.properties["timestamp_property"] = point.timestamp
        point.properties["float_property"] = point[0]

    return all_points

# These would be good candidates to move up into conftest.py

@pytest.fixture
def sample_object_id() -> str:
    return "my_object_id"

@pytest.fixture
def albuquerque_coordinates() -> list[float]:
    return [35.106, -106.629]

@pytest.fixture
def sample_timestamp() -> datetime.datetime:
    return datetime.datetime(year=2025, month=8, day=9,
                             hour=2, minute=12,
                             tzinfo=zoneinfo.ZoneInfo("UTC"))

@pytest.fixture
def sample_string_property() -> str:
    return "jabberwocky"

@pytest.fixture
def sample_float_property() -> float:
    return 3.14159

@pytest.fixture
def sample_timestamp_property() -> datetime.datetime:
    # that's one small step for a man...
    return datetime.datetime(year=1969, month=7, day=20,
                             hour=2, minute=56, second=15,
                             tzinfo=zoneinfo.ZoneInfo("UTC"))


@pytest.fixture
def sample_terrestrial_point(albuquerque_coordinates,
                             sample_object_id,
                             sample_timestamp,
                             sample_string_property,
                             sample_float_property,
                             sample_timestamp_property) -> terrestrial.TrajectoryPoint:
    my_point = terrestrial.TrajectoryPoint()
    my_point.object_id = sample_object_id
    my_point[0] = albuquerque_coordinates[0]
    my_point[1] = albuquerque_coordinates[1]
    my_point.timestamp = sample_timestamp
    my_point.properties["string_property"] = sample_string_property
    my_point.properties["float_property"] = sample_float_property
    my_point.properties["timestamp_property"] = sample_timestamp_property

    return my_point


@pytest.fixture
def sample_cartesian2d_point(albuquerque_coordinates,
                             sample_object_id,
                             sample_timestamp,
                             sample_string_property,
                             sample_float_property,
                             sample_timestamp_property) -> cartesian2d.TrajectoryPoint:
    my_point = cartesian2d.TrajectoryPoint()
    my_point.object_id = sample_object_id
    my_point[0] = albuquerque_coordinates[0]
    my_point[1] = albuquerque_coordinates[1]
    my_point.timestamp = sample_timestamp
    my_point.properties["string_property"] = sample_string_property
    my_point.properties["float_property"] = sample_float_property
    my_point.properties["timestamp_property"] = sample_timestamp_property

    return my_point


@pytest.fixture
def sample_cartesian3d_coordinates() -> list[float]:
    return [1.2, 3.4, 5.6]


@pytest.fixture
def sample_cartesian3d_point(sample_cartesian3d_coordinates,
                             sample_object_id,
                             sample_timestamp,
                             sample_string_property,
                             sample_float_property,
                             sample_timestamp_property) -> cartesian3d.TrajectoryPoint:
    my_point = cartesian3d.TrajectoryPoint()
    my_point.object_id = sample_object_id
    my_point[0] = sample_cartesian3d_coordinates[0]
    my_point[1] = sample_cartesian3d_coordinates[1]
    my_point[2] = sample_cartesian3d_coordinates[2]
    my_point.timestamp = sample_timestamp
    my_point.properties["string_property"] = sample_string_property
    my_point.properties["float_property"] = sample_float_property
    my_point.properties["timestamp_property"] = sample_timestamp_property

    return my_point

# Also need sample_trajectories fixture - this is probably written elsewhere

def test_points_from_df_sample_csv(sample_csv_df_with_timestamps,
                                   sample_csv_points):

    # Convert the timestamp column to actual timestamps
    my_df = sample_csv_df_with_timestamps

    df_points = list(
        tt_data_frame.read_points_from_data_frame(
            my_df,
            object_id_column="object_id",
            timestamp_column="timestamp",
            coordinate_columns=["longitude", "latitude"],
            property_columns=["speed", "altitude", "heading",
                              "string_property", "timestamp_property",
                              "float_property"]
        ))

    assert len(df_points) == len(sample_csv_points)
    which_point = 0
    for (df_point, ground_truth_point) in zip(df_points, sample_csv_points):
        assert test_utilities.points_equal(df_point, ground_truth_point)
        which_point += 1


def test_points_from_df_missing_column_requested(sample_csv_df_with_timestamps):
    """Make sure an exception gets raised when we ask for a nonexistent column
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.MissingColumnError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="NONEXISTENT_COLUMN",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                    "string_property", "timestamp_property",
                                    "float_property"]
            ))
    assert e.value.column_name == "NONEXISTENT_COLUMN"


def test_points_from_df_nonexistent_domain(sample_csv_df_with_timestamps):
    """Wrong point domain raises exception
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.NoSuchDomainError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"],
                domain="NO_SUCH_DOMAIN"
        ))
    assert e.value.domain_name == "NO_SUCH_DOMAIN"



def test_points_from_df_not_enough_coordinates_terrestrial(sample_csv_df_with_timestamps):
    """1 coordinate for terrestrial raises WrongCoordinatesError
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.WrongCoordinatesError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        ))
    assert e.value.domain == "terrestrial"
    assert e.value.expected_num == 2
    assert e.value.actual_num == 1


def test_points_from_df_too_many_coordinates_terrestrial(sample_csv_df_with_timestamps):
    """3 coordinates for terrestrial raises WrongCoordinatesError
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.WrongCoordinatesError) as e:
        _ = list(tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude", "altitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        ))
    assert e.value.domain == "terrestrial"
    assert e.value.expected_num == 2
    assert e.value.actual_num == 3


def test_points_from_df_not_enough_coordinates_cartesian2d(sample_csv_df_with_timestamps):
    """1 coordinate for cartesian2d raises WrongCoordinatesError
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.WrongCoordinatesError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"],
                domain="cartesian2d"
        ))
    assert e.value.domain == "cartesian2d"
    assert e.value.expected_num == 2
    assert e.value.actual_num == 1


def test_points_from_df_too_many_coordinates_cartesian2d(sample_csv_df_with_timestamps):
    """3 coordinates for cartesian2d raises WrongCoordinatesError
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.WrongCoordinatesError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude", "altitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"],
                domain="cartesian2d"
        ))
    assert e.value.domain == "cartesian2d"
    assert e.value.expected_num == 2
    assert e.value.actual_num == 3


def test_points_from_df_not_enough_coordinates_cartesian3d(sample_csv_df_with_timestamps):
    """2 coordinates for cartesian3d raises WrongCoordinatesError
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.WrongCoordinatesError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"],
                domain="cartesian3d"
        ))
    assert e.value.domain == "cartesian3d"
    assert e.value.expected_num == 3
    assert e.value.actual_num == 2


def test_points_from_df_too_many_coordinates_cartesian3d(sample_csv_df_with_timestamps):
    """4 coordinates for cartesian3d raises WrongCoordinatesError
    """

    my_df = sample_csv_df_with_timestamps

    with pytest.raises(tt_exceptions.WrongCoordinatesError) as e:
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude", "altitude", "heading"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"],
                domain="cartesian3d"
        ))
    assert e.value.domain == "cartesian3d"
    assert e.value.expected_num == 3
    assert e.value.actual_num == 4


def test_validate_timestamp_dtype(sample_csv_df_with_timestamps):
    """Ensure that we raise an exception if timestamps aren't timestamps"""


    my_df = sample_csv_df_with_timestamps

    with pytest.raises(TypeError):
        _ = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp_as_string",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        ))


def test_nulls_in_important_columns(sample_csv_df_with_timestamps,
                                    sample_csv_points):
    """Make sure that nulls in important columns just cause rows to be ignored"""

    my_df = sample_csv_df_with_timestamps
    # These four should cause points to be ignored
    my_df["object_id"].iat[0] = pd.NA
    my_df["timestamp"].iat[1] = pd.NA
    my_df["longitude"].iat[2] = pd.NA
    my_df["latitude"].iat[3] = pd.NA
    # These should go through OK
    my_df["string_property"].iat[4] = pd.NA
    my_df["timestamp_property"].iat[5] = pd.NA
    my_df["float_property"].iat[6] = pd.NA

    surviving_points = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        ))
    assert len(surviving_points) == len(sample_csv_points) - 4


def test_na_translation(sample_csv_df_with_timestamps,
                        sample_csv_points):
    """Make sure that nulls in properties get translated to None"""

    my_df = sample_csv_df_with_timestamps
    # These should go through OK
    my_df["string_property"].iat[0] = pd.NA
    my_df["timestamp_property"].iat[0] = pd.NA
    my_df["float_property"].iat[0] = pd.NA

    surviving_points = list(
            tt_data_frame.read_points_from_data_frame(
                my_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        ))

    my_point = surviving_points[0]
    assert my_point.properties["string_property"] is None
    assert my_point.properties["timestamp_property"] is None
    assert my_point.properties["float_property"] is None
    assert len(surviving_points) == len(sample_csv_points)


def test_many_points_to_data_frame(sample_csv_df_with_timestamps):
    """Test write_points_to_data_frame

    The real test is if we can write points to a data frame,
    read them back out, and get the same points back.
    """

    original_df = sample_csv_df_with_timestamps
    first_pass_points = list(
        tt_data_frame.read_points_from_data_frame(
                original_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        )
    )

    intermediate_df = tt_data_frame.write_points_to_data_frame(first_pass_points)

    second_pass_points = list(
        tt_data_frame.read_points_from_data_frame(
                intermediate_df,
                object_id_column="object_id",
                timestamp_column="timestamp",
                coordinate_columns=["longitude", "latitude"],
                property_columns=["speed", "altitude", "heading",
                                "string_property", "timestamp_property",
                                "float_property"]
        )
    )

    assert(len(first_pass_points) == len(second_pass_points))

    which_point = 0
    for (original_point, new_point) in zip(first_pass_points, second_pass_points):
        assert test_utilities.points_equal(original_point, new_point)
        which_point += 1


def test_empty_points_to_data_frame():
    points = []
    df = tt_data_frame.write_points_to_data_frame(points)
    assert len(df) == 0
    assert "object_id" in df.columns
    assert "timestamp" in df.columns
    # When we can't find any points we default to terrestrial
    assert "longitude" in df.columns
    assert "latitude" in df.columns


def test_cartesian2d_point_to_data_frame(sample_cartesian2d_point):

    point = sample_cartesian2d_point
    df = tt_data_frame.write_points_to_data_frame([point])
    assert len(df) == 1

    restored_point = list(
        tt_data_frame.read_points_from_data_frame(
            df,
            object_id_column="object_id",
            timestamp_column="timestamp",
            coordinate_columns=["x", "y"],
            property_columns=["string_property",
                              "float_property",
                              "timestamp_property"],
            domain="cartesian2d"
        )
    )[0]

    assert test_utilities.points_equal(point, restored_point)



def test_cartesian3d_point_to_data_frame(sample_cartesian3d_point):

    point = sample_cartesian3d_point
    df = tt_data_frame.write_points_to_data_frame([point])
    assert len(df) == 1

    restored_point = list(
        tt_data_frame.read_points_from_data_frame(
            df,
            object_id_column="object_id",
            timestamp_column="timestamp",
            coordinate_columns=["x", "y", "z"],
            property_columns=["string_property",
                              "float_property",
                              "timestamp_property"],
            domain="cartesian3d"
        )
    )[0]

    assert test_utilities.points_equal(point, restored_point)

