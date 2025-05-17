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

"""
tracktable.applications.prediction - Predict trajectory end point

We can use a database of already-seen trajectories to try to find matches
for a newly identified trajectory.  We do this by breaking up our
already-seen trajectories into fragments, computing a feature vector for
each one, and storing that feature vector in an R-tree.  Then, when we
want to predict where a new trajectory might be going, we compute a
feature vector for it and look for the nearest neighbor in our R-tree.

Like many prediction methods, this is not guaranteed to find the right
answer every time (especially when observing trajectories that don't
behave like anything else).  The exact success rate depends on the
quality of the match between the new trajectory and history.
"""

import datetime
import logging
import os
import random
from math import acos, cos

import folium
import matplotlib.colors
import matplotlib.pyplot
import matplotlib.pyplot as plt
import numpy as np
from folium.plugins import HeatMap
from tqdm import tqdm
from tracktable.applications.assemble_trajectories import \
    AssembleTrajectoryFromPoints
from tracktable.core.geomath import (ECEF_from_feet, distance, interpolate,
                                     km_to_radians, length,
                                     point_at_length_fraction, point_at_time)
from tracktable.domain.cartesian3d import BasePoint as CartesianPoint3D
from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.domain.rtree import RTree
from tracktable.domain.terrestrial import (Trajectory, TrajectoryPointReader,
                                           TrajectoryReader, TrajectoryWriter)
from tracktable.render.map_decoration.coloring import matplotlib_cmap_to_dict
from tracktable.render.render_trajectories import render_trajectories

logger = logging.getLogger(__name__)

###############################################################################
########################### FILE INPUT HELPER CLASS ###########################
###############################################################################
class InputFile(object):
    """ File-like object. """

    def __init__(self, file):
        self.file = file
        self.bytes = 0

    def __iter__(self):
        return self

    def get_bytes_and_reset(self):
        tmp = self.bytes
        self.bytes = 0
        return tmp

    def read(self, size=-1):
        data = self.file.read(size)
        self.bytes += len(data)
        return data

    def __next__(self):
        data = self.file.readline()
        if not data:
            raise StopIteration
        self.bytes += len(data)
        return data.decode('utf-8')

    next = __next__

###############################################################################
######################### PREDICTION HELPER FUNCTIONS #########################
###############################################################################

def _minimum_total_distance(trajectory_list, distance):
    """Will remove trajectories that are less than the given distance

    Arguments:
        trajectory_list (list): List of trajectory objects to filter
        distance (float): minimum distance in km trajectories must be to remain in final
            list

    Returns:
	    the trajectory object list whose trajectories are over the given
        distance
    """

    return [trajectory for trajectory in trajectory_list if length(trajectory) > distance]


def _keep_flights(trajectory_list, flight_type):
    """Keep trajectories of a certain type, i.e. Commercial, private

    Arguments:
        trajectory_list (list): List of trajectory objects to filter
        flight_type (str): 'C' for commercial or 'P' for private, these will be kept

    Returns:
        the trajectory object list with the flight type specified
    """

    # Keep commercial flights based off of id number
    if flight_type == 'C':
        return [trajectory for trajectory in trajectory_list if (trajectory.object_id[0] != 'N') or
                (trajectory.object_id[1] < '0' or trajectory.object_id[1] > '9')]
    else:
        return [trajectory for trajectory in trajectory_list if trajectory.object_id[0] == 'N']


def _consistent_origin(trajectory_list):
    """Removes trajectories whose points do not contain a consistent point of
    origin

    Arguments:
        trajectory_list (list): List of trajectory objects to filter

    Returns:
        the trajectory list whose trajectories contain consistent origins
    """

    filtered_list = []
    for trajectory in trajectory_list:
        front_origin = trajectory[0].properties['origin']
        end_origin = trajectory[-1].properties['origin']
        if front_origin == end_origin and front_origin is not None and \
                end_origin is not None:
            filtered_list.append(trajectory)
    return filtered_list


def _consistent_destination(trajectory_list):
    """Removes trajectories whose points do not contain a consistent destination

    Arguments:
        trajectory_list (list): List of trajectory objects to filter

    Returns:
        the trajectory list whose trajectories contain consistent
        destinations
    """

    filtered_list = []
    for trajectory in trajectory_list:
        front_dest = trajectory[0].properties['destination']
        end_dest = trajectory[-1].properties['destination']
        if front_dest == end_dest and front_dest is not None and \
                end_dest is not None:
            filtered_list.append(trajectory)
    return filtered_list


