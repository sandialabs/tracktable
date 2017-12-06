# Copyright (c) 2017, National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).
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

# Author: Ben Newton
# Date:   November, 15, 2017

#this is currently just a playground to play around with some different
# sub-trajectoryization ideas.  NOT PRODUCTION CODE

#Data
coords0=[[0,0],[5,5],[10,0]]
coords1=[[0,0],[5,5],[6,-6],[8,3],[10,0]]
coords2=[[0,0],[1,2],[2,0],[3,0],[4,0],[5,2],[6,0],[7,0],[8,0],[9,2],[10,0]]
coords3=[[-1,0],[0,0],[1,2],[2,0],[3,0],[4,0],[5,2],[6,0],[7,0],[8,0],[9,2],[10,0]]
coords4=[[-3,0],[-2,2],[-1,0],[0,0],[1,2],[2,0],[3,0],[4,0],[5,2],[6,0],[7,0],[8,0],[9,2],[10,0]]
coords=[[-111.501, 47.3697], [-111.528, 47.3353], [-111.551, 47.3039], [-111.575, 47.2719], [-111.599, 47.2403], [-111.621, 47.2081], [-111.646, 47.1761], [-111.676, 47.1375], [-111.699, 47.1036], [-111.726, 47.0692], [-111.752, 47.0336], [-111.778, 46.9972], [-111.804, 46.9608], [-111.838, 46.9175], [-111.863, 46.8822], [-111.889, 46.8464], [-111.914, 46.8106], [-111.942, 46.7742], [-111.967, 46.7386], [-112.001, 46.6944], [-112.025, 46.6581], [-112.052, 46.6211], [-112.08, 46.5833], [-112.108, 46.5439], [-112.134, 46.5067], [-112.165, 46.4619], [-112.194, 46.4228], [-112.232, 46.3742], [-112.267, 46.3225], [-112.305, 46.2683], [-112.355, 46.2008], [-112.395, 46.1428], [-112.436, 46.0844], [-112.478, 46.0267], [-112.518, 45.9681], [-112.56, 45.9083], [-112.61, 45.8383], [-112.653, 45.7808], [-112.693, 45.72], [-112.719, 45.655], [-112.632, 45.6189], [-112.563, 45.5775], [-112.652, 45.5803], [-112.719, 45.6153], [-112.721, 45.6864], [-112.721, 45.7581], [-112.724, 45.8308], [-112.727, 45.9019], [-112.729, 45.9744], [-112.731, 46.0644], [-112.737, 46.2106], [-112.74, 46.2847], [-112.739, 46.3592], [-112.742, 46.4308], [-112.746, 46.5192], [-112.747, 46.5933], [-112.75, 46.6672], [-112.753, 46.7411], [-112.756, 46.815], [-112.757, 46.8894], [-112.759, 46.98], [-112.762, 47.0536], [-112.764, 47.1294], [-112.767, 47.2031], [-112.769, 47.2778], [-112.8, 47.3469], [-112.868, 47.3569], [-112.89, 47.2806], [-112.888, 47.2086], [-112.885, 47.1372], [-112.882, 47.0672], [-112.881, 46.9956], [-112.878, 46.91], [-112.875, 46.8381], [-112.873, 46.7658], [-112.871, 46.6947], [-112.868, 46.6236], [-112.866, 46.5511], [-112.863, 46.4653], [-112.861, 46.3992], [-112.86, 46.3133], [-112.856, 46.2414], [-112.853, 46.1703], [-112.851, 46.0969], [-112.849, 46.0253], [-112.845, 45.9528], [-112.842, 45.8672], [-112.841, 45.7947], [-112.838, 45.7231], [-112.837, 45.6506], [-112.876, 45.5911], [-112.94, 45.5817], [-112.951, 45.6711], [-112.952, 45.7472], [-112.955, 45.8225], [-112.958, 45.8983], [-112.962, 45.9736], [-112.963, 46.0497], [-112.965, 46.1253], [-112.97, 46.215], [-112.973, 46.2908], [-112.973, 46.3686], [-112.977, 46.4481], [-112.98, 46.5233], [-112.982, 46.6003], [-112.986, 46.6764], [-112.989, 46.7619], [-112.994, 46.9122], [-112.997, 46.9878], [-112.999, 47.0633], [-113.003, 47.1539], [-113.006, 47.2294], [-113.025, 47.2992], [-113.109, 47.315], [-113.193, 47.3242], [-113.28, 47.3344], [-113.383, 47.3469], [-113.469, 47.3544], [-113.557, 47.36], [-113.642, 47.3656], [-113.685, 47.3128], [-113.682, 47.2422], [-113.678, 47.1578], [-113.675, 47.0861], [-113.671, 47.015], [-113.667, 46.9433], [-113.661, 46.8], [-113.656, 46.7125], [-113.653, 46.6422], [-113.649, 46.57], [-113.646, 46.4992], [-113.642, 46.4281], [-113.64, 46.3569], [-113.635, 46.2711], [-113.632, 46.2], [-113.63, 46.1219], [-113.626, 46.0506], [-113.623, 45.9797], [-113.619, 45.9078], [-113.616, 45.8356], [-113.612, 45.7631], [-113.608, 45.6769], [-113.556, 45.6172], [-113.477, 45.6708], [-113.401, 45.6414], [-113.329, 45.6028], [-113.215, 45.6303], [-113.072, 45.6603], [-112.951, 45.6878], [-112.83, 45.7164], [-112.706, 45.7422], [-112.584, 45.7708], [-112.459, 45.7972], [-112.335, 45.8244], [-112.187, 45.8569], [-112.065, 45.8853], [-111.94, 45.9106], [-111.816, 45.9392], [-111.692, 45.9661], [-111.568, 45.9936], [-111.442, 46.0231], [-111.291, 46.0558], [-111.165, 46.0853], [-111.071, 46.0042], [-110.966, 45.9964], [-110.918, 46.5919], [-110.918, 46.6658], [-110.919, 46.755], [-110.918, 46.8286], [-110.918, 46.9022], [-110.919, 46.9756], [-110.918, 47.0489], [-110.918, 47.1222], [-110.915, 47.2094], [-110.934, 47.2747], [-110.994, 47.2997], [-111.04, 47.245], [-111.041, 47.1714], [-111.043, 47.0975], [-111.041, 47.0106], [-111.043, 46.9372], [-111.043, 46.8642], [-111.044, 46.7908], [-111.043, 46.7167], [-111.039, 46.6444], [-111.039, 46.5558], [-111.039, 46.4817], [-111.041, 46.41], [-111.041, 46.3336], [-111.041, 46.2617], [-111.04, 46.1878], [-111.079, 46.1136], [-111.138, 46.0719], [-111.155, 46.1308], [-111.161, 46.2008], [-111.16, 46.275], [-111.16, 46.3489], [-111.162, 46.4378], [-111.16, 46.5083], [-111.161, 46.5806], [-111.161, 46.6517], [-111.163, 46.7253], [-111.163, 46.7989], [-111.162, 46.8892], [-111.162, 46.9636], [-111.163, 47.04], [-111.162, 47.1131], [-111.202, 47.2375], [-111.275, 47.1861], [-111.28, 47.1131], [-111.279, 47.0411], [-111.279, 46.9675], [-111.278, 46.8211], [-111.278, 46.7331], [-111.276, 46.6594], [-111.276, 46.5864], [-111.275, 46.5131], [-111.275, 46.4344], [-111.275, 46.3592], [-111.275, 46.2842], [-111.274, 46.1958], [-111.273, 46.1214], [-111.274, 46.0475], [-111.274, 45.9725], [-111.274, 45.8992], [-111.321, 45.8253], [-111.38, 45.8469], [-111.388, 45.9183], [-111.386, 45.9919], [-111.386, 46.0661], [-111.387, 46.14], [-111.388, 46.2131], [-111.387, 46.3017], [-111.389, 46.3775], [-111.388, 46.445], [-111.388, 46.5206], [-111.389, 46.61], [-111.389, 46.6844], [-111.391, 46.7603], [-111.391, 46.8347], [-111.392, 46.9081], [-111.393, 46.9819], [-111.393, 47.0717], [-111.393, 47.1461], [-111.428, 47.2106], [-111.491, 47.2411], [-111.518, 47.1778], [-111.516, 47.1044], [-111.515, 47.0175], [-111.517, 46.9467], [-111.515, 46.8753], [-111.514, 46.8036], [-111.514, 46.73], [-111.514, 46.6567], [-111.512, 46.5697], [-111.512, 46.4958], [-111.51, 46.4261], [-111.511, 46.3392], [-111.509, 46.2661], [-111.508, 46.1956], [-111.508, 46.1253], [-111.507, 46.0544], [-111.506, 45.9828], [-111.506, 45.8958], [-111.508, 45.8228], [-111.509, 45.7442], [-111.549, 45.6875], [-111.612, 45.7292], [-111.678, 45.6767], [-111.687, 45.8181], [-111.671, 45.8961], [-111.656, 45.9742], [-111.642, 46.0519], [-111.627, 46.1319], [-111.612, 46.2117], [-111.594, 46.3067], [-111.578, 46.3881], [-111.563, 46.4728], [-111.547, 46.5531], [-111.532, 46.6314], [-111.518, 46.7078], [-111.504, 46.7814], [-111.488, 46.8686], [-111.476, 46.9367], [-111.463, 47.0064], [-111.448, 47.0764], [-111.436, 47.1408], [-111.425, 47.2042], [-111.41, 47.2781], [-111.397, 47.3389], [-111.387, 47.3947], [-111.362, 47.4414], [-111.319, 47.4808], [-111.337, 47.5011], [-111.371, 47.4781]]

