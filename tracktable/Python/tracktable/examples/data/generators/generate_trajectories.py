#
# Copyright (c) 2014-2020 National Technology and Engineering
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

"""
This file contains functions for generating trajectories.
"""

from __future__ import division, absolute_import

import operator
import random
import datetime

from tracktable.core import geomath
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.info import airports

import tracktable.core.log

import logging
LOGGER = logging.getLogger(__name__)
DOMAIN_MODULE = None

def __time_between_positions(start, end, desired_speed=800):
    """
    Given two points and a constant speed, calculate the amount of
    time (expressed in seconds as a timedelta) to travel from hither to
    yon.
    
    Args:
        start (Point): starting position
        end (Point): end position
        desired_speed (float (km/h)): speed between points  
    
    Returns:
        datetime.timedelta
    """

    distance = geomath.distance(start, end)
    seconds = 3600.0 * (distance / desired_speed)
    return datetime.timedelta(seconds=seconds)

# ----------------------------------------------------------------------

def __num_points_between_positions(start, end, seconds_between_points=60, 
                                    desired_speed=800):

    """
    Calculate how many points need to be between the start and end
    points supplied at the desired speed given a desired time between
    adjacent points.  The default speed value (800 km/h) is Mach 0.83, the
    ideal cruising speed for a Boeing 777.
    
    Args:
        start (Point): starting position
        end (Point): end position
        seconds_between_points (int): time between points
        desired_speed (float (km/h)): speed between points
    
    Returns:
        int
    
    """
    
    travel_time = __time_between_positions(start, end, desired_speed)
    return int(travel_time.total_seconds() / seconds_between_points)

# ----------------------------------------------------------------------

def __trajectory_point_generator(start, end, start_time, object_id, 
                                    desired_speed=800, 
                                    seconds_between_points=60, 
                                    minimum_num_points=10):
    """
    Generate a trajectory that goes from the starting point to
    the ending point with the desired speed and time between points.
    
    Args:
        start (Point): starting point
        end (Point): ending point
        start_time (Timestamp): time to start trajectory
        object_id (string): id to store with trajectory
        desired_speed (float, km/h): speed of trajectory
        seconds_between_points (int): time between points
        minimum_num_points (int): minimum size of trajectory
        
    Returns:
        Point Generator
    """

    travel_time = __time_between_positions(start, end,
                                         desired_speed=desired_speed)

    num_points = __num_points_between_positions(start, end,
                              desired_speed=desired_speed,
                              seconds_between_points=seconds_between_points)

    if num_points < minimum_num_points:
        num_points = minimum_num_points

    start.object_id = object_id
    start.timestamp = start_time
    end.object_id = object_id
    end.timestamp = start_time + travel_time

    point_list = [ start ]
    if num_points == 2:
        point_list.append(end)
    else:
        interpolant_increment = 1.0 / (num_points - 1)
        for i in range(1, num_points-1):
            interpolant = i * interpolant_increment
            point_list.append(geomath.interpolate(start, end, interpolant))
        point_list.append(end)

    return point_list

# ----------------------------------------------------------------------

def __airport_random_path_point_generators(start_airport_list,
                                         end_airport_list,
                                         num_paths,
                                         desired_speed=800, 
                                         seconds_between_points=60):
    """
    Given lists of airports, a desired speed and a time between
    points, construct a whole bunch of iterables.  Each iterable
    contains points for a great-circle path between two randomly
    selected elements of the list of airports. If airport lists
    are None or Empty, then all possible airports are used.
    
    Args:
        start_airport_list (List of Airports): starting airports to sample from
        end_airport_list (List of Airports): ending airports to sample from
        num_paths (int): number of trajectories to create
        desired_speed (float, km/h): speed of trajectory
        seconds_between_points (int): time between points
    
    Returns:
        List of Point Generators
    """

    flight_counters = {}

    iterables = []
    start_airport = None
    end_airport = None

    if start_airport_list is None or len(start_airport_list) == 0:
        start_airport_list = list(airports.all_airports());
    
    if end_airport_list is None or len(end_airport_list) == 0:
        end_airport_list = list(airports.all_airports());
    
    for i in range(num_paths):
        while start_airport == end_airport:
            start_airport = random.sample(start_airport_list, 1)[0]
            end_airport =  random.sample(end_airport_list, 1)[0]
        flight_id = 'GEN{}{}'.format(start_airport.iata_code, 
                                     end_airport.iata_code)
        flight_number = flight_counters.get(flight_id, 0)
        flight_counters[flight_id] = flight_number + 1
        full_flight_id = '{}{}'.format(flight_id, flight_number)

        print("INFO: generating trajectory for {} - {}"\
            .format(start_airport.name,end_airport.name))
            
        start_position = TerrestrialTrajectoryPoint(start_airport.position)
        end_position = TerrestrialTrajectoryPoint(end_airport.position)
        
        generator = __trajectory_point_generator(start_position,
                               end_position, 
                               start_time=datetime.datetime.now(), 
                               object_id=full_flight_id, 
                               desired_speed=desired_speed, 
                               seconds_between_points=seconds_between_points)

        start_airport = end_airport
        iterables.append(generator)

    return iterables

