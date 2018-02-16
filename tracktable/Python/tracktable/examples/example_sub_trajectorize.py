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

import matplotlib.pyplot as plt
import tracktable.analysis.sub_trajectorize as st
import networkx as nx
from shapely.geometry import Point, LineString
import numpy as np
import tracktable.io.trajectory as trajectory

coords=[[-111.501, 47.3697], [-111.528, 47.3353], [-111.551, 47.3039],
        [-111.575, 47.2719], [-111.599, 47.2403], [-111.621, 47.2081],
        [-111.646, 47.1761], [-111.676, 47.1375], [-111.699, 47.1036],
        [-111.726, 47.0692], [-111.752, 47.0336], [-111.778, 46.9972],
        [-111.804, 46.9608], [-111.838, 46.9175], [-111.863, 46.8822],
        [-111.889, 46.8464], [-111.914, 46.8106], [-111.942, 46.7742],
        [-111.967, 46.7386], [-112.001, 46.6944], [-112.025, 46.6581],
        [-112.052, 46.6211], [-112.08, 46.5833], [-112.108, 46.5439],
        [-112.134, 46.5067], [-112.165, 46.4619], [-112.194, 46.4228],
        [-112.232, 46.3742], [-112.267, 46.3225], [-112.305, 46.2683],
        [-112.355, 46.2008], [-112.395, 46.1428], [-112.436, 46.0844],
        [-112.478, 46.0267], [-112.518, 45.9681], [-112.56, 45.9083],
        [-112.61, 45.8383], [-112.653, 45.7808], [-112.693, 45.72],
        [-112.719, 45.655], [-112.632, 45.6189], [-112.563, 45.5775],
        [-112.652, 45.5803], [-112.719, 45.6153], [-112.721, 45.6864],
        [-112.721, 45.7581], [-112.724, 45.8308], [-112.727, 45.9019],
        [-112.729, 45.9744], [-112.731, 46.0644], [-112.737, 46.2106],
        [-112.74, 46.2847], [-112.739, 46.3592], [-112.742, 46.4308],
        [-112.746, 46.5192], [-112.747, 46.5933], [-112.75, 46.6672],
        [-112.753, 46.7411], [-112.756, 46.815], [-112.757, 46.8894],
        [-112.759, 46.98], [-112.762, 47.0536], [-112.764, 47.1294],
        [-112.767, 47.2031], [-112.769, 47.2778], [-112.8, 47.3469],
        [-112.868, 47.3569], [-112.89, 47.2806], [-112.888, 47.2086],
        [-112.885, 47.1372], [-112.882, 47.0672], [-112.881, 46.9956],
        [-112.878, 46.91], [-112.875, 46.8381], [-112.873, 46.7658],
        [-112.871, 46.6947], [-112.868, 46.6236], [-112.866, 46.5511],
        [-112.863, 46.4653], [-112.861, 46.3992], [-112.86, 46.3133],
        [-112.856, 46.2414], [-112.853, 46.1703], [-112.851, 46.0969],
        [-112.849, 46.0253], [-112.845, 45.9528], [-112.842, 45.8672],
        [-112.841, 45.7947], [-112.838, 45.7231], [-112.837, 45.6506],
        [-112.876, 45.5911], [-112.94, 45.5817], [-112.951, 45.6711],
        [-112.952, 45.7472], [-112.955, 45.8225], [-112.958, 45.8983],
        [-112.962, 45.9736], [-112.963, 46.0497], [-112.965, 46.1253],
        [-112.97, 46.215], [-112.973, 46.2908], [-112.973, 46.3686],
        [-112.977, 46.4481], [-112.98, 46.5233], [-112.982, 46.6003],
        [-112.986, 46.6764], [-112.989, 46.7619], [-112.994, 46.9122],
        [-112.997, 46.9878], [-112.999, 47.0633], [-113.003, 47.1539],
        [-113.006, 47.2294], [-113.025, 47.2992], [-113.109, 47.315],
        [-113.193, 47.3242], [-113.28, 47.3344], [-113.383, 47.3469],
        [-113.469, 47.3544], [-113.557, 47.36], [-113.642, 47.3656],
        [-113.685, 47.3128], [-113.682, 47.2422], [-113.678, 47.1578],
        [-113.675, 47.0861], [-113.671, 47.015], [-113.667, 46.9433],
        [-113.661, 46.8], [-113.656, 46.7125], [-113.653, 46.6422],
        [-113.649, 46.57], [-113.646, 46.4992], [-113.642, 46.4281],
        [-113.64, 46.3569], [-113.635, 46.2711], [-113.632, 46.2],
        [-113.63, 46.1219], [-113.626, 46.0506], [-113.623, 45.9797],
        [-113.619, 45.9078], [-113.616, 45.8356], [-113.612, 45.7631],
        [-113.608, 45.6769], [-113.556, 45.6172], [-113.477, 45.6708],
        [-113.401, 45.6414], [-113.329, 45.6028], [-113.215, 45.6303],
        [-113.072, 45.6603], [-112.951, 45.6878], [-112.83, 45.7164],
        [-112.706, 45.7422], [-112.584, 45.7708], [-112.459, 45.7972],
        [-112.335, 45.8244], [-112.187, 45.8569], [-112.065, 45.8853],
        [-111.94, 45.9106], [-111.816, 45.9392], [-111.692, 45.9661],
        [-111.568, 45.9936], [-111.442, 46.0231], [-111.291, 46.0558],
        [-111.165, 46.0853], [-111.071, 46.0042], [-110.966, 45.9964],
        [-110.918, 46.5919], [-110.918, 46.6658], [-110.919, 46.755],
        [-110.918, 46.8286], [-110.918, 46.9022], [-110.919, 46.9756],
        [-110.918, 47.0489], [-110.918, 47.1222], [-110.915, 47.2094],
        [-110.934, 47.2747], [-110.994, 47.2997], [-111.04, 47.245],
        [-111.041, 47.1714], [-111.043, 47.0975], [-111.041, 47.0106],
        [-111.043, 46.9372], [-111.043, 46.8642], [-111.044, 46.7908],
        [-111.043, 46.7167], [-111.039, 46.6444], [-111.039, 46.5558],
        [-111.039, 46.4817], [-111.041, 46.41], [-111.041, 46.3336],
        [-111.041, 46.2617], [-111.04, 46.1878], [-111.079, 46.1136],
        [-111.138, 46.0719], [-111.155, 46.1308], [-111.161, 46.2008],
        [-111.16, 46.275], [-111.16, 46.3489], [-111.162, 46.4378],
        [-111.16, 46.5083], [-111.161, 46.5806], [-111.161, 46.6517],
        [-111.163, 46.7253], [-111.163, 46.7989], [-111.162, 46.8892],
        [-111.162, 46.9636], [-111.163, 47.04], [-111.162, 47.1131],
        [-111.202, 47.2375], [-111.275, 47.1861], [-111.28, 47.1131],
        [-111.279, 47.0411], [-111.279, 46.9675], [-111.278, 46.8211],
        [-111.278, 46.7331], [-111.276, 46.6594], [-111.276, 46.5864],
        [-111.275, 46.5131], [-111.275, 46.4344], [-111.275, 46.3592],
        [-111.275, 46.2842], [-111.274, 46.1958], [-111.273, 46.1214],
        [-111.274, 46.0475], [-111.274, 45.9725], [-111.274, 45.8992],
        [-111.321, 45.8253], [-111.38, 45.8469], [-111.388, 45.9183],
        [-111.386, 45.9919], [-111.386, 46.0661], [-111.387, 46.14],
        [-111.388, 46.2131], [-111.387, 46.3017], [-111.389, 46.3775],
        [-111.388, 46.445], [-111.388, 46.5206], [-111.389, 46.61],
        [-111.389, 46.6844], [-111.391, 46.7603], [-111.391, 46.8347],
        [-111.392, 46.9081], [-111.393, 46.9819], [-111.393, 47.0717],
        [-111.393, 47.1461], [-111.428, 47.2106], [-111.491, 47.2411],
        [-111.518, 47.1778], [-111.516, 47.1044], [-111.515, 47.0175],
        [-111.517, 46.9467], [-111.515, 46.8753], [-111.514, 46.8036],
        [-111.514, 46.73], [-111.514, 46.6567], [-111.512, 46.5697],
        [-111.512, 46.4958], [-111.51, 46.4261], [-111.511, 46.3392],
        [-111.509, 46.2661], [-111.508, 46.1956], [-111.508, 46.1253],
        [-111.507, 46.0544], [-111.506, 45.9828], [-111.506, 45.8958],
        [-111.508, 45.8228], [-111.509, 45.7442], [-111.549, 45.6875],
        [-111.612, 45.7292], [-111.678, 45.6767], [-111.687, 45.8181],
        [-111.671, 45.8961], [-111.656, 45.9742], [-111.642, 46.0519],
        [-111.627, 46.1319], [-111.612, 46.2117], [-111.594, 46.3067],
        [-111.578, 46.3881], [-111.563, 46.4728], [-111.547, 46.5531],
        [-111.532, 46.6314], [-111.518, 46.7078], [-111.504, 46.7814],
        [-111.488, 46.8686], [-111.476, 46.9367], [-111.463, 47.0064],
        [-111.448, 47.0764], [-111.436, 47.1408], [-111.425, 47.2042],
        [-111.41, 47.2781], [-111.397, 47.3389], [-111.387, 47.3947],
        [-111.362, 47.4414], [-111.319, 47.4808], [-111.337, 47.5011],
        [-111.371, 47.4781]]

