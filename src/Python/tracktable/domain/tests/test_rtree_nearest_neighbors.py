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

from __future__ import absolute_import, division, print_function

import enum
import sys

from six.moves import range
from tracktable.domain.rtree import RTree
from tracktable.domain import feature_vectors as fv


class CreationMethod(enum.Enum):
    CONSTRUCTOR = 1
    ONE_POINT_AT_A_TIME = 2
    ALL_POINTS_AT_ONCE = 3


def test_nearest_neighbors(point_type,
                           rtree_creation=CreationMethod.CONSTRUCTOR):
    points = []

    for i in range(10):
        point = point_type()
        for d in range(len(point)):
            point[d] = i
        points.append(point)

    sample_point = point_type()
    for d in range(len(sample_point)):
        sample_point[d] = 4.5

    if rtree_creation == CreationMethod.CONSTRUCTOR:
        tree = RTree(points)
    elif rtree_creation == CreationMethod.ALL_POINTS_AT_ONCE:
        tree = RTree()
        tree.insert_points(points)
    elif rtree_creation == CreationMethod.ONE_POINT_AT_A_TIME:
        tree = RTree()
        for point in points:
            tree.insert_point(point)
    else:
        raise ValueError('Unknown RTree construction type {}'.format(rtree_creation))

    nearby_point_indices = tree.find_nearest_neighbors(sample_point, 4)
    # The sample point is at 4.5.  We expect the nearest neighbors to
    # be at 3, 4, 5 and 6.
    if set([3, 4, 5, 6]) != set(nearby_point_indices):
        print("ERROR: Expected nearby points to have indices [3, 4, 5, 6].  Instead we got {}.".format(sorted(nearby_point_indices)))
        return 1
    else:
        return 0

def main():
    error_count = 0

    for dimension in range(1, 30):
        point_type = fv.POINT_TYPES[dimension]
        error_count += test_nearest_neighbors(
            point_type,
            rtree_creation=CreationMethod.CONSTRUCTOR
            )
        error_count += test_nearest_neighbors(
            point_type,
            rtree_creation=CreationMethod.ALL_POINTS_AT_ONCE
            )
        error_count += test_nearest_neighbors(
            point_type,
            rtree_creation=CreationMethod.ONE_POINT_AT_A_TIME
            )

    return error_count

if __name__ == '__main__':
    sys.exit(main())
