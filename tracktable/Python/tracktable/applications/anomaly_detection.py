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
tracktable.applications.anomaly_detection - Determine if trajectories are anomalous based
on the number of historical trajectories that pass by the same area.

The anomaly_detection() and R-Tree related functions
are the primary driver functions for anomaly detection.
"""

import logging

from tqdm import tqdm
from tracktable.core.geomath import (ECEF_from_feet, compute_bounding_box,
                                     intersects, point_at_length_fraction)
from tracktable.domain.cartesian3d import BasePoint as CartesianPoint3D
from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.domain.rtree import RTree
from tracktable.domain.terrestrial import Trajectory

logger = logging.getLogger(__name__)

##############################################################################
# ANOMALY DETECTION FUNCTIONS
##############################################################################

def anomaly_detection(trajectories_to_analyze,
                      historical_trajectories=[],
                      historical_points_rtree=None,
                      point_idx_to_traj_idx={},
                      num_historical_trajectories=0,
                      nearness_radius=5,
                      consider_direction=False, # Currently not able to consider direction.
                      num_control_points=4,
                      start_fraction=0,
                      end_fraction=1,
                      anomaly_threshold=0,
                      include_segments=False,
                      ram_limited=False,
                      filename=None):
    """
    Analyzes a list of trajectories against a list of historical trajectories
    to detect anomalies. Anomalies are any trajectories with no historical
    trajectories that pass by them.

    "Passing by" a trajectory is determined by examining num_control_points
    points equally-spaced along the trajectory and finding historical
    trajectories within a (2*nearness_radius) cube of all control points.

    Arguments:
        trajectories_to_analyze (list): list of Tracktable trajectorys
            We will compare each of these trajectories to all of the historical
            trajectories to determine anomalous behavior.

    Keyword Arguments:
        historical_trajectories (list): list of Tracktable trajectorys, opt.
            We will compare each trajectory in trajectories_to_analyze to these
            trajectories to determine anomalous behavior. If not specified,
            the historical_points_rtree must be given. (Default: [])
        historical_points_rtree (Tracktable RTree object): We will compare
            each trajectory in trajectories_to_analyze to these
            trajectory points to determine anomalous behavior. If not specified,
            historical_trajectories must be given so that an rtree can be
            created. (Default: None)
        point_idx_to_traj_idx (dict): A quick lookup to check what
            trajectory index a point index from the
            rtree corresponds to. If not specified, will be created. (Default: {})
        num_historical_trajectories (int): The total number of historical trajectories. (Default: 0)
        nearness_radius (float): The inradius, in km, of the cubes
            centered at each control point. Only trajectories within all of
            these cubes will be considered passersby. (Default: 5)
        consider_direction (bool): CURRENTLY UNABLE TO CONSIDER DIRECTION
            If true, we will only consider a historical
            trajectory to be a passerby if it is traveling the same direction as the trajectory
            being analyzed. (Default: False)
        num_control_points (int): The number of equally-spaced points to sample along each trajectory
            when looking for passersby. (Default: 4)
        start_fraction (float): The fraction along the trajectory where you want to start sampling
            control points when looking for passersby. (Default: 0)
        end_fraction (float): The fraction along the trajectory where you want to stop sampling
            control points when looking for passersby. (Default: 1)
        anomaly_threshold (int): Trajectories with total passersby equal to or less than this number
            will be considered anomalous. (Default: 0)
        include_segments (bool): Flag to find historical passersby with by spliting the trajectories
            into segments, requires additional computational resources (Default: False)
        ram_limited (bool): Create an rtree from points WITHOUT creating a points list by adding points to the
            tree one at a time, helps build rtrees on resource constrained systems. (Default: False)
        filename (bool): CURRENTLY UNABLE TO OUTPUT ANOMALIES TO FILE. File to output anomalies to. (Default: False)

    Returns:
        List that contains the index for every trajectory index that passes by the given trajectory.
    """

    # TODO: Get the logger to output to a file
    # if filename != None:
    #     open(filename, 'w').close() # To clear the file before we do a new run
    #     logging.basicConfig(filename=filename, filemode='a', level=logging.DEBUG)

    if historical_points_rtree == None:
        if len(historical_trajectories) == 0:
            raise Exception('Either list of historical trajectories or '
                            'R-Tree of points must be specified.')
        else:
            # Set up RTree containing the historical trajectory points
            historical_points_rtree, point_idx_to_traj_idx = create_rtree(historical_trajectories,
                                                                          ram_limited=ram_limited)
            num_historical_trajectories = len(historical_trajectories)
    elif num_historical_trajectories == 0:
        if len(historical_trajectories) == 0:
            raise Exception('If historical trajectories list is not given, the '
                            'number of historical trajectories must be specified.')
        else:
            num_historical_trajectories = len(historical_trajectories)

    logger.debug('Analyzing Each Trajectory for Anomalousness')

    nearby_trajectories = []

    anomalies_detected_with_points = 0
    anomalies_detected_with_segments = 0

    # Finding any historical trajectories that pass by each trajectory we
    #  are analyzing.
    for i, trajectory in enumerate(tqdm(trajectories_to_analyze, position=0, leave=True)):
        nearby_trajs = _find_passersby(trajectory,
                                          point_idx_to_traj_idx,
                                          historical_points_rtree,
                                          num_historical_trajectories,
                                          nearness_radius,
                                          consider_direction=consider_direction,
                                          num_control_points=num_control_points,
                                          start_fraction=start_fraction,
                                          end_fraction=end_fraction,
                                          anomaly_threshold=anomaly_threshold)

        if len(nearby_trajs) == 0:
            anomalies_detected_with_points += 1

            if include_segments:

                logger.debug(f'{i}: Point search found {len(nearby_trajs)} nearby trajectories.')

                nearby_trajs = _find_passersby_using_segments(trajectory,
                                                             historical_trajectories,
                                                             nearness_radius,
                                                             num_control_points=num_control_points,
                                                             start_fraction=start_fraction,
                                                             end_fraction=end_fraction,
                                                             anomaly_threshold=anomaly_threshold)
                if len(nearby_trajs) == 0:
                    anomalies_detected_with_segments += 1

                logger.debug(f'***Segment search found {len(nearby_trajs)} nearby trajectories.')

        nearby_trajectories.append(nearby_trajs)

    logger.debug(f'Detected {anomalies_detected_with_points} anomalies ')

    if include_segments:
        logger.debug(f'This was reduced to '
                f'{anomalies_detected_with_segments} anomalies '
                f'historical segments.')

    return nearby_trajectories


# TODO: Test if this is faster/slower than Tracktable's compute_bounding_box with buffer, then ECEF conversion to corners.
def _create_rtree_bounding_box(center_point,
                              buffer,
                              num_trajectories=0,
                              include_traj_index=True):
    """Create a bounding box around the values of the rtree.

    Arguments:
        center_point (Tracktable point): Point to use as the center of the bounding box.
        buffer (float): Amount of area to consider as valid around the bounding box.

    Keyword Arguments:
        num_trajectories (int): Number of trajectories to inlcude in the bounding box. (Default: 0)
        include_traj_index (bool): Include the index value associated with the trajectories. (Default: True)

    Returns:
        The min and max corner values of the bounding box.
    """

    # Convert this point to ECEF for more exact distance calculations.
    center_point.set_property("altitude", 0)
    center_point_ecef = ECEF_from_feet(center_point)

    # Create a bounding box around the center point. This will be a cube
    #  of length (2 * nearness_radius).
    min_corner = CartesianPoint3D(center_point_ecef)
    max_corner = CartesianPoint3D(center_point_ecef)
    for j in range(3):
        min_corner[j] -= buffer
        max_corner[j] += buffer
    min_corner_fv = [min_corner[0], min_corner[1], min_corner[2]]
    max_corner_fv = [max_corner[0], max_corner[1], max_corner[2]]

    # Last value is index in list of trajectories, and we want to
    #  include all of the trajectories.
    if include_traj_index:
        min_corner_fv.append(0)
        max_corner_fv.append(num_trajectories)

    return min_corner_fv, max_corner_fv


def _add_nearby_historical_points(traj_indices_near_all_control_points,
                                 control_point,
                                 nearness_radius,
                                 point_idx_to_traj_idx,
                                 num_historical_trajs,
                                 historical_points_rtree,
                                 i):
    """Given a set of historical trajectory indices that have been near all of the
       control points thus far, reduce this set to include only trajectories that
       are also near the given control point.

    Arguments:
        traj_indices_near_all_control_points (list): List that contains
            the index for every trajectory that passes by the given trajectory.
        control_point (Tracktable point): Point along the trajectory equally-spaced
            from the previous and next points.
        nearness_radius (float): The inradius, in km, of the cubes
            centered at each control point. Only trajectories within all of
            these cubes will be considered passersby.
        point_idx_to_traj_idx (dict): A quick lookup to check what
            trajectory index a point index from the
            rtree corresponds to. If not specified, will be created.
        num_historical_trajs (int): The total number of historical trajectories.
        historical_points_rtree (Tracktable RTree object): We will compare
            each trajectory in trajectories_to_analyze to these
            trajectory points to determine anomalous behavior. If not specified,
            historical_trajectories must be given so that an rtree can be
            created.
        i (int): Index of current control point along the trajectory.

    Returns:
        The min and max corner values of the bounding box.
    """

    # If we don't have a quick lookup dict, we'll need to use the rtree's list.
    if len(point_idx_to_traj_idx) == 0:
        points = historical_points_rtree.points

    # Create a search box around this control point to use in the rtree.
    min_corner, max_corner = _create_rtree_bounding_box(control_point,
                                                       nearness_radius,
                                                       num_historical_trajs)

    # Find points from the historical trajectories that are within
    #  our bounding box.
    point_indices_near_control_point = historical_points_rtree.find_points_in_box(min_corner=min_corner,
                                                                                 max_corner=max_corner)

    # Identify unique trajectories near this control point.
    if len(point_idx_to_traj_idx) == 0:
        traj_indices_near_control_point = {points[point_index][3]
                                           for point_index in point_indices_near_control_point}
    else:
        traj_indices_near_control_point = {point_idx_to_traj_idx[point_index]
                                           for point_index in point_indices_near_control_point}

    # Identify unique trajectories near ALL control points.
    if i == 0:
        traj_indices_near_all_control_points = traj_indices_near_control_point
    else:
        traj_indices_near_all_control_points = traj_indices_near_control_point.intersection(traj_indices_near_all_control_points)

    return traj_indices_near_all_control_points


def _find_passersby(trajectory,
                   point_idx_to_traj_idx,
                   historical_points_rtree,
                   num_historical_trajs,
                   nearness_radius=5,
                   consider_direction=False, # Currently not able to consider direction.
                   num_control_points=4,
                   start_fraction=0,
                   end_fraction=1,
                   anomaly_threshold=0):
    """
    Determines what vehicles from the historical dataset have passed by the
    trajectory. A historical trajectory must pass within a (2*nearness radius)
    length cube centered at each of num_control_points equally-spaced along
    the trajectory. These control points will start at fraction start_fraction
    along the trajectory, and end at end_fraction.

    Note that, to improve computation speed, anomalous trajectories will not
    have their passersby stored. (Only relevant for anomaly_threshold >= 1.)

    Arguments:
        trajectory (Tracktable Trajectory): Tracktable trajectory
            We will find all trajectories from the historical dataset that pass
            by this trajectory.
        point_idx_to_traj_idx (dict): A dictionary for converting a trajectory
            point index into the index of the trajectory that it came from.
        historical_points_rtree (Tracktable R-Tree): An r-tree containing every
            point from each historical trajectory as (x,y,z,trajectory_index),
            where (x,y,z) are ECEF coordinates and the last value is a unique
            ID indicating which trajectory the point came from.
        num_historical_trajs (int): The total number of historical trajectories.

    Keyword Arguments:
        nearness_radius (float): The inradius, in km, of the cubes
            centered at each control point. Only trajectories within all of
            these cubes will be considered passersby. (Default: 5)
        consider_direction (bool): CURRENTLY UNABLE TO CONSIDER DIRECTION
            If true, we will only consider a historical
            trajectory to be a passerby if it is traveling the same direction as the trajectory
            being analyzed. (Default: False)
        num_control_points (int): The number of equally-spaced points to sample along each trajectory
            when looking for passersby. (Default: 4)
        start_fraction (float): The fraction along the trajectory where you want to start sampling
            control points when looking for passersby. (Default: 0)
        end_fraction (float): The fraction along the trajectory where you want to stop sampling
            control points when looking for passersby. (Default: 1)
        anomaly_threshold (int): Trajectories with total passersby equal to or less than this number
            will be considered anomalous. (Default: 0)

    Returns
    -------
    List that contains the index for every trajectory that passes by the given trajectory.
    """

    # If we don't have a quick lookup dict, we'll need to use the rtree's list.
    if len(point_idx_to_traj_idx) == 0:
        points = historical_points_rtree.points

    traj_indices_near_all_control_points = set()

    for i in range(num_control_points):
        # Get a point along the trajectory (equally-spaced from the previous and next points).
        control_point = point_at_length_fraction(trajectory,
                                                 start_fraction + (end_fraction - start_fraction) * i / (num_control_points - 1))

        traj_indices_near_all_control_points = _add_nearby_historical_points(traj_indices_near_all_control_points,
                                                                            control_point,
                                                                            nearness_radius,
                                                                            point_idx_to_traj_idx,
                                                                            num_historical_trajs,
                                                                            historical_points_rtree,
                                                                            i)

        # If there are not enough unique trajectories near all control points so far, this trajectory must be anomalous.
        if len(traj_indices_near_all_control_points) == anomaly_threshold:
            traj_indices_near_all_control_points = set()
            break

    return traj_indices_near_all_control_points


def _find_passersby_using_segments(trajectory,
                                  historical_trajectories,
                                  nearness_radius,
                                  start_fraction=0,
                                  end_fraction=1,
                                  num_control_points=4,
                                  anomaly_threshold=0):

    """
    Determines what vehicles from the historical dataset have passed by the
    trajectory while utilizing segments of the given trajectory. A historical
    trajectory must pass within a (2*nearness radius)
    length cube centered at each of num_control_points equally-spaced along
    the trajectory. These control points will start at fraction start_fraction
    along the trajectory, and end at end_fraction.

    Note that, to improve computation speed, anomalous trajectories will not
    have their passersby stored. (Only relevant for anomaly_threshold >= 1.)

    Arguments:
        trajectory (Tracktable Trajectory): Tracktable trajectory
            We will find all trajectories from the historical dataset that pass
            by this trajectory.
        point_idx_to_traj_idx (dict): A dictionary for converting a trajectory
            point index into the index of the trajectory that it came from.
        historical_points_rtree (Tracktable R-Tree): An r-tree containing every
            point from each historical trajectory as (x,y,z,trajectory_index),
            where (x,y,z) are ECEF coordinates and the last value is a unique
            ID indicating which trajectory the point came from.
        num_historical_trajs (int): The total number of historical trajectories.

    Keyword Arguments:
        nearness_radius (float): The inradius, in km, of the cubes
            centered at each control point. Only trajectories within all of
            these cubes will be considered passersby. (Default: 5)
        consider_direction (bool): CURRENTLY UNABLE TO CONSIDER DIRECTION
            If true, we will only consider a historical
            trajectory to be a passerby if it is traveling the same direction as the trajectory
            being analyzed. (Default: False)
        num_control_points (int): The number of equally-spaced points to sample along each trajectory
            when looking for passersby. (Default: 4)
        start_fraction (float): The fraction along the trajectory where you want to start sampling
            control points when looking for passersby. (Default: 0)
        end_fraction (float): The fraction along the trajectory where you want to stop sampling
            control points when looking for passersby. (Default: 1)
        anomaly_threshold (int): Trajectories with total passersby equal to or less than this number
            will be considered anomalous. (Default: 0)

    Returns
    -------
    List that contains the index for every trajectory that passes by the given trajectory.
    """

    traj_indices_near_all_control_points = set()

    for i in range(num_control_points):
        # Get a point along the trajectory (equally-spaced from the previous
        #  and next points).
        control_point = point_at_length_fraction(trajectory,
                                                 start_fraction + (end_fraction - start_fraction) * i / (num_control_points - 1))

        traj_indices_near_control_point = set()

        for traj_index, hist_trajectory in enumerate(historical_trajectories):
            if intersects(hist_trajectory,
                          compute_bounding_box([control_point], buffer=(nearness_radius,)*2)):
                traj_indices_near_control_point.add(traj_index)

        # Identify unique trajectories near ALL control points.
        if i == 0:
            traj_indices_near_all_control_points = traj_indices_near_control_point
        else:
            traj_indices_near_all_control_points = traj_indices_near_control_point.intersection(traj_indices_near_all_control_points)

        # If there are not enough unique trajectories near all control points so far,
        #  this trajectory must be anomalous.
        if len(traj_indices_near_all_control_points) == anomaly_threshold:
            traj_indices_near_all_control_points = set()
            break

    return traj_indices_near_all_control_points


##############################################################################
# R-TREE FUNCTIONS
##############################################################################


def create_points_list(trajectories):

    """Create a list of points for a list of trajectories.

    Arguments:
        trajectories (list): List of trajectories to get points of.

    Returns:
        List of points
    """
    return create_points_list_and_lookup(trajectories,
                                         create_lookup=False)


def create_points_list_and_lookup(trajectories, create_lookup=True):

    """Create a list and lookup of points for a list of trajectories.

    Arguments:
        trajectories (list): List of trajectories to get points of.

    Keyword Arguments:
        create_lookup (bool): Create a dictionary for reverse-lookup of trajectory index. (Default: True)

    Returns:
        List of points and lookup
    """

    logger.debug('Create List of Points')

    points = []
    point_idx_to_traj_idx = {}
    #for traj_index, trajectory in enumerate(trajectories):
    for traj_index, trajectory in tqdm(enumerate(trajectories),
                                       total=len(trajectories)):
        for point in trajectory:
            # Convert this point to ECEF for more exact distance calculations.
            point.set_property("altitude", 0)
            converted_point = ECEF_from_feet(point, "altitude")
            # Append each point with its trajectory index to our points list.
            points.append((converted_point[0], converted_point[1], converted_point[2], traj_index))
            if create_lookup:
                # Create a dictionary for reverse-lookup of trajectory index.
                point_idx_to_traj_idx[len(points)-1] = traj_index

    if create_lookup:
        return points, point_idx_to_traj_idx
    else:
        return points


def points_to_rtree(points):

    """Put points into R-Tree.

    Arguments:
        points (list): List of points to put into an R-Tree.

    Returns:
        R-Tree of points
    """

    logger.debug('Create Points R-Tree (no bar)')

    return RTree(points=points)


def trajectories_to_rtree(trajectories, create_lookup=True):

    """Put trajectories in R-Tree.

    Arguments:
        trajectories (list): List of trajectories to put into R-Tree.

    Keyword Arguments:
        create_lookup (bool): Create a dictionary for reverse-lookup of trajectory index. (Default: True)

    Returns:
        R-Tree of points and lookup
    """

    if create_lookup:
        points, point_idx_to_traj_idx = create_points_list_and_lookup(trajectories)
    else:
        points = create_points_list(trajectories)

    points_rtree = points_to_rtree(points)

    if create_lookup:
        return points_rtree, point_idx_to_traj_idx
    else:
        return points_rtree


def traj_reader_to_rtree(reader):
    """Create an rtree given the trajectory reader, avoiding the need to store any tracks.

    Arguments:
        reader (Tracktable trajectory reader): Trajectory reader to create an rtree from.

    Returns:
        R-Tree of points and trajectory index
    """

    points_rtree = RTree()
    for traj_index, trajectory in enumerate(tqdm(reader)):
        for point in trajectory:
            # Convert this point to ECEF for more exact distance calculations.
            point.set_property("altitude", 0)
            ecef_point = ECEF_from_feet(point, "altitude")
            # Add the point (and its trajectory index) to our r-tree.
            points_rtree.insert_point(convert_to_feature_vector([ecef_point[0],
                                                                 ecef_point[1],
                                                                 ecef_point[2],
                                                                 traj_index]))

    return points_rtree, traj_index+1


def trajectories_to_rtree_ram_limited(trajectories):
    """
    Create an rtree from points WITHOUT creating a points list by adding points to the
    tree one at a time.

    Arguments:
        trajectories (list): trajectories to create an rtree from.

    Returns:
        R-Tree of points and trajectory index
    """

    points_rtree = RTree()
    for traj_index, trajectory in enumerate(tqdm(trajectories)):
        for point in trajectory:
            # Convert this point to ECEF for more exact distance calculations.
            point.set_property("altitude", 0)
            ecef_point = ECEF_from_feet(point, "altitude")
            # Add the point (and its trajectory index) to our r-tree.
            points_rtree.insert_point(convert_to_feature_vector([ecef_point[0],
                                                                 ecef_point[1],
                                                                 ecef_point[2],
                                                                 traj_index]))

    return points_rtree


def create_rtree(trajectories=None, reader=None, ram_limited=False):

    """Create an rtree.

    Keyword Arguments:
        trajectories (list): trajectories to create an rtree from. (Default: None)
        reader (Tracktable trajectory reader): Trajectory reader to create an rtree from. (Default: None)
        ram_limited (bool): Create an R-Tree without storing the trajectory points. (Default: False)

    Returns:
        R-Tree of points and trajectory index
    """
    if trajectories is None:
        if reader is None:
            raise Exception('Either a trajectory list or TrajectoryReader object must be given.')
        else:
            return traj_reader_to_rtree(reader)
    else:
        if ram_limited:
            return trajectories_to_rtree_ram_limited(trajectories)
        else:
            return trajectories_to_rtree(trajectories)


##############################################################################
# HELPER FUNCTIONS
##############################################################################


def count_anomalies(nearby_trajectories):
    """Given a dictionary with test trajectory indices as keys and passerby
       historical trajectory indices as values (as a list), count how many
       test trajectories have no historical trajectories passing by.

    Arguments:
        nearby_trajectories (list): nearby trajectories that pass by the anomalous trajectories.

    Returns:
        Number of anomalous trajectories
    """
    num_anomalous_trajectories = 0
    for i, nearby_traj_indices in enumerate(nearby_trajectories):
        if len(nearby_traj_indices) == 0:
            num_anomalous_trajectories += 1

    return num_anomalous_trajectories


def get_trajectory_segments(trajectory):
    """Represents a trajectory by a list of segments

    Arguments:
        trajectory (Trajectory): Trajectory to get the segments of.

    Returns:
        list of trajectory segments
    """

    segments = []

    for i in range(len(trajectory) - 1):
        segment = Trajectory.from_position_list([trajectory[i],
                                                 trajectory[i+1]])
        segments.append(segment)

    return segments
