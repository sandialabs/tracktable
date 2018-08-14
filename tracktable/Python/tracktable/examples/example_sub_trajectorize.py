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
#matplotlib.use("Agg") #uncomment for headless/non-graphical operation
import matplotlib.pyplot as plt
import tracktable.analysis.sub_trajectorize as st
import networkx as nx
from shapely.geometry import Point, LineString
import numpy as np
import tracktable.inout.trajectory as trajectory
import datetime
import argparse

from mpl_toolkits.basemap import Basemap
from tracktable.render import colormaps, mapmaker, paths
from matplotlib.patches import Polygon
from matplotlib import gridspec

from tracktable.domain.terrestrial import Trajectory, TrajectoryPoint
from tracktable.core import geomath

from tracktable.examples.kml_writer import write_kml_graph
from tracktable.analysis.parseTreeCategorizations import TreeParseError
import time
from tracktable.analysis.ExtendedPoint import IntersectionError

from fastkml import kml
from fastkml import styles
from fastkml import geometry as fg

#todo.  Uses too much memory when many trajs are processed.  Fix leak.
#todo may want to try a value of 5 or 4 not 7 for length threshold
from enum import Enum

row_count = 0
processed_count = 0

class Method(Enum):   #duplicated from example_sub_trajectoirze_mongo.  Fix todo
    straight = 'straight'
    accel = 'accel'
    semantic = 'semantic'
    curvature = 'curvature'

    def __str__(self):
        return self.value


def get_path_altitudes(start, end, coords):
    altitudes = []
    for coord in coords[start:end+1]:
        altitudes.append(coord[2])
    return altitudes

def get_path_piece(start, end, coords):
    points = []
    for coord in coords[start:end+1]:
        points.append(Point(coord[:2])) #don't include altitude
    return LineString(points)

def traj_to_coords(traj):
    coordinates = []
    for point in traj: #make into coordinate list
        if 'altitudes' in point.properties.keys(): #add altitude if exists
            coordinates.append([point[0], point[1], point.properties['altitudes']])
        else:
            coordinates.append([point[0], point[1], None])
    return coordinates

# below adapted from https://stackoverflow.com/questions/12251189/
#                                          how-to-draw-rectangles-on-a-basemap
def draw_screen_poly( lats, lons, m):
    x, y = m( lons, lats )
    xy = list(zip(x,y))
    poly = Polygon( xy, facecolor='red', alpha=0.4, zorder=10)
    plt.gca().add_patch(poly)

def export_kml(traj, leaves, filename_out='test.kml'):  #Ben's kml exporter version using pyKML
    lstyle = styles.LineStyle(id="redThick", color='FF0000FF', width=3.0)
    style = styles.Style(styles = [lstyle])
    k = kml.KML()
    ns = '{http://www.opengis.net/kml/2.2}'
    d = kml.Document(ns, 'docid', 'doc name', 'doc description', styles = [style])
    k.append(d)

    f = kml.Folder(ns, 'fid', 'f name' , 'f description')
    d.append(f)

    coords = traj_to_coords(traj)
    for i in range(len(leaves)):
        leaf = leaves[i]
        p2 = kml.Placemark(ns, 'id2', 'name2', 'descriptoin2', styles=[style])#, styleUrl="#redThick")
        #p2 = kml.Placemark(ns, 'id2', 'name2', 'descriptoin2', styleUrl="#redThick") #why does this not work?
        p2.geometry = get_path_piece(leaf[0], leaf[1], coords) #fg.LineString([(0,0,0), (1,1,1)])
        f.append(p2)

    with open(filename_out, 'w') as outfile:
        outfile.write(k.to_string())#prettyprint=True))

def export_colored_segments_path_kml(traj, tree_graph, threshold=None, bbox=None,
                                     savefig=False, insetMap=False,
                                     altitudePlot=False, ext="kml", output=''):
    if len(output) == 0:
        return

    extension = '.' + ext
    out_file_name = output + extension

    write_kml_graph(out_file_name, traj, tree_graph)
    if os.path.exists(out_file_name):
        print(f'successfully created {out_file_name}')



