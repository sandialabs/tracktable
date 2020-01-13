#!/usr/bin/env python
# coding: utf-8

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
# 

# # Trajectory Clustering Example
# 
# This notebook is an end-to-end example of how to cluster trajectories in Tracktable using distance geometry.  It goes through the following steps:
# 
# 1.  Read in points from a file.
# 2.  Assemble those points into trajectories.
# 3.  Create a distance geometry signature for each trajectory.
# 4.  Using those signatures as feature vectors, compute clusters using DBSCAN.
# 5.  Print statistics about each cluster.
# 6.  Render the resulting clusters onto a map.
# 
# Eventually, distance geometry computation will move into the library itself.

# Set up Matplotlib to render in a notebook before anyone else can change its back end.
import matplotlib
get_ipython().run_line_magic('matplotlib', 'inline')


# Compute an N-point distance geometry signature    
#     
# Distance geometry is a technique for characterizing a curve in space by measuring the distances between evenly spaced points (called control points) on the curve. This implementation has three parameters:    
#   1. A trajectory    
#   2. The number of control points     
#   3. Whether to normalize the distances in the signature so that the largest distance is always 1.    
#     
# The number of control points controls the fidelity of the resulting signature. The more control points, the more accurately the features of the curve can be represented, but the longer it takes to compute.    
#     
# Normalizing the distance allows shape-based comparison between trajectories by taking the dot product of their respective distance geometry signatures. The higher the dot product, the more similar the trajectories. There are many possible normalization schemes; this is the one we find useful.    
#     
# Returns:    
#   tracktable.domain.feature_vectors.FeatureVectorNN where NN is the size of the resulting distance geometry signature. 

from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.core.geomath import point_at_length_fraction
from tracktable.core.geomath import distance

def distance_geometry_signature(trajectory, num_control_points=4, normalize_distance = True):
    # Sets the distance increment for control points based on the number of control points
    # Calculates the fractions of the trajectory where control points should be
    # Gives the values where the control points are located
    control_point_increment = 1.0/(num_control_points-1)    
    control_point_fractions = [control_point_increment * i for i in range(num_control_points)]    
    control_points = [point_at_length_fraction(trajectory, t) for t in control_point_fractions]
    
    # A signature is a collection of the calculated distances that will be converted to a feature vector
    signature = []
    # Calculate the list of distances
    for stepsize in range(num_control_points-1, 0, -1):
        for start in range(0, num_control_points-stepsize):
            end = start + stepsize
            signature.append(distance(control_points[start], control_points[end]))
    # Normalize distances to compare trajectory shapes
    if normalize_distance:
        largest_distance = max(signature)
        signature = [0 if not largest_distance else d/largest_distance for d in signature]
    # Convert distances to a feature vector
    return convert_to_feature_vector(signature)


# Now we are going to gather our points from file and assemble them into trajectories. We will use the same point reader and trajectory builder we used in previous examples. Then, we will computer the cluster labels.

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
builder.minimum_distance = 100
builder.minimum_time = 20

all_trajectories = list(builder)
# Get feature vectors for each trajectory describing their distance geometry
num_control_points = 4
feature_vectors = [distance_geometry_signature(trajectory, num_control_points, True)
                   for trajectory in all_trajectories]

# DBSCAN needs two parameters
#  1. Size of the box that defines when two points are close enough to one another to
#     belong to the same cluster.
#  2. Minimum number of points in a cluster
#
signature_length = len(feature_vectors[0])

# This is the default search box size. Feel free to change to fit your data.
search_box_span = [0.01] * signature_length
minimum_cluster_size = 5

cluster_labels = compute_cluster_labels(feature_vectors, search_box_span, minimum_cluster_size)


# Cluster Statistics    
# Here we calculate the size of the clusters we labeled.

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


# Cluster Visualization    
# You can use pyplot to see your clusters that were created

from tracktable.render import paths
from tracktable.domain import terrestrial
from tracktable.render import mapmaker
from matplotlib import pyplot

sorted_ids = sorted(clusters.keys())
for cluster_id in sorted_ids:
    # Set up the canvas and map projection
    figure = pyplot.figure(figsize=[20, 15])
    axes = figure.add_subplot(1, 1, 1)
    (mymap, map_actors) = mapmaker.mapmaker(domain = 'terrestrial', map_name='region:conus')
    paths.draw_traffic(traffic_map = mymap, trajectory_iterable = clusters[cluster_id])
    figure.suptitle('{}: {} members'.format(cluster_name(cluster_id),
                                           len(clusters[cluster_id])))
    pyplot.show()

