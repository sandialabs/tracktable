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

from tracktable.domain import cartesian2d as c2d, terrestrial as terr, cartesian3d as c3d
from tracktable.core.geomath import geometric_median
from six.moves import range

import sys

def test_median(point_type):
    points = []
    for i in range(9):
        next_point = point_type()
        for d in range(len(next_point)):
            next_point[d] = 0
        next_point[0] = i
        points.append(next_point)

    median = geometric_median(points)
    if median != points[4]:
        print("ERROR testing geometric median: Expected median to be {} but was instead {}".format(str(points[4]), str(median)))
        return 1
    else:
        return 0

def main():
    error_count = 0
    for point_type in [
            c2d.BasePoint, c2d.TrajectoryPoint,
            terr.BasePoint, terr.TrajectoryPoint,
            c3d.BasePoint, c3d.TrajectoryPoint
            ]:
        error_count += test_median(point_type)

    return error_count

if __name__ == '__main__':
    sys.exit(main())
