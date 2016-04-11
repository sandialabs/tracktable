# Copyright (c) 2014, Sandia Corporation.
# All rights reserved.
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

import codecs
import csv
import sys

from tracktable.io.writer import DelimitedTextPointWriter
from tracktable.io.reader import DelimitedTextPointReader

def test_point_writer(in_filename, out_filename):
    # This function expects to be called on Points1000.tsv.
    with codecs.open(in_filename, 'r', 'utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')

        point_reader = DelimitedTextPointReader()
        point_reader.input = reader
        point_reader.field_map = {
            'object_id': 0,
            'timestamp': 1,
            'latitude': 2,
            'longitude': 3,
            'altitude': 4,
            'heading': 5,
            'speed': 8
        }

        with codecs.open(out_filename, 'w', 'utf-8') as outfile:
            writer = DelimitedTextPointWriter()
            writer.set_output(outfile)
            writer.field_map = {
                'object_id': 0,
                'timestamp': 1,
                'latitude': 2,
                'longitude': 3,
                'altitude': 4,
                'heading': 5,
                'speed': 8
            }
            writer.delimiter = ','
            writer.input = point_reader

            writer.write()

    return 0

def main():
    return test_point_writer(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    sys.exit(main())


