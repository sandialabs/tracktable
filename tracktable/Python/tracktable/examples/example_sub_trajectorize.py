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

# Author: Ben Newton  - February, 2018

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tracktable.analysis.sub_trajectorize as st
import networkx as nx
from shapely.geometry import Point, LineString
import numpy as np
import tracktable.io.trajectory as trajectory
import datetime
import argparse

from mpl_toolkits.basemap import Basemap
from tracktable.render import colormaps, mapmaker, paths
from matplotlib.patches import Polygon
from matplotlib import gridspec

from tracktable.domain.terrestrial import Trajectory, TrajectoryPoint
from tracktable.core import geomath

#todo.  Uses too much memory when many trajs are processed.  Fix leak.
#todo may want to try a value of 5 or 4 not 7 for length threshold
from enum import Enum

class Method(Enum):   #duplicated from example_sub_trajectoirze_mongo.  Fix todo
    straight = 'straight'
    accel = 'accel'

    def __str__(self):
        return self.value

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

# below adapted from https://stackoverflow.com/questions/12251189/
#                                          how-to-draw-rectangles-on-a-basemap
def draw_screen_poly( lats, lons, m):
    x, y = m( lons, lats )
    xy = list(zip(x,y))
    poly = Polygon( xy, facecolor='red', alpha=0.4, zorder=10)
    plt.gca().add_patch(poly)

def plot_colored_segments_path(traj, leaves, threshold, bbox,
                               savefig=False):
    fig = plt.figure(figsize=(25, 14), dpi=80)
    gs = gridspec.GridSpec(1,2,width_ratios=[3,1])
    ax = fig.add_subplot(gs[0])

    (mymap, map_actors) = mapmaker.mapmaker(map_name='custom',
                                            domain='terrestrial',
                                            map_bbox=bbox,
                                            map_projection="merc",
                                            land_color='w',
                                            sea_color='gray',
                                            resolution='f')

    coords = traj_to_coords(traj)

    for i in range(len(leaves)):
        leaf = leaves[i]
        line = get_path_piece(leaf[0], leaf[1], coords)
        lons, lats = line.xy
        x,y = mymap(lons, lats)

        color = 'b'
        if i%2 == 1:
            color='r'
        mymap.plot(x, y, color=color, linewidth=1)
        mymap.plot(x,y, 'go', markersize=1)

    ax = fig.add_subplot(gs[1])
    #draw box showing where in us the map is
    (mymap2, map_actors) = mapmaker.mapmaker(map_name='conus',
                                             domain='terrestrial',
                                             land_color='w', sea_color='gray',
                                             resolution='c')
    lons = [bbox.min_corner[0], bbox.max_corner[0],
            bbox.max_corner[0], bbox.min_corner[0]]
    lats = [bbox.min_corner[1], bbox.min_corner[1],
            bbox.max_corner[1], bbox.max_corner[1]]
    draw_screen_poly(lats, lons, mymap2)

    if savefig:
        plt.savefig('sub_trajectorization-colored-'+
                    traj[0].object_id+'-'+str(traj[0].timestamp)+'-'+str(threshold)+'.png')
    else:
        plt.show()
    plt.close()

def plot_path(ax, line, pos, color, zorder, max_width_height, magnification,
              xoffset, yoffset, linewidth=1):
    x, y = line.xy
    xr = np.array(x)*magnification#18.87#1.5   #    y=-.000004252x+21.454678635  where x is max width/height
    yr = np.array(y)*magnification#18.87#1.5
    ax.plot(xr+pos[0]+xoffset, yr+pos[1]+yoffset,
            color=color, linewidth=linewidth, solid_capstyle='round', zorder=zorder)

    #note this func does not take into account curvature of the earth
def plot_tree(G, traj, bbox, with_labels=False, node_size=5000,
              threshold=1.1, savefig=False):
    #max_width, max_height = mymap(bbox.max_corner[0], bbox.max_corner[1])
    max_width_height = max(bbox.max_corner[0], bbox.max_corner[1])
    coords = traj_to_coords(traj)
    starts = nx.get_node_attributes(G, 's')
    ends = nx.get_node_attributes(G, 'e')
    for i in range(len(starts)):
        G.node[i+1]['p'] = get_path_piece(starts[i+1], ends[i+1], coords)

    plot_tree_helper(G, traj[0].object_id, traj[0].timestamp,
                     max_width_height, with_labels=with_labels,
                     node_size=node_size, threshold=threshold,
                     savefig=savefig)