def get_path_piece(start, end, coords):
    points = []
    for coord in coords[start:end+1]:
        points.append(Point(coord))
    return LineString(points)

def plot_colored_segments_path(coords, leaves, threshold, savefig=False):
    fig = plt.figure(figsize=(25, 14), dpi=80)
    ax = fig.gca()

    for i in range(len(leaves)):
        leaf = leaves[i]
        line = get_path_piece(leaf[0], leaf[1], coords)
        x, y = line.xy
        color = 'b'
        if i%2 == 1:
            color='r'
        ax.plot(np.array(x), np.array(y), color=color, linewidth=1,
            solid_capstyle='round')
    if savefig:
        plt.savefig('sub_trajectorization-colored-'+str(threshold)+'.png')
    else:
        plt.show()

def plot_path(ax, line, pos, color, zorder):
    x, y = line.xy
    xr = np.array(x)*20
    yr = np.array(y)*20
    ax.plot(xr+pos[0]+2250, yr+pos[1]-930, color=color, linewidth=1,
            solid_capstyle='round', zorder=zorder)

def plot_tree(G, coords, with_labels=False, node_size=1000, threshold=1.1,
             savefig=False):
    starts = nx.get_node_attributes(G, 's')
    ends = nx.get_node_attributes(G, 'e')
    for i in range(len(starts)):
        G.node[i+1]['p'] = get_path_piece(starts[i+1], ends[i+1], coords)

    plot_tree_helper(G, with_labels=with_labels, node_size=node_size,
                   threshold=threshold, savefig=savefig)