#below seemed to have issues
#Wrapper to make it hashable see: https://github.com/Toblerity/Shapely/issues/209
#likely not a good long-term solution todo!
#class Sub:
#    def __init__(self, linestring):
#        #self.num = num
#        #num+=1
#        self.linestring = linestring
#
#    def __hash__(self):
#        return hash(tuple(self.linestring.coords))
#
#    def __eq__(self, other): #may be slow todo!
#        if len(self.linestring.coords) != len(other.linestring.coords):
#            return False
#        for i in range(len(self.linestring.coords)):
#            if self.linestring.coords[i] != other.linestring.coords[i]:
#                return False
#        return True

import numpy as np
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import split, linemerge
import networkx as nx
#from networkx.drawing.nx_pydot import write_dot
import matplotlib.pyplot as plt



#Adjust position and scale for plotting over the tree
def plot_path(ax, line, pos, color, zorder):
    x, y = line.xy
    xr = np.array(x)*20
    yr = np.array(y)*20
    ax.plot(xr+pos[0]+2250, yr+pos[1]-930, color=color, linewidth=1, solid_capstyle='round', zorder=zorder)

#Calculate the ratio of path length to separation of endpoints.
def calcRatio(line):
    return line.length / LineString([line.coords[0], line.coords[-1]]).length

