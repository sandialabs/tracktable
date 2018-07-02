# Copyright (c) 2014-2018 National Technology and Engineering
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

# Author: Ben Newton  - February 21, 2018

import tracktable.inout.trajectory as trajectory
from tracktable.core import geomath

from sklearn.cluster import AgglomerativeClustering

import matplotlib.pyplot as plt

import argparse


###########
#following adapted from https://stackoverflow.com/questions/29127013/plot-dendrogram-using-sklearn-agglomerativeclustering
import numpy as np
import ete3

def build_Newick_tree(children, n_leaves, X, leaf_labels, spanner):
    """
    build_Newick_tree(children,n_leaves,X,leaf_labels,spanner)

    Get a string representation (Newick tree) from the sklearn
    AgglomerativeClustering.fit output.

    Input:
        children: AgglomerativeClustering.children_
        n_leaves: AgglomerativeClustering.n_leaves_
        X: parameters supplied to AgglomerativeClustering.fit
        leaf_labels: The label of each parameter array in X
        spanner: Callable that computes the dendrite's span

    Output:
        ntree: A str with the Newick tree representation

    """
    return go_down_tree(children, n_leaves, X, leaf_labels, len(children)+n_leaves-1, spanner)[0]+';'

def go_down_tree(children,n_leaves,X,leaf_labels,nodename,spanner):
    """
    go_down_tree(children,n_leaves,X,leaf_labels,nodename,spanner)

    Iterative function that traverses the subtree that descends from
    nodename and returns the Newick representation of the subtree.

    Input:
        children: AgglomerativeClustering.children_
        n_leaves: AgglomerativeClustering.n_leaves_
        X: parameters supplied to AgglomerativeClustering.fit
        leaf_labels: The label of each parameter array in X
        nodename: An int that is the intermediate node name whos
            children are located in children[nodename-n_leaves].
        spanner: Callable that computes the dendrite's span

    Output:
        ntree: A str with the Newick tree representation

    """
    nodeindex = nodename-n_leaves
    if nodename<n_leaves:
        return leaf_labels[nodeindex],np.array([X[nodeindex]])
    else:
        node_children = children[nodeindex]
        branch0,branch0samples = go_down_tree(children,n_leaves,X,leaf_labels,node_children[0], spanner)# added spanner?
        branch1,branch1samples = go_down_tree(children,n_leaves,X,leaf_labels,node_children[1], spanner)
        node = np.vstack((branch0samples,branch1samples))
        branch0span = spanner(branch0samples)
        branch1span = spanner(branch1samples)
        nodespan = spanner(node)
        branch0distance = nodespan-branch0span
        branch1distance = nodespan-branch1span
        nodename = '({branch0}:{branch0distance},{branch1}:{branch1distance})'.format(branch0=branch0,branch0distance=branch0distance,branch1=branch1,branch1distance=branch1distance)
        return nodename,node

def get_cluster_spanner(aggClusterer):
    """
    spanner = get_cluster_spanner(aggClusterer)

    Input:
        aggClusterer: sklearn.cluster.AgglomerativeClustering instance

    Get a callable that computes a given cluster's span. To compute
    a cluster's span, call spanner(cluster)

    The cluster must be a 2D numpy array, where the axis=0 holds
    separate cluster members and the axis=1 holds the different
    variables.

    """
    if aggClusterer.linkage=='ward':
        if aggClusterer.affinity=='euclidean':
            spanner = lambda x:np.sum((x-aggClusterer.pooling_func(x,axis=0))**2)
    elif aggClusterer.linkage=='complete':
        if aggClusterer.affinity=='euclidean':
            spanner = lambda x:np.max(np.sum((x[:,None,:]-x[None,:,:])**2,axis=2))
        elif aggClusterer.affinity=='l1' or aggClusterer.affinity=='manhattan':
            spanner = lambda x:np.max(np.sum(np.abs(x[:,None,:]-x[None,:,:]),axis=2))
        elif aggClusterer.affinity=='l2':
            spanner = lambda x:np.max(np.sqrt(np.sum((x[:,None,:]-x[None,:,:])**2,axis=2)))
        elif aggClusterer.affinity=='cosine':
            spanner = lambda x:np.max(np.sum((x[:,None,:]*x[None,:,:]))/(np.sqrt(np.sum(x[:,None,:]*x[:,None,:],axis=2,keepdims=True))*np.sqrt(np.sum(x[None,:,:]*x[None,:,:],axis=2,keepdims=True))))
        else:
            raise AttributeError('Unknown affinity attribute value {0}.'.format(aggClusterer.affinity))
    elif aggClusterer.linkage=='average':
        if aggClusterer.affinity=='euclidean':
            spanner = lambda x:np.mean(np.sum((x[:,None,:]-x[None,:,:])**2,axis=2))
        elif aggClusterer.affinity=='l1' or aggClusterer.affinity=='manhattan':
            spanner = lambda x:np.mean(np.sum(np.abs(x[:,None,:]-x[None,:,:]),axis=2))
        elif aggClusterer.affinity=='l2':
            spanner = lambda x:np.mean(np.sqrt(np.sum((x[:,None,:]-x[None,:,:])**2,axis=2)))
        elif aggClusterer.affinity=='cosine':
            spanner = lambda x:np.mean(np.sum((x[:,None,:]*x[None,:,:]))/(np.sqrt(np.sum(x[:,None,:]*x[:,None,:],axis=2,keepdims=True))*np.sqrt(np.sum(x[None,:,:]*x[None,:,:],axis=2,keepdims=True))))
        else:
            raise AttributeError('Unknown affinity attribute value {0}.'.format(aggClusterer.affinity))
    else:
        raise AttributeError('Unknown linkage attribute value {0}.'.format(aggClusterer.linkage))
    return spanner

