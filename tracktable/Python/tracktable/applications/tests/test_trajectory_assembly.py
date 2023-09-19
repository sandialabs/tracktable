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

from __future__ import division, print_function

import itertools
import sys
from datetime import timedelta

from tracktable.applications.assemble_trajectories import \
    AssembleTrajectoryFromPoints
from tracktable.core import Timestamp, geomath
from tracktable.feature.interpolated_points import TrajectoryPointSource


def run_test():
    # Define three sets of points: ABQ to San Diego, San Diego to
    # Seattle, Denver to NYC.  ABQ->SAN->SEA should break into two
    # trajectories because of a timestamp break in San Diego.  The
    # flight to Denver will begin right when the flight to Seattle
    # ends so we expect to break that one based on the distance
    # threshold.

    print("Beginning run_test()")

    from tracktable.domain.terrestrial import TrajectoryPoint

    albuquerque = TrajectoryPoint( -106.5, 35.25 )
    albuquerque.timestamp = Timestamp.from_string('2010-01-01 12:00:00')
    albuquerque.object_id = 'flight1'

    san_diego1 = TrajectoryPoint( -117.16, 32.67 )
    san_diego1.timestamp = Timestamp.from_string('2010-01-01 15:00:00')
    san_diego1.object_id = 'flight1'

    san_diego2 = TrajectoryPoint( -117.16, 32.67 )
    san_diego2.timestamp = Timestamp.from_string('2010-01-01 16:00:00')
    san_diego2.object_id = 'flight1'

    seattle = TrajectoryPoint( -122.31, 47.60 )
    seattle.timestamp = Timestamp.from_string('2010-01-01 19:00:00')
    seattle.object_id = 'flight1'

    denver = TrajectoryPoint( -104.98, 39.79 )
    denver.timestamp = Timestamp.from_string('2010-01-01 19:01:00')
    denver.object_id = 'flight1'

    new_york = TrajectoryPoint( -74.02, 40.71 )
    new_york.timestamp = Timestamp.from_string('2010-01-02 00:00:00')
    new_york.object_id = 'flight1'

    # Now we want sequences of points for each flight.
    abq_to_sd = TrajectoryPointSource()
    abq_to_sd.start_point = albuquerque
    abq_to_sd.end_point = san_diego1
    abq_to_sd.num_points = 180

    sd_to_sea = TrajectoryPointSource()
    sd_to_sea.start_point = san_diego2
    sd_to_sea.end_point = seattle
    sd_to_sea.num_points = 360 # flying very slowly

    denver_to_nyc = TrajectoryPointSource()
    denver_to_nyc.start_point = denver
    denver_to_nyc.end_point = new_york
    denver_to_nyc.num_points = 600 # wow, very densely sampled

    print("Done creating point sources")

    all_points = list(itertools.chain( abq_to_sd.points(),
                                       sd_to_sea.points(),
                                       denver_to_nyc.points() ))

    trajectory_assembler = AssembleTrajectoryFromPoints()
    trajectory_assembler.input = all_points
    trajectory_assembler.separation_time = timedelta(minutes=30)
    trajectory_assembler.separation_distance = 100
    trajectory_assembler_minimum_length = 10

    print("Done instantiating assembler")

    all_trajectories = list(trajectory_assembler.trajectories())
    print("Assembler statistics: {} points, {} valid trajectories, {} invalid trajectories".format(
        trajectory_assembler.valid_trajectory_count,
        trajectory_assembler.invalid_trajectory_count,
        trajectory_assembler.points_processed_count
        ))

    print("Done creating trajectories.  Found {}.".format(len(all_trajectories)))

    test_point_proximity = geomath.sanity_check_distance_less_than(1)
    def test_timestamp_proximity(time1, time2):
        return ( (time2 - time1).total_seconds() < 1 )

    error_count = 0
    if len(all_trajectories) != 3:
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected 3 trajectories but got {}\n'.format(len(all_trajectories)))
        error_count += 1

    if not test_point_proximity(all_trajectories[0][0], albuquerque):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected point 0 of first trajectory to be Albuquerque ({}) but it is instead {}\n'.format(albuquerque, str(all_trajectories[0][0])))
        error_count += 1

    if not test_point_proximity(all_trajectories[0][-1], san_diego1):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected last point of first trajectory to be San Diego ({}) but it is instead {}\n'.format(san_diego, str(all_trajectories[0][-1])))
        error_count += 1

    if not test_point_proximity(all_trajectories[1][0], san_diego2):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected point 0 of second trajectory to be San Diego ({}) but it is instead {}\n'.format(san_diego, str(all_trajectories[1][0])))
        error_count += 1

    if not test_point_proximity(all_trajectories[1][-1], seattle):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected last point of second trajectory to be Seattle ({}) but it is instead {}\n'.format(seattle, str(all_trajectories[1][-1])))
        error_count += 1

    if not test_point_proximity(all_trajectories[2][0], denver):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected first point of third trajectory to be Denver ({}) but it is instead {}\n'.format(denver, str(all_trajectories[2][0])))
        error_count += 1

    if not test_point_proximity(all_trajectories[2][-1], new_york):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected last point of third trajectory to be New York ({}) but it is instead {}\n'.format(new_york, str(all_trajectories[2][-1])))
        error_count += 1

    if not test_timestamp_proximity(all_trajectories[0][0].timestamp, albuquerque.timestamp):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected timestamp at beginning of trajectory 0 to be {} but it is instead {}\n'.format(albuquerque.timestamp, all_trajectories[0][0].timestamp))
        error_count += 1

    if not test_timestamp_proximity(all_trajectories[0][-1].timestamp, san_diego1.timestamp):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected timestamp at end of trajectory 0 to be {} but it is instead {}\n'.format(san_diego1.timestamp, all_trajectories[0][-1].timestamp))
        error_count += 1

    if not test_timestamp_proximity(all_trajectories[1][0].timestamp, san_diego2.timestamp):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected timestamp at beginning of trajectory 1 to be {} but it is instead {}\n'.format(san_diego2.timestamp, all_trajectories[1][0].timestamp))
        error_count += 1

    if not test_timestamp_proximity(all_trajectories[1][-1].timestamp, seattle.timestamp):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected end at beginning of trajectory 1 to be {} but it is instead {}\n'.format(seattle.timestamp, all_trajectories[1][-1].timestamp))
        error_count += 1

    if not test_timestamp_proximity(all_trajectories[2][0].timestamp, denver.timestamp):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected timestamp at beginning of trajectory 2 to be {} but it is instead {}\n'.format(denver.timestamp, all_trajectories[2][0].timestamp))
        error_count += 1

    if not test_timestamp_proximity(all_trajectories[2][-1].timestamp, new_york.timestamp):
        sys.stdout.write('ERROR: test_trajectory_assembly: Expected timestamp at end of trajectory 2 to be {} but it is instead {}\n'.format(new_york.timestamp, all_trajectories[2][-1].timestamp))
        error_count += 1

    print("Done checking proximities")

    return error_count

# ----------------------------------------------------------------------

if __name__ == '__main__':
    print("About to call run_test()")
    sys.exit(run_test())

