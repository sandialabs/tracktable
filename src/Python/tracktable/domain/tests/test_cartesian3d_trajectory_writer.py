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
import datetime
import sys
import random

from . import create_points_and_trajectories as tt_generators

from tracktable.domain.cartesian3d import Trajectory, TrajectoryPoint, TrajectoryPointWriter, TrajectoryPointReader, TrajectoryWriter, TrajectoryReader

from tracktable.core import Timestamp
from tracktable.core.test_utilities import version_appropriate_string_buffer

import datetime



# ----------------------------------------------------------------------

def write_trajectories_to_string(trajectories):
    output = version_appropriate_string_buffer()
    writer = TrajectoryWriter(output)
    writer.write(trajectories)

    result = output.getvalue()
    print("Length of result string: {}".format(len(result)))
    return result

# ----------------------------------------------------------------------

def read_trajectories_from_string(text):
    input = version_appropriate_string_buffer(text)
    reader = TrajectoryReader(input)
    points = list(reader)
    return points

# ----------------------------------------------------------------------

def main():
    random.seed(0)
    num_errors = 0
    num_trajectories = 10
    num_point_properties = 5
    num_trajectory_properties = 15


    original_trajectories = [ tt_generators.generate_random_trajectory(Trajectory,
                                                                       num_point_properties,
                                                                       num_trajectory_properties) for i in range(num_trajectories) ]

    #Test single trajectory
    trajectories_as_string = write_trajectories_to_string(original_trajectories[0])
    reconstituted_trajectories = read_trajectories_from_string(trajectories_as_string)

    if len(reconstituted_trajectories) != 1:
        print("ERROR: Reconstituted array contains {}, which is more than 1.".format(len(original_trajectories[0]), len(reconstituted_trajectories)))
        return 1

    if original_trajectories[0] != reconstituted_trajectories[0]:
            print("ERROR: Trajectory was not reconstituted successfully.")
            print("Original trajectory ({}):\n{}".format(repr(original_trajectories[0]), str(original_trajectories[0])))
            print("Reconstituted trajectory ({}):\n{}".format(repr(reconstituted_trajectories[0]), str(reconstituted_trajectories[0])))
            num_errors += 1

    #Test Array of Trajectories
    trajectories_as_string = write_trajectories_to_string(original_trajectories)
    reconstituted_trajectories = read_trajectories_from_string(trajectories_as_string)

    if len(original_trajectories) != len(reconstituted_trajectories):
        print("ERROR: Original trajectory array contains {} entries.  Reconstituted array contains {}.".format(len(original_trajectories), len(reconstituted_trajectories)))
        return 1

    for i in range(num_trajectories):
        if original_trajectories[i] != reconstituted_trajectories[i]:
            print("ERROR: Trajectory {} was not reconstituted successfully.".format(i))
            print("Original trajectory ({}):\n{}".format(repr(original_trajectories[i]), str(original_trajectories[i])))
            print("Reconstituted trajectory ({}):\n{}".format(repr(reconstituted_trajectories[i]), str(reconstituted_trajectories[i])))
            num_errors += 1

    return (num_errors != 0)


if __name__ == '__main__':
    sys.exit(main())
