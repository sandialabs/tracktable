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

from datetime import datetime

from numpy import linspace
from tracktable.analysis.dbscan import compute_cluster_labels
from tracktable.core.geomath import (distance, length,
                                     point_at_length_fraction, point_at_time,
                                     time_at_fraction)
from tracktable.domain.feature_vectors import convert_to_feature_vector

# TODO: Finish documentation throughout.
def rendezvous_signature(trajectory,
                         control_time_fractions,
                         epoch=None):
    """Creates a list of values that will be used to form
    feature vectors when clustering by co-travel geometry.

    Args:
        trajectory : Tracktable trajectory object
            We will create a co-travel feature vector for this trajectory,
            stored as a list.
        control_time_fractions : list of floats
            Temporospatial information at points at these fractions along
            the trajectory (in time) will be used to create our co-travel
            feature vector.
        epoch : datetime object
            An arbitrary start time that allows us to convert datetimes
            into seconds-since-epoch for comparability between trajectory
            points.

    Returns : list of float
        A list of concatenated (long, lat, timestamp) info for the
        trajectory points at each of control_time_fractions along the
        trajectory.
    """
    # Get timestamps at given fractions along the trajectory.
    control_times = [time_at_fraction(trajectory, f) for f in
                     control_time_fractions]

    # Get points at the specified control times.
    control_points = [point_at_time(trajectory, t) for t in control_times]

    if epoch is None:
        # The timezone information is necessary to find accurate differences
        # from our starting epoch.
        tz_info = control_times[0].tzinfo
        # If no epoch is given, use Jan 1, 2014 00:00:00.
        epoch = datetime(year=2014,
                         month=1,
                         day=1,
                         hour=0,
                         minute=0,
                         second=0,
                         tzinfo=tz_info)

    cotravel_geometries = []
    for j in range(len(control_points)):
        # For comparability, we want our timestamp in seconds-since-epoch.
        time_diff = control_times[j] - epoch
        # Concatenate [long, lat, timestamp] for all control points into a
        # single list.
        cotravel_geometries.extend([control_points[j][0],
                                    control_points[j][1],
                                    time_diff.total_seconds()])

    return cotravel_geometries


def distance_geometry_signature(trajectory, depth=4):
    """Creates a list of values that will be used to form feature vectors when
    clustering by distance geometry.

    Args:
        trajectory : Tracktable trajectory object
            We will create a distance geometry feature vector for this
            trajectory, stored as a list.
        depth : int
            We start computing our distance geometry vector with the entire
            trajectory, then the trajectory broken into two equal-length
            sub-trajectories, and so on.  The last values in our distance
            geometry vector should correspond two when the trajectory has
            been broken into depth number of pieces.

    Returns : list of float
        A list representing the distance geometry feature of the given
        trajectory.
    """

    distance_geometry_vector = []

    # Calculating trajectory length, which will be used in our distance
    # geometry calculation.
    traj_length = length(trajectory)

    # Interpolate depth+1 equally-spaced control points along the trajectory,
    # then use these control points to calculate the distance geometry for the
    # trajectory.
    for num_control_points in range(2, depth + 2):

        # spacing between control points, as a proportion of the trajectory
        control_point_increment = 1.0 / (num_control_points - 1)

        # fractions of the trajectory where control points should be
        control_point_fractions = [control_point_increment * i
                                   for i in range(num_control_points)]

        # get num_control_points points equally-spaced points along the
        # trajectory
        control_points = [point_at_length_fraction(trajectory, t)
                          for t in control_point_fractions]

        # Normalize by the length of a single segment between control points.
        normalization_term = traj_length * control_point_increment

        # Calculate the list of distances
        for j in range(len(control_points) - 1):
            if traj_length != 0:
                distance_geometry_vector.append(distance(control_points[j],
                                                         control_points[j + 1])
                                                / normalization_term)
            else:
                # In the trivial case (all points in the same place),
                # don't normalize (division by zero).
                distance_geometry_vector.append(distance(control_points[j],
                                                         control_points[j + 1]))

    return distance_geometry_vector


def cluster_trajectories(trajectories,
                         feature_vector_function,
                         search_box_span,
                         *args,
                         min_cluster_size=2,
                         verbose=False,
                         **kwargs):

    feature_vectors = []
    for i, trajectory in enumerate(trajectories):
        signature = feature_vector_function(trajectory,
                                            *args,
                                            **kwargs)
        feature_vectors.append(convert_to_feature_vector(signature))

    return group_clusters(compute_cluster_labels(feature_vectors,
                                                 search_box_span,
                                                 min_cluster_size),
                          trajectories,
                          verbose=verbose)


