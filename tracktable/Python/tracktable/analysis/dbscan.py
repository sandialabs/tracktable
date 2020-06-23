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
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Label points with cluster IDs using DBSCAN."""

from __future__ import division, absolute_import, print_function

from tracktable.lib import _dbscan_clustering

from tracktable.domain.feature_vectors import convert_to_feature_vector
import logging

def is_decorated(point):
    """Returns True if point is decorated
    
    A decorated point contains more than the individual point data. 
    
    Args:
        point (Tuple): Usually this will be the first point from a 
            feature vector. It will either only contain the point
            data or it may also contain other features and labels. 
    
    Returns:
        Boolean indicating the point is decorated or not
        
    """

    logger = logging.getLogger(__name__)
    logger.debug("Testing for point decoration.  First point: {}".format(
        point))
    try:
        if len(point) == 2 and len(point[0]) > 0:
            logger.debug(
                ("Points are decorated. First point: {}").format(
                    point))
            return True
            
    except TypeError:
        # The second element of the point is something that doesn't
        # have a len().  It is probably a coordinate, meaning we've
        # got bare points.
        return False
    return False     


def compute_cluster_labels(feature_vectors, search_box_half_span, min_cluster_size):
    """Use DBSCAN to compute clusters for a set of points.

    DBSCAN is a clustering algorithm that looks for regions of high
    density in a set of points.  Connected regions of high density are
    identified as clusters.  Small regions of low density or even
    single points get identified as noise (belonging to no cluster).

    There are three arguments to the process.  First, you supply the points
    to cluster.  Second, you ask for cluster labels with respect to
    two parameters: the search box size (defining "nearby" points) and
    the minimum number of points that you're willing to call a
    cluster.

    You will get back a list of (vertex_id, cluster_id) pairs.  If you
    supplied a list of points as input the vertex IDs will be indices
    into that list.  If you supplied pairs of (my_vertex_id, point)
    instead, the vertex IDs will be whatever you supplied.

    """
    logger = logging.getLogger(__name__)
    
    # Are we dealing with decorated points?
    first_point = feature_vectors[0]
    decorated_points = is_decorated(first_point)
    
    if decorated_points:
        vertex_ids = [ point[1] for point in feature_vectors ]
    else:
        vertex_ids = list(range(len(feature_vectors)))

    if not decorated_points:
        logger.debug("Points are not decorated", logger)
    if decorated_points:
        native_feature_vectors = [ convert_to_feature_vector(p[0]) for p in feature_vectors ]
    else:
        native_feature_vectors = [ convert_to_feature_vector(p) for p in feature_vectors ]

    native_box_half_span = convert_to_feature_vector(search_box_half_span)

    if decorated_points:
        point_size = len(first_point[0])
    else:
        point_size = len(first_point)

    cluster_engine_name = 'dbscan_learn_cluster_ids_{}'.format(point_size)
    dbscan_learn_cluster_labels = getattr(_dbscan_clustering, cluster_engine_name)
    integer_labels = dbscan_learn_cluster_labels(
        native_feature_vectors,
        native_box_half_span,
        min_cluster_size
        )

    final_labels = []
    for (vertex_index, cluster_id) in integer_labels:
        final_labels.append((vertex_ids[vertex_index], cluster_id))

    return final_labels

   
def cluster_labels_to_dict(cluster_labels, feature_vectors):
    """Returns a dictionary from array of cluster label pairs.
    
    The dictionary uses the cluster labels as keys. The values of each 
        key is an array of tuples containing the feature vector data. In
        the case of undecorated points, the vertex id is also included 
        in the tuple. 
    
    Args:
        cluster_labels (Array of Tuples): pairs of cluster ids and 
            vector ids. The vector ids map to the index of points
            in the feature vector. This is usually generated from the
            compute_cluster_labels function.
        feature_vectors (Array of Tuples): the feature vectors used to 
            compute the cluster labels.
    
    Returns:
        Dictionary of cluster labels mapped to feature vectors.
    """
    decorated_points = is_decorated(feature_vectors[0])
    dict = {}
    for (v_id, c_id) in cluster_labels:
        if str(c_id) in dict:
            if decorated_points:
                dict[str(c_id)].append(feature_vectors[int(v_id)])
            else:
                dict[str(c_id)].append((feature_vectors[int(v_id)], v_id))
        else:
            if decorated_points:
                dict[str(c_id)] = [feature_vectors[int(v_id)]]
            else:
                dict[str(c_id)] = [(feature_vectors[int(v_id)], v_id)]
    return dict