def plot_colored_segments_path(traj, leaves, threshold, bbox,
                               savefig=False, insetMap=True,
                               altitudePlot=True, ext="png", output=''):

    fig = plt.figure(figsize=(14,14), dpi=150)#dpi=300)
    if (insetMap and not altitudePlot) or (altitudePlot and not insetMap):
        gs = gridspec.GridSpec(1,2,width_ratios=[3,1])
        ax = fig.add_subplot(gs[0])
    elif insetMap and altitudePlot:
        gs = gridspec.GridSpec(1,3,width_ratios=[3,1,1])
        ax = fig.add_subplot(gs[0])
    else:
        ax = fig.gca()

    (mymap, map_actors) = mapmaker.mapmaker(map_name='custom',
                                            domain='terrestrial',
                                            map_bbox=bbox,
                                            map_projection="merc",
                                            land_color='w',#\/was gray before
                                            sea_color='gray',#'#ADD8E6', #light blue
                                            resolution='f') #f=full

    coords = traj_to_coords(traj)

    for i in range(len(leaves)):
        leaf = leaves[i]
        line = get_path_piece(leaf[0], leaf[1], coords)
        lons, lats = line.xy
        x,y = mymap(lons, lats)

        parallels = np.arange(20,60,1.)
        # labels = [left,right,top,bottom]
        mymap.drawparallels(parallels,labels=[True,False,False,False],
                            color='#dddddd', zorder=0, fontsize=7)#fontsize=25)
        meridians = np.arange(10.,351.,1.)
        mymap.drawmeridians(meridians,labels=[False,False,False,True],
                            color='#dddddd', zorder=0, fontsize=7)#fontsize=25)

        color = '#005376'
        if i%2 == 1:
            color='#A92C00'
        mymap.plot(x, y, color=color, alpha=1.0, linewidth=1, zorder=5)#6) #.67
        # if i%4 == 0:
        #     size = 50
        #     colr = '#005376'
        #     marker = 'x'
        # else:
        size = 8
        colr = '#A92C00'
        marker = 'o'
        mymap.scatter(x,y, c=color, marker=marker, s=size, zorder=4) #, color=colr)#7) #eeeeee
        # anXY = (x[-1], y[-1])
        # ax.annotate(str(i), xy=anXY, xycoords='data',
        #                xytext=(0.8, 0.95),
        #                textcoords='figure points',
        #                color='r')


    if insetMap:
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

    if insetMap and altitudePlot:
        ax = fig.add_subplot(gs[2])
    elif altitudePlot:
        ax = fig.add_subplot(gs[1])

    if altitudePlot:
        for i in range(len(leaves)):
            leaf = leaves[i]
            alts = get_path_altitudes(leaf[0], leaf[1], coords)

            color = '#005376'
            if i%2 == 1:
                color='#A92C00'
            ax.plot(range(leaf[0],leaf[1]+1), alts, color=color, zorder=5) #just plot sample altitudes
            ax.scatter(range(leaf[0],leaf[1]+1), alts, c='#bbbbbb', marker='o', s=2, zorder=4)#7)#eeeeee

    #plt.tight_layout(pad=7.0) #uncomment for tight layout for paper figures

    if savefig:
        if output == '':
            output = 'sub_trajectorization-colored-'+\
                     traj[0].object_id+'-'+str(traj[0].timestamp)+'-'+str(threshold)
        plt.savefig(output+'.'+ext)
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
              threshold=1.1, savefig=False, ext="png"):
    #max_width, max_height = mymap(bbox.max_corner[0], bbox.max_corner[1])
    max_width_height = max(bbox.max_corner[0], bbox.max_corner[1])
    coords = traj_to_coords(traj)
    starts = nx.get_node_attributes(G, 's')
    ends = nx.get_node_attributes(G, 'e')
    for i in range(len(starts)):
        G.node[i+1]['p'] = get_path_piece(starts[i+1], ends[i+1], coords)

    # plot_tree_helper(G, traj[0].object_id, traj[0].timestamp,
    #                  max_width_height, with_labels=with_labels,
    #                  node_size=node_size, threshold=threshold,
    #                  savefig=savefig, ext=ext)

