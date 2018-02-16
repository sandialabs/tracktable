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

import networkx as nx
import numpy as np
from math import sqrt

class NormalizedDistanceMatrix:
    """Generates a matrix giving the ratio of the distance along each
    sub-trajectory to the distance from the start to the end of that
    sub-trajectory"""

    def __init__(self, coords, threshold=1.1):
        self.dist_mat = np.zeros(shape=(len(coords), len(coords)))
        self.threshold = threshold

        for x in range(1, len(coords)):
            self.dist_mat[0, x] = \
            self.dist(coords[x], coords[x-1]) + self.dist_mat[0,x-1]
            self.dist_mat[x, 0] = self.dist_mat[0, x]

        for start in range(1, len(coords)):
            for end in range(start+1, len(coords)):
                self.dist_mat[start,end] = \
                self.dist_mat[start-1, end] - self.dist_mat[start-1,start]
                self.dist_mat[end,start] = self.dist_mat[start,end]

        #ratio of distance traveled to separation distance of start and end
        self.norm_dist_mat = np.copy(self.dist_mat)
        for start in range(0, len(coords)):
            for end in range(start+1, len(coords)):
                dist = self.dist(coords[start], coords[end])
                if dist != 0.0:
                    self.norm_dist_mat[start,end] /= self.dist(coords[start],
                                                               coords[end])
                else:
                    self.norm_dist_mat[start,end]= 0.0 #is this okay?
                self.norm_dist_mat[end,start] = self.norm_dist_mat[start,end]

    def squared_dist(self, a, b):
        return (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])

    def dist(self, a, b):
        return sqrt(self.squared_dist(a,b))

    def is_straight(self, start, end):
        return self.norm_dist_mat[start,end] < self.threshold

class SubTrajectorizer:
    'Splits a trajectory into straight-ish segments'
    def __init__(self, straightness_threshold=1.1, length_threshold_samples=2): #2 is minimum
        self.threshold = straightness_threshold
        self.length_threshold_samples = length_threshold_samples
        self.currentNodeIndex = 1 #change to 0
        self.norm_dist_mat = NormalizedDistanceMatrix([]) #todo better way?

    def split_at_indices(self, indices, start, end):
        """returns a list of index pairs, and/or "None" objects.  Even
        elements are not straight segments or are None.  Odd elements are the
        straight segments"""
        segments = []
        remainderStart = start
        remainderEnd = end
        for i in indices:
            if i >= remainderStart:
                if i == start:
                    segments.append(None)
                elif i== remainderStart:
                    segments.append(None)
                else:
                    segments.append([remainderStart, i])
                    remainderStart = i
            else: #overalpping segments, ignore second one.  TODO, later may
                #want to use a better way to determine which overlapping
                #segment to use
                segments.append(None)
        if remainderStart == remainderEnd:
            segments.append(None)
        else:
            segments.append([remainderStart, remainderEnd])
        return segments

    def longest_straight_segments(self, G, coords, thisIndex,
                                       start_length, start, end):
        if start_length >= (end-start+1):
            start_length = end-start
        #print(start, end, start_length)
        if (not self.norm_dist_mat.is_straight(start, end)) and (end-start+1) > self.length_threshold_samples :
            indices = []
            new_start_length = start_length
            for segment_length in range(start_length, 1, -1):
                num_segments_of_length = ((end-start+1)-segment_length)+1
                for start_index in range(num_segments_of_length):
                    end_index = start_index+segment_length-1
                    if self.norm_dist_mat.is_straight(start_index+start,
                                                         end_index+start):
                        indices.append(start_index+start)
                        indices.append(end_index+start)
                if indices:
                    new_start_length = segment_length-1
                    break
            segs = self.split_at_indices(indices, start, end)
            for i in range(len(segs)):
                if i%2 == 0: #even = not straight, recurse
                    if segs[i] != None:
                        G.add_node(self.currentNodeIndex, s=segs[i][0],
                                   e=segs[i][1])
                        G.add_edge(thisIndex, self.currentNodeIndex)
                        self.currentNodeIndex+=1
                        self.longest_straight_segments(G, coords,
                                                       self.currentNodeIndex-1,
                                                       new_start_length,
                                                       segs[i][0],
                                                       segs[i][1])
                else: #odd = straight, make leaf node
                    G.add_node(self.currentNodeIndex, s=segs[i][0],
                               e=segs[i][1])
                    G.add_edge(thisIndex, self.currentNodeIndex)
                    self.currentNodeIndex+=1

    def subtrajectorize(self, trajectory, returnGraph=False):
        coordinates = [] 
        for point in trajectory: #make into coordinate list
            coordinates.append([point[0], point[1]])
        self.currentNodeIndex = 1
        self.norm_dist_mat = NormalizedDistanceMatrix(coordinates,
                                                      threshold=self.threshold)

        G = nx.DiGraph()
        start = 0
        end = len(coordinates)-1
        G.add_node(self.currentNodeIndex, s=start, e=end)
        self.currentNodeIndex += 1
        self.longest_straight_segments(G, coordinates, 1,
                                            len(coordinates), start, end)
        leaves = [(G.node[x]['s'], G.node[x]['e'])
                  for x in G.nodes() if G.out_degree(x)==0 and
                  G.in_degree(x)==1]
        if returnGraph:
            return leaves, G
        else:
            return leaves
