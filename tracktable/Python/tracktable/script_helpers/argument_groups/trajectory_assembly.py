#
# Copyright (c) 2014-2017 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
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

"""Options for creating trajectories from points.

This argument group lets you control the parameters for the algorithm
that assembles sequences of time-stamped points into continuous
trajectories.

Arguments:

| ``--separation-distance NUMBER``
|   A gap of at least this many units between successive points will result in a new trajectory.
|
| ``--separation-time NUMBER``
|   A gap of at least this many MINUTES between successive points will result in a new trajectory.
|
| ``--minimum-length NUMBER``
|   Discard finished trajectories with fewer than this many points.

"""

from tracktable.script_helpers.argument_groups import create_argument_group, add_argument


GROUP_INSTALLED = False

def install_group():
    """Create and populate the argument group for trajectory assembly.
    """

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True

    create_argument_group("trajectory_assembly",
                          title="Trajectory Builder Arguments",
                          description="Set the parameters that govern how we assemble sequences of time-stamped points into continuous trajectories.")

    add_argument("trajectory_assembly", ['--separation-distance'],
                 type=float,
                 default=100,
                 help='Start a new trajectory after a gap of this far between points (measured in KM)')

    add_argument("trajectory_assembly", ['--separation-time'],
                 type=float,
                 default=20,
                 help='Start a new trajectory after a gap of at least this long between points (measured in minutes)')

    add_argument("trajectory_assembly", ['--minimum-length'],
                 type=int,
                 default=10,
                 help='Only return trajectories that contain at least this many points')
