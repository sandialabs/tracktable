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
tracktable.applications.cluster - Determine if trajectories are clustered together.

cluster_trajectories(), cluster_trajectories_rendezvous() and cluster_trajectories_shape()
are the main driver functions for clustering.
"""

import logging
from datetime import datetime

from numpy import linspace
from tracktable.algorithms.dbscan import compute_cluster_labels
from tracktable.core.geomath import (distance, length,
                                     point_at_length_fraction, point_at_time,
                                     time_at_fraction)
from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.algorithms.distance_geometry import distance_geometry_by_distance

logger = logging.getLogger(__name__)

def cluster_trajectories(trajectories,
                         feature_vector_function,
                         search_box_span,
                         *args,
                         min_cluster_size=2,
                         **kwargs):
    """Create a cotravel feature vector for each trajectory and use box-DBSCAN
    to cluster the trajectories.

    Arguments:
        trajectories (list): Trajectories to cluster.
        feature_vector_function (function): Function to use when generating the feature vector.
        search_box_span (int): The cluster labels with respect to
            two parameters: the search box size (defining "nearby" points).

    Keyword Arguments:
        min_cluster_size (int): The minimum number of points that you're willing to call a
            cluster. (Default: 2)

    Returns:
        list of ordered pairs. The first value of each ordered pair corresponds to trajectory index
        (matching the ordering of the given list of trajectories), and the
        second number is the number of the cluster that the trajectory belongs
        to.
    """

    feature_vectors = []
    for i, trajectory in enumerate(trajectories):
        signature = feature_vector_function(trajectory,
                                            *args,
                                            **kwargs)
        feature_vectors.append(convert_to_feature_vector(signature))

    return group_clusters(compute_cluster_labels(feature_vectors,
                                                 search_box_span,
                                                 min_cluster_size),
                                                 trajectories)


def cluster_trajectories_rendezvous(trajectories,
                                    start_fraction=0,
                                    end_fraction=1,
                                    num_control_points=10,
                                    epsilon_longitude=0.02,
                                    epsilon_latitude=0.02,
                                    epsilon_timestamp=3000,
                                    min_cluster_size=2):
    """Create a cotravel feature vector for each trajectory and use box-DBSCAN
    to cluster the trajectories.

    Arguments:
        trajectories (list): Trajectories to cluster.

    Keyword Arguments:
        start_fraction (float): The fraction along the trajectory where you want to start sampling
            control points when looking for passersby. (Default: 0)
        end_fraction (float): The fraction along the trajectory where you want to stop sampling
            control points when looking for passersby. (Default: 1)
        num_control_points (int): The number of equally-spaced points to sample along each trajectory
            when clustering. (Default: 10)
        epsilon_longitude (float): The longitude in degrees to bound the DBSCAN clsutering (Default: 0.02)
        epsilon_latitude (float): The latitude in degrees to bound the DBSCAN clsutering (Default: 0.02)
        epsilon_timestamp (int): The timestamp in seconds to bound the DBSCAN clsutering (Default: 3000)
        min_cluster_size (int): The minimum number of points that you're willing to call a
            cluster. (Default: 2)

    Returns:
        list of ordered pairs. The first value of each ordered pair corresponds to trajectory index
        (matching the ordering of the given list of trajectories), and the
        second number is the number of the cluster that the trajectory belongs
        to.
    """

    # DBSCAN needs to know values for which we define closeness in each
    # dimension. The larger our epsilon values, the more likely our
    # trajectories will cluster.
    search_box_span = [epsilon_longitude,
                       epsilon_latitude,
                       epsilon_timestamp] * num_control_points

    # proportions (in time) along our trajectory to get temporospatial info
    control_time_fractions = list(linspace(start_fraction,
                                           end_fraction,
                                           num_control_points))

    return cluster_trajectories(trajectories,
                                _rendezvous_signature,
                                search_box_span,
                                control_time_fractions,
                                min_cluster_size=min_cluster_size)


def cluster_trajectories_shape(trajectories,
                               depth=4,
                               epsilon=0.05,
                               min_cluster_size=2):
    """Create a cotravel feature vector for each trajectory and use box-DBSCAN
    to cluster the trajectories.

    Arguments:
        trajectories (list): Trajectories to cluster.

    Keyword Arguments:
        depth (int): How many levels to compute. Must be greater than zero.(Default: 4)
        epsilon (float): The epsilon value to generate the search box span. (Default: 0.05)
        min_cluster_size (int): The minimum number of points that you're willing to call a
            cluster. (Default: 2)

    Returns:
        list of ordered pairs. The first value of each ordered pair corresponds to trajectory index
        (matching the ordering of the given list of trajectories), and the
        second number is the number of the cluster that the trajectory belongs
        to.
    """
    search_box_span = [epsilon] * round((depth * (depth + 1) / 2))

    return cluster_trajectories(trajectories,
                                distance_geometry_by_distance,
                                search_box_span,
                                min_cluster_size=min_cluster_size,
                                depth=depth)

def _rendezvous_signature(trajectory,
                         control_time_fractions,
                         epoch=None):
    """Creates a list of values that will be used to form
    feature vectors when clustering by co-travel geometry.

    Arguments:
        trajectory (Tracktable trajectory): We will create
            a co-travel feature vector for this trajectory,
            stored as a list.
        control_time_fractions (list of floats): Temporospatial
            information at points at these fractions along
            the trajectory (in time) will be used to create our co-travel
            feature vector.

    Keyword Arguments:
        epoch (datetime): An arbitrary start time that allows
            us to convert datetimes into seconds-since-epoch
            for comparability between trajectory points. (Default: None)

    Returns:
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

def cluster_name(cluster_id):
    """Retrieve the cluster name for the given cluster ID.

    Arguments:
        cluster_id (int): Cluster ID to retrieve the name for.

    Returns:
        The name of the cluser ID.
    """

    if cluster_id == 0:
        # If a cluster has a zero id, it is an outlier.
        return 'Outliers'
    else:
        return 'Cluster {}'.format(cluster_id)


def print_cluster_sizes(clusters):
    """Print the cluster id and the number of trajectories in the cluster.

    Arguments:
        clusters (dict): Clsuters to print information about.
    """

    cluster_list = clusters.items()
    cluster_list = sorted(cluster_list, key=lambda x: len(x[1]), reverse=True)

    if 0 in clusters.keys():
        logger.debug(str(len(cluster_list) - 1) + ' Total Clusters + ' + str(
            len(clusters[0])) + ' Outliers')
    else:
        logger.debug(str(len(cluster_list)) + ' Total Clusters + 0 Outliers')
    logger.debug('-----------------')

    for (cluster_id, cluster) in cluster_list:
        logger.debug("{}: {}".format(cluster_name(cluster_id), len(cluster)))


def group_clusters(cluster_labels, trajectories):
    """Group clusters together with labels corresponding to trajectories.

    Arguments:
        cluster_labels (list): Labels for the cluster.
        trajectories (list): Trajectories to group together.

    Returns:
        The clusters of trajectories.
    """

    # This dictionary will include all trajectories, even outliers.
    clusters = {}

    # Assemble each cluster as a list of its component trajectories.
    for (vertex_id, cluster_id) in cluster_labels:
        if cluster_id not in clusters:
            clusters[cluster_id] = [trajectories[vertex_id]]
        else:
            clusters[cluster_id].append(trajectories[vertex_id])

    if logger.level == logging.DEBUG:
        print_cluster_sizes(clusters)

    return clusters
