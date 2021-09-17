#
# Copyright (c) 2014-2021 National Technology and Engineering
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
tracktable.applications.tutorial_helpers - Helper functions to assist the jupyter notebook tutorials
"""

import os.path
from datetime import timedelta

from numpy import zeros
from tracktable.applications.assemble_trajectories import \
    AssembleTrajectoryFromPoints
from tracktable.applications.trajectory_splitter import split_when_idle
from tracktable.core import data_directory
from tracktable.core.geomath import (convex_hull_area, end_to_end_distance,
                                     length, speed_between)
from tracktable.domain.terrestrial import (TrajectoryPointReader,
                                           TrajectoryReader)
from tracktable.render import render_map
from tracktable.render.map_processing import maps

# TODO: Error handling throughout.

SAMPLE_DATA_FILENAMES = {'tutorial-csv': os.path.join(data_directory(),'NYHarbor_2020_06_30_first_hour.csv'),
                         'tutorial-traj': os.path.join(data_directory(),'NYHarbor_2020_06_30_first_hour.traj'),
                         'tutorial-static-viz': os.path.join(data_directory(), 'SampleTrajectories.traj'),
                         'rendezvous': os.path.join(data_directory(),'VirginiaBeach_2020_06_04_to_06_filtered.traj'),
                         'boxiness': os.path.join(data_directory(),'VirginiaBeach_2020_06_04_to_06_filtered.traj'),
                         'shape': os.path.join(data_directory(),'US_coastal_2020_06_30.traj'),
                         'anomaly-historical': os.path.join(data_directory(),'NYHarbor_2020_12_first_week.traj'),
                         'anomaly-test': os.path.join(data_directory(),'NYHarbor_2020_12_08.traj')
                        }


###############################################################################
# HELPER FUNCTIONS FOR TRACKTABLE TUTORIALS
###############################################################################

def create_point_reader(filename=SAMPLE_DATA_FILENAMES['tutorial-csv'],
                        object_id_column=3,
                        timestamp_column=0,
                        longitude_column=1,
                        latitude_column=2,
                        real_fields={'heading': 6},
                        string_fields={'vessel-name': 7},
                        time_fields={'eta': 17}):

    # set up the reader to match the file structure
    reader = TrajectoryPointReader()
    reader.input = open(filename, 'r')

    # required columns
    reader.object_id_column = object_id_column
    reader.timestamp_column = timestamp_column
    reader.coordinates[0] = longitude_column
    reader.coordinates[1] = latitude_column

    for name, column_num in real_fields.items():
        reader.set_real_field_column(name, column_num)

    for name, column_num in string_fields.items():
        reader.set_string_field_column(name, column_num)

    for name, column_num in time_fields.items():
        reader.set_time_field_column(name, column_num)

    return reader


def get_trajectory_list_from_csv(filename=SAMPLE_DATA_FILENAMES['tutorial-csv'],
                                 object_id_column=3,
                                 timestamp_column=0,
                                 longitude_column=1,
                                 latitude_column=2,
                                 real_fields={'heading': 6},
                                 string_fields={'vessel-name': 7},
                                 time_fields={'eta': 17},
                                 separation_distance=10, # km
                                 separation_time=timedelta(minutes=20),
                                 minimum_length=5 # points
                                ):

    # create the reader using Tracktable sample data
    reader = create_point_reader(filename=filename,
                                 object_id_column=object_id_column,
                                 timestamp_column=timestamp_column,
                                 longitude_column=longitude_column,
                                 latitude_column=latitude_column,
                                 real_fields=real_fields,
                                 string_fields=string_fields,
                                 time_fields=time_fields)

    # create the builder object
    builder = AssembleTrajectoryFromPoints()
    builder.input = reader

    # specify optional builder parameters
    builder.separation_distance = separation_distance # km
    builder.separation_time = separation_time
    builder.minimum_length = minimum_length # points

    # assemble trajectories
    return list(builder)


def get_trajectory_list(dataset='tutorial-traj'):

    with open(SAMPLE_DATA_FILENAMES[dataset], 'r') as traj_file:
        # create a Tracktable TrajectoryReader object
        reader = TrajectoryReader()
        # tell it where to find the traj file
        reader.input = traj_file
        # import the list of trajectories
        return list(reader)


def count_points(trajectories):

    num_points = 0
    for trajectory in trajectories:
        num_points += len(trajectory)
    return num_points


def average_speed(trajectory):

    return speed_between(trajectory[0], trajectory[-1])


def straightness(trajectory):

    # get the distance between endpoints of a trajectory
    end_to_end_dist = end_to_end_distance(trajectory)

    # get the distance traveled along the trajectory
    dist_traveled = length(trajectory)

    # if the trajectory doesn't move, it is not straight
    if dist_traveled == 0:
        return 0

    # measure how well the trajectory followed the straight path
    return end_to_end_dist / dist_traveled


def print_statistic(trajectories, feature, units, function):
    """Prints the min/max for a given feature over a list of trajectories."""

    values = []
    for trajectory in trajectories:
        values.append(function(trajectory))
    print(f'The {feature} of the given trajectories ranges from {min(values)}{units} '
          f'to {max(values)}{units}.')


def print_statistics(trajectories, feature_list):

    # allow input of single statistic or lists
    if not isinstance(feature_list, list):
        feature_list = [feature_list]

    statistic_function = {'length': length,
                          'straightness': straightness,
                          'convex hull area': convex_hull_area,
                          'average speed': average_speed}

    statistic_units = {'length': ' km',
                       'straightness': '',
                       'convex hull area': ' km^2',
                       'average speed': ' km/hr'}

    if 'total trajectories' in feature_list or 'all' in feature_list:
        print(f'There are {len(trajectories)} total trajectories.')

    if 'total points' in feature_list or 'all' in feature_list:
        num_points = 0
        for trajectory in trajectories:
            num_points += len(trajectory)
        print(f'The total number of points in the given trajectory list is {num_points}.')

    for feature, function in statistic_function.items():
        if feature in feature_list or 'all' in feature_list:
            print_statistic(trajectories,
                            feature,
                            statistic_units[feature],
                            statistic_function[feature])


def annotation_generator(annotator, traj_source):
    for trajectory in traj_source:
        yield(annotator(trajectory))


def constant_linewidth_generator(linewidth = 2):
    def linewidth_generator(trajectory):
        scalars = zeros(len(trajectory))
        scalars += float(linewidth)
        return scalars
    return linewidth_generator


def trajectories_to_end_points(trajectories):
    points = []
    for traj in trajectories:
        points.append(traj[0])
        points.append(traj[-1])
    return points


def get_bbox(area, domain):
    coords = []
    location = maps.CONVENIENCE_MAPS[area]
    coords.append(location['min_corner'][0])
    coords.append(location['min_corner'][1])
    coords.append(location['max_corner'][0])
    coords.append(location['max_corner'][1])
    return render_map._make_bounding_box(coords, domain)

###############################################################################
# HELPER FUNCTIONS FOR TRACKTABLE DEMOS
###############################################################################


def split_trajectories(trajectories):

    new_trajectories = []
    for trajectory in trajectories:
        # split the trajectory and add the new, split trajectories to our new
        # trajectory list
        new_trajectories.extend(split_when_idle(trajectory))

    return new_trajectories


def filter_trajectories(trajectories,
                        min_length=0,
                        max_length=float('inf'),
                        min_average_speed=0,
                        max_average_speed=float('inf'),
                        min_convex_hull_area=0,
                        max_convex_hull_area=float('inf'),
                        min_straightness=0,
                        max_straightness=1):

    return [trajectory for trajectory in trajectories
            if ((min_length <= length(trajectory) <= max_length) and
                (min_average_speed <= speed_between(trajectory[0], trajectory[-1]) <= max_average_speed) and
                (min_convex_hull_area <= convex_hull_area(trajectory) <= max_convex_hull_area) and
                (min_straightness <= end_to_end_distance(trajectory) / length(trajectory) <= max_straightness))]
