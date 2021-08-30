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

# TODO (mjfadem): Update this
"""
tracktable.analysis.assemble_trajectories - Sources that turn a sequence of points into a sequence of trajectories
"""

import datetime
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
from tracktable.analysis.assemble_trajectories import \
    AssembleTrajectoryFromPoints
from tracktable.analysis.rtree import RTree
from tracktable.core.geomath import (ECEF_from_feet, distance, interpolate,
                                     length, point_at_length_fraction,
                                     point_at_time)
from tracktable.domain.cartesian3d import BasePoint as CartesianPoint3D
from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.domain.terrestrial import (Trajectory, TrajectoryPointReader,
                                           TrajectoryReader, TrajectoryWriter)
from tracktable.render.render_trajectories import render_trajectories
from tracktable.render.map_decoration.coloring import matplotlib_cmap_to_dict

###############################################################################
######################### PREDICTION HELPER FUNCTIONS #########################
###############################################################################

def min_total_distance(traj_list, distance):
    """Will remove trajectories that are less than the given distance

    Args:
        traj_list: list of trajectory objects to filter
        distance: minimum distance in km trajectories must be to remain in final
            list

    Returns: the trajectory object list whose trajectories are over the given
    distance

    """

    return [traj for traj in traj_list if length(traj) > distance]


def keep_flights(traj_list, flight_type):
    """Keep trajectories of a certain type, i.e. Commercial, private

    Args:
        traj_list: List of trajectory objects to filter
        flight_type: 'C' for commercial or 'P' for private, these will be kept

    Returns: the trajectory object list with the flight type specified

    """

    # Keep commercial flights based off of id number
    if flight_type == 'C':
        return [traj for traj in traj_list if (traj.object_id[0] != 'N') or
                (traj.object_id[1] < '0' or traj.object_id[1] > '9')]
    else:
        return [traj for traj in traj_list if traj.object_id[0] == 'N']


def consistent_origin(traj_list):
    """Removes trajectories whose points do not contain a consistent point of
    origin

    Args:
        traj_list: List of trajectory objects to filter

    Returns: the trajectory list whose trajectories contain consistent origins

    """

    filtered_list = []
    for traj in traj_list:
        front_origin = traj[0].properties['orig']
        end_origin = traj[-1].properties['orig']
        if front_origin == end_origin and front_origin is not None and \
                end_origin is not None:
            filtered_list.append(traj)
    return filtered_list


def consistent_dest(traj_list):
    """Removes trajectories whose points do not contain a consistent destination

    Args:
        traj_list: List of trajectory objects to filter

    Returns: the trajectory list whose trajectories contain consistent
    destinations

    """

    filtered_list = []
    for traj in traj_list:
        front_dest = traj[0].properties['dest']
        end_dest = traj[-1].properties['dest']
        if front_dest == end_dest and front_dest is not None and \
                end_dest is not None:
            filtered_list.append(traj)
    return filtered_list


def find_subtrajectory(trajectory, fragment_length, samples, start_frac=None):
    """Chooses a sub-trajectory of length fragment_length from a whole
    trajectory where the starting point is more than 100km from the end

    Args:
        trajectory: A trajectory to find a sub-trajectory from
        fragment_length: Length of the trajectory to keep as the sub-trajectory
        samples: Number of points to represent the sub-trajectory with
        start_frac (optional): where to begin the sub-trajectory in the whole
            trajectory

    Returns:a tuple whose first element is the fraction of the initial whole
    trajectory at which the sub-trajectory begins and whose second element is
    the sub-trajectory represented as a list of points that is samples long

    """

    t_length = length(trajectory)
    # pick a random start_frac
    if start_frac is None:
        start_frac = random.uniform(0, 1) * (1.0 - fragment_length / t_length)
    samples_list = []
    for i in range(samples):
        frac = start_frac + (fragment_length / t_length) * i / (samples - 1)
        samples_list.append(point_at_length_fraction(trajectory, frac))
    return start_frac, samples_list