#split the path into numResultingPieces (or as nearly as possible)
def splitPath(path, numResultingPieces):
    if len(path.coords) <= numResultingPieces:
        numResultingPieces = len(path.coords)-1  #handle situations where we're trying to divide a two segment path into three pieces
    coordsInPart = len(path.coords)/numResultingPieces
    points=[]
    for i in range(numResultingPieces-1):
        points.append(Point(path.coords[int((i+1)*coordsInPart)]))
    subs = []
    pathRemaining = path
    for point in points:
        parts = list((split(pathRemaining, point)))
        subs.append(parts[0])
        pathRemaining = parts[1]
    subs.append(pathRemaining)
    return subs

nodeNum=1  #global variable.  Find a better way! todo  #should it be 0?

#recursively subdivide the trajectory until the threshold is reached.
def subTrajectorize(path, G, prevNum):
    threshold = 1.1
    #threshold = 2.0
    splitFactor = 2  #can change these parameters
    if calcRatio(path) < threshold:
        pass
    else:
        subs = splitPath(path, splitFactor)
        for sub in subs:
            global nodeNum
            G.add_node(nodeNum, p=sub)
            G.add_edge(prevNum, nodeNum)
            nodeNum+=1
            subTrajectorize(sub, G, nodeNum-1)

# divide trajectory and then plot
def setup(coords):
    points = []
    for coord in coords:
        points.append(Point(coord))
    return LineString(points)

def plotTree(G, fullIndex, with_labels=False, node_size=1000):
    #fig = plt.figure(figsize=(25, 14), dpi=80)
    fig = plt.figure(figsize=(12, 7), dpi=80)
    ax = fig.gca()

    pos=nx.nx_agraph.graphviz_layout(G, prog='dot')
    #write_dot(G, "test.dot")
    #nx.write_dot(G, "test.dot")
    nx.draw(G, pos, with_labels=with_labels, arrows=False, node_size=node_size, zorder=1, width=1, linewidths=0, node_color='w') #size was 1000

    paths=nx.get_node_attributes(G, 'p')

    for i in range(len(paths)):
        plot_path(ax, paths[i+1], pos[i+1], 'b', 5)
        plot_path(ax, paths[fullIndex], pos[i+1], '#f2f2f2', 4) #light grey
    plt.show()

    #uncomment below to also plot just the trajectory
    #fig = plt.figure()
    #ax = fig.gca()
    #x, y = path.xy
    #ax.plot(x, y, color='b', linewidth=3, solid_capstyle='round', zorder=1)
    #plt.show()

def test_sub_trajectorize():
    path = setup(coords)

    global nodeNum

    G = nx.Graph()
    G.add_node(nodeNum, p=path)
    nodeNum+=1
    subTrajectorize(path, G, nodeNum-1)

    plotTree(G, 1)


def get_next_piece(path, threshold):
    parts = list((split(path, Point(path.coords[1]))))#was 0
    sub_traj = parts[0]
    if(len(parts)>1):
        remainder = parts[1]
    else:
        remainder = None
    for coord in path.coords[2:]:  #skip first point  and second is above
        parts = list((split(path, Point(coord))))
        if calcRatio(parts[0]) > threshold:
            return (sub_traj, remainder) #return previous split results
        else:
            sub_traj = parts[0]
            if(len(parts)>1):
                remainder = parts[1]
            else:
                remainder = None
    return (path, None) #can't subdivide

