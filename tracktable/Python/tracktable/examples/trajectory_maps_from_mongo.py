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

# Author: Ben Newton  - April 17, 2018

import argparse
from pymongo import MongoClient
import tracktable.inout.trajectory as trajectory
import sys

import matplotlib
matplotlib.use('Agg')

from tracktable.core import geomath
from tracktable.info import cities
from tracktable.render import colormaps, mapmaker, paths
from tracktable.script_helpers import argument_groups, argparse

from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap

from tracktable.examples import example_trajectory_rendering

#Example: python trajectory_maps_from_mongo.py --map "custom" HoldingTrajectories hold.png
#         python trajectory_maps_from_mongo.py --map "custom" VerifiedHoldingTrajectories vhold.png

def parse_args():
    parser = argparse.ArgumentParser()
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)


    parser.add_argument('--resolution', '-r',
                        nargs=2,
                        type=int,
                        help='Resolution of output image.  Defaults to 800 600.')

    parser.add_argument('--dpi',
                        type=int,
                        default=72,
                        help='DPI of output image')

    parser.add_argument('mongo_collection',
                        help='mongo collection containing trajectory data')

    parser.add_argument('image_file',
                        nargs=1,
                        help='base filename for trajectory images')

    parser.add_argument('-r', '--regex', default="")

    args = parser.parse_args()

    if args.resolution is None:
        args.resolution = [ 800, 600 ]

    if args.map_name is "world":
        args.map_name = 'custom'  #I think world is the default but what if you want world? todo

    return args

# ----------------------------------------------------------------------

def render_trajectories(basemap,
                        trajectory_source,
                        args):

    render_args = argument_groups.extract_arguments("trajectory_rendering", args)

    example_trajectory_rendering.render_trajectories(basemap,
                                                     trajectory_source,
                                                     **render_args)

# ----------------------------------------------------------------------

def main():
    print("command line:\n{}\n".format(' '.join(sys.argv)))

    args = parse_args()

    dpi = args.dpi
    image_resolution = args.resolution
    figure_dimensions = [ float(image_resolution[0]) / dpi, float(image_resolution[1]) / dpi ]

    client = MongoClient('localhost', 27017)
    db = client.ASDI
    traj_db = db[args.mongo_collection]

    for traj_dict in traj_db.find():#'{'+args.regex+'}'):
        traj = trajectory.from_dict(traj_dict)
        #print("STATUS: Initializing canvas")
        figure = pyplot.figure(figsize=figure_dimensions)

        axes = figure.add_axes([0, 0, 1, 1], frameon=False)
        axes.set_frame_on(False)

        #print("STATUS: Initializing trajectory source")
        all_points = [point for point in traj]
        args.map_bbox = geomath.compute_bounding_box(all_points)
        #if args.domain == 'cartesian2d' and args.map_bbox is None:
        #    print("STATUS: Collecting points to compute bounding box")
        #    all_trajectories = itertools.chain(list(trajectory_source))
        #    data_bbox = geomath.compute_bounding_box(all_points)
        #    point_source = all_points
        #    args.map_bbox = data_bbox

        #print("STATUS: Creating map projection")
        mapmaker_args = argument_groups.extract_arguments("mapmaker", args)
        (mymap, map_actors) = mapmaker.mapmaker(**mapmaker_args)

        #print("STATUS: Reading trajectories and rendering data")
        color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)

        render_trajectories(mymap,
                            [traj],
                            args)

        print("STATUS: Saving figure to file")
        pyplot.savefig(traj_dict['_id']+'-'+args.image_file[0],
                       facecolor='white',
                       figsize=figure_dimensions,
                       dpi=dpi,
                       frameon=False)

        pyplot.close()

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
