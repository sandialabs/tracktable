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

from __future__ import print_function

import csv
import sys

from tracktable.features import annotations
from tracktable.source import path_point_source
from tracktable.core import Timestamp
from tracktable.domain.terrestrial import TrajectoryPoint as AirTrajectoryPoint
from tracktable.domain.terrestrial import Trajectory as AirTrajectory

def create_trajectory():
    los_angeles = AirTrajectoryPoint( -118.25, 34.05 )
    los_angeles.object_id = 'TEST'
    los_angeles.timestamp = Timestamp.from_any('2014-01-01 00:00:00')
    los_angeles.properties['altitude'] = 0

    new_york = AirTrajectoryPoint( -74.0, 40.71 )



    source = path_point_source.TrajectoryPointSource(AirTrajectoryPoint)
    source.start_time = Timestamp.from_any('2014-01-01 04:00:00')
    source.end_time = Timestamp.from_any('2014-01-01 04:00:00')
    source.start_point = los_angeles
    source.end_point = new_york
    source.num_points = 240
    source.object_id = 'TEST'

    all_points = list(source.points())

    # Now we need to add altitude.  Let's say that we get to maximum
    # altitude (50,000 feet) at point 90.  We start descending at
    # point 150 and get back to zero altitude at point 240.
    max_altitude = 50000
    for i in range(240):
        all_points[i].altitude = max_altitude

    for i in range(90):
        x = float(i) / 90

        level = 1 - (x-1)*(x-1)
        altitude = level * max_altitude
        all_points[i].altitude = altitude
        all_points[-(i+1)].altitude = altitude

    trajectory = AirTrajectory.from_position_list(all_points)
    return trajectory

# ----------------------------------------------------------------------

def write_trajectory(trajectory, outfile):
    writer = csv.writer(outfile, delimiter=',')
    writer.writerow([ '# object_id', 'timestamp', 'longitude', 'latitude', 'altitude' ])
    for point in trajectory:
        latest_row = [ point.object_id,
                       Timestamp.to_string(point.timestamp, include_dst=False),
                       str(point.longitude),
                       str(point.latitude),
                       str(int(point.altitude)) ]
        writer.writerow(latest_row)

# ----------------------------------------------------------------------

def main():
    trajectory = create_trajectory()
    with open('/tmp/test_trajectory.csv', 'wb') as outfile:
        write_trajectory(trajectory, outfile)

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())