def _find_subtrajectory(trajectory, fragment_length, samples, start_fraction=None):
    """Chooses a sub-trajectory of length fragment_length from a whole
    trajectory where the starting point is more than 100km from the end

    Arguments:
        trajectory (Tracktable trajectory): A trajectory to find a sub-trajectory from
        fragment_length (int): Length of the trajectory to keep as the sub-trajectory in km
        samples (int): Number of points to represent the sub-trajectory with

    Keyword Arguments:
        start_fraction (float): where to begin the sub-trajectory in the whole
            trajectory. (Default: None)

    Returns:
        a tuple whose first element is the fraction of the initial whole
        trajectory at which the sub-trajectory begins and whose second element is
        the sub-trajectory represented as a list of points that is samples long
    """

    t_length = length(trajectory)
    # pick a random start_fraction
    if start_fraction is None:
        start_fraction = random.uniform(0, 1) * (1.0 - fragment_length / t_length)
    samples_list = []
    for i in range(samples):
        frac = start_fraction + (fragment_length / t_length) * i / (samples - 1)
        samples_list.append(point_at_length_fraction(trajectory, frac))
    return start_fraction, samples_list


def _pick_observed(trajectories, index=None, fragment_length=100, samples=4,
                  start_fraction=0.2):
    """Chooses an observed trajectory of length fragment_length from a whole
    trajectory where the starting point is more than 100km from the end

    Arguments:
        trajectories (list): a list of trajectories

    Keyword Arguments:
        index (int): index in the list of trajectories to use as the
               'observed trajectory'. (Default: None)
        fragment_length (int): Length of the trajectory to keep as the
            observed trajectory in km. (Default: 100)
        samples (int): Number of points to represent the observed
            trajectory with. (Default: 4)
        start_fraction (float): where to begin the observed trajectory in the
            whole trajectory. (Default: 0.2)

    Returns:
        a Trajectory, the observed trajectory
    """

    if index is None:
        # pick a random index
        index = random.randint(0, len(trajectories - 1))
    observed_trajectory = _find_subtrajectory(trajectories[index], fragment_length, samples,
                                       start_fraction=start_fraction)[1]
    return Trajectory.from_position_list(observed_trajectory)

def _create_feature_vector(point, index):
    """Creates a feature vector from long, lat, altitude (set to 0) and the
    trajectory a point belongs to

    Arguments:
        point (Tracktable point): to make into a feature vector
        index (int): The index from a list of trajectories that indicates which
            trajectory the point belongs to

    Returns:
        a feature vector
    """

    # altitude is not guaranteed in the data
    point.set_property('altitude', 0)
    converted_point = ECEF_from_feet(point, 'altitude')
    return convert_to_feature_vector([converted_point[0],
                                      converted_point[1], converted_point[2],
                                      index])


def _create_id_to_index(trajectories):
    """Create a dictionary that maps original_traj_id to its index in trajectories

    Arguments:
        trajectories (list): list of trajectories

    Returns:
        dictionary described above
    """

    id_to_index = {}
    for trajectory in range(len(trajectories)):
        id_to_index[trajectories[trajectory].trajectory_id] = trajectory
    return id_to_index


def _linear_weights(x):
    """Creates a linear weight function where x will scale the distance weights
    0 and 1 (use neigh distance)

    Arguments:
        x (int): used to scale the weights between 0 and 1

    Returns:
        a weight function that takes one parameter (distance)
    """

    return lambda d: 1 - d / x

def _represent_trajectory_with_segments(trajectory):
    """Represents a trajectory by a list of segments

    Arguments:
        trajectory (Tracktable tracjectory): Trajectory

    Returns:
        a list of trajectories (segments)
    """

    segments = []

    for point in range(len(trajectory) - 1):
        segment = Trajectory.from_position_list([trajectory[point], trajectory[point + 1]])
        segments.append(segment)

    return segments


def _find_best_segment(segments, point):
    """Finds the closest segment to the point

    Arguments:
        segments (list): list of segments (which are trajectories made up of two
            points)
        point (Tracktable point): point object

    Returns:
        a tuple where the first element is the distance to the closest
        segment and the second is the segment
    """

    closest_distance = float('inf')
    closest_seg = None
    for segment in segments:
        d = distance(point, segment)
        # need to account for if two consecutive points are at the same location
        if d < closest_distance and distance(segment[0], segment[1]) > 0:
            closest_distance = d
            closest_seg = segment
    # note that we want spherical distance here, convert to radians
    return km_to_radians(closest_distance), closest_seg


