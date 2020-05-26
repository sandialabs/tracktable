#
# Copyright (c) 2014-2020 National Technology and Engineering
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

"""heatmap_from_csv.py - Render a 2D geographic heatmap using points in a
delimited text file


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

import logging
import sys

from tracktable.core import geomath
from tracktable.script_helpers import argparse, argument_groups
from tracktable.render import histogram2d, mapmaker
from tracktable.domain import domain_module_from_name
from tracktable.domain import terrestrial, cartesian2d

import matplotlib
matplotlib.use('Agg')

# Traditionally, importing modules in Python after the first non-
# import statement is considered poor style.  We have to do it anyway
# in this case because we need to set Matplotlib's back end before
# we do anything with the toolkit.  The #noqa comment is to tell
# flake8, the Python style checker, that we really did mean to do this.
from matplotlib import pyplot # noqa

# ----------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser()
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("image", parser)

    parser.add_argument('--colormap', '-c',
                        default='gist_heat',
                        help=(
                          'Name of colormap for histogram.  Defaults to '
                          '"gist_heat" thermal scale.  See matplotlib '
                          'documentation for a list of possibilities.'))
    parser.add_argument('--scale', '-s',
                        default='linear',
                        choices=['linear', 'log', 'logarithmic'],
                        help=(
                          'Mapping from histogram counts to colors.  Defaults '
                          'to "linear" but can also be "log" or '
                          '"logarithmic".'))
    parser.add_argument('--histogram-bin-size', '-b',
                        type=float,
                        default=1,
                        help=(
                          'Resolution of underlying histogram: each bin is '
                          'this many degrees on a side.'))
    parser.add_argument('--bgcolor', '-bg',
                        default='black',
                        help='Background color for image')
    parser.add_argument('--title',
                        help='Title for figure.  Will be rendered at top.')
    parser.add_argument('point_data_file',
                        nargs=1,
                        help='Delimited text file containing point data')
    parser.add_argument('image_file',
                        nargs=1,
                        help='Filename for histogram image')

    args = parser.parse_args()
    if args.resolution is None:
        args.resolution = [800, 600]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

# ----------------------------------------------------------------------


def render_histogram(mymap,
                     domain,
                     point_source,
                     bounding_box,
                     bin_size=2,
                     color_map='gist_gray',
                     scale_type='linear',
                     zorder=8):
    """Compile all the points in a source into a 2D histogram, then render
    that histogram onto an already-prepared map."""

    if scale_type.lower() == 'linear':
        scale = matplotlib.colors.Normalize()
    elif scale_type.lower() in ['log', 'logarithmic']:
        scale = matplotlib.colors.LogNorm()
    else:
        raise ValueError((
          'ERROR: Unknown scale type "{}".  Legal values are "linear", '
          '"log" and "logarithmic".').format(scale_type))

    if domain not in ['terrestrial', 'cartesian2d']:
        raise AttributeError(('Domain {} is either misspelled (case matters) '
                              'or does not have histogram '
                              'support.').format(domain))

    if domain == 'terrestrial' and bounding_box is None:
        # Deduce bounding box from map.  Whatever the user requested
        # has already been figured out there.
        extent = mymap.get_extent()
        # Matplotlib axes supply their extent as (x_min, xmax, y_min, y_max)
        bounding_box = terrestrial.BoundingBox(
            terrestrial.BasePoint(extent[0], extent[2]),
            terrestrial.BasePoint(extent[1], extent[3]))

    return histogram2d.render_histogram(map_projection=mymap,
                                        point_source=point_source,
                                        bounding_box=bounding_box,
                                        bin_size=bin_size,
                                        colormap=color_map,
                                        colorscale=scale,
                                        zorder=zorder)

# ----------------------------------------------------------------------


def points_from_file(
    infile,
    coordinate0_column,
    coordinate1_column,
    comment_character='#',
    field_delimiter=',',
    domain='terrestrial'
      ):
    """points_from_file: Load a list of points from a delimited text file

    Use tracktable.domain.<domain>.BasePointReader to read points from a file.
    Results are returned as an iterable.

    Note: You can only iterate over the resulting point sequence once.  If you
    need to do more than that, save the points in a list:

    >>> all_points = list(points_from_file(infile, 2, 3))

    Arguments:
        infile {file-like object}: Data source for points
        coordinate0_column {int}: Column in file for x/longitude
        coordinate1_column {int}: Column in file for y/latitude

    Keyword Arguments:
        comment_character {single-character string}: Ignore lines in the input
            that have this as the first non-whitespace character.  Defaults to
            '#'.
        field_delimiter {single-character string}: This character is the field
            separator in the input and must be escaped inside strings.
            Defaults to ','.
        domain {(}string naming point domain}: Must be either 'terrestrial' or
            'cartesian2d' depending on whether your points are
            longitude/latitude or arbitrary Cartesian coordinates.  Defaults
            to 'terrestrial'.

    Returns:
        Iterable of tracktable.domain.<domain>.BasePoints.
  """
    domain_module = domain_module_from_name(domain)
    reader_type = getattr(domain_module, 'BasePointReader')
    reader = reader_type()
    reader.input = infile
    reader.coordinates[0] = coordinate0_column
    reader.coordinates[1] = coordinate1_column
    reader.comment_character = comment_character
    reader.field_delimiter = field_delimiter

    return reader


# ----------------------------------------------------------------------

def main():
    args = parse_args()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    dpi = args.dpi
    image_resolution = args.resolution
    figure_dimensions = [
        float(image_resolution[0]) / dpi,
        float(image_resolution[1]) / dpi
    ]

    logger.info("Initializing image canvas.")
    figure = pyplot.figure(figsize=figure_dimensions,
                           facecolor='black',
                           edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    logger.info("Initializing point source.")
    point_filename = args.point_data_file[0]
    with open(point_filename, 'r') as infile:
        point_source = points_from_file(
            infile,
            args.coordinate0,
            args.coordinate1,
            comment_character=args.comment_character,
            field_delimiter=args.delimiter,
            domain=args.domain)

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
        if args.domain == 'cartesian2d':
            if args.map_bbox is None:
                logger.info(('Collecting points to compute Cartesian '
                             'bounding box.'))
                point_source = list(point_source)
                data_bbox = geomath.compute_bounding_box(point_source)
            else:
                # The bounding box on the command line is
                # [x_min, y_min, x_max, y_max]
                data_bbox = cartesian2d.BoundingBox(
                    (args.map_bbox[0], args.map_bbox[1]),
                    (args.map_bbox[2], args.map_bbox[3])
                    )
        else:
            # Default to taking the histogram bounds from the map extent.
            data_bbox = None
            if args.map_bbox is not None:
                # The bounding box on the command line is
                # [x_min, y_min, x_max, y_max]
                data_bbox = terrestrial.BoundingBox(
                    (args.map_bbox[0], args.map_bbox[1]),
                    (args.map_bbox[2], args.map_bbox[3])
                    )

        logger.info("Creating map projection.")
        # There are a lot of keyword arguments for the map -- see
        # tracktable.script_helpers.argument_groups.mapmaker --
        # so rather than pull them out individually like we did for
        # the point reader we extract the whole dict using
        # tracktable.script_helpers.argument_groups.extract_arguments().
        mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
        (mymap, artists) = mapmaker.mapmaker(**mapmaker_kwargs)

        logger.info("Rendering histogram.")
        render_histogram(mymap,
                         domain=args.domain,
                         bounding_box=data_bbox,
                         point_source=point_source,
                         bin_size=args.histogram_bin_size,
                         color_map=args.colormap,
                         scale_type=args.scale)

    # We're done with the points so we exit the with: block where we held
    # the input file open.
    if args.title is not None:
        logger.info("Setting title: {}".format(args.title))
        figure.suptitle(args.title, color='white')

    logger.info("STATUS: Saving figure to file")
    savefig_kwargs = {'figsize': figure_dimensions,
                      'dpi': dpi,
                      'facecolor': args.bgcolor
                      }
    pyplot.savefig(args.image_file[0],
                   **savefig_kwargs)

    pyplot.close()

    return 0

# ----------------------------------------------------------------------


if __name__ == '__main__':
    sys.exit(main())