def plot_tree_helper(G, object_id, timestamp, max_width_height,
                     with_labels=False, node_size=5000, threshold=1.1,
                     savefig=False, ext="png"):
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
                    str(threshold)+'.'+ext)
    else:
        plt.show()
    plt.close()

def parse_args():
    desc = 'Subtrajectorize and render the trajectories in a given json file.'\
           ' Example (accel figure for paper) python example_sub_trajectorize.py -f -m accel -t -d -o "accelp025"'\
           ' Example (straight, 2, 1.1 for paper) python example_sub_trajectorize.py -f -m straight -l 2 -s 1.1 -d -o "straight1p1"'\
           ' Example (straight, 2, 1.001 for paper) python example_sub_trajectorize.py -f -m straight -l 2 -s 1.001 -d -o "straight1p001"'\
           ' Example (straight, 7, 1.001 for paper) python example_sub_trajectorize.py -f -m straight -l 7 -s 1.001 -d -o "straight-71p001"'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--input', dest='json_trajectory_file',
                        type=argparse.FileType('r'),
                        default="../../../..//TestData/mapping_flight.json")
    parser.add_argument('-f', '--saveFigures', dest='save_fig',
                        action="store_true")
    parser.add_argument('-k', '--kml', dest='export_kml', action="store_true", help="flag to output as kml as well")
    parser.add_argument('-o', '--outputImageFilenameNoExt', dest='image_file', type=str, default='', help="filename and optional path without extension or period")
    parser.add_argument('-m', dest='method', type=Method, choices=list(Method), default='straight')
    parser.add_argument('-s', dest='straightness_threshold', type=float,
                        default=1.001)
    #below - 2 is minimum  #could likely decrease?
    parser.add_argument('-l', dest='length_threshold', type=int, default=7)

    #below params for Accel only
    parser.add_argument('-a', dest='accel_threshold', type=float, default=0.025)
    parser.add_argument('-t', '--tight', dest='tight', action="store_true")

    parser.add_argument('-p', '--insetMap', dest='insetMap', action="store_true")
    parser.add_argument('-u', '--altitudePlot', dest='altitudePlot', action="store_true")

    parser.add_argument('-d', '--pdf', dest='pdf', action="store_true") #output as pdf

    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true")
    return parser.parse_args()


import os
sandboxDirectory = '/ascldap/users/pschrum/Documents/tracktableTesting'
flightListFile = os.path.join(sandboxDirectory, 'TrajectoriesToSample.txt')
summaryJsonFile = os.path.join(sandboxDirectory, 'binSummary.json')

import getpass
outputDir = os.getcwd()
if getpass.getuser() == 'pschrum':
    outputDir = os.path.join(sandboxDirectory, 'testResults')

import json, sys
import gc
import psutil
from collections import deque, defaultdict


def get_point_count(aTraj):
    return sum([1 for x in aTraj])

def readFlistListFile():
    with open(flightListFile, 'r') as flf:
        return deque([x.rstrip() for x in flf.readlines()])


def _composeName(aTraj):
    ts = aTraj[0].timestamp.strftime('%m%d%H%M')
    oid = ts + '_' + aTraj[0].object_id
    return oid

def point_count_greater_than(gen, max_count):
    for ctr, _ in enumerate(gen):
        if ctr > max_count:
            return True

    return False

def output_category_hash_dict(the_dict: defaultdict, outpath: str,
                              should_write_report: bool = False) -> None:
    if not should_write_report:
        return

    keys = the_dict.keys()
    if len(keys) == 0:
        return
    out_file_name = os.path.join(outpath, "hash_report.csv")
    try:
        os.mkdir(outpath)
    except FileExistsError:
        pass
    with open(out_file_name, 'w') as fout:
        for a_key, traj_list in the_dict.items():
            out_str = a_key + ','
            out_str += str(len(traj_list)) + ','
            for idx, a_traj in enumerate(traj_list):
                if idx < 200:
                    out_str += a_traj + ','
            fout.write(out_str[:-1] + '\n')
            fout.flush()