nodeNum2=1

from itertools import izip_longest

def pairs(iterable):
    even = iterable[::2]
    odd = iterable[1::2]
    return izip_longest(even,odd, fillvalue=None)


def bottom_up_sub_trajectorize():
    #threshold = 1.1
    threshold = 2
    path = setup(coords)
    remainder = path

    global nodeNum2
    G = nx.Graph()

    leaves = []
    while remainder != None:
        (sub, remainder) = get_next_piece(remainder, threshold)
        G.add_node(nodeNum2, p=sub)
        leaves.append(nodeNum2)
        nodeNum2+=1

    nodes = leaves
    nextNodes = []

    while(True):
        paths=nx.get_node_attributes(G, 'p')
        if len(nodes) == 1:
            break
        else:
            for pair in pairs(nodes):
                if pair[1] == None:
                    nextNodes.append(pair[0])
                else:
                    G.add_node(nodeNum2, p=linemerge([paths[pair[0]].coords, paths[pair[1]].coords]))
                    G.add_edge(pair[0], nodeNum2)
                    G.add_edge(pair[1], nodeNum2)
                    nextNodes.append(nodeNum2)
                    nodeNum2+=1
            nodes = nextNodes
            nextNodes = []

    #relabel in opposite order (root is 1)
    mapping = {}
    for i in range(nodeNum2-1):
        mapping[i+1] = nodeNum2-1-i
    H=nx.relabel_nodes(G, mapping)
    plotTree(H, 1, with_labels=False, node_size=4000)#False)#True) #was nodeNum2-1

nodeNum3 = 1

#assumes indices are in order could check or sort.
def split_line_at_indices(line, indices):
    segments = []
    remainder = line
    for i in indices:
        if i == 0:
            segments.append(LineString())
        elif i == len(line.coords)-1: #this is the end.  append remainder then set remainder to empty
            segments.append(remainder)
            remainder = LineString()
        else:
            parts = list((split(remainder, Point(line.coords[i]))))
            if len(parts) == 1: #regions are incident #add empty
                segments.append(LineString())
            else:
                segments.append(parts[0])
                remainder = parts[1]
    segments.append(remainder)
    return segments

def find_straight(path, threshold, start_length):
    num_points = len(path.coords)
    if num_points == 3:
        return split_line_at_indices(path, [1]), start_length # split at middle of three points making two segments
    if num_points == 2:
        print "************two****" #return [path] #??
    straight_indices = []
    for i in range(num_points)[num_points-start_length+1:]: #start at where we left off previously (don't redo work)  #had +1
        print i, num_points-i
        for j in range(i+1):
            end_index = num_points-1-i+j
            #print j, end_index, "///"
            segs = split_line_at_indices(path, [j, end_index])
            if calcRatio(segs[1]) < threshold:
                #straight_segments.append({"seg": segs[1], "start_index": j, "end_index": num_points-1-i+j})
                straight_indices.append(j)
                straight_indices.append(end_index)
        if straight_indices: #not empty
            break
    print "start", straight_indices
    return split_line_at_indices(path, straight_indices), num_points-i
    #print straight_indices #straight_segments

    #consider only segments of length start_length or smaller
def adapt_helper(G, path, thisIndex, threshold, start_length):
    print "start", path.coords[0], path.coords[-1]
    global nodeNum3
    if calcRatio(path) >= threshold:
        segs, strt_len = find_straight(path, threshold, start_length)
        print(segs, strt_len, "***")
        for i in range(len(segs)):
            if i%2 == 0:#even = not straight
                if segs[i].coords: #not empty
                    G.add_node(nodeNum3, p=segs[i])
                    G.add_edge(nodeNum3, thisIndex)
                    nodeNum3+=1
                    adapt_helper(G, segs[i], nodeNum3-1, threshold, strt_len)
            else: #odd = straight
                G.add_node(nodeNum3, p=segs[i])
                G.add_edge(nodeNum3, thisIndex)
                nodeNum3+=1

def adapt_sub_trajectorize():
    threshold = 1.01#1.05#2#1.1
    path = setup(coords)#2

    G = nx.Graph()
    global nodeNum3
    G.add_node(nodeNum3, p=path)
    nodeNum3+=1
    adapt_helper(G, path, nodeNum3-1, threshold, len(path.coords))

    plotTree(G, 1, with_labels=False, node_size=4000)#False)#True) #was nodeNum2-1

def test_bottom_up_sub_trajectorize():
    bottom_up_sub_trajectorize()

def test_adapt_sub_trajectorize():
    adapt_sub_trajectorize()

if __name__ == "__main__":
    #test_sub_trajectorize()
    #test_bottom_up_sub_trajectorize()
    test_adapt_sub_trajectorize()
