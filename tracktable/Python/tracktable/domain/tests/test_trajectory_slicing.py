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
import random
from six.moves import range

from tracktable.domain.tests import create_points_and_trajectories as tt_generator
from tracktable.domain import terrestrial, cartesian2d, cartesian3d
from tracktable.core import geomath

def main():

    random.seed(0)
    error_count = 0

    for trajectory_proto in [terrestrial.Trajectory,
      cartesian2d.Trajectory, cartesian3d.Trajectory]:

        traj = tt_generator.generate_random_trajectory(trajectory_proto,
              3,0)
        traj.properties["number"] = 123
        traj.properties["pilot"] = "Andy"

        new_traj = traj[1:5]
        if len(new_traj) != 4:
            print("ERROR: In trajectory type ", trajectory_proto, " slicing should result in 4 points but was actually ", len(new_traj))
            error_count += 1
        if not new_traj.has_property("number"):
            print("ERROR: Trajectory of type ", trajectory_proto, " slicing did not have property number")
            error_count += 1
        elif not new_traj.properties["number"] == traj.properties["number"]:
            print("ERROR: Trajectory of type ", trajectory_proto, " has property number but was suppose to have value",
                 traj.properties["number"]," but instead has value ", new_traj.properties["number"])
            error_count += 1

        if not new_traj.has_property("pilot"):
            print("ERROR: Trajectory of type ", trajectory_proto, " slicing did not have property pilot")
            error_count += 1
        elif not new_traj.properties["pilot"] == traj.properties["pilot"]:
            print("ERROR: Trajectory of type ", trajectory_proto, " has property pilot but was suppose to have value ",
                 traj.properties["pilot"], " but instead has value ", new_traj.properties["pilot"])
            error_count += 1

    return error_count

if __name__ == '__main__':
    sys.exit(main())