def cluster_trajectories_rendezvous(trajectories,
                                    start_frac=0,
                                    end_frac=1,
                                    num_control_points=10,
                                    epsilon_longitude=0.02, # deg
                                    epsilon_latitude=0.02, # deg
                                    epsilon_timestamp=3000, # sec
                                    min_cluster_size=2,
                                    verbose=False):
    """Create a cotravel feature vector for each trajectory and use box-DBSCAN
    to cluster the trajectories.

    Args:
        trajectories : list of Trajectory objects
        TODO: FILL IN KEYWORD ARGS

    Returns : list of ordered pairs
        The first value of each ordered pair corresponds to trajectory index
        (matching the ordering of the given list of trajectories), and the
        second number is the number of the cluster that the trajectory belongs
        to.
    """

    # DBSCAN needs to know values for which we define closeness in each
    # dimension.  The larger our epsilon values, the more likely our
    # trajectories will cluster.
    search_box_span = [epsilon_longitude,
                       epsilon_latitude,
                       epsilon_timestamp] * num_control_points

    # proportions (in time) along our trajectory to get temporospatial info
    control_time_fractions = list(linspace(start_frac,
                                           end_frac,
                                           num_control_points))

    return cluster_trajectories(trajectories,
                                rendezvous_signature,
                                search_box_span,
                                control_time_fractions,
                                min_cluster_size=min_cluster_size,
                                verbose=verbose)


def cluster_trajectories_shape(trajectories,
                               depth=4,
                               epsilon=0.05,
                               min_cluster_size=2,
                               verbose=False):
    """Create a distance geometry feature vector for each trajectory and use
    box-DBSCAN to cluster the trajectories

    Args:
        trajectories: list of Trajectory objects
        depth: Depth to compute the distance geometry calculation to

    Returns: a tuple where the first value contains the labels for the clusters
    and the second value contains the feature vectors in that cluster

    """
    search_box_span = [epsilon] * round((depth * (depth + 1) / 2))

    return cluster_trajectories(trajectories,
                                distance_geometry_signature,
                                search_box_span,
                                min_cluster_size=min_cluster_size,
                                depth=depth,
                                verbose=True)


#def cluster_trajectories_shape(trajectories, depth):
#    """Create a distance geometry feature vector for each trajectory and use
#    box-DBSCAN to cluster the trajectories
#
#    Args:
#        trajectories: list of Trajectory objects
#        depth: Depth to compute the distance geometry calculation to
#
#    Returns: a tuple where the first value contains the labels for the clusters
#    and the second value contains the feature vectors in that cluster
#
#    """
#
#    # If we make decrease (increase) epsilon, our boxes get smaller (larger)
#    # and trajectories are less (more) likely to cluster.
#    epsilon = 0.05
#
#    search_box_span = [epsilon] * round((depth * (depth + 1) / 2))
#
#    # Create a list containing each trajectory's feature vector.
#    feature_vectors = []
#    for i, trajectory in enumerate(trajectories):
#        signature = distance_geometry_signature(trajectory, depth=depth)
#        feature_vectors.append(convert_to_feature_vector(signature))
#
#    # If we decrease (increase) the minimum cluster size, trajectories are
#    # more (less) likely to cluster.
#    minimum_cluster_size = 10
#
#    # Cluster over the feature vectors.
#    return [compute_cluster_labels(feature_vectors, search_box_span,
#                                   minimum_cluster_size), feature_vectors]


def cluster_name(cluster_id):
    if cluster_id == 0:
        # If a cluster has a zero id, it is an outlier.
        return 'Outliers'
    else:
        return 'Cluster {}'.format(cluster_id)


def print_cluster_sizes(clusters):
    """Print the cluster id and the number of trajectories in the cluster."""

    cluster_list = clusters.items()
    cluster_list = sorted(cluster_list, key=lambda x: len(x[1]), reverse=True)

    if 0 in clusters.keys():
        print(str(len(cluster_list) - 1) + ' Total Clusters + ' + str(
            len(clusters[0])) + ' Outliers')
    else:
        print(str(len(cluster_list)) + ' Total Clusters + 0 Outliers')
    print('-----------------')

    for (cluster_id, cluster) in cluster_list:
        print("{}: {}".format(cluster_name(cluster_id), len(cluster)))


def group_clusters(cluster_labels, trajectories, verbose=False):
    # This dictionary will include all trajectories, even outliers.
    clusters = {}

    # Assemble each cluster as a list of its component trajectories.
    for (vertex_id, cluster_id) in cluster_labels:
        if cluster_id not in clusters:
            clusters[cluster_id] = [trajectories[vertex_id]]
        else:
            clusters[cluster_id].append(trajectories[vertex_id])

    if verbose:
        print_cluster_sizes(clusters)

    return clusters
