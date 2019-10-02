#
# Copyright (c) 2014-2019 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""tracktable.io.point: Readers and writers for points

Here you will find convenience functions for instantiating and
configuring point readers (trajectory points or base points)
given the name of the domain and the parameters you want to apply.

TODO: Add support for point writers as well.
"""

from tracktable.domain import select_domain_from_name

def trajectory_point_reader(
    infile,
    comment_character='#',
    domain='terrestrial',
    delimiter=',',
    object_id_column=0,
    timestamp_column=1,
    longitude_column=2,
    latitude_column=3,
    x_column=2,
    y_column=3,
    z_column=4, 
    string_fields=dict(),
    real_fields=dict(),
    time_fields=dict()
    ):
    """Instantiate and configure a trajectory point reader.

    Tracktable point readers live in the domain modules:
    `tracktable.domain.<domain_name>.TrajectoryPointReader`
    where `domain_name` is one of `terrestrial`, `cartesian2d`
    or `cartesian3d`.  This is a convenience function to set 
    one up.

    A trajectory point must have all of the following elements:

    1.  An object ID.  We use the object ID to group points into 
        trajectories.
    2.  A timestamp.  For the purposes of this function, that timestamp
        must be in the format 'YYYY-mm-dd HH:MM:SS' where YYYY is the 
        4-digit year, mm is the 2-digit month, dd is the 2-digit day of
        the month, and HH:MM:SS are the 2-digit hours, minutes, and 
        seconds within the day, respectively.
    3.  Coordinates.  For the terrestrial domain, these coordinates are
        longitude and latitude.  For the cartesian2d domain, these are
        x and y.  The cartesian3d domain adds z.

    By default, we look for the object ID in column 0, the timestamp in
    column 1, longitude (or x) in column 2, latitude (or y) in column 3,
    and the Z coordinate in column 4.  We only pay attention to the 
    coordinate assignments for the selected point domain.

    You may also specify other fields to be added to each point.  See the
    documentation for the `string_fields`, `real_fields` and `time_fields`
    keyword arguments.

    This function will probably move into the main library at some point 
    soon.  We will keep a binding here to avoid breaking existing code.

    Arguments:
        infile {file-like object}: Source for trajectory point data

    Keyword arguments:
        comment_character {character}: Any row where this is the first
            non-whitespace character will be ignored.  (default '#')
        delimiter {character}: What character separates columns? 
            (default ',')
        domain {string}: Which point domain will the points belong to? 
            (default 'terrestrial')
        object_id_column {int}: Which column contains the object ID 
            (default 0)
        timestamp_column {int}: Which column contains the timestamp 
            (default 1)
        longitude_column {int}: Which column contains the longitude for
            each point? (default 2, assumes terrestrial domain)
        latitude_column {int}: Which column contains the latitude for
            each point? (default 3, assumes terrestrial domain)
        x_column {int}: Which column contains the X coordinate for
            each point? (default 2, assumes cartesian2d or cartesian3d)
        y_column {int}: Which column contains the Y coordinate for
            each point? (default 3, assumes cartesian2d or cartesian3d)
        z_column {int}: Which column contains the X coordinate for
            each point? (default 4, assumes cartesian3d)
        string_fields {dict, int -> string}: Columns in the input that
            should be attached to each point as a string.  The keys
            in this dictionary are column numbers.  Their corresponding
            values are the name of the field that will be added to
            the point's properties. (default: empty)
        real_fields {dict, int -> string}: Columns in the input that
            should be attached to each point as a real number.  The keys
            in this dictionary are column numbers.  Their corresponding
            values are the name of the field that will be added to
            the point's properties. (default: empty)
        time_fields {dict, int -> string}: Columns in the input that
            should be attached to each point as a timestamp.  The keys
            in this dictionary are column numbers.  Their corresponding
            values are the name of the field that will be added to
            the point's properties. The timestamps must be in the same
            format as for the point as a whole, namely `YYYY-mm-dd HH:MM:SS`.
            (default: empty)
    
    Returns:
        Trajectory point reader from the appropriate domain with all fields
        configured according to arguments.  Iterate over the reader object
        to retrieve the points.
    """

    domain_module = select_domain_from_name(domain)
    reader = domain_module.TrajectoryPointReader()
    reader.input = infile

    _configure_reader_coordinates(
        reader,
        domain.lower(),
        longitude_column=longitude_column,
        latitude_column=latitude_column,
        x_column=x_column,
        y_column=y_column,
        z_column=z_column
        )

    _configure_reader_trajectory_point_fields(
        reader,
        object_id_column=object_id_column,
        timestamp_column=timestamp_column,
        string_fields=string_fields,
        real_fields=real_fields,
        time_fields=time_fields
        )

    _configure_reader_file_properties(
        reader,
        comment_character=comment_character,
        delimiter=delimiter
        )

    return reader

# ---------------------------------------------------------------------


def base_point_reader(
    infile,
    comment_character='#',
    domain='terrestrial',
    delimiter=',',
    object_id_column=0,
    timestamp_column=1,
    longitude_column=2,
    latitude_column=3,
    x_column=2,
    y_column=3,
    z_column=4, 
    string_fields=dict(),
    real_fields=dict(),
    time_fields=dict()
    ):
    """Instantiate and configure an undecoated point reader.

    Tracktable point readers live in the domain modules:
    `tracktable.domain.<domain_name>.PointReader`
    where `domain_name` is one of `terrestrial`, `cartesian2d`
    or `cartesian3d`.  This is a convenience function to set 
    one up.

    A base (undecorated) point must have all of the following elements:

    1.  Coordinates.  For the terrestrial domain, these coordinates are
        longitude and latitude.  For the cartesian2d domain, these are
        x and y.  The cartesian3d domain adds z.

    By default, we expect longitude (or x) in column 2, latitude (or y) 
    in column 3, and the Z coordinate in column 4.  We only pay attention 
    to the coordinate assignments for the selected point domain.

    The difference between base points and trajectory points is that base
    points don't have an object ID, a timestamp, or any metadata fields:
    just coordinates.

    This function will probably move into the main library at some point 
    soon.  We will keep a binding here to avoid breaking existing code.

    Arguments:
        infile {file-like object}: Source for trajectory point data

    Keyword arguments:
        comment_character {character}: Any row where this is the first
            non-whitespace character will be ignored.  (default '#')
        delimiter {character}: What character separates columns? 
            (default ',')
        domain {string}: Which point domain will the points belong to? 
            (default 'terrestrial')
        longitude_column {int}: Which column contains the longitude for
            each point? (default 2, assumes terrestrial domain)
        latitude_column {int}: Which column contains the latitude for
            each point? (default 3, assumes terrestrial domain)
        x_column {int}: Which column contains the X coordinate for
            each point? (default 2, assumes cartesian2d or cartesian3d)
        y_column {int}: Which column contains the Y coordinate for
            each point? (default 3, assumes cartesian2d or cartesian3d)
        z_column {int}: Which column contains the X coordinate for
            each point? (default 4, assumes cartesian3d)
    
    Returns:
        Base point reader from the appropriate domain with all fields
        configured according to arguments.  Iterate over the reader object
        to retrieve the points.
    """

    domain_module = select_domain_from_name(domain)
    reader = domain_module.BasePointReader()
    reader.input = infile
    _configure_reader_file_properties(
        reader,
        comment_character=comment_character,
        delimiter=delimiter
        )
    _configure_reader_coordinates(
        reader,
        domain.lower(),
        x_column=x_column,
        y_column=y_column,
        z_column=z_column,
        longitude_column=longitude_column,
        latitude_column=latitude_column)

    return reader

###
### Below this point are the utility functions that apply arguments 
### to readers.
###

def _configure_reader_trajectory_point_fields(
    reader,
    object_id_column=0,
    timestamp_column=1,
    string_fields=dict(),
    real_fields=dict(),
    time_fields=dict()
    ):

    """Configure a point reader to load metadata fields
    
    This is a utility function.  See the arguments for 
    configure_trajectory_point_reader for information on
    the parameters here.
    """

    reader.object_id_column = object_id_column
    reader.timestamp_column = timestamp_column

    for (field, column) in string_fields.items():
        reader.set_string_field_column(field, column)
    
    for (field, column) in real_fields.items():
        reader.set_real_field_column(field, column)

    for (field, column) in time_fields.items():
        reader.set_time_field_column(field, column)


def _configure_reader_coordinates(
    reader,
    domain,
    **kwargs):
    """Configure coordinate fields on a point reader

    This is a utility function.  This is where we select
    which coordinate arguments the reader should have.

    """

    if domain == 'terrestrial':
        reader.coordinates[0] = kwargs['longitude_column']
        reader.coordinates[1] = kwargs['latitude_column']
    elif domain in ['cartesian2d', 'cartesian3d']:
        reader.coordinates[0] = kwargs['x_column']
        reader.coordinates[1] = kwargs['y_column']
        if domain == 'cartesian3d':
            reader.coordinates[2] = kwargs['z_column']
    else:
        raise KeyError('Unsupported domain: {}'.format(domain))
    

def _configure_reader_file_properties(reader,                        
                                      comment_character='#',
                                      delimiter=','):
   
    """Configure delimiter and comment character for a reader

    This is a utility function.
    """
    reader.comment_character = comment_character
    reader.delimiter = delimiter



