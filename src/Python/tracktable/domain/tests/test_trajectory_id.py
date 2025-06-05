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
import sys
import random

from . import create_points_and_trajectories as tt_generators

from tracktable.domain import terrestrial, cartesian2d, cartesian3d
import logging


def test_trajectory_id(trajectory_class):
    """Test the trajectory_id property on a trajectory class

    Create a sample trajectory and ensure that the trajectory_id property is
    both present and working properly.

    Args:
        trajectory_class {class}: Which trajectory class to instantiate

    Returns:
        0 on success, 1 on error (also prints error message)
    """

    sample_trajectory = tt_generators.generate_random_trajectory(
        trajectory_class, 0, 0
        )
    expected_id = '{}_{}_{}'.format(
        sample_trajectory.object_id,
        sample_trajectory[0].timestamp.strftime('%Y%m%d%H%M%S'),
        sample_trajectory[-1].timestamp.strftime('%Y%m%d%H%M%S')
        )

    if expected_id != sample_trajectory.trajectory_id:
        logger = logging.getLogger(__name__)
        logger.error(('Trajectory ID mismatch in test_trajectory_id.  '
                      'Expected {}, got {}.').format(
            expected_id, sample_trajectory.trajectory_id))
        return 1
    else:
        return 0

# ----------------------------------------------------------------------

def main():
    random.seed(0)
    num_errors = 0
    num_errors += test_trajectory_id(terrestrial.Trajectory)
    num_errors += test_trajectory_id(cartesian2d.Trajectory)
    num_errors += test_trajectory_id(cartesian3d.Trajectory)

    return num_errors

if __name__ == '__main__':
    sys.exit(main())
