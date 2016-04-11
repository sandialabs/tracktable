# Copyright (c) 2014, Sandia Corporation.  All rights
# reserved.
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

import datetime
import math
import sys

from tracktable.source.path_point_source import TrajectoryPointSource
from tracktable.domain.terrestrial import TrajectoryPoint
from tracktable.core import Timestamp

def run_test():
    num_errors = 0

    source = TrajectoryPointSource()

    start_time = Timestamp.from_any(datetime.datetime(2010, 10, 13, 12, 00, 00))
    end_time = Timestamp.from_any(datetime.datetime(2010, 10, 13, 18, 00, 00))

    start_point = TrajectoryPoint(-100, 35.0)
    start_point.object_id = 'foo'
    start_point.timestamp = start_time

    end_point = TrajectoryPoint(-80, 45.0)
    end_point.object_id = 'foo'
    end_point.timestamp = end_time

    num_points = 100

    source.start_point = start_point
    source.end_point = end_point
    source.num_points = num_points

    all_points = list( source.points() )

    if len(all_points) != num_points:
        sys.stderr.write('ERROR: GreatCircleTrajectoryPointSource: Expected {} points but got {}\n'.format(num_points, len(all_points)))
        num_errors += 1

    traj_start_point = ( all_points[0][0], all_points[0][1] )
    d_lon = all_points[0][0] - start_point[0]
    d_lat = all_points[0][1] - start_point[1]
    if math.fabs(d_lon) > 1e-5 or math.fabs(d_lat) > 1e-5:
        sys.stderr.write('ERROR: GreatCircleTrajectoryPointSource: Expected first point to be {} but got {} instead\n'.format(start_point, traj_start_point))
        num_errors += 1

    traj_end_point = ( all_points[-1][0], all_points[-1][1] )
    d_lon = all_points[-1][0] - end_point[0]
    d_lat = all_points[-1][1] - end_point[1]
    if math.fabs(d_lon) > 1e-5 or math.fabs(d_lat) > 1e-5:
        sys.stderr.write('ERROR: GreatCircleTrajectoryPointSource: Expected last point to be {} but got {} instead\n'.format(end_point, traj_end_point))
        num_errors += 1

    traj_start_time = all_points[0].timestamp
    d_time = math.fabs((traj_start_time - start_time).total_seconds())
    if d_time > 0.001:
        sys.stderr.write('ERROR: GreatCircleTrajectoryPointSource: Expected timestamp on first point to be {} but got {} instead\n'.format(start_time, traj_start_time))
        num_errors += 1

    traj_end_time = all_points[-1].timestamp
    d_time = math.fabs((traj_end_time - end_time).total_seconds())
    if d_time > 0.001:
        sys.stderr.write('ERROR: GreatCircleTrajectoryPointSource: Expected timestamp on last point to be {} but got {} instead\n'.format(end_time, traj_end_time))
        num_errors += 1

    return num_errors

if __name__ == '__main__':
    sys.exit(run_test())
