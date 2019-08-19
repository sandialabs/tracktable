#
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

"""trajectory_map_from_csv.py - Example of how to render trajectories on top of a geographic map using points in a CSV file


This is both an example of how to use the library and a convenient
script that you can use to get started quickly.  You must provide as
input a delimited text file with at least 4 columns: object_id,
timestamp, longitude, latitude.  (All columns beyond those first four
will be ignored.)  The points in this file will be assembled into
trajectories and then rendered onto a map of part of the world.  The
points in the input file MUST be sorted either (1) by object ID and
then by ascending timestamp or (2) strictly by ascending timestamp.

You can control the following aspects of the rendering:

- What domain the points are in.  You must specify this with '--domain
  cartesian' or '--domain terrestrial'.

- Which part of the world is displayed in the map (terrestrial
  domain).  This defaults to the whole world but can be changed with
  the --map argument.  Your options are 'world', 'conus' (continental
  US), 'north_america' and 'europe'.

TODO: Make sure that custom bounding boxes work for Cartesian
trajectories as well.

- Whether or not trajectories are colored differently at beginning and
  end.  By default, trajectories will be greenish when they begin and
  white-yellow when they end.

- Which colormap is used to render the scalars.  This defaults to the
  'autumn' color scale built into matplotlib.  You may specify the
  name of another if you prefer.  Note that you can only use the
  predefined colormaps here.  If you need a custom colormap, use this
  script as a starting point for your own code.

- The resolution of the output image with '--resolution 800 600' or
  whatever you choose.

- The output format.  This is automatically deduced from the output
  filename.

- The DPI of the output image.  Defaults to 72 (typical screen
  resolution).  Note that this will affect things like line thickness
  for borders: matplotlib sizes those things in points rather than
  pixels.

- Terrestrial domain only: Whether to draw continent boundaries,
  country borders, latitude/longitude graticules and (within North
  America) state borders.  By default all four are turned on.  Use
  '--omit-continents', '--omit-countries', '--omit-states' and
  '--omit-lonlat' to turn them off.  These will by default be drawn
  over the top of the histogram.

- The delimiter used to separate columns in the text file.  You can
  specify any single character to the '--delimiter' option or the
  magic strings 'tab' or '\t'.  (If it's easy for you to type in a
  literal tab then go ahead.  Just be sure to quote it.)

- Terrestrial domain only: Whether or not to draw cities, either with
  --draw-largest-cities or --draw-cities-above-size.

CAVEAT: This first version of the script loads all the points into
memory at once.

"""

from __future__ import print_function

# Tell Matplotlib to use the non-interactive backend so that we can
# run this script without a window system.  We do this before anything
# else so that we can be sure that no other package can initialize
# Matplotlib to default to a window system.
import matplotlib

if __name__ == '__main__':
    matplotlib.use('Agg')


import csv
import datetime
import numpy
import os.path
import pprint
import sys

from tracktable.core import geomath
from tracktable.feature import annotations
from tracktable.info import cities
from tracktable.render import colormaps, mapmaker, paths
from tracktable.script_helpers import argument_groups, argparse
from tracktable.examples import example_point_reader
from tracktable.examples import example_trajectory_builder
from tracktable.examples import example_trajectory_rendering

from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap


# ----------------------------------------------------------------------

# Note: There is more work to do here to expose options for the
# linewidths, line colors, Z-order and background color for the map.
# That work will happen once we get this script up and running in the
# first place.

def parse_args():
    parser = argparse.ArgumentParser()
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)


    parser.add_argument('--resolution', '-r',
                        nargs=2,
                        type=int,
                        help='Resolution of output image.  Defaults to 800 600.')

    parser.add_argument('--dpi',
                        type=int,
                        default=72,
                        help='DPI of output image.')

    parser.add_argument('point_data_file',
                        nargs=1,
                        help='Delimited text file containing point data')

    parser.add_argument('image_file',
                        nargs=1,
                        help='Filename for trajectory image')

    args = parser.parse_args()

    if args.resolution is None:
        args.resolution = [ 800, 600 ]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

# ----------------------------------------------------------------------

