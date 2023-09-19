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
from six import StringIO
import sys

from . import create_points_and_trajectories as tt_generators

from tracktable.domain.terrestrial import TrajectoryPoint, TrajectoryPointWriter
from tracktable.core import Timestamp
from tracktable.core.test_utilities import version_appropriate_string_buffer

import datetime
import sys
import io

# ----------------------------------------------------------------------

def write_points_to_string(points):
    output = version_appropriate_string_buffer()

    writer = TrajectoryPointWriter(output)
    writer.write(points)

    return output.getvalue()

# ----------------------------------------------------------------------

def main():
    points_as_string = write_points_to_string(tt_generators.generate_random_points(
        TrajectoryPoint,
        num_points=10,
        num_point_properties=5))

    print("Trajectory points as string:\n{}(end)".format(points_as_string))

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())

