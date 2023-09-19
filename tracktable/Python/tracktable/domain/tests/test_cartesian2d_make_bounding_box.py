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

from __future__ import print_function, division
import sys

from tracktable.domain import cartesian2d

def test_make_bounding_box():
    min_corner_base = cartesian2d.BasePoint(12, 34)
    max_corner_base = cartesian2d.BasePoint(56, 78)

    min_corner_trajectory = cartesian2d.TrajectoryPoint(12, 34)
    max_corner_trajectory = cartesian2d.TrajectoryPoint(56, 78)

#    bbox1 = cartesian2d.make_bounding_box(min_corner=(12, 34), max_corner=(56, 78))
    bbox2 = cartesian2d.BoundingBox([12, 34], [56, 78])
    bbox3 = cartesian2d.BoundingBox((12, 34), (56, 78))
    bbox4 = cartesian2d.BoundingBox(min_corner_base, max_corner_base)
    bbox5 = cartesian2d.BoundingBox(min_corner_trajectory, max_corner_trajectory)

#    print("make_bounding_box: {} {}".format(str(bbox1), repr(bbox1)))
    print("BoundingBox(list): {} {}".format(str(bbox2), repr(bbox2)))
    print("BoundingBox(tuples): {} {}".format(str(bbox3), repr(bbox3)))
    print("BoundingBox(BasePoint): {} {}".format(str(bbox4), repr(bbox4)))
    print("BoundingBox(TrajectoryPoint): {} {}".format(str(bbox5), repr(bbox5)))

    return 0


def main():
    return test_make_bounding_box()

if __name__ == '__main__':
    sys.exit(main())