def plot_tree_helper(G, with_labels=False, node_size=1000, threshold=1.1,
                   savefig=False):
    fig = plt.figure(figsize=(25, 14), dpi=80)
    ax = fig.gca()

    pos=nx.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=with_labels, arrows=False,
            node_size=node_size, zorder=1, width=1, linewidths=0,
            node_color='w') #size was 1000

    paths=nx.get_node_attributes(G, 'p')

    for i in range(len(paths)):
        plot_path(ax, paths[i+1], pos[i+1], 'b', 5) #remove +1
        plot_path(ax, paths[1], pos[i+1], '#f2f2f2', 4) #light grey
        #change 1 to 0 above

    if savefig:
        plt.savefig('sub_trajectorization-'+str(threshold)+'.png')
    else:
        plt.show()

def main():

    threshold = 1.001
    length_threshold_samples = 7  #2 is minimum

    subtrajer = st.SubTrajectorizer(straightness_threshold=threshold,
                                    length_threshold_samples=length_threshold_samples)

    with open("/home/bdnewto/research/edamame/tracktable/TestData/two_trajectories.json", 'r') as file:
        coordinates = []
        for traj in trajectory.from_ijson_file_iter(file):
            leaves, G = subtrajer.subtrajectorize(traj, returnGraph=True)
            plot_tree(G, coords, with_labels=False, node_size=4000,
                      threshold=threshold, savefig=False)
            plot_colored_segments_path(coords, leaves, threshold, savefig=False)

if __name__ == '__main__':
    main()