def main():
    global row_count
    global processed_count
    args = parse_args()
    write_hash_report = False

    ext="png"
    if args.pdf:
        ext="pdf"

    if args.verbose:
        print("Segmentation method is "+str(args.method))

    should_plot_kml = False

    if args.method == Method.accel:
        subtrajer = \
            st.SubTrajerAccel(accel_threshold=args.accel_threshold,
                              tight=args.tight)
    elif args.method == Method.semantic:
        subtrajer = \
            st.SubTrajerSemantic(straightness_threshold=args.straightness_threshold,
                                 length_threshold_samples=args.length_threshold)
    elif args.method == Method.curvature:
        subtrajer = st.SubTrajerCurvature()
        curvature_instructions: dict = {}
        instructions_file = './curvature_instructions.txt'
        if os.path.exists(instructions_file):
            with open(instructions_file, 'r') as infile:
                for a_line in infile:
                    if ':' in a_line:
                        cmd_line = a_line.split(':')
                        cmd_type = cmd_line[0].strip()
                        cmd_val = cmd_line[1].strip()
                        curvature_instructions[cmd_type] = cmd_val
    else:
        subtrajer = \
            st.SubTrajerStraight(
                straightness_threshold=args.straightness_threshold,
                length_threshold_samples=args.length_threshold)

    process_names_deque = deque()
    instructions_parsed = False
    process_these_str = ''
    should_plot_kml = False
    category_hashes_dict = defaultdict(list)

    block_step_count = 10000
    clicks_per_second = 1000000
    start_time = time.time()
    skip_count = 0

    for traj in trajectory.from_json_file_iter(args.json_trajectory_file):
        row_count += 1
        if row_count < skip_count:
            if row_count == 500:
                print("500 rows skipped.")
            elif row_count % block_step_count == 0:
                # new_time = timeit.default_timer() * clicks_per_second
                # seconds = new_time - start_time
                # start_time = new_time
                # rate = block_step_count / seconds
                print(f"{row_count} rows skipped.") # in {seconds} seconds at {rate} trajs per second.")
            continue
        trajectoryName = _composeName(traj)

        if args.method == Method.straight:
            leaves, G = subtrajer.subtrajectorize(traj, returnGraph=True)
        elif args.method == Method.curvature:
            output_path = './'
            kml_file_name = ''
            if curvature_instructions and \
                    not instructions_parsed:
                instructions_parsed = True
                output_path = \
                    curvature_instructions.get('out_path', output_path)
                outputDir = output_path

                if 'plot graph' in curvature_instructions.get('action', []):
                    subtrajer.request_plot_graph()

                if 'generate summary' in curvature_instructions.get('action', []):
                    summary_csv_name = \
                        os.path.basename(args.json_trajectory_file.name)

                    subtrajer.request_summary_csv(output_path,
                                                  summary_csv_name)
                if 'generate kml' in curvature_instructions.get('action', []):
                    if not os.path.exists(output_path):
                        os.mkdir(output_path)
                    kml_file_name = os.path.join(output_path, trajectoryName)
                    should_plot_kml = True

                write_hash_report = False
                if 'generate groupings summary' in \
                        curvature_instructions.get('action', []):
                    write_hash_report = True


                write_kml_in_hash_directory = False
                if 'generate kml in grouping directories' in \
                        curvature_instructions.get('action', []):
                    write_kml_in_hash_directory = True
                    should_plot_kml = True

                if 'flights' in curvature_instructions.keys():
                    process_these_str = curvature_instructions['flights'] \
                        .strip()
                    process_these_str = process_these_str.split(',')
                    for a_name in process_these_str:
                        process_names_deque.append(a_name.strip())

            # try:
            if row_count % 500 == 0:
                mem_report = psutil.virtual_memory()
                ttl_mem, free_mem = mem_report[0], mem_report[1]
                available_percent = free_mem / ttl_mem
                print(f'Processing item {row_count}. {processed_count} pr' \
                      f'ocessed so far. {available_percent} memory left.')
                if available_percent < 0.10:
                    ttl_time = time.time() - start_time
                    print(
                        f'Took {ttl_time} seconds to process {processed_count} trajectories.')
                    output_category_hash_dict(category_hashes_dict,
                                              outputDir, write_hash_report)
                    raise MemoryError
                else:
                    pass
            if len(process_names_deque) > 0:
                if trajectoryName not in process_names_deque:
                    continue
                process_names_deque.remove(trajectoryName)
            else:
                if len(process_these_str) > 0:
                    print('Process complete.')
                    print(
                        f'{processed_count} processed out of {row_count}' \
                        ' flights.')
                    exit(0)

            try:
                leaves, G = subtrajer.subtrajectorize(traj, returnGraph=True)
                if G:
                    if write_hash_report:
                        category_hashes_dict[G.L1catHash].append(G.name)
                else:
                    processed_count += 1
                    continue
                processed_count += 1
                kml_file_name = os.path.join(outputDir, trajectoryName)
                if write_kml_in_hash_directory:
                    particular_output_path = \
                        os.path.join(outputDir, 'binnedKML')
                    particular_output_path = \
                        os.path.join(particular_output_path, G.L1catHash)
                    if not os.path.exists(particular_output_path):
                        os.mkdir(particular_output_path)
                    kml_file_name = os.path.join(particular_output_path, trajectoryName)

            except KeyboardInterrupt:
                output_category_hash_dict(category_hashes_dict, outputDir,
                                          write_hash_report)
            except TreeParseError as TPerror:
                # print (f'{TPerror} for {trajectoryName}')
                pass
            except IndexError:
                output_category_hash_dict(category_hashes_dict, outputDir,
                                          write_hash_report)
                raise
            # except TypeError:
            #     print(f'TypeError example_sub_trajecorize.py, Line 522, process row= {row_count}.')
            #     continue
        else:
            leaves = subtrajer.subtrajectorize(traj, returnGraph=False)

        if leaves is None: # or pointCount < 3:
            continue

        trajectoryName = _composeName(traj)
        if args.verbose:
            print("Segmentation=", traj[0].object_id, leaves)

        if args.method != Method.curvature:
            #below expand 5% or .1 degrees when bbox has no expanse in some dim
            bbox = geomath.compute_bounding_box(traj, expand=.05,
                                                expand_zero_length=.1)

        plotFileName = _composeName(traj) + '_' + args.image_file


        # trajectoryName = os.path.join(outputDir, trajectoryName)
        # the mymap parameter below is only needed to get the max width or
        # height in terms ov the values used to scale the maps
        if args.method != Method.curvature and not args.export_kml:
            plot_colored_segments_path(traj, leaves,
                                       args.straightness_threshold,
                                       None, savefig=args.save_fig,
                                       insetMap=args.insetMap,
                                       altitudePlot=args.altitudePlot, ext=ext,
                                       output=args.image_file)
        elif should_plot_kml:
            if args.method == Method.curvature:
                # kml_file_name = os.path.join(output_path, )
                export_colored_segments_path_kml(traj, G,
                                                 args.straightness_threshold,
                                                 None, savefig=args.save_fig,
                                                 insetMap=args.insetMap,
                                                 altitudePlot=args.altitudePlot,
                                                 ext='kml',
                                                 output=kml_file_name)
            else:
                export_kml(traj, leaves, filename_out="test.kml")

        if args.method != Method.curvature:
            print(plotFileName,"saved.")
        if args.method == Method.straight:
            plot_tree(G, traj, bbox, with_labels=False,
                      node_size=5000, threshold=args.straightness_threshold,
                      savefig=args.save_fig, ext=ext)

    ttl_time = time.time() - start_time
    print(
        f'Took {ttl_time} seconds to process {processed_count} trajectories.')
    output_category_hash_dict(category_hashes_dict, outputDir,
                              write_hash_report)
    print(f'{processed_count} processed out of {row_count} flights.')


if __name__ == '__main__':
    main()
