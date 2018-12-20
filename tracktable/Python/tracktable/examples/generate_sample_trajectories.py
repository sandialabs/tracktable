#!/usr/bin/env python

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

# generate_sample_trajectories - Generate example trajectories between big airporst

# Our larger trajecotry sample data file contains trajectories that go
# between the largest airports in the world.  This script is what we
# use to generate that file.
#
# The example data in tracktable/Examples/Data/SampleTrajectories.tsv
# was generated with the following command line:
#
# python generate_sample_trajectories.py SampleTrajectories.tsv

from __future__ import print_function, division, absolute_import

import argparse
import csv
import datetime
import math
import operator
import random
import sys

from six.moves import range

from tracktable.core import geomath, timestamp, conversions
from tracktable.info import cities, airports
from tracktable.source import trajectory, path_point_source, combine
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--speed',
                        type=float,
                        default=1036,
                        help='Speed for trajectories (in km/h)')

    parser.add_argument('--speed-jitter', '-j',
                        type=float,
                        default=200,
                        help='Add or subtract this much noise in the speed for each trajectory')

    parser.add_argument('--spacing',
                        type=float,
                        default=60,
                        help='Time between points in a trajectory (in seconds)')

    parser.add_argument('--paths', '-n',
                        type=int,
                        default=200,
                        help='How many paths to generate between random pairs of airports')

    parser.add_argument('--airports', '-a',
                        type=int,
                        default=100,
                        help='How many airports to use as start/end points')

    parser.add_argument('output',
                        nargs=1,
                        help='Filename for output points')

    args = parser.parse_args()

    return args

# ----------------------------------------------------------------------

def n_largest_airports(howmany):
    """
    n_largest_airports(howmany: int) -> list of Airport objects

    Retrieve a list of the N busiest airports in the world (by
    passenger traffic) sorted in descending order.
    """

    all_airports = sorted(airports.all_airports(), key=operator.attrgetter('size_rank'))
    return all_airports[0:howmany]


# ----------------------------------------------------------------------

def time_between_positions(start, end, desired_speed=800):
    """time_between_positions(start: position, end: position, desired_speed: float (km/h)) -> datetime.timedelta

    Given two points and a constant speed, calculate the amount of
    time (expressed in seconds as a timedelta) to travel from hither to
    yon.
    """

    distance = geomath.distance(start, end)
    seconds = 3600.0 * (distance / desired_speed)
    return datetime.timedelta(seconds=seconds)

# ----------------------------------------------------------------------

def num_points_between_positions(start, end, seconds_between_points=60, desired_speed=800):

    """num_points_between_positions(start: position, end: position, seconds_between_points: int, desired_speed: float (km/h)) -> int

    Calculate how many points need to be between the start and end
    points supplied at the desired speed given a desired time between
    adjacent points.  The default speed value (800 km/h) is Mach 0.83, the
    ideal cruising speed for a Boeing 777.
    """

    travel_time = time_between_positions(start, end, desired_speed)
    return int(travel_time.total_seconds() / seconds_between_points)

# ----------------------------------------------------------------------

def trajectory_point_generator(start_airport, end_airport, start_time, object_id='ANON', desired_speed=800, seconds_between_points=60, minimum_num_points=10):
    """trajectory_point_generator(start_airport: Airport,
                                  end_airport: Airport,
                                  start_time=Timestamp (datetime.datetime),
                                  object_id='ANON' (string),
                                  desired_speed=60 (float, km/h),
                                  seconds_between_points=60 (int),
                                  minimum_num_points=10 (int)) -> iterable of points

    Generate a sequence of points that go from the starting airport to
    the ending airport with the desired speed and time between points.
    """

    start_position = TerrestrialTrajectoryPoint()
    start_position[0] = start_airport.position[0]
    start_position[1] = start_airport.position[1]

    end_position = TerrestrialTrajectoryPoint()
    end_position[0] = end_airport.position[0]
    end_position[1] = end_airport.position[1]

    travel_time = time_between_positions(start_position, end_position, desired_speed=desired_speed)

    num_points = num_points_between_positions(start_position, end_position,
                                              desired_speed=desired_speed,
                                              seconds_between_points=seconds_between_points)

    if num_points < minimum_num_points:
        num_points = minimum_num_points

    start_position.object_id = object_id
    start_position.timestamp = start_time
    end_position.object_id = object_id
    end_position.timestamp = start_time + travel_time

    point_list = [ start_position ]
    if num_points == 2:
        point_list.append(end_position)
    else:
        interpolant_increment = 1.0 / (num_points - 1)
        for i in range(1, num_points-1):
            interpolant = i * interpolant_increment
            point_list.append(geomath.interpolate(start_position, end_position, interpolant))
        point_list.append(end_position)
    
    return point_list

# ----------------------------------------------------------------------

def all_path_point_generators(airports, num_paths, desired_speed=800, speed_jitter=200, seconds_between_points=60):
    """all_path_point_generators(airports: list(Airport),
                              num_paths: int,
                              desired_speed=800 (float, km/h),
                              seconds_between_points=60 (int)) -> list(iterable(Point))

    Given a list of airports, a desired speed and a time between
    points, construct a whole bunch of iterables.  Each iterable
    contains points for a great-circle path between two randomly
    selected elements of the list of airports.
    """

    flight_counters = {}

    iterables = []
    start_airport = None
    end_airport = None

    for i in range(num_paths):
        while start_airport == end_airport:
            chosen_airports = random.sample(airports, 2)
            start_airport = chosen_airports[0]
            end_airport = chosen_airports[1]
        flight_id = 'TST{}{}'.format(start_airport.iata_code, end_airport.iata_code)
        flight_number = flight_counters.get(flight_id, 0)
        flight_counters[flight_id] = flight_number + 1
        full_flight_id = '{}{}'.format(flight_id, flight_number)

        print("INFO: generating sample trajectory for {} - {}".format(start_airport.iata_code,
                                                                       end_airport.iata_code))

        generator = trajectory_point_generator(start_airport, end_airport, 
                                               start_time=datetime.datetime.now(), 
                                               object_id=full_flight_id, 
                                               desired_speed=desired_speed, 
                                               seconds_between_points=seconds_between_points)

        start_airport = end_airport
        iterables.append(generator)

    return iterables

# ----------------------------------------------------------------------

def write_points_to_file(point_source, outfile):
    outfile.write('# object_id timestamp longitude latitude\n')
    writer = csv.writer(outfile, delimiter='\t')

    for point in point_source:
        row = [ point.object_id, timestamp.Timestamp.to_string(point.timestamp), point.longitude, point.latitude ]
        writer.writerow(row)

# ----------------------------------------------------------------------

def main():
    args = parse_args()

    if args.airports > 100:
        print("WARNING: We only have size statistics for the busiest 100 airports in the world.  Reducing num_airports from {} to 30.".format(args.airports))
        args.airports = 100

    airports = n_largest_airports(args.airports)

    print("INFO: Generating {} trajectories among random pairs of the world's {} largest airports.".format(args.paths, args.airports))

    point_iterables = all_path_point_generators(airports,
                                                args.paths,
                                                desired_speed=args.speed,
                                                speed_jitter=args.speed_jitter,
                                                seconds_between_points=args.spacing)

    print("DEBUG: Acquired {} point iterables.".format(len(point_iterables)))
    
    single_point_list = combine.interleave_points_by_timestamp(*point_iterables)

    with open(args.output[0], 'wb') as outfile:
        write_points_to_file(single_point_list, outfile)

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