def _nearest_trajectory_point(trajectory, point, segments):
    """Finds the closest point on a trajectory (trajectory) to a point (point)

    Arguments:
        trajectory (Tracktable trajectory): index of the trajectory in the list of all historical trajectories
        point (Tracktable point): point object
        segments (list): list of all historical trajectories represented as segments

    Returns:
        the closest point
    """

    traj_as_segs = segments[trajectory]
    # Find the segment in the trajectory that the point is nearest
    min_distance, segment = _find_best_segment(traj_as_segs, point)
    # Nearest point could be nearest to either of the endpoints of the segments
    if distance(segment[0], point) == min_distance:
        return segment[0]
    elif distance(segment[1], point) == min_distance:
        return segment[1]
    else:
        # note that we want spherical distance here, convert to radians
        interpolant = acos(cos(km_to_radians(distance(segment[0], point)))
                           / cos(min_distance)) \
                      / km_to_radians(distance(segment[0], segment[1]))
        return interpolate(segment[0], segment[1], interpolant)

def _predict_helper(prediction_dictionary, observed_trajectory, neighbor_distance, group_origin_destination):
    """Will find historical trajectories that are well aligned with the
    observed trajectory and assign weights to these trajectories by
    origin/destination pair or individual historical trajectory.

    Arguments:
        prediction_dictionary (dict): dictionary returned from process_historical_trajectories
            function
        observed_trajectory (Tracktable trajectory): Trajectory to make a prediction for
        neighbor_distance (int): points within this distance to the observed trajectory
            are considered close to it/nearby
        group_origin_destination (bool): If true weight by origin/destination pair, if false
            weight by individual historical trajectory

    Returns:
        a list whose contents depend on which function is used to assign
        weights either find_weights_trajectories or find_weights_origin_destination
    """

    weight_function = _linear_weights(neighbor_distance)

    # find well-aligned trajectories
    well_aligned_trajs = find_well_aligned_trajectories(observed_trajectory,
                                                        prediction_dictionary,
                                                        neighbor_distance)

    # find historical trajectories that go in the same direction as observed trajectory
    same_direction_trajs = find_same_direction_trajectories(observed_trajectory,
                                                            well_aligned_trajs,
                                                            prediction_dictionary)

    # results in terms of od pairs
    if group_origin_destination:
        return find_weights_origin_destination(observed_trajectory, same_direction_trajs,
                               prediction_dictionary, weight_function)
    # results in terms of trajectories
    else:
        return find_weights_trajectories(observed_trajectory, same_direction_trajs,
                                  prediction_dictionary, weight_function)

################################################################################
########################### PREDICTION FUNCTIONS ###############################
################################################################################

def sample_trajectory(trajectory, samples):
    """ Represent a trajectory as a list of samples evenly spaced points

    Arguments:
        trajectory (Tracktable trajectory): trajectory to sample
        samples (int): number of points to represent the trajectory with

    Returns:
        list of sampled points
    """

    t_length = length(trajectory)
    samples_list = []
    for i in range(samples):
        frac = t_length * i / (samples - 1)
        samples_list.append(point_at_length_fraction(trajectory, frac/t_length))
    return samples_list

