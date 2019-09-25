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

"""example_point_reader - Common code to configure a DelimitedText point reader
"""

from tracktable.domain import all_domains as ALL_DOMAINS
from tracktable.script_helpers.argument_groups import extract_arguments

import importlib
import itertools

# ----------------------------------------------------------------------

def example_point_reader():

    '''To create a point, we create a generic TrajectoryPointReader object and give it the following:
    input file - File stream connected to a data file  delimiter - The character separating fields in the fileie, a csv will have ',' as a delimiter)
    comment character - The character marking comments in the file and will be ignored by the point reader
    domain - Which domain the points come from. Options are 'terrestrial', 'Cartesian2d', and 'Cartesian3d'''

    inFile = open('./data/SampleASDI.csv')
    domain = 'terrestrial'                 # we want to create a terrestrial point reader
    
    if domain.lower() not in ALL_DOMAINS:  #Format domain and make sure it is an available domain
        raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(domain, ', '.join(ALL_DOMAINS)))
    else:
        domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
        domain_module = importlib.import_module(domain_to_import)

    reader = domain_module.TrajectoryPointReader()
    reader.input = inFile
    reader.comment_character = '#'
    reader.field_delimiter = ','
    
    # In order to view the points the reader has read, we iterate over the reader. 
    for x in reader:
        print(x)
        
    '''So what happens in the background?
    The reader has several attributes that can be set. Some of these attributes are:
     object_id_column - Column in dataset holding the object id
     timestamp_column - Column in dataset holding the timestamp
     coordinate0 - Column in dataset holding the longitude
     coordinate1 - Column in dataset holding the latitude
     coordinate2 - Column in dataset holding the z-order

    Note: Coordinates are referenced like a list and there are three, coordinates[0], coordinates[1], and coordinates[2] representing longitude, latitude, and z-order respectively.
    In addition to these attributes, custom columns can be set such as 'altitude', 'speed', 'airline', etc so long as it is numeric, timestamp, or string. Any columns not given values will be assigned the default, or 'None'. 

    In the next example, we set a numeric field (speed) and a string field(status) and see the results.'''
    
    inFile.close()
      
    
    inFile = open('./data/SampleASDI.csv')
    reader.input = inFile
    reader.object_id_column = 0
    reader.timestamp_column = 1
    reader.coordinates[0] = 2
    reader.coordinates[1] = 3
    reader.set_real_field_column('speed', 4)
    reader.set_string_field_column('status', 9)
    
    for x in reader:
        print(x)

    inFile.close()
# ----------------------------------------------------------------------

def configure_point_reader(infile, **kwargs):
    """Set up a TrajectoryPointReader for terrestrial points.

    Args:
        infile: An open file or file-like object containing the input.
        delimiter: A single character that separates fields.
        comment_character: Lines where this character is the first
            non-whitespace character will be ignored.
        coordinate_map: Map from coordinate number to column number.
        field_map: Mapping from field name to column number.  See below
            for more details.

    Returns:
        The ready-to-use point reader.  In order to actually retrieve
        the points, iterate over the contents of 'reader'.


    \note Coordinate Map

    You must tell the reader how to populate coordinates by supplying
    a coordinate->column map.  Here is how you would tell it to use
    columns 10 and 11 for longitude and latitude (coordinates 0 and
    1)::

    coordinate0 = 10
    coordinate1 = 11

    \note Field Map

    TrajectoryPoints can take named fields such as 'object_id',
    'timestamp', 'altitude', 'airline_name', 'paint_color',
    'time_plane_first_turned_on'... pretty much anything that can take
    a string, numeric or timestamp value.  These are populated from
    columns in the file just like coordinates are.  Here is an example:

    field_map = dict()
    field_map["object_id"] = 0
    field_map["timestamp"] = 1
    field_map["altitude"] = 4
    field_map["speed"] = 5
    field_map["airline_name"] = 6

    TrajectoryPoint has 'object_id' and 'timestamp' as class members
    accessed with 'my_point.object_id' and 'my_point.timestamp'.  All
    other named properties are accessed as
    'my_point.properties["prop_name"]'.

    """

    reader_args = extract_arguments('delimited_text_point_reader', kwargs)

    print("Arguments after extract(): {}".format(reader_args))

    domain = reader_args['domain']
    if domain.lower() not in ALL_DOMAINS:
        raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(
            domain, ', '.join(ALL_DOMAINS)))
    else:
        domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
        domain_module = importlib.import_module(domain_to_import)

    reader = domain_module.TrajectoryPointReader()
    reader.input = infile
    reader.comment_character = reader_args['comment_character']
    reader.field_delimiter = reader_args['delimiter']

    if reader_args['object_id_column'] is not None:
        reader.object_id_column = reader_args['object_id_column']

    if reader_args['timestamp_column'] is not None:
        reader.timestamp_column = reader_args['timestamp_column']

    if reader_args['coordinate0'] is not None:
        reader.coordinates[0] = int(reader_args['coordinate0'])

    if reader_args['coordinate1'] is not None:
        reader.coordinates[1] = int(reader_args['coordinate1'])

    if reader_args['coordinate2'] is not None:
        reader.coordinates[2] = int(reader_args['coordinate2'])

    if (reader_args['string_field_column'] is not None and
        len(reader_args['string_field_column']) > 0):
        for (field, column) in group(reader_args['string_field_column'], 2):
            reader.string_fields[field] = column

    if (reader_args['time_field_column'] is not None and
        len(reader_args['time_field_column']) > 0):
        for (field, column) in group(reader_args['time_field_column'], 2):
            reader.time_fields[field] = column

    if (reader_args['numeric_field_column'] is not None and
        len(reader_args['numeric_field_column']) > 0):
        for (field, column) in group(reader_args['numeric_field_column'], 2):
            reader.numeric_fields[field] = column

    return reader

# ----------------------------------------------------------------------
# Utility function for reading groups of elements from an iterable

def group(iterable, howmany, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"

    # group('ABCDEFG', 3, 'x') -> ABC DEF Gxx
    args = [ iter(iterable) ] * howmany
    return izip_longest(fillvalue=fillvalue, *args)
