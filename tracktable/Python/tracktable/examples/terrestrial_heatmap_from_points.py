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

"""heatmap_from_csv.py - Example of how to render a 2D geographic heatmap using points in a CSV file


This is both an example of how to use the library and a convenient
script that you can use to get started quickly.  You must provide as
input a delimited text file with at least 4 columns: object_id,
timestamp, longitude, latitude.  (All columns beyond those first four
will be ignored.)  The points in this file will be rendered onto a map
of part of the world.

You can control the following aspects of the rendering:

- Which part of the world is displayed in the map.  This defaults to
  the whole world but can be changed with the --map argument.  Your
  options are 'world', 'conus' (continental US), 'north_america' and
  'europe'.

- Which colormap is used to render the colors.  This defaults to the
  'gist_heat' thermal scale built into matplotlib.  You may specify
  the name of another if you prefer.  Note that you can only use the
  predefined colormaps here.  If you need a custom colormap, use this
  script as a starting point for your own code.

- The mapping from point density to color.  This defaults to 'linear'
  but you may also specify 'logarithmic' (or 'log' for short).

- The size of each histogram bin.  To create bins that are 0.5 degree
  on a side you would say '--histogram-bin-size 0.5'.

- The resolution of the output image with '--resolution 800 600' or
  whatever you choose.

- The output format.  This is automatically deduced from the output
  filename.

- The DPI of the output image.  Defaults to 72 (typical screen
  resolution).  Note that this will affect things like line thickness
  for borders: matplotlib sizes those things in points rather than
  pixels.

- Whether to draw continent boundaries, country borders,
  latitude/longitude graticules and (within North America) state
  borders.  By default all four are turned on.  Use
  '--omit-continents', '--omit-countries', '--omit-states' and
  '--omit-lonlat' to turn them off.  These will by default be drawn
  over the top of the histogram.

- The delimiter used to separate columns in the text file.  You can
  specify any single character to the '--delimiter' option or the
  magic strings 'tab' or '\t'.  (If it's easy for you to type in a
  literal tab then go ahead.  Just be sure to quote it.)

- Whether or not to draw cities, either with --draw-largest-cities
  or --draw-cities-above-size.

"""

from __future__ import print_function

# Tell Matplotlib to use the non-interactive backend so that we can
# run this script without a window system.  We do this before anything
# else so that we can be sure that no other package can initialize
# Matplotlib to default to a window system.
import matplotlib
matplotlib.use('Agg')

import numpy
import pprint
import sys

from tracktable.script_helpers import argparse, argument_groups
from tracktable.render import colormaps, histogram2d, mapmaker, projection
from tracktable.domain.cartesian2d import BasePoint as Point2D
from tracktable.domain.cartesian2d import BoundingBox as BoundingBox2D

from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap

import example_point_reader

# ----------------------------------------------------------------------

# Note: There is more work to do here to expose options for the
# linewidths, line colors, Z-order and background color for the map.
# That work will happen once we get this script up and running in the
# first place.

def parse_args():
    parser = argparse.ArgumentParser()
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("delimited_text_point_reader", parser)

    parser.add_argument('--colormap', '-c',
                        default='gist_heat',
                        help='Name of colormap for histogram.  Defaults to "bone".  See matplotlib documentation for a list of possibilities.')

    parser.add_argument('--scale', '-s',
                        default='linear',
                        choices=['linear', 'log', 'logarithmic'],
                        help='Mapping from histogram counts to colors.  Defaults to "linear" but can also be "log" or "logarithmic".')

    parser.add_argument('--histogram-bin-size', '-b',
                        type=float,
                        default=1,
                        help='Resolution of underlying histogram: each bin is this many degrees on a side.')

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
                        help='Filename for histogram image')

    args = parser.parse_args()
    if args.resolution is None:
        args.resolution = [ 800, 600 ]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

# ----------------------------------------------------------------------