def setup_point_source(filename, args):
    """
    Instantiate and configure a delimited text point source using the
    filename and parameters supplied by the user.
    """

    config_reader = example_point_reader.configure_point_reader
    arg_dict = vars(args)

    infile = open(os.path.expanduser(filename), 'rb')
    point_source = config_reader(infile, **arg_dict)

                                 # delimiter=args.delimiter,
                                 # comment_character=args.comment_character,
                                 # object_id_column=args.object_id_column,
                                 # timestamp_column=args.timestamp_column,
                                 # string_field_assignments=args.string_field_column,
                                 # time_field_assignments=args.time_field_column,
                                 # numeric_field_assignments=args.numeric_field_column,
                                 # coordinate_assignments=args.coordinate_column,
                                 # domain=args.domain)

    return point_source

# ----------------------------------------------------------------------

def setup_trajectory_source(point_source, args):
    trajectory_args = argument_groups.extract_arguments("trajectory_assembly", args)
    source = example_trajectory_builder.configure_trajectory_builder(
        **trajectory_args
          )
    source.input = point_source

    return source.trajectories()

# ----------------------------------------------------------------------

def render_trajectories(basemap,
                        trajectory_source,
                        args):

    render_args = argument_groups.extract_arguments("trajectory_rendering", args)

    example_trajectory_rendering.render_trajectories(basemap,
                                                     trajectory_source,
                                                     **render_args)

def initialize_matplotlib_figure(figure_size_in_inches,
                                 axis_span=[0, 0, 1, 1],
                                 facecolor='black',
                                 edgecolor='black'):
    """Initialize a figure for Matplotlib to draw into.

    Args:
       figure_size_in_inches: 2-tuple of floats (width, height)
       axis_span: list of 4 floats (left, bottom, width, height) with size of axes in figure.
           Quantities are in fractions of figure width and height.
       facecolor: string (default 'black') - what's the background color of the plot?
       edgecolor: string (default 'black') - color of edge aroudn the figure

    Returns:
       (figure, axes) - both Matplotlib data structures
    """

    figure = pyplot.figure(figsize=figure_size_in_inches,
                           facecolor='black',
                           edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    return (figure, axes)

# ----------------------------------------------------------------------

def main():
    print("command line:\n{}\n".format(' '.join(sys.argv)))

    args = parse_args()

    dpi = args.dpi
    image_resolution = args.resolution
    figure_dimensions = [ float(image_resolution[0]) / dpi, float(image_resolution[1]) / dpi ]

    print("STATUS: Initializing canvas")
    (figure, axes) = initialize_matplotlib_figure(figure_dimensions)

    print("STATUS: Initializing point source")
    point_source = setup_point_source(args.point_data_file[0], args)

    # This is a little bit ugly but I don't yet know of a better way
    # to do it.  If we want to automatically compute the bounding box
    # of the data points before we render anything we must read all the
    # points at least once.
    #
    # That gives us a choice: read them once and keep them all in
    # memory, or make one pass through the file to compute the
    # bounding box and then another to read and render the points?
    #
    # For the moment I elect to read the points and keep them in memory.
    if args.domain == 'cartesian2d' and args.map_bbox is None:
        print("STATUS: Collecting points to compute bounding box")
        all_points = [ point for point in point_source ] # list(point_source)
        data_bbox = geomath.compute_bounding_box(all_points)
        point_source = all_points
        args.map_bbox = data_bbox

    print("STATUS: Creating map projection")
    mapmaker_args = argument_groups.extract_arguments("mapmaker", args)
    (mymap, map_actors) = mapmaker.mapmaker(**mapmaker_args)

    print("STATUS: Initializing trajectory source")
    trajectory_source = setup_trajectory_source(point_source, args)

    print("STATUS: Reading points, assembling trajectories and rendering data")
    color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)

    render_trajectories(mymap,
                        trajectory_source,
                        args)

    print("STATUS: Saving figure to file")
    pyplot.savefig(args.image_file[0],
                   facecolor=figure.get_facecolor(),
                   figsize=figure_dimensions,
                   dpi=dpi,
                   frameon=False)

    pyplot.close()

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
