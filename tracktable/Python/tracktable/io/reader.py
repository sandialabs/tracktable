#
# Copyright (c) 2014-2017 National Technology and Engineering
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

"""
tracktable.io.reader - Read points from various lower-level sources
"""

from tracktable.core import TrajectoryPoint, Timestamp
import pprint
# import traceback


class DelimitedTextPointReader(object):
    """Read points from a delimited text file

    This class is an adapter that clamps onto a CSV reader and
    produces a sequence of points.  To use it you must supply an
    appropriately configured CSV reader and some information on how to
    map between the CSV output and the point class that you want.  To
    be specific, you must supply the following things:

    - An input source: This must be an iterable that produces lists of
      values.  You can do this with the standard Python class
      csv.CSVReader or with your own code.

    - A field map: This must be a dict that maps from attribute names
      ('object_id', 'timestamp', etc) to indices in the list of values
      produced by the input.  The attributes 'object_id', 'timestamp',
      'longitude', 'latitude', 'heading', 'speed' and 'altitude'
      correspond to built-in fields in Tracktable's TrajectoryPoint
      class.  Any other fields will be stored as named properties.

    You get access to the list of parsed points via the output()
    method.  This will be a generator instead of a list so that we
    don't have to load the whole (potentially enormous) file into
    memory at once.  As with every other iterable in Python you can
    loop over it by saying 'for my_point in reader.output()' or
    collect it into a list by saying 'foo = list(reader.output())'

    Attributes:
      input (csv.reader): Python CSV reader for file
      field_map (dict): Map from field names to integers (column IDs in input).  You must supply values for 'object_id', 'longitude', 'latitude' and 'timestamp'.  An 'altitude' column and other properties are optional.

    """

    def __init__(self):
        """Initialize an empty point reader."""
        self.input = None
        self.field_map = { 'object_id': 0,
                           'timestamp': 1,
                           'longitude': 2,
                           'latitude': 3 }

    def __iter__(self):
        """Set up parsing pipeline as an iterator

        This is a standard Python method that gets called when you
        execute a line of code like 'for x in foo:'.  It means
        "prepare to generate values".  In our case, it is a signal to
        set up the pipeline that will yield points.

        Raises:
          ValueError: the input source is missing or the field map is incomplete.
        """

        if self.input is None:
            raise ValueError('You must set the input attribute on DelimitedTextPointSource before calling output().')

        if self.field_map is None:
            raise ValueError('You must supply a field map from column index to attribute name before calling DelimitedTextPointSource.output().')

        # We have to have at least these entries in the field map
        longitude_found = False
        latitude_found = False
        timestamp_found = False
        object_id_found = False

        for (name, column_id) in self.field_map.items():
            if name == 'longitude':
                longitude_found = True
            if name == 'latitude':
                latitude_found = True
            if name == 'timestamp':
                timestamp_found = True
            if name == 'object_id':
                object_id_found = True

        if not (longitude_found and latitude_found and timestamp_found and object_id_found):
            raise ValueError("The field map for DelimitedTextPointReader must contain entries for all of 'object_id', 'longitude', 'latitude' and 'timestamp'.\nMap contains {} entries: {}".format(len(self.field_map), pprint.pformat(self.field_map)))

        num_good_points = 0
        num_bad_points = 0
        num_lines = 0

        def do_nothing(field, point): pass

        column_handlers = []
        for i in range(1 + max(self.field_map.values())):
            column_handlers.append((i, do_nothing))

        native_fields = set([ 'object_id',
                              'timestamp',
                              'longitude',
                              'latitude',
                              'altitude',
                              'speed',
                              'heading' ])

        field_coercion = {
            'object_id': str,
            'timestamp': Timestamp.from_any,
            'longitude': float,
            'latitude': float,
            'altitude': float,
            'speed': float,
            'heading': float
        }

        def make_column_handler(field_name):
            if field_name in native_fields:
                def handler(data, point):
                    point.__setattr__(field_name, field_coercion[field_name](data))
            else:
                def handler(data, point):
                    point.properties[field_name] = data

            return handler

        for (field_name, column_id) in self.field_map.items():
            column_handlers[column_id] = (column_id, make_column_handler(field_name))

        # Now that we have a handler for each column we can go through
        # the input and turn it into points.
        def make_point_generator():
            num_lines = 0
            num_good_points = 0
            num_bad_points = 0

            for next_line in self.input:
                num_lines += 1

                if num_lines % 10000 == 0:
                    print("STATUS: Read {} lines with {} good points and {} unusable.".format(num_lines, num_good_points, num_bad_points))
                try:
                    next_point = TrajectoryPoint()
                    for (i, column_handler) in column_handlers:
                        column_handler(next_line[i], next_point)
                    num_good_points += 1
                    yield(next_point)
                except (ValueError, IndexError):
                # print("object_id '{}', longitude '{}', latitude '{}', timestamp '{}'".format(next_line[object_id_column],
                #                                                                              next_line[longitude_column],
                #                                                                              next_line[latitude_column],
                #                                                                              next_line[timestamp_column]))
                # traceback.print_exc()
                    num_bad_points += 1

        return make_point_generator()
