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

import sys
from datetime import datetime
from tracktable.data_generators import trajectory
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.info import airports

def test_gen_single_airport_trajectory():
    '''
    Build one trajectory between the two airports.
    '''

    EXPECTED_LENGTH = 84

    ABQ_AIRPORT = airports.airport_information("ABQ")
    DEN_AIRPORT = airports.airport_information("DEN")
    test_traj = trajectory.generate_airport_trajectory(
                                                    start_airport=ABQ_AIRPORT,
                                                    end_airport=DEN_AIRPORT,
                                                    start_time=datetime.now(),
                                                    object_id='ABQ-DEN',
                                                    desired_speed=400,
                                                    seconds_between_points=60,
                                                    minimum_num_points=10)

    assert len(test_traj) == EXPECTED_LENGTH

    assert test_traj[0][0] == ABQ_AIRPORT.position[0]
    assert test_traj[0][1] == ABQ_AIRPORT.position[1]

    assert test_traj[-1][0] == DEN_AIRPORT.position[0]
    assert test_traj[-1][1] == DEN_AIRPORT.position[1]

# ----------------------------------------------------------------------

def test_gen_five_random_airport_trajectories():
    '''
    Build five random trajectories between a group of large airports.
    '''

    EXPECTED_LENGTH = 5

    ten_largest_airports = trajectory.n_largest_airports(10)
    test_trajs = trajectory.generate_random_airport_trajectories(
                                                  start_airport_list=ten_largest_airports[:5],
                                                  end_airport_list=ten_largest_airports[5:],
                                                  num_paths=EXPECTED_LENGTH,
                                                  desired_speed=400,
                                                  seconds_between_points=60)

    assert len(test_trajs) == EXPECTED_LENGTH

    #Check each trajectory to make sure nothing wonky has happened
    for traj in test_trajs:
        assert len(traj) >= 10

# ----------------------------------------------------------------------

def test_gen_totally_random_airport_trajectories():
    '''
    Build completely random trajectories between any airports.
    '''

    EXPECTED_LENGTH = 5

    test_trajs = trajectory.generate_random_airport_trajectories(
                                                  start_airport_list=None,
                                                  end_airport_list=[],
                                                  num_paths=EXPECTED_LENGTH,
                                                  desired_speed=400,
                                                  seconds_between_points=60)

    assert len(test_trajs) == EXPECTED_LENGTH

# ----------------------------------------------------------------------

def test_gen_bbox_trajectories():
    '''
    Build trajectories between points in two bounding boxes.
    '''

    bbox_type = TerrestrialTrajectoryPoint.domain_classes['BoundingBox']
    starting_min_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    starting_max_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    ending_min_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    ending_max_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()

    albuquerque = TerrestrialTrajectoryPoint(-106.6504, 35.0844)
    san_francisco = TerrestrialTrajectoryPoint( -122.4194, 37.7749)
    atlanta = TerrestrialTrajectoryPoint(-84.42806, 33.636719)
    miami = TerrestrialTrajectoryPoint(-80.290556, 25.79325)

    starting_min_corner[0] = san_francisco[0]
    starting_min_corner[1] = albuquerque[1]
    starting_max_corner[0] = albuquerque[0]
    starting_max_corner[1] = san_francisco[1]

    ending_min_corner[0] = atlanta[0]
    ending_min_corner[1] = miami[1]
    ending_max_corner[0] = miami[0]
    ending_max_corner[1] = atlanta[1]

    starting_bbox = bbox_type(starting_min_corner, starting_max_corner)
    ending_bbox = bbox_type(ending_min_corner, ending_max_corner)

    EXPECTED_LIST_SIZE = 5
    MIN_EXPECTED_LENGTH = 300
    MAX_EXPECTED_LENGTH = 650

    test_trajs = trajectory.generate_bbox_trajectories(
                                                    starting_bbox,
                                                    ending_bbox,
                                                    EXPECTED_LIST_SIZE,
                                                    'BBOXTST',
                                                    start_time=datetime.now(),
                                                    desired_speed=400,
                                                    seconds_between_points=60,
                                                    minimum_num_points=10)

    assert len(test_trajs) == EXPECTED_LIST_SIZE

    for traj in test_trajs:
        assert len(traj) >= MIN_EXPECTED_LENGTH
        assert len(traj) <= MAX_EXPECTED_LENGTH
