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
import datetime
import argparse

from tracktable.domain.terrestrial import Trajectory, TrajectoryPoint

def get_path_piece(start, end, coords):
    points = []
    for coord in coords[start:end+1]:
        points.append(Point(coord))
    return LineString(points)

def traj_to_coords(traj):
    coordinates = []
    for point in traj: #make into coordinate list
        coordinates.append([point[0], point[1]])
    return coordinates

def plot_colored_segments_path(traj, leaves, threshold, savefig=False):
    coords = traj_to_coords(traj)
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

def plot_tree(G, traj, with_labels=False, node_size=1000, threshold=1.1,
             savefig=False):
    coords = traj_to_coords(traj)
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

def parse_args():
    parser = argparse.ArgumentParser(description='Subtrajectorize the trajectories in a given json file.')
    parser.add_argument('-i', '--input', dest='json_trajectory_file', type=argparse.FileType('r'), default="/home/bdnewto/research/edamame/tracktable/TestData/mapping_flight.json")
    return parser.parse_args()

def main():
    args = parse_args()
    threshold = 1.001
    length_threshold_samples = 7  #2 is minimum

    subtrajer = st.SubTrajectorizer(straightness_threshold=threshold,
                                    length_threshold_samples=length_threshold_samples)
    for traj in trajectory.from_ijson_file_iter(args.json_trajectory_file):
        leaves, G = subtrajer.subtrajectorize(traj, returnGraph=True)
        print(leaves)
        plot_tree(G, traj, with_labels=False, node_size=4000,
                  threshold=threshold, savefig=False)
        plot_colored_segments_path(traj, leaves, threshold, savefig=False)

if __name__ == '__main__':
    main()