def process_historical_trajectories(data_file, raw_data=None, separation_time=20,
                                    separation_distance=100, minimum_length=20,
                                    minimum_total_distance=200,
                                    only_commercial=True, quiet=False):
    """Process historical trajectories from a file, filter them, and
    construct all of the data structures needed for prediction

    Arguments:
        data_file (file): .csv, .tsv, or .traj file containing historical trajectory
            information

    Keyword Arguments:
        raw_data (Tracktable trajectories): Trajectories that need processed and
            aren't coming from a file. . (Default: None)
        separation_time (int): Maximum permissible time (in minutes)
            difference between adjacent points in a trajectory. (Default: 20)
        separation_distance (int): Maximum permissible geographic distance
            (km) between adjacent points in a trajectory. (Default: 100)
        minimum_length (int): Complete trajectories with fewer than this
            many points will be discarded. (Default: 20)
        minimum_total_distance (int): require trajectories be longer than
            this distance (km). (Default: 200)
        only_commercial (bool): True if you want to work with only
            commercial flights. (Default: True)
        quiet (bool): produce no output, no tqdm output

    Returns:
        A dictionary of data structures which will be used in the prediction algorithm.
    """

    # reading in points
    if raw_data:
        reader = TrajectoryReader()
        reader.input = raw_data
        trajectories = list(reader)
    elif data_file.endswith('.csv') or data_file.endswith('.tsv'):
        # read in the data
        try:
            with open(data_file, 'rb') as inFile:
                bytes_to_read = os.path.getsize(data_file)
                wrapped_file = InputFile(inFile)

                reader = TrajectoryPointReader()
                reader.input = wrapped_file
                reader.comment_character = '#'
                reader.field_delimiter = '\t'
                reader.object_id_column = 0
                reader.timestamp_column = 1
                reader.coordinates[0] = 2
                reader.coordinates[1] = 3
                reader.set_real_field_column('altitude', 6)
                reader.set_string_field_column('origin', 25)
                reader.set_string_field_column('destination', 30)

                builder = AssembleTrajectoryFromPoints()
                builder.input = reader
                builder.minimum_length = minimum_length
                builder.separation_time = datetime.timedelta(minutes=
                                                             separation_time)
                builder.separation_distance = separation_distance
                trajectories = []
                if not quiet:
                    logger.info('Begin reading in trajectories from file')
                with tqdm(total=bytes_to_read, disable=quiet) as pbar:
                    for trajectory in builder.trajectories():
                        pbar.update(wrapped_file.get_bytes_and_reset())
                        trajectories.append(trajectory)
        except:
            logger.error("Cannot open file.")
            raise IOError

        # filter
        trajectories = _minimum_total_distance(trajectories, minimum_total_distance)
        if only_commercial:
            trajectories = _keep_flights(trajectories, 'C')
        trajectories = _consistent_origin(trajectories)
        trajectories = _consistent_destination(trajectories)
    # reading in trajectories
    elif data_file.endswith('.traj'):
        reader = TrajectoryReader()
        reader.input = open(data_file, 'r')
        trajectories = list(reader)
    else:
        logger.error("Improper file type")
        raise IOError

    prediction_dictionary = {}
    prediction_dictionary['trajectories'] = trajectories

    # Set up RTree with all the points we are looking at and which trajectory
    # each point belongs to
    all_points = []
    if not quiet:
        logger.info('Begin constructing feature vectors from all points')
    for i in tqdm(range(0, len(trajectories)), disable=quiet):
        for point in trajectories[i]:
            all_points.append(_create_feature_vector(point, i))
    if not quiet:
        logger.info('Begin constructing RTree')
    tree = RTree(points=tqdm(all_points, disable=quiet))

    prediction_dictionary['all_points'] = all_points
    prediction_dictionary['tree'] = tree

    segments = []
    if not quiet:
        logger.info('Begin creating segment representation for all trajectories')
    for trajectory in tqdm(trajectories, disable=quiet):
        segments.append(_represent_trajectory_with_segments(trajectory))

    prediction_dictionary['segments'] = segments

    id_to_index = _create_id_to_index(trajectories)

    prediction_dictionary['id_to_index'] = id_to_index

    return prediction_dictionary

