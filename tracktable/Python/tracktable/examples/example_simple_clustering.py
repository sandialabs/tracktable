# Copyright (c) 2014-2019 National Technology and Engineering
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

# # Trajectory Clustering Example    
#     
# This is a simple end-to-end clustering example using feature vectors. 
# In this example, we cluster based on the convex hull area and the end to 
# end distance. This can give us similar shaped trajectories that travel 
# the same distance.    

import matplotlib


# First, we will define our method to grab the features we want. Given a trajectory, 
# the method will build a list of features that we want to define our trajectory. In 
# this instance, we get the convex hull area and we calculate the end to end distance 
# of the trajectory. We convert the list of features into a feature vector.

from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.core.geomath import convex_hull_area as cha
from tracktable.core.geomath import distance
from datetime import timedelta

def get_features(trajectory):
    signature = []
    signature.append(cha(trajectory))
    signature.append(distance(trajectory[0], trajectory[len(trajectory)-1]))
    return convert_to_feature_vector(signature)


# Now we need to collect our data from our dataset and organize it into trajectories. 
# We save the trajectories to a list so we can work with them as many times as we want.

from tracktable.domain.terrestrial import TrajectoryPointReader
from tracktable.source.trajectory import AssembleTrajectoryFromPoints
from tracktable.analysis.dbscan import compute_cluster_labels
from tracktable.core import data_directory
import os.path

data_filename = os.path.join(data_directory(), 'april_04_2013.csv')
inFile = open(data_filename, 'r')
reader = TrajectoryPointReader()
reader.input = inFile
reader.comment_character = '#'
reader.field_delimiter = ','
reader.object_id_column = 0
reader.timestamp_column = 1
reader.coordinates[0] = 2
reader.coordinates[1] = 3

builder = AssembleTrajectoryFromPoints()
builder.input = reader
builder.minimum_length = 5
builder.separation_time = timedelta(minutes=20)

all_trajectories = list(builder)


# Now we collect a list of feature vectors from all of our trajectories we formed. In order to computer cluster labels, we will need:    
#    1. A list of feature vectors for the trajectories    
#    2. Size of the box that defines when two points are close enough to be considered in the same cluster. This is a great parameter 
#       to play with to see how the clusters change.    
#    3. The minimum number of points to keep a cluster.    

feature_vectors = [get_features(trajectory) for trajectory in all_trajectories]
signature_length = len(feature_vectors[0])
search_box_span = [0.01] * signature_length
minimum_cluster_size = 5

cluster_labels = compute_cluster_labels(feature_vectors, search_box_span, minimum_cluster_size)


# Now we can actually cluster the trajectories based on the labels built. 

# Assemble each cluster as a list of its component trajectories.
clusters = {}
for(vertex_id, cluster_id) in cluster_labels:
    if cluster_id not in clusters:
        clusters[cluster_id] = [all_trajectories[vertex_id]]
    else:
        clusters[cluster_id].append(all_trajectories[vertex_id])

# If a cluster does not have an id, it is an outlier
def cluster_name(cid):
    if cid == 0:
        return 'Outliers'
    else:
        return 'Cluster {}'.format(cid)

#Print the cluster id and the number of trajectories in the cluster.
print("RESULT: Cluster sizes:")
for(cid, cluster) in clusters.items():
    print("{}: {}".format(cluster_name(cid), len(cluster)))