# ----------------------------------------------------------------------

def n_largest_airports(howmany):
    """
    Retrieve a list of the N busiest airports in the world (by
    passenger traffic) sorted in descending order.
    
    Args:
        howmany (int): n

    Returns:
        List of Airport Objects
    
    """
    
    all_airports = sorted(airports.all_airports(), 
                          key=operator.attrgetter('size_rank'))
    return all_airports[0:howmany]


# ----------------------------------------------------------------------

def generate_airport_trajectory(start_airport, end_airport, **kwargs):
    '''
    Create a trajectory object from a starting airport to an ending
    airport. 
    
    Args:
        start_airport (Airport): starting airport
        end_airport (Airport): ending airport
        **kwargs: see __trajectory_point_generator for values
    
    Returns:
        TerrestrialTrajectory
    '''
    
    start_position = TerrestrialTrajectoryPoint(start_airport.position)
    end_position = TerrestrialTrajectoryPoint(end_airport.position)
    
    print("INFO: generating trajectory for {} - {}"\
            .format(start_airport.name,end_airport.name))
    
    point_list = __trajectory_point_generator(start=start_position, 
                                            end=end_position,
                                            **kwargs)
    new_trajectory = TerrestrialTrajectory.from_position_list(point_list)
    return new_trajectory
    
# ----------------------------------------------------------------------

def generate_random_airport_trajectories(**kwargs):
    '''
    Create a list of trajectories from a list of iterables. 
    This function is basically a trajectory wrapper for the 
    __airport_random_path_point_generators method.
    
    Args:
        **kwargs: see __airport_random_path_point_generators for values
    
    Returns:
        List of TerrestrialTrajectory Objects
    '''
    random_trajectories = []
    iterable_list = __airport_random_path_point_generators(**kwargs)
    for point_list in iterable_list:
        random_trajectories.append(
                    TerrestrialTrajectory.from_position_list(point_list))
        
    return random_trajectories
   
# ----------------------------------------------------------------------

def generate_bbox_trajectories(start_bbox, end_bbox, num_paths,
                               flight_prefix, **kwargs):
    '''
    Generate terrestrial trajectories using randomly selected points
    from within two bounding boxes.
    
    Uses parameters from __trajectory_point_generator.
    
    Args:
        start_bbox (BoundingBox): starting airport
        end_bbox (BoundingBox): ending airport
        num_paths (int): number of trajectories to generate
        flight_prefix (string): prefix to use for trajectory ids
        **kwargs: see __trajectory_point_generator for values
    
    Returns:
        List of TerrestrialTrajectory Objects
    '''
    
    new_trajectories = []
    for i in range(num_paths):
        #Select random start and end points
        start_position = TerrestrialTrajectoryPoint()
        start_position[0] = random.uniform(
                        min(start_bbox.min_corner[0], start_bbox.max_corner[0]),
                        max(start_bbox.min_corner[0], start_bbox.max_corner[0]))
        start_position[1] = random.uniform(
                        min(start_bbox.min_corner[1], start_bbox.max_corner[1]),
                        max(start_bbox.min_corner[1], start_bbox.max_corner[1]))

        end_position = TerrestrialTrajectoryPoint()
        end_position[0] = random.uniform(
                        min(end_bbox.min_corner[0], end_bbox.max_corner[0]),
                        max(end_bbox.min_corner[0], end_bbox.max_corner[0]))
        end_position[1] = random.uniform(
                        min(end_bbox.min_corner[1], end_bbox.max_corner[1]),
                        max(end_bbox.min_corner[1], end_bbox.max_corner[1]))
        
        flight_id = flight_prefix + str(i)
        
        print("INFO: generating trajectory for {} - {}"\
            .format(start_position,end_position))
        
        point_list = __trajectory_point_generator(start=start_position, 
                                                end=end_position,
                                                object_id=flight_id,
                                                **kwargs)
        new_trajectory = TerrestrialTrajectory.from_position_list(point_list)
        new_trajectories.append(new_trajectory)
    return new_trajectories   