def align(rtree, all_points, trajectories, observed_trajectory,
          neighbor_distance, quiet=False):
    """Find historical trajectories that are close to at least one sample point
    of the observed trajectory

    Arguments:
        rtree (R-Tree): an rtree containing all of the points from historical
            trajectories
        all_points (list): a list of all the points in the rtree
        trajectories (list): a list of all the historical trajectories
        observed_trajectory (Tracktable trajectory): Trajectory
        neighbor_distance (int): points within this distance to the observed trajectory
            are considered close to it/nearby
        quiet (bool): disable output, no tqdm output

    Returns:
        a dictionary of historical trajectories that align with the
        observed trajectory. Maps trajectory indices in trajectories to the number of
        sample points the historical trajectory is close to
    """

    results0 = []
    aligning_trajs = {}
    for point in tqdm(observed_trajectory, disable=quiet):
        point.set_property('altitude', 0)
        # convert to ECEF for more exact distance calculations
        converted_point = ECEF_from_feet(point, 'altitude')
        # create a bounding box of size neighbor_distance around the point
        min_corner = CartesianPoint3D(converted_point)
        max_corner = CartesianPoint3D(converted_point)
        for j in range(3):
            min_corner[j] -= neighbor_distance
            max_corner[j] += neighbor_distance
        # account for points being stored as feature vectors with last point
        # being its index in list of trajectories
        min_corner_fv = [min_corner[0], min_corner[1], min_corner[2], 0]
        max_corner_fv = [max_corner[0], max_corner[1], max_corner[2],
                         len(trajectories)]
        # perform a search in the rtree for points from other trajectories
        results0 = rtree.find_points_in_box(min_corner=min_corner_fv,
                                            max_corner=max_corner_fv)
        # ensure trajectory is in neighbor_distance of sample point
        # remember that we searched a box, but we really want points in a
        # sphere ensure that each trajectory is only added to the dictionary
        # once
        already_added = set()
        for t_index in results0:
            trajectory = int(all_points[t_index][3])
            # calculate distance from point to trajectory
            traj_to_point = distance(trajectories[trajectory], point)
            if (not (trajectory in already_added)) \
                    and (traj_to_point < neighbor_distance):
                already_added.add(trajectory)
                if trajectory in aligning_trajs.keys():
                    aligning_trajs[trajectory] = aligning_trajs[trajectory] + 1
                else:
                    aligning_trajs[trajectory] = 1

    return aligning_trajs


def find_well_aligned_trajectories(observed_trajectory, prediction_dictionary,
                                   neighbor_distance, quiet=False):
    """Find the well-aligned trajectories for a given observed trajectory
    in historical data. A historical trajectory is well aligned to an observed
    trajectory if it is within neighbor_distance to each of the observed
    trajectory's sample points

    Arguments:
        observed_trajectory (Tracktable trajectory): Trajectory
        prediction_dictionary (dict): prediction dictionary object returned from
            process_historical data
        neighbor_distance (int): points within this distance to the observed trajectory
            are considered close to it/nearby
        quiet (bool): produce no output, no tqdm output

    Returns:
        a list of well-aligned trajectories' indices
    """

    rtree = prediction_dictionary['tree']
    trajectories = prediction_dictionary['trajectories']
    all_points = prediction_dictionary['all_points']

    # find trajectories that are close to at least one sample point
    aligned_trajs = align(rtree, all_points, trajectories, observed_trajectory,
                          neighbor_distance, quiet=quiet)
    # filter to find trajectories that are close to all sample points
    well_aligned_trajs = [trajectory for trajectory, close_sample_points in
                          aligned_trajs.items()
                          if close_sample_points == len(observed_trajectory)]

    return well_aligned_trajs


def find_same_direction_trajectories(observed_trajectory, historical_trajectories,
                                     prediction_dictionary, quiet=False):
    """Find the historical trajectories that go in the same direction as the
    observed trajectory

    Arguments:
        observed_trajectory (Tracktable trajectory): Trajectory
        historical_trajectories (list): list of historical trajectories
        prediction_dictionary (dict): prediction dictionary object returned from
            process_historical data
        quiet (bool): produce no output, no tqdm output

    Returns:
        a list of trajectory indices of trajectories that go in the
        same direction as the observed trajectory
    """

    segments = prediction_dictionary['segments']
    correct_direction = []
    for trajectory in tqdm(historical_trajectories, disable=quiet):
        # closest point to beginning of observed trajectory
        nearest_front = _nearest_trajectory_point(trajectory, observed_trajectory[0], segments)
        # closest point to end of observed trajectory
        nearest_back = _nearest_trajectory_point(trajectory, observed_trajectory[
            len(observed_trajectory) - 1], segments)
        # t2-t1
        duration = nearest_back.timestamp - nearest_front.timestamp
        # only add the trajectory if the direction is the same
        if duration >= datetime.timedelta(0):
            correct_direction.append(trajectory)

    return correct_direction