def pick_observed(trajs, index=None, fragment_length=100, samples=4,
                  start_frac=0.2):
    """Chooses an observed trajectory of length fragment_length from a whole
    trajectory where the starting point is more than 100km from the end

    Args:
        trajs: a list of trajectories
        index: (optional) index in the list of trajectories to use as the
               'observed trajectory'
        fragment_length: (optional) Length of the trajectory to keep as the
            observed trajectory
        samples: (optional) Number of points to represent the observed
            trajectory with
        start_frac (optional): where to begin the observed trajectory in the
            whole trajectory

    Returns: a Trajectory, the observed trajectory

    """
    if index is None:
        # pick a random index
        index = random.randint(0, len(trajs - 1))
    observed_traj = find_subtrajectory(trajs[index], fragment_length, samples,
                                       start_frac=start_frac)[1]
    return Trajectory.from_position_list(observed_traj)


def sample_traj(trajectory, samples):
    """ Represent a trajectory as a list of samples evenly spaced points

    Args:
        trajectory: trajectory to sample
        samples: number of points to represent the trajectory with

    Returns: list of sampled points

    """

    t_length = length(trajectory)
    samples_list = []
    for i in range(samples):
        frac = t_length * i / (samples - 1)
        samples_list.append(point_at_length_fraction(trajectory, frac/t_length))
    return samples_list


def create_feature_vector(point, index):
    """Creates a feature vector from long, lat, altitude (set to 0) and the
    trajectory a point belongs to

    Args:
        point: to make into a feature vector
        index: The index from a list of trajectories that indicates which
            trajectory the point belongs to

    Returns: a feature vector

    """

    # altitude is not guaranteed in the data
    point.set_property("altitude", 0)
    converted_point = ECEF_from_feet(point, "altitude")
    return convert_to_feature_vector([converted_point[0],
                                      converted_point[1], converted_point[2],
                                      index])


def create_id_to_index(trajs):
    """Create a dictionary that maps original_traj_id to its index in trajs

    Args:
        trajs: list of trajectories

    Returns: dictionary described above

    """

    id_to_index = {}
    for traj in range(len(trajs)):
        id_to_index[trajs[traj].trajectory_id] = traj
    return id_to_index


def linear_weights(x):
    """Creates a linear weight function where x will scale the distance weights
    0 and 1 (use neigh distance)

    Args:
        x: used to scale the weights between 0 and 1

    Returns: a weight function that takes one parameter (distance)

    """

    return lambda d: 1 - d / x


def km2radians(distance):
    """Convert distance from km to radians given that we are working on the
    surface of the earth

    Args:
        distance: distance in km

    Returns: distance in radians

    """

    # divide the distance by the radius of the sphere (in this case the earth)
    return float(distance / 6371)


def rep_traj_with_segments(traj):
    """Represents a trajectory by a list of segments

    Args:
        traj: Trajectory

    Returns: a list of trajectories (segments)

    """

    segments = []

    for point in range(len(traj) - 1):
        segment = Trajectory.from_position_list([traj[point], traj[point + 1]])
        segments.append(segment)

    return segments


