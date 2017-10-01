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

from __future__ import division, print_function

class DelimitedTextPointWriter(object):
    """Write points to a text file

    This class is the counterpart of DelimitedTextPointReader.  It
    writes a list of tracktable.core.TrajectoryPoint objects to a
    file.

    Attributes:
       field_map (dict): Map from column name to column index
       delimiter (character): String to put between columns
       include_header (boolean): Whether or not to write a header line with field names
       input (iterable): Iterable of points
       output (file): Where to write points
    """

    def __init__(self, output=None):
        """Allocate an uninitialized writer

        This writer will have an empty output (unless you specify
        one when you call the constructor) and a default field map
        (object_id, timestamp, longitude, latitude, heading, speed,
        altitude).

        Keyword Args:
           _output (file): Where to write output. Defaults to None.

        """

        self.delimiter = ','
        self.output = output
        self.field_map = {
            'object_id': 0,
            'timestamp': 1,
            'longitude': 2,
            'latitude': 3,
            'heading': 4,
            'speed': 5,
            'altitude': 6
        }
        self.include_header = True
        self.input = None

    # ----------------------------------------------------------------------

    def write(self):
        """Write points to the writer's output

        Raises:
          ValueError: the 'points' member is not set
          KeyError: the field map is empty
          FileError: the 'output' member is not set or
            something goes wrong while writing
        """

        def empty_field(point): return ''

        native_fields = set([ 'object_id',
                              'timestamp',
                              'longitude',
                              'latitude',
                              'altitude',
                              'heading',
                              'speed' ])

        print("debug: field map max value is {}".format(max(self.field_map.values())))

        accessors = [ ]
        for i in range(1 + max(self.field_map.values())):
            accessors.append(empty_field)

        def to_string(thing):
            if thing is None:
                return ''
            else:
                return str(thing)

        def make_property_accessor(field_name):
            if field_name in native_fields:
                def accessor(point):
                    return to_string(point.__getattribute__(field_name))
            else:
                def accessor(point):
                    try:
                        return to_string(point.properties[field_name])
                    except KeyError:
                        return ''
            return accessor

        for (field_name, column) in self.field_map.items():
            accessors[column] = make_property_accessor(field_name)

        if self.include_header:
            column_names = [ '(empty)' ] * len(accessors)
            for (name, value) in self.field_map.items():
                column_names[value] = name
            self.output.write('# ')
            self.output.write(self.delimiter.join(column_names))
            self.output.write('\n')

        for point in self.input:
            strings_for_row = [ accessor(point) for accessor in accessors ]
            self.output.write(self.delimiter.join(strings_for_row))
            self.output.write('\n')


    def set_output(self, outfile):
        """Supply an output sink

        Call this method to provide a pointer to the file-like object
        into which we will write our points.

        Args:
          outfile (file-like): Destination for points
        """

        self.output = outfile

    def set_input(self, point_iter):
        self.input = point_iter