def plot_tree_helper(G, object_id, timestamp, max_width_height,
                     with_labels=False, node_size=5000, threshold=1.1,
                     savefig=False):
    fig = plt.figure(figsize=(25,14), dpi=80)
    ax = fig.gca()

    pos=nx.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=with_labels, arrows=False,
            node_size=node_size, zorder=1, width=1, edge_color='#A92C00',
            style='dotted', linewidths=0, node_color='w')

    paths=nx.get_node_attributes(G, 'p')

    magnification = (-.000004252*max_width_height)+21.454678635
    #                                                   hold
    #                              continental mapping  AWE50   AFR6737   AWE297  AWE681 AWE1612  CLX771
    xoffset = magnification*112.5 #    93.33     112.5    114     76        113?    112    77       83
    yoffset = magnification*-46.5 #   -33.33    -46.5    -32.85  -41.33    -33.85   33    -38      -42
    #print(magnification, xoffset, yoffset)

    for i in range(len(paths)):
        plot_path(ax, paths[i+1], pos[i+1], '#005376', #matches poster color
                  5, max_width_height,
                  magnification, xoffset, yoffset, linewidth=2) #remove +1
        light_gray = '#afafaf' #'#f2f2f2'
        plot_path(ax, paths[1], pos[i+1], light_gray, 4, max_width_height,
                  magnification, xoffset, yoffset)
        #change 1 to 0 above

    if savefig:
        plt.savefig('sub_trajectorization-'+object_id+'-'+str(timestamp)+'-'+
                    str(threshold)+'.png')
    else:
        plt.show()
    plt.close()

def parse_args():
    desc = 'Subtrajectorize and render the trajectories in a given json file.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--input', dest='json_trajectory_file',
                        type=argparse.FileType('r'),
                        default="../../../..//TestData/mapping_flight.json")
    parser.add_argument('-f', '--saveFigures', dest='save_fig',
                        action="store_true")
    parser.add_argument('-m', dest='method', type=Method, choices=list(Method), default='straight')
    parser.add_argument('-s', dest='straightness_threshold', type=float,
                        default=1.001)
    #below - 2 is minimum  #could likely decrease?
    parser.add_argument('-l', dest='length_threshold', type=int, default=7)

    #below params for Accel only
    parser.add_argument('-a', dest='accel_threshold', type=float, default=0.025)
    parser.add_argument('-t', '--tight', dest='tight', action="store_true")

    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()

    if args.verbose:
        print("Segmentation method is "+str(args.method))

    if args.method == Method.accel:
        subtrajer = \
        st.SubTrajerAccel(accel_threshold=args.accel_threshold,
                          tight=args.tight)
    else:
        subtrajer = \
        st.SubTrajerStraight(straightness_threshold=args.straightness_threshold,
                          length_threshold_samples=args.length_threshold)

    for traj in trajectory.from_ijson_file_iter(args.json_trajectory_file):
        if args.method == Method.accel:
            leaves = subtrajer.subtrajectorize(traj, returnGraph=True)
        else:
            leaves, G = subtrajer.subtrajectorize(traj, returnGraph=True)
        print(traj[0].object_id, leaves)

        #below expand 5% or .1 degrees when bbox has no expanse in some dim
        bbox = geomath.compute_bounding_box(traj, expand=.05,
                                            expand_zero_length=.1)

        # the mymap parameter below is only needed to get the max width or
        # height in terms ov the values used to scale the maps
        plot_colored_segments_path(traj, leaves, args.straightness_threshold, bbox,
                                   savefig=args.save_fig)
        if args.method == Method.straight:
            plot_tree(G, traj, bbox, with_labels=False,
                      node_size=5000, threshold=args.straightness_threshold, savefig=args.save_fig)


if __name__ == '__main__':
    main()
