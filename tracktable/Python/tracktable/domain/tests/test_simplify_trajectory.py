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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


from __future__ import print_function, division, absolute_import

import sys
from six.moves import range

from tracktable.domain import terrestrial, cartesian2d, cartesian3d
from tracktable.core import geomath

def test_simplify_trajectory(trajectory_type):
    point_type = trajectory_type.domain_classes['TrajectoryPoint']

    trajectory = trajectory_type()
    for i in range(9):
        next_point = point_type.zero()
        next_point[0] = i
        if i == 4:
            next_point[1] = 5
        trajectory.append(next_point)

    simplified = geomath.simplify(trajectory, 0.01)
    error_count = 0

    if len(simplified) != 5:
        error_count += 1
        print("ERROR: test_simplify_trajectory on {}: Simplified trajectory has {} points.  We were expecting 5.".format(trajectory_type, len(simplified)))

    if simplified[0] != trajectory[0]:
        error_count += 1
        print("ERROR: test_simplify_trajectory on {}: Expected simplified[0] == trajectory[0].".format(trajectory_type))

    if simplified[1] != trajectory[3]:
        error_count += 1
        print("ERROR: test_simplify_trajectory on {}: Expected simplified[1] == trajectory[3].".format(trajectory_type))

    if simplified[2] != trajectory[4]:
        error_count += 1
        print("ERROR: test_simplify_trajectory on {}: Expected simplified[2] == trajectory[4].".format(trajectory_type))

    if simplified[3] != trajectory[5]:
        error_count += 1
        print("ERROR: test_simplify_trajectory on {}: Expected simplified[3] == trajectory[5].".format(trajectory_type))

    if simplified[4] != trajectory[8]:
        error_count += 1
        print("ERROR: test_simplify_trajectory on {}: Expected simplified[4] == trajectory[8].".format(trajectory_type))

    if error_count > 0:
        print("DEBUG: Original trajectory:")
        for point in trajectory:
            print("{}".format(str(point)))
        print("DEBUG: Simplified trajectory:")
        for point in simplified:
            print("{}".format(str(point)))

    return error_count

# ----------------------------------------------------------------------

def main():
    overall_error_count = 0

    overall_error_count += test_simplify_trajectory(terrestrial.Trajectory)
    overall_error_count += test_simplify_trajectory(cartesian2d.Trajectory)
    overall_error_count += test_simplify_trajectory(cartesian3d.Trajectory)

    return overall_error_count

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
