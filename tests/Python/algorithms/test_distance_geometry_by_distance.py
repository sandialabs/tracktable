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

# Test distance geometry sampled by distance
#
# This is a test to make sure that the Python binding returns the
# expected results.  The more exhaustive tests for multiple
# point domains are in C++.

from __future__ import absolute_import, division, print_function

import math
import sys

from tracktable.algorithms.distance_geometry import \
    distance_geometry_by_distance
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import \
    TrajectoryPoint as TerrestrialTrajectoryPoint


def make_sample_trajectory():
    coordinates = [
        (0, 80),
        (90, 80),
        (180, 80),
        (-90, 80),
        (0, 80)
        ]

    trajectory = TerrestrialTrajectory()
    for coords in coordinates:
        point = TerrestrialTrajectoryPoint(coords)
        point.object_id = 'terrestrial_dg_test'
        trajectory.append(point)

    return trajectory


def test_dg():
    sample_trajectory = make_sample_trajectory()
    dg_values = distance_geometry_by_distance(sample_trajectory, 4)

    expected_values = [
        0.0,
        0.708916,
        0.708916,
        0.793393,
        0.710916,
        0.793393,
        1.0,
        1.0,
        1.0,
        1.0
        ]

    error_count = 0
    i = 0
    if len(expected_values) != len(dg_values):
        print((
            'ERROR: distance_geometry_by_distance: Expected '
            '{} values but got {}'
            ).format(len(expected_values), len(dg_values)))
        error_count += 1

    for (actual, expected) in zip(dg_values, expected_values):
        if not math.isclose(actual, expected, rel_tol=1e-6):
            print(
                ('ERROR: test_distance_geometry_by_distance: Expected '
                 '{} for value {} but got {}').format(
                    expected, i, actual))
            error_count += 1
        i += 1

    return error_count


def main():
    error_count = test_dg()

    return error_count


if __name__ == '__main__':
    sys.exit(main())
