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

# This file contains a test case for tracktable.geomath.speed_between.
#
from __future__ import print_function

import datetime
import math
import sys

from tracktable.core import geomath
from tracktable.domain import terrestrial, cartesian2d, cartesian3d


def test_speed_between(point1, point2, expected_result):
    actual_result = geomath.speed_between(point1, point2)
    if math.fabs(actual_result - expected_result) > 0.01:
        print(('ERROR: test_speed_between: Expected result for points of '
               'type {} to be {} but got {} instead').format(
                    type(point1),
                    expected_result,
                    actual_result),
              file=sys.stderr)
        return 1
    else:
        return 0


def main():
    error_count = 0

    start_time = datetime.datetime(year=2010, month=1, day=1, hour=0, minute=0, second=0)
    end_time = start_time + datetime.timedelta(hours=1)

    point1 = terrestrial.TrajectoryPoint(0, 0)
    point2 = terrestrial.TrajectoryPoint(50, 0)
    point1.timestamp = start_time
    point2.timestamp = end_time
    error_count += test_speed_between(point1, point2, 5559.7463)

    point1 = cartesian2d.TrajectoryPoint(0, 0)
    point2 = cartesian2d.TrajectoryPoint(50, 0)
    point1.timestamp = start_time
    point2.timestamp = end_time
    error_count += test_speed_between(point1, point2, 50.0/3600.0)

    point1 = cartesian3d.TrajectoryPoint(0, 0, 0)
    point2 = cartesian3d.TrajectoryPoint(50, 0, 0)
    point1.timestamp = start_time
    point2.timestamp = end_time
    error_count += test_speed_between(point1, point2, 50.0/3600.0)

    return error_count


if __name__ == '__main__':
    sys.exit(main())