#clusterer = AgglomerativeClustering(n_clusters=2,compute_full_tree=True) # You can set compute_full_tree to 'auto', but I left it this way to get the entire tree plotted
#clusterer.fit(X) # X for whatever you want to fit
#spanner = get_cluster_spanner(clusterer)
#newick_tree = build_Newick_tree(clusterer.children_,clusterer.n_leaves_,X,leaf_labels,spanner) # leaf_labels is a list of labels for each entry in X
#tree = ete3.Tree(newick_tree)
#tree.show()


##########



def parse_args():
    desc = "Given a set of trajectory segments (possibly from multiple \
    original trajectories) create a hierarchical clustering of the \
    trajectory segments.\
    Example: python example_dendrogram.py ../../../../TestData/july_2013_2191Segs_from800Trajs.json -s"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('input', type=argparse.FileType('r'))
    parser.add_argument('-n', "--numSamples", dest="num_samples", type=int,
                        default=4)
    parser.add_argument('-s', '--saveFigures', dest='savefig',
                        action="store_true")
    return parser.parse_args()

def equally_spaced_points(traj, num_points): #check inputs? todo
    points = []
    for i in range(num_points):
        fraction = 0.5
        if num_points != 1:
            fraction = float(i)/(num_points-1)
        points.append(geomath.point_at_fraction(traj, fraction))
    return points

def distance_geometry(traj, maximum_num_segments):
    #check maximum_num_segments >=1
    #for now normalize by the entire length of the traj as below
    total_len = geomath.length(traj)
    if total_len == 0.0:
        total_len = 1.0e-300  #very small number??? todo is this the right thing to do?
    featureVec = []
    for num_segments in range(1, maximum_num_segments+1):
        points = equally_spaced_points(traj, num_segments+1)
        for i in range(len(points)-1):
            featureVec.append(geomath.distance(points[i],
                                               points[i+1])/total_len)
    return featureVec

#def distance_geometry(traj, samples):  #this version uses the same sample points(abcd) then looks at all segments of 2 points, 3 points, etc
#    points = []
#    for i in range(samples):
#        fraction = 0.5
#        if samples != 1:
#            fraction = float(i)/(samples-1)
#        points.append(geomath.point_at_fraction(traj, fraction)) # of dist
#    featureVec = []
#    for segment_length in range(2,samples+1): #similar to code in sub_trajectorize.py
#        #print(segment_length)
#        num_segments_of_length = (samples-segment_length)+1
#        for start_index in range(num_segments_of_length):
#            end_index = start_index+segment_length-1
#            #print(start_index, end_index)
#            featureVec.append(geomath.distance(points[start_index],
#                                               points[end_index]))
#    return featureVec

def main():
    args = parse_args()
    samples = args.num_samples
    features = []
    normalize = True
    num_clusters = 6
    xs = []
    ys = []
    for traj in trajectory.from_ijson_file_iter(args.input):
        features.append(distance_geometry(traj, samples))
        x = []
        y = []
        for point in traj:
            x.append(point[0])
            y.append(point[1])
        xs.append(x)
        ys.append(y) #append x's and y's (lons lats) to list of lists
    clusterer = AgglomerativeClustering(n_clusters=num_clusters,
                                        linkage='ward')
    labels = clusterer.fit_predict(features)
    #indices = []#could group indices first?  todo? woudl that be better?

    for i in range(num_clusters):
        fig = plt.figure(figsize=(25, 14), dpi=80) #new fig
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)
        count = 0
        for j in range(len(labels)):
            if labels[j] == i:
                if count < 62:
                    ax = fig.add_subplot(8, 8, count + 1, xticks=[], yticks=[])
                    ax.plot(xs[j], ys[j], color='blue', linewidth=1)
                    count += 1
        if args.savefig:
            plt.savefig('cluster-'+str(i)+'.png')
        else:
            plt.show()
    #spanner = get_cluster_spanner(clusterer)
    #leaf_labels = range(len(features)) # later make it object_ids
    #newick_tree = build_Newick_tree(clusterer.children_, clusterer.n_leaves_,
    #                                features, leaf_labels, spanner)
    #tree = ete3.Tree(newick_tree)
    #tree.show()

if __name__ == '__main__':
    main()