def find_best_segment(segments, point):
    """Finds the closest segment to the point

    Args:
        segments: list of segments (which are trajectories made up of two
            points)
        point: point object

    Returns: a tuple where the first element is the distance to the closest
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
    return km2radians(closest_distance), closest_seg


def nearest_traj_point(traj, point, segs):
    """Finds the closest point on a trajectory (traj) to a point (point)

    Args:
        traj: index of the trajectory in the list of all historical trajectories
        point: point object
        segs: list of all historical trajectories represented as segments

    Returns: the closest point

    """

    traj_as_segs = segs[traj]
    # Find the segment in the trajectory that the point is nearest
    min_distance, segment = find_best_segment(traj_as_segs, point)
    # Nearest point could be nearest to either of the endpoints of the segments
    if distance(segment[0], point) == min_distance:
        return segment[0]
    elif distance(segment[1], point) == min_distance:
        return segment[1]
    else:
        # note that we want spherical distance here, convert to radians
        interpolant = acos(cos(km2radians(distance(segment[0], point)))
                           / cos(min_distance)) \
                      / km2radians(distance(segment[0], segment[1]))
        return interpolate(segment[0], segment[1], interpolant)


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


def import_observed(data_file):
    """Import trajectories from a .traj file into a list
    note: this is a place holder function

    Args:
        data_file: .traj file containing observed trajectory information

    Returns: a list of Trajectory objects

    """

    reader = TrajectoryReader()
    reader.input = open(data_file, 'r')
    return list(reader)


def process_historical_trajectories(data_file, raw_data=None, separation_time=20,
                                    separation_distance=100, minimum_length=20,
                                    minimum_total_distance=200,
                                    only_commercial=True):
    """Process historical trajectories from a file, filter them,
    and construct all of the data structures needed for prediction

    Args:
        data_file: .csv, .tsv, or .traj file containing historical trajectory
            information
        separation_time (optional): Maximum permissible time (in minutes)
            difference between adjacent points in a trajectory. Default= 20 min
        separation_distance (optional): Maximum permissible geographic distance
            (km) between adjacent points in a trajectory. Default = 100.
        minimum_length (optional): Complete trajectories with fewer than this
            many points will be discarded. Default = 20.
        minimum_total_distance (optional): require trajectories be longer than
            this distance (km). Default = 200 km.
        only_commercial (optional): Boolean. True if you want to work with only
            commercial flights. Default = True.

    Returns: a dictionary of datastructures which wil be used in the prediction
    algorithm
    trajs : a list of all of the historical trajectories
    all_points : a list of all of the points of all of the historical
        trajectories
    tree : rtree containing all of the points of the historical trajectories
        where the point is represented as a
    feature vector of coordinates and whose fourth component is the index of
        the trajectory in trajs to which the point belongs
    segs : a list of all of the historical trajectories represented as lists of
        segments (trajectories comprised of 2 points)
    id_to_index : dictionary mapping trajectory id to index in trajs

    """

    # reading in points
    if raw_data:
        reader = TrajectoryReader()
        reader.input = raw_data
        trajs = list(reader)
    elif data_file[-4:] == '.csv' or data_file[-4:] == '.tsv':
        # read in the data
        try:
            with open(data_file, 'rb') as inFile:
                bytes_to_read = os.path.getsize(data_file)
                wrapped_file = InputFile(inFile)

                reader = TrajectoryPointReader()
                reader.input = wrapped_file
                reader.comment_character = '#'
                reader.field_delimiter = "\t"
                reader.object_id_column = 0
                reader.timestamp_column = 1
                reader.coordinates[0] = 2
                reader.coordinates[1] = 3
                reader.set_real_field_column('altitude', 6)
                reader.set_string_field_column('orig', 25)
                reader.set_string_field_column('dest', 30)

                builder = AssembleTrajectoryFromPoints()
                builder.input = reader
                builder.minimum_length = minimum_length
                builder.separation_time = datetime.timedelta(minutes=
                                                             separation_time)
                builder.separation_distance = separation_distance
                trajectories = []
                print('Begin reading in trajectories from file', flush=True)
                with tqdm(total=bytes_to_read) as pbar:
                    for traj in builder.trajectories():
                        pbar.update(wrapped_file.get_bytes_and_reset())
                        trajectories.append(traj)
        except:
            print("Cannot open file.", flush=True)
            return

        # filter
        trajs = min_total_distance(trajectories, minimum_total_distance)
        if only_commercial:
            trajs = keep_flights(trajs, 'C')
        trajs = consistent_origin(trajs)
        trajs = consistent_dest(trajs)
    # reading in trajectories
    elif data_file[-5:] == '.traj':
        reader = TrajectoryReader()
        reader.input = open(data_file, 'r')
        trajs = list(reader)
    else:
        print("Improper file type", flush=True)
        return

    predict_dict = {}
    predict_dict['trajs'] = trajs

    # Set up RTree with all the points we are looking at and which trajectory
    # each point belongs to
    all_points = []
    print('Begin constructing feature vectors from all points', flush=True)
    for i in tqdm(range(0, len(trajs))):
        for point in trajs[i]:
            all_points.append(create_feature_vector(point, i))
    print('Begin constructing RTree', flush=True)
    tree = RTree(points=tqdm(all_points))

    predict_dict['all_points'] = all_points
    predict_dict['tree'] = tree

    segs = []
    print('Begin creating segment representation for all trajectories',
          flush=True)
    for traj in tqdm(trajs):
        segs.append(rep_traj_with_segments(traj))

    predict_dict['segs'] = segs

    id_to_index = create_id_to_index(trajs)

    predict_dict['id_to_index'] = id_to_index

    return predict_dict


###############################################################################
########################### PREDICTION FUNCTION ###############################
###############################################################################

def align(rtree, all_points, trajs, observed_traj, neigh_distance):
    """Find historical trajectories that are close to at least one sample point
    of the observed trajectory

    Args:
        rtree: an rtree containing all of the points from historical
            trajectories
        all_points: a list of all the points in the rtree
        trajs: a list of all the historical trajectories
        observed_traj: Trajectory
        neigh_distance: points within this distance to the observed trajectory
            are considered close to it/nearby

    Returns: a dictionary of historical trajectories that align with the
    observed trajectory. Maps trajectory indices in trajs to the number of
    sample points the historical trajectory is close to

    """
    results0 = []
    aligning_trajs = {}
    for point in tqdm(observed_traj):
        point.set_property("altitude", 0)
        # convert to ECEF for more exact distance calculations
        converted_point = ECEF_from_feet(point, "altitude")
        # create a bounding box of size neigh_distance around the point
        min_corner = CartesianPoint3D(converted_point)
        max_corner = CartesianPoint3D(converted_point)
        for j in range(3):
            min_corner[j] -= neigh_distance
            max_corner[j] += neigh_distance
        # account for points being stored as feature vectors with last point
        # being its index in list of trajectories
        min_corner_fv = [min_corner[0], min_corner[1], min_corner[2], 0]
        max_corner_fv = [max_corner[0], max_corner[1], max_corner[2],
                         len(trajs)]
        # perform a search in the rtree for points from other trajectories
        results0 = rtree.find_points_in_box(min_corner=min_corner_fv,
                                            max_corner=max_corner_fv)
        # ensure trajectory is in neigh_distance of sample point
        # remember that we searched a box, but we really want points in a
        # sphere ensure that each trajectory is only added to the dictionary
        # once
        already_added = set()
        for t_index in results0:
            traj = int(all_points[t_index][3])
            # calculate distance from point to trajectory
            traj_to_point = distance(trajs[traj], point)
            if (not (traj in already_added)) \
                    and (traj_to_point < neigh_distance):
                already_added.add(traj)
                if traj in aligning_trajs.keys():
                    aligning_trajs[traj] = aligning_trajs[traj] + 1
                else:
                    aligning_trajs[traj] = 1

    return aligning_trajs


def find_well_aligned_trajectories(observed_traj, predict_dict,
                                   neigh_distance):
    """Find the well-aligned trajectories for a given observed trajectory
    in historical data. A historical trajectory is well aligned to an observed
    trajectory if it is within neigh_distance to each of the observed
    trajectory's sample points

    Args:
        observed_traj: Trajectory
        predict_dict: prediction dictionary object returned from
            process_historical data
        neigh_distance: points within this distance to the observed trajectory
            are considered close to it/nearby

    Returns: a list of well-aligned trajectories' indices
    """

    rtree = predict_dict['tree']
    trajs = predict_dict['trajs']
    all_points = predict_dict['all_points']

    # find trajectories that are close to at least one sample point
    aligned_trajs = align(rtree, all_points, trajs, observed_traj,
                          neigh_distance)
    # filter to find trajectories that are close to all sample points
    well_aligned_trajs = [trajectory for trajectory, close_sample_points in
                          aligned_trajs.items()
                          if close_sample_points == len(observed_traj)]

    return well_aligned_trajs


def find_same_direction_trajectories(observed_traj, historical_trajectories,
                                     predict_dict):
    """Find the historical trajectories that go in the same direction as the
    observed trajectory

    Args:
        observed_traj: Trajectory
        historical_trajectories: list of historical trajectories
        predict_dict: prediction dictionary object returned from
            process_historical data

    Returns: a list of trajectory indices of trajectories that go in the
    same direction as the observed trajectory
    """

    segs = predict_dict['segs']
    correct_direction = []
    for traj in tqdm(historical_trajectories):
        # closest point to beginning of observed trajectory
        nearest_front = nearest_traj_point(traj, observed_traj[0], segs)
        # closest point to end of observed trajectory
        nearest_back = nearest_traj_point(traj, observed_traj[
            len(observed_traj) - 1], segs)
        # t2-t1
        duration = nearest_back.timestamp - nearest_front.timestamp
        # only add the trajectory if the direction is the same
        if duration >= datetime.timedelta(0):
            correct_direction.append(traj)

    return correct_direction


def find_weights_od(observed_traj, historical_trajectories, predict_dict,
                    weight_fn):
    """If an origin/destination prediction is being made, find the weights for
    each origin destination

    Args:
        observed_traj: Trajectory
        historical_trajectories: list of historical trajectories
        predict_dict: prediction dictionary object returned from
            process_historical data
        weight_fn: function that takes one parameter, distance, and returns a
            weight inversely related to distance

    Returns: a list. The first element is a list of origin/destination pairs
    sorted by weight, the second is a dictionary mapping origin/destination
    pairs to historical trajectory indices, the third is a dictionary mapping
    origin/destination pairs to weights

    """
    trajs = predict_dict['trajs']
    weights = {}
    pairs_to_trajs = {}
    for traj in historical_trajectories:
        # assume consistent origin/destination
        origin = trajs[traj][0].properties['orig']
        destination = trajs[traj][0].properties['dest']
        pair = (origin, destination)
        add_weight = []
        for point in observed_traj:
            new_distance = distance(trajs[traj], point)
            new_weight = weight_fn(new_distance)
            add_weight.append(new_weight)

        # pick the worst performing weight/point that is the farthest
        # away
        weight = min(add_weight)

        if pair in weights.keys():
            weights[pair] += weight
            pairs_to_trajs[pair].append(traj)
        else:
            weights[pair] = weight
            pairs_to_trajs[pair] = [traj]

    sum_of_weights = 0
    # find the sum of all the weights
    for traj in weights.keys(): sum_of_weights = sum_of_weights + weights[traj]
    # normalize
    for traj in weights.keys(): weights[traj] = weights[traj] / sum_of_weights

    # sort in descending order
    sorted_results = sorted(weights.items(), key=lambda x: x[1], reverse=True)

    return [x[0] for x in sorted_results], pairs_to_trajs, weights


def find_weights_trajs(observed_traj, historical_trajectories, predict_dict,
                       weight_fn):
    """If an location prediction is being made, find the weights for each
    historical trajectory

    Args:
        observed_traj: Trajectory
        historical_trajectories: list of historical trajectories
        predict_dict: prediction dictionary object returned from
            process_historical data
        weight_fn: function that takes one parameter, distance, and returns a
            weight inversely related to distance

    Returns: a list. The first element is a list of trajectory ids sorted by
    weight, the second is an empty dictionary this is a place holder to keep
    format consistent with od weighting function, the third is a dictionary
    mapping trajectory ids to weights

    """

    trajs = predict_dict['trajs']
    weights = {}
    for traj in historical_trajectories:
        name = trajs[traj].trajectory_id
        add_weight = []
        for point in observed_traj:
            new_distance = distance(trajs[traj], point)
            new_weight = weight_fn(new_distance)
            add_weight.append(new_weight)

        # choose the worst weight
        weight = min(add_weight)
        weights[name] = weight

    sum_of_weights = 0
    # find the sum of all the weights
    for traj in weights.keys(): sum_of_weights = sum_of_weights + weights[traj]
    # normalize
    for traj in weights.keys(): weights[traj] = weights[traj] / sum_of_weights

    # sort in descending order
    sorted_results = sorted(weights.items(), key=lambda x: x[1], reverse=True)

    return [x[0] for x in sorted_results], {}, weights


def predict_helper(predict_dict, observed_traj, neigh_distance, group_od):
    """Will find historical trajectories that are well aligned with the
    observed trajectory and assign weights to these trajectories by
    origin/destination pair or individual historical trajectory.

    Args:
        predict_dict: dictionary returned from process_historical_trajectories
            function
        observed_traj: Trajectory to make a prediction for
        neigh_distance: points within this distance to the observed trajectory
            are considered close to it/nearby
        group_od: boolean, if true weight by origin/destination pair, if false
            weight by individual historical trajectory

    Returns: a list whose contents depend on which function is used to assign
        weights : find_weights_trajs or find_weights_od

    """

    weight_fn = linear_weights(neigh_distance)

    # find well-aligned trajectories
    well_aligned_trajs = find_well_aligned_trajectories(observed_traj,
                                                        predict_dict,
                                                        neigh_distance)

    # find historical trajs that go in the same direction as observed traj
    same_direction_trajs = find_same_direction_trajectories(observed_traj,
                                                            well_aligned_trajs,
                                                            predict_dict)

    # results in terms of od pairs
    if group_od:
        return find_weights_od(observed_traj, same_direction_trajs,
                               predict_dict, weight_fn)
    # results in terms of trajectories
    else:
        return find_weights_trajs(observed_traj, same_direction_trajs,
                                  predict_dict, weight_fn)


def predict_location(observed_traj, predict_dict, minutes, neigh_distance=5,
                     samples=4):
    """Predicts the location of the trajectory in the specified amount of
    minutes

    Args:
        observed_traj: the observed trajectory for which to make a prediction
        predict_dict: prediction dictionary object returned from
            process_historical data
        minutes: Number of minutes forward to predict
        neigh_distance (optional) : points within this distance (km) to the
            observed trajectory are considered close to it/nearby. Default = 5.
        samples (optional) : the number of points to represent the observed
            trajectory with. Default = 4.

    Returns: a list. The first element is a dictionary of predicted points, the
    second element is a dictionary of paths to the points, and the third is a
    dictionary of weights for the points (for all the keys are the
    trajectory_ids)

    """
    end_point = observed_traj[-1]
    observed_traj = sample_traj(observed_traj, samples)

    predictions, _, weights = predict_helper(predict_dict, observed_traj,
                                             neigh_distance, False)

    points = {}
    paths = {}
    for traj in predictions:
        traj_index = predict_dict['id_to_index'][traj]
        nearest_point = nearest_traj_point(traj_index, end_point,
                                           predict_dict['segs'])
        predict_time = nearest_point.timestamp + \
                       datetime.timedelta(minutes=minutes)
        predicted_point = point_at_time(predict_dict['trajs'][traj_index],
                                        predict_time)
        predicted_path = []
        for p in predict_dict['trajs'][traj_index]:
            if nearest_point.timestamp <= p.timestamp <= \
                    predicted_point.timestamp:
                predicted_path.append(p)
        points[predict_dict['trajs'][traj_index].trajectory_id] = \
            predicted_point
        paths[predict_dict['trajs'][traj_index].trajectory_id] = predicted_path

    return points, paths, weights


def predict_origin_destination(observed_traj, predict_dict, neigh_distance=5,
                               samples=4, printResults=True):
    """Predicts the origin and destination of an observed trajectory

    Args:
        observed_traj: the observed trajectory for which to make a prediction
        predict_dict: prediction dictionary object returned from
            process_historical data
        neigh_distance (optional) : points within this distance (km) to the
            observed trajectory are considered close to
            it/nearby
        samples (optional) : the number of points to represent the observed
            trajectory with. Default = 4.

    Returns: a dictionary of results

    The results dictionary has the following fields:

    predictions:                ordered list of origin/destination pairs (pairs
                                of strings)
    OD_pairs_to_trajs:          dictionary mapping origin/destination pair to
                                the trajectory objects whose weights went
                                towards the total weight of the
                                origin/destination pair on the prediction list
    weights:                    a dictionary mapping origin/destination pair to
                                weight
    integrated_weights:         a dictionary mapping origin/destination pair to
                                integrated weight. Where integrated weight is
                                the sum of the weights of the previous
                                positions on the prediction list (the first
                                position on the prediction list has weight 0)

    """

    # Sub select the observed trajectory by the number of samples (parameter)
    observed_traj = sample_traj(observed_traj, samples)

    predictions, pairs_to_trajs, weights = predict_helper(predict_dict,
                                                          observed_traj,
                                                          neigh_distance, True)

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
        pairs_to_traj_ids[od] = [predict_dict['trajs'][traj].trajectory_id
                                 for traj in pairs_to_trajs[od]]
    results['OD_pairs_to_trajs'] = pairs_to_traj_ids

    # print results
    if printResults:
        print("List of possible origin destinations with weights:")
        print("Orig\tDest\tWeight")
        for result in results['predictions']:
            print(result[0] + '\t' + result[1] + '\t' + '%.2f' % weights[result])
        print(str(len(results['predictions'])) + ' possible prediction(s)')
        print()

    return results


###############################################################################
############################# IMAGE GENERATION ################################
###############################################################################

def display_color_map(cmap):
    """Create a visual representation of a Matplotlib color map.

    Args:
        cmap (string): Name of one of Matplotlib built-in color maps.

    Returns:
        Matplotlib figure that displays the indicated colormap in a gradient

    """

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    plt.figure(figsize=(20, 2))
    ax = plt.axes()
    ax.get_xticklabels()
    ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap))
    ax.tick_params(labelbottom=False, labelleft=False, bottom=False,
                   left=False)
    plt.title('lower', fontsize=20, loc='left')
    plt.xlabel('higher', fontsize=20, loc='right')

    plt.show()


def heat_map_helper(points, weights):
    """Creates the approriate point formatting to use a heatmap

    Args:
        points: list of points to format
        weights: the weights those points received in the prediction algorithm

    Returns: a list of properly formatted points to feed into a heatmap

    """

    return [[points[key][1], points[key][0], weights[key]]
            for key in points.keys()]


def pos_heatmap(predicted_points, predicted_paths, predicted_weights,
                observed_traj, tiles='CartoDBPositron', attr='.',
                crs="EPSG3857", heat_map=None):
    """Creates a viz for predicting an observed trajectory's position in a
    given time

    Args:
        predicted_points: list of predicted points
        predicted_paths: list of predicted paths from the current end point of
            the observed trajectory to the predicted point
        predicted_weights: list of weights associated with each of the
            predicted points
        observed_traj: Trajectory
        tiles (optional): name of map tiling to use
        attr (optional): folium specific parameter
        crs (optional): folium specific parameter
        heat_map (optional): a pre-rendered folium map on which to overlay
            the map being rendered here

    Returns: a visualization of position prediction

    """
    # create the heat map
    if not heat_map:
        heat_map = folium.Map(tiles=tiles, zoom_start=4)

    # lat, long, weight of points to render
    display_points = heat_map_helper(predicted_points, predicted_weights)
    to_render = list(predicted_paths.values())
    # group all trajectories (including observed trajectory) in one list for
    # rendering
    to_render.append(observed_traj)
    colors = ['grey'] * len(predicted_paths)
    colors.append('red')
    gradient = matplotlib_cmap_to_dict('viridis')
    heat_map = render_trajectories(to_render, map_canvas=heat_map, backend='folium',
                                   line_color=colors, linewidth=1.0,
                                   tiles=tiles, attr=attr, crs=crs)
    HeatMap(display_points, gradient=gradient).add_to(heat_map)
    return heat_map


def od_render(observed_traj, results, predict_dict, tiles='CartoDBPositron',
              filename='pred_results.html', save=False, attr='.',
              crs="EPSG3857"):
    """Creates a viz for predicting an observed trajectory's origin and
    destination

    Args:
        observed_traj: Trajectory
        results: a results dictionary returned from predict_origin_destination
        predict_dict: a dictionary returned from
            process_historical_trajectories
        tiles (optional): name of map tiling to use
        filename (optional): name of file to save viz to
        save (optional): boolean, if you want to save the viz. Default = False.
        attr (optional): folium specific parameter
        crs (optional): folium specific parameter

    Returns: a visualization of origin/destination prediction

    """
    # pick one trajectory to render for each OD pair
    possibilities = []
    for prediction in results['predictions']:
        trajs = results['OD_pairs_to_trajs'][prediction]
        possibilities.append(predict_dict['trajs']
                             [predict_dict['id_to_index'][trajs[0]]])

        # render trajectories in different colors
    cmap = matplotlib.cm.get_cmap('viridis')
    colors = []
    for x in range(0, len(possibilities)):
        rgb = cmap(x * (1 / len(possibilities)))[:3]
        colors.append(matplotlib.colors.to_hex(rgb))
    # reverse so that more likely predictions have lighter colors
    colors.reverse()

    # make the sub trajectory red
    possibilities.append(observed_traj)
    colors.append('red')
    map_canvas = render_trajectories(possibilities, line_color=colors, show=True, save=save,
                        backend='folium', tiles=tiles, filename=filename,
                        attr=attr, crs=crs)
    return map_canvas


###############################################################################
########################### SAVE RELEVANT TRAJS ###############################
###############################################################################

def find_relevant_trajs_od(results, predict_dict):
    """Finds the trajectory objects associated with the historical trajectories
    that were well aligned with the observed trajectory

    Args:
        results: a results dictionary returned from predict_origin_destination
        predict_dict: dictionary returned from processing historical
            trajectories

    Returns: A list of relevant trajectories

    """

    relevant_trajectories = []
    for v in results['OD_pairs_to_trajs'].values():
        for traj in v:
            index = predict_dict['id_to_index'][traj]
            relevant_trajectories.append(predict_dict['trajs'][index])

    return relevant_trajectories


def find_relevant_trajs_location(points, predict_dict):
    """Finds the trajectory objects associated with the historical trajectories
    that were well aligned with the observed trajectory

    Args:
        points: the points dictionary returned from predict_location (first
            argument of the list)
        predict_dict: dictionary returned from processing historical
            trajectories

    Returns: A list of relevant trajectories

    """

    relevant_trajectories = []
    for traj in points.keys():
        index = predict_dict['id_to_index'][traj]
        relevant_trajectories.append(predict_dict['trajs'][index])

    return relevant_trajectories


def write_trajs(filename, relevant_trajectories):
    """ Writes relevant trajectories to a .traj file

    Args:
        filename: file to write the relevant trajectories to, must end in .traj
        relevant_trajectories: list of trajectory objects to write to file

    Returns: writes relevant trajectories to the specified file

    """
    if filename[-5:] == '.traj':
        with open(filename, 'wb') as output:
            writer = TrajectoryWriter(output)
            writer.write(relevant_trajectories)