def render_histogram(mymap,
                     point_source,
                     bin_size=2,
                     color_map='gist_gray',
                     scale_type='linear',
                     zorder=8):
    """Compile all the points in a source into a 2D histogram, then render
    that histogram onto an already-prepared map."""

    if scale_type.lower() == 'linear':
        scale = matplotlib.colors.Normalize()
    elif scale_type.lower() in [ 'log', 'logarithmic' ]:
        scale = matplotlib.colors.LogNorm()
    else:
        raise ValueError("ERROR: Unknown scale type '{}'.  Legal values are 'linear', 'log' and 'logarithmic'.".format(scale_type))


    if domain == 'terrestrial':
        # Deduce bounding box from map
        min_corner = Point2D(mymap.llcrnrlon, mymap.llcrnrlat)
        max_corner = Point2D(mymap.urcrnrlon, mymap.urcrnrlat)
        return histogram2d.render_histogram(mymap,
                                            point_source,
                                            BoundingBox2D(min_corner, max_corner),
                                            bin_size=bin_size,
                                            colormap=color_map,
                                            colorscale=scale,
                                            zorder=zorder)
    elif domain == 'cartesian2d':
        print("DEBUG: Computing data bounds from point source.")
        # This will load all points into memory at once and will
        # produce a histogram covering the entire point domain.  We
        # will fix this soon.
        all_points = list(point_source)
        x_min = min( point[0] for point in all_points )
        x_max = max( point[0] for point in all_points )
        y_min = min( point[1] for point in all_points )
        y_max = max( point[1] for point in all_points )
        bbox = BoundingBox2D(Point2D(x_min, y_min), Point2D(x_max, y_max))

        print("DEBUG: Data bounds: {}".format(bbox))
        return histogram2d.render_histogram(mymap,
                                            all_points,
                                            bbox,
                                            bin_size=bin_size,
                                            colormap=color_map,
                                            colorscale=scale,
                                            zorder=zorder)
    else:
        raise AttributeError('Domain {} does not yet have histogram support.'.format(domain))

# ----------------------------------------------------------------------

def setup_point_source(filename, args):
    """
    Instantiate and configure a delimited text point source using the
    filename and parameters supplied by the user.
    """

    config_reader = example_point_reader.configure_point_reader
    field_map = {}
    coordinate_map = {}
    arg_dict = vars(args)
    for column_name in [ 'object_id',
                         'timestamp',
                         'altitude',
                         'speed',
                         'heading' ]:

        field_name_in_args = '{}_column'.format(column_name)
        if arg_dict.get(field_name_in_args, None) is not None:
            field_map[column_name] = arg_dict[field_name_in_args]

    print("setup_point_source: args:\n{}".format(pprint.pformat(arg_dict)))

    infile = open(filename, 'rb')
    point_source = config_reader(infile,
                                 delimiter=args.delimiter,
                                 domain=args.domain,
                                 comment_character=args.comment_character,
                                 coordinate_assignments=args.coordinate_column,
                                 field_assignments=args.field_column)

    return point_source


# ----------------------------------------------------------------------

def main():
    args = parse_args()

    dpi = args.dpi
    image_resolution = args.resolution
    figure_dimensions = [
        float(image_resolution[0]) / dpi,
        float(image_resolution[1]) / dpi
    ]

    print("STATUS: Initializing image")
    figure = pyplot.figure(figsize=figure_dimensions, facecolor='black', edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, axisbg='black')
    axes.set_frame_on(False)

    print("STATUS: Creating geographic map")
    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    if args.domain == 'terrestrial':
        (mymap, artists) = mapmaker.terrestrial_map(axes=axes,
                                                    **mapmaker_kwargs)
    elif args.domain == 'cartesian2d':
        if len(mapmaker_kwargs.map_bbox) == 0:
            bbox = 'auto'
        else:
            bbox = BoundingBox2D(Point2D(mapmaker_kwargs.bbox[0],
                                         mapmaker_kwargs.bbox[1]),
                                 Point2D(mapmaker_kwargs.bbox[2],
                                         mapmaker_kwargs.bbox[3]))
        (mymap, artists) = mapmaker.cartesian_map(axes=axes,
                                                  map_bbox=bbox)

    else:
        raise AttributeError('Domain {} does not yet have render support.'.format(args.domain))

    print("STATUS: Initializing point source")
    source = setup_point_source(args.point_data_file[0], args)

    all_points = [ point for point in source ]

    print("STATUS: Reading points and rendering histogram")
    render_histogram(mymap,
                     args.domain,
                     all_points,
                     args.histogram_bin_size,
                     args.colormap,
                     args.scale)

    print("STATUS: Saving figure to file")
    pyplot.savefig(args.image_file[0],
                   figsize=figure_dimensions,
                   dpi=dpi,
                   frameon=False)

    pyplot.close()

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
