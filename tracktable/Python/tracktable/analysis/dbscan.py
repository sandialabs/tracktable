# Copyright (c) 2015, Sandia Corporation.
# All rights reserved.
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

from . import _dbscan_clustering

from tracktable.domain.feature_vectors import convert_to_feature_vector

def compute_cluster_labels(feature_vectors, search_box_half_span, min_cluster_size):
    """Use DBSCAN to compute clusters for a set of points.

    DBSCAN is a clustering algorithm that looks for regions of high
    density in a set of points.  Connected regions of high density are
    identified as clusters.  Small regions of low density or even
    ingle points get identified as noise (belonging to no cluster).

    There are three arguments to the process.  First, you supply the points
    to cluster.  Second, you ask for cluster labels with respect to
    two parameters: the search box size (defining "nearby" points) and
    the minimum number of points that you're willing to call a
    cluster.
    """

    native_feature_vectors = [ convert_to_feature_vector(p) for p in feature_vectors ]
    native_box_half_span = convert_to_feature_vector(search_box_half_span)


    cluster_engine_name = 'dbscan_learn_cluster_ids_{}'.format(len(feature_vectors[0]))
    dbscan_learn_cluster_labels = getattr(_dbscan_clustering, cluster_engine_name)
    return dbscan_learn_cluster_labels(native_feature_vectors, native_box_half_span, min_cluster_size)
