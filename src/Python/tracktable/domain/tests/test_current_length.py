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
import random

from tracktable.domain.tests import create_points_and_trajectories as tt_generators
from tracktable.domain import terrestrial, cartesian2d, cartesian3d
from tracktable.core import geomath

def main():
    random.seed(0)
    error_count = 0

    for trajectory_prototype in [
            terrestrial.Trajectory,
            cartesian2d.Trajectory,
            cartesian3d.Trajectory
    ]:
        trajectory = tt_generators.generate_random_trajectory(
            trajectory_prototype,
            3, 3
        )
        # All we have to do in this test is make sure they're present
        # and sensible.  Since the coordinates are random, there's no
        # ground truth to check them against.
        lengths = [ point.current_length for point in trajectory ]
        for i in range(1, len(lengths)):
            if lengths[i] < lengths[i-1]:
                print(("ERROR: In trajectory {}, current length at "
                       "point {} ({}) is less than current length "
                       "at point {} ({}).  This shouldn't ever "
                       "happen.").format(
                           type(trajectory),
                           i, lengths[i],
                           i-1, lengths[i-1]))
                error_count += 1

    return error_count

if __name__ == '__main__':
    sys.exit(main())
