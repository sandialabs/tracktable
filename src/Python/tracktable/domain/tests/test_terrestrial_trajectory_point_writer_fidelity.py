#
# Copyright (c) 2014-2023 National Technology and Engineering
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

from __future__ import print_function, division, absolute_import

from six.moves import range
import io
import random
import sys

from tracktable.domain.terrestrial import TrajectoryPoint, TrajectoryPointWriter, TrajectoryPointReader
from tracktable.core import Timestamp
from tracktable.core.test_utilities import version_appropriate_string_buffer
import datetime

from . import create_points_and_trajectories as tt_generators

# ----------------------------------------------------------------------

def write_points_to_string(points):
    output = version_appropriate_string_buffer()

    print("Point list contains {} entries".format(len(points)))
    writer = TrajectoryPointWriter(output)
    writer.write(points)

    result = output.getvalue()
    print("Length of result string: {}".format(len(result)))
    return result

# ----------------------------------------------------------------------

def read_points_from_string(text):
    print("Input text:\n{}(end)".format(text))

    input = version_appropriate_string_buffer(text)

    reader = TrajectoryPointReader(input)
    points = list(reader)
    return points

# ----------------------------------------------------------------------

def main():
    random.seed(0)

    num_points = 10
    original_points = tt_generators.generate_random_points(TrajectoryPoint,
                                                           num_points,
                                                           num_point_properties=6)

    points_as_string = write_points_to_string(original_points)

    reconstituted_points = read_points_from_string(points_as_string)


    if len(original_points) != len(reconstituted_points):
        print("ERROR: Original point array contains {} points.  Reconstituted array contains {}.".format(len(original_points), len(reconstituted_points)))
        return 1

    num_errors = 0
    for i in range(num_points):
        if original_points[i] != reconstituted_points[i]:
            print("ERROR: Point {} was not reconstituted successfully.".format(i))
            print("Original point ({}, type {}):\n{}".format(repr(original_points[i]), type(original_points[i]), str(original_points[i])))
            print("Reconstituted point ({}, type {}):\n{}".format(repr(reconstituted_points[i]), type(original_points[i]), str(reconstituted_points[i])))
            num_errors += 1

    return (num_errors != 0)

if __name__ == '__main__':
    sys.exit(main())