def find_weights_origin_destination(observed_trajectory, historical_trajectories,
                    prediction_dictionary, weight_function):
    """If an origin/destination prediction is being made, find the weights for
    each origin destination

    Arguments:
        observed_trajectory (Tracktable trajectory): Trajectory
        historical_trajectories (list): list of historical trajectories
        prediction_dictionary (dict): prediction dictionary object returned from
            process_historical data
        weight_function (function): function that takes one parameter, distance, and returns a
            weight inversely related to distance

    Returns:
        a list. The first element is a list of origin/destination pairs
        sorted by weight, the second is a dictionary mapping origin/destination
        pairs to historical trajectory indices, the third is a dictionary mapping
        origin/destination pairs to weights
    """

    trajectories = prediction_dictionary['trajectories']
    weights = {}
    pairs_to_trajs = {}
    for trajectory in historical_trajectories:
        # assume consistent origin/destination
        origin = trajectories[trajectory][0].properties['orig']
        destination = trajectories[trajectory][0].properties['dest']
        pair = (origin, destination)
        add_weight = []
        for point in observed_trajectory:
            new_distance = distance(trajectories[trajectory], point)
            new_weight = weight_function(new_distance)
            add_weight.append(new_weight)

        # pick the worst performing weight/point that is the farthest
        # away
        weight = min(add_weight)

        if pair in weights.keys():
            weights[pair] += weight
            pairs_to_trajs[pair].append(trajectory)
        else:
            weights[pair] = weight
            pairs_to_trajs[pair] = [trajectory]

    sum_of_weights = 0
    # find the sum of all the weights
    for trajectory in weights.keys(): sum_of_weights = sum_of_weights + weights[trajectory]
    # normalize
    for trajectory in weights.keys(): weights[trajectory] = weights[trajectory] / sum_of_weights

    # sort in descending order
    sorted_results = sorted(weights.items(), key=lambda x: x[1], reverse=True)

    return [x[0] for x in sorted_results], pairs_to_trajs, weights


def find_weights_trajectories(observed_trajectory, historical_trajectories, prediction_dictionary,
                       weight_function):
    """If an location prediction is being made, find the weights for each
    historical trajectory

    Arguments:
        observed_trajectory (Tracktable trajectory): Trajectory
        historical_trajectories (list): list of historical trajectories
        prediction_dictionary (dict): prediction dictionary object returned from
            process_historical data
        weight_function (function): function that takes one parameter, distance, and returns a
            weight inversely related to distance

    Returns:
        a list. The first element is a list of trajectory ids sorted by
        weight, the second is an empty dictionary this is a place holder to keep
        format consistent with od weighting function, the third is a dictionary
        mapping trajectory ids to weights
    """

    trajectories = prediction_dictionary['trajectories']
    weights = {}
    for trajectory in historical_trajectories:
        name = trajectories[trajectory].trajectory_id
        add_weight = []
        for point in observed_trajectory:
            new_distance = distance(trajectories[trajectory], point)
            new_weight = weight_function(new_distance)
            add_weight.append(new_weight)

        # choose the worst weight
        weight = min(add_weight)
        weights[name] = weight

    sum_of_weights = 0
    # find the sum of all the weights
    for trajectory in weights.keys(): sum_of_weights = sum_of_weights + weights[trajectory]
    # normalize
    for trajectory in weights.keys(): weights[trajectory] = weights[trajectory] / sum_of_weights

    # sort in descending order
    sorted_results = sorted(weights.items(), key=lambda x: x[1], reverse=True)

    return [x[0] for x in sorted_results], {}, weights


def predict_location(observed_trajectory, prediction_dictionary, minutes, neighbor_distance=5,
                     samples=4):
    """Predicts the location of the trajectory in the specified amount of
    minutes

    Arguments:
        observed_trajectory (Tracktable trajectory): the observed trajectory for which to make a prediction
        prediction_dictionary (dict): prediction dictionary object returned from
            process_historical data
        minutes (int): Number of minutes forward to predict

    Keyword Arguments:
        neighbor_distance (int): points within this distance (km) to the
            observed trajectory are considered close to it/nearby. (Default: 5)
        samples (int): the number of points to represent the observed
            trajectory with. (Default: 4)

    Returns:
        a list. The first element is a dictionary of predicted points, the
        second element is a dictionary of paths to the points, and the third is a
        dictionary of weights for the points (for all the keys are the
        trajectory_ids)
    """

    end_point = observed_trajectory[-1]
    observed_trajectory = sample_trajectory(observed_trajectory, samples)

    predictions, _, weights = _predict_helper(prediction_dictionary, observed_trajectory,
                                             neighbor_distance, False)

    points = {}
    paths = {}
    for trajectory in predictions:
        traj_index = prediction_dictionary['id_to_index'][trajectory]
        nearest_point = _nearest_trajectory_point(traj_index, end_point,
                                           prediction_dictionary['segments'])
        predict_time = nearest_point.timestamp + \
                       datetime.timedelta(minutes=minutes)
        predicted_point = point_at_time(prediction_dictionary['trajectories'][traj_index],
                                        predict_time)
        predicted_path = []
        for p in prediction_dictionary['trajectories'][traj_index]:
            if nearest_point.timestamp <= p.timestamp <= \
                    predicted_point.timestamp:
                predicted_path.append(p)
        points[prediction_dictionary['trajectories'][traj_index].trajectory_id] = \
            predicted_point
        paths[prediction_dictionary['trajectories'][traj_index].trajectory_id] = predicted_path

    return points, paths, weights


def predict_origin_destination(observed_trajectory, prediction_dictionary, neighbor_distance=5,
                               samples=4, printResults=True):
    """Predicts the origin and destination of an observed trajectory

    Arguments:
        observed_trajectory (Tracktable trajectory): the observed trajectory for which to make a prediction
        prediction_dictionary (dict): prediction dictionary object returned from
            process_historical data

    Keyword Arguments:
        printResults (bool): Flag to print the results of prediction to the logger (Default: True)
        neighbor_distance (int): points within this distance (km) to the
            observed trajectory are considered close to
            it/nearby. (Default: 5)
        samples (int): the number of points to represent the observed
            trajectory with. (Default: 4)

    Returns:
        a dictionary of results
    """

    # Sub select the observed trajectory by the number of samples (parameter)
    observed_trajectory = sample_trajectory(observed_trajectory, samples)

    predictions, pairs_to_trajs, weights = _predict_helper(prediction_dictionary,
                                                          observed_trajectory,
                                                          neighbor_distance, True)

    sum_weights = 0
    integrated_weights = {}
    for pair in predictions:
        integrated_weights[pair] = sum_weights
        sum_weights = sum_weights + weights[pair]

    results = {}

    # initialize
    results['predictions'] = predictions
    results['weights'] = weights
    results['integrated_weights'] = integrated_weights
    pairs_to_traj_ids = {}
    for od in pairs_to_trajs.keys():
        pairs_to_traj_ids[od] = [prediction_dictionary['trajectories'][trajectory].trajectory_id
                                 for trajectory in pairs_to_trajs[od]]
    results['OD_pairs_to_trajs'] = pairs_to_traj_ids

    if printResults:
        logger.info("List of possible origin destinations with weights:")
        logger.info("Orig\tDest\tWeight")
        for result in results['predictions']:
            logger.info(result[0] + '\t' + result[1] + '\t' + '%.2f' % weights[result])
        logger.info(str(len(results['predictions'])) + ' possible prediction(s)')

    return results


###############################################################################
########################### SAVE RELEVANT TRAJS ###############################
###############################################################################

def find_relevant_trajectories_origin_destination(results, prediction_dictionary):
    """Finds the trajectory objects associated with the historical trajectories
    that were well aligned with the observed trajectory

    Arguments:
        results (dict): a results dictionary returned from predict_origin_destination
        prediction_dictionary (dict): dictionary returned from processing historical
            trajectories

    Returns:
        A list of relevant trajectories
    """

    relevant_trajectories = []
    for v in results['OD_pairs_to_trajs'].values():
        for trajectory in v:
            index = prediction_dictionary['id_to_index'][trajectory]
            relevant_trajectories.append(prediction_dictionary['trajectories'][index])

    return relevant_trajectories


def find_relevant_trajectories_location(points, prediction_dictionary):
    """Finds the trajectory objects associated with the historical trajectories
    that were well aligned with the observed trajectory

    Arguments:
        points (dict): the points dictionary returned from predict_location (first
            argument of the list)
        prediction_dictionary (dict): dictionary returned from processing historical
            trajectories

    Returns:
        A list of relevant trajectories
    """

    relevant_trajectories = []
    for trajectory in points.keys():
        index = prediction_dictionary['id_to_index'][trajectory]
        relevant_trajectories.append(prediction_dictionary['trajectories'][index])

    return relevant_trajectories


def write_trajectories(filename, relevant_trajectories):
    """ Writes relevant trajectories to a .traj file

    Arguments:
        filename (str): file to write the relevant trajectories to, must end in .traj
        relevant_trajectories (list): list of trajectory objects to write to file

    Returns: writes relevant trajectories to the specified file
    """

    if filename.endswith('.traj'):
        with open(filename, 'wb') as output:
            writer = TrajectoryWriter(output)
            writer.write(relevant_trajectories)
