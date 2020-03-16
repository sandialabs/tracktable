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

"""trajectory_map_from_csv.py - Render trajectories on a map


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
  cartesian2d' or '--domain terrestrial'.

- Which part of the world is displayed in the map (terrestrial domain).
  This defaults to the whole world but can be changed with the --map
  argument.  Your options are 'region:world', 'region:conus' (continental
  US), 'region:north_america' and 'region:europe'.  You may also specify
  'airport:KJFK' for a region surrounding an airport.

- What part of the Cartesian plane is displayed in the image (
  cartesian2d domain).

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
"""

from __future__ import print_function

import datetime
import itertools
import logging
import sys

from tracktable.core import geomath
from tracktable.domain import domain_module_from_name
from tracktable.render import mapmaker, paths
from tracktable.source.trajectory import AssembleTrajectoryFromPoints
from tracktable.script_helpers import argument_groups, argparse, n_at_a_time

import matplotlib
matplotlib.use('Agg')

# Traditionally, importing modules in Python after the first non-
# import statement is considered poor style.  We have to do it anyway
# in this case because we need to set Matplotlib's back end before
# we do anything with the toolkit.  The #noqa comment is to tell
# flake8, the Python style checker, that we really did mean to do this.
from matplotlib import pyplot # noqa

# ----------------------------------------------------------------------

# Note: There is more work to do here to expose options for the
# linewidths, line colors, Z-order and background color for the map.
# That work will happen once we get this script up and running in the
# first place.


def parse_args():
    parser = argparse.ArgumentParser()
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("mapmaker", parser)

    parser.add_argument('--trajectory-colormap',
                        default='gist_heat',
                        help='Name of Matplotlib colormap for trajectories')

    parser.add_argument('--trajectory-linewidth',
                        type=int,
                        default=1,
                        help='Width of trajectories on map in points')

    parser.add_argument('--resolution', '-r',
                        nargs=2,
                        type=int,
                        help=('Resolution of output image.  Defaults to '
                              '800 600.'))

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
        args.resolution = [800, 600]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

# --------------------------------------------------------------------


def extract_field_assignments_from_arguments(arguments,
                                             field_type):
    """Extract named field definitions from a dict of arguments

    When running this script, the user specifies named fields that
    the reader should process with arguments like
    '--real-field-column altitude 12'.  This will cause the reader
    to take column 12 in the data file, convert its contents to a
    floating-point number, and store the result in a property
    named "altitude" on each point.

    This function is a convenience: it extracts those declarations
    for a given field type (string, real, timestamp) from a dictionary
    or namespace of arguments, then returns the result as a dictionary
    that can be passed to trajectory_points_from_file().

    Arguments:
        arguments {dict}: Dictionary of parsed command-line arguments
        field_type {string}: What type of property to extract.  Must be
            'string', 'real' or 'time'.

    Returns:
        Dictionary containing { field_name: column_number } for the
        specified field type.  Dictionary will be empty if there are
        no assignments of that type.

    Raises:
        ValueError: invalid field type
    """

    if field_type not in ['string', 'real', 'time']:
        raise ValueError(('Field type ({}) must be one of "string", '
                          '"real", or "time".  Case matters').format(
                                field_type))

    arg_name = '{}_field_column'.format(field_type)
    arg_dict = dict(arguments)
    field_assignments = dict()
    definition_list = arg_dict.get(arg_name, None)
    if definition_list is not None:
        if len(definition_list) > 0:
            for (field_name, column) in n_at_a_time(definition_list, 2):
                field_assignments[field_name] = int(column)

    return field_assignments

# ----------------------------------------------------------------------


def trajectories_from_points(point_source,
                             separation_distance=1000,
                             separation_time=datetime.timedelta(hours=24),
                             minimum_length=2):
    """Assemble a sequence of points into trajectories

    This function will instantiate and configure a `tracktable.source.
    trajectory.AssembleTrajectoryFromPoints` to convert a sequence
    of points into a sequence of trajectories.

    You must specify an iterable of points.  You can also specify
    parameters that determine when a series of points with the
    same object ID will be cut into separate trajectories and the
    minimum number of points a trajectory must have in order to
    be worthy of consideration.

    Note: This function does not actually build the trajectories.  It
        only sets up the pipeline to generate them.  Assembly does
        not happen until you start to pull elements from the iterable
        that gets returned.

    Arguments:
        point_source {iterable} -- Sequence of points to assemble

    Keyword Arguments:
        separation_distance {float} -- Points with the same object ID
            that are at least this far apart will be used as the end
            of one trajectory and the beginning of the next.  Defaults
            to 1000 (km in terrestrial domain, units in cartesian2d).
        separation_time {datetime.timedelta} -- Points with the same
            object ID that have timestamps at least this far apart will
            be used as the end of one trajectory and the beginning of
            the next.  Defaults to 24 hours.
        minimum_length {integer} -- Trajectories with fewer than this
            many points will be discarded.  (default: 2)
    """

    assembler = AssembleTrajectoryFromPoints()
    assembler.input = point_source
    assembler.separation_distance = separation_distance
    assembler.separation_time = separation_time
    assembler.minimum_length = minimum_length

    return assembler

# ---------------------------------------------------------------------


def render_trajectories(trajectories,
                        map_canvas,
                        color_map='gist_heat',
                        linewidth=1):
    """Render trajectories onto a map

    This function will draw trajectories onto a map and color them
    by progress from beginning to end with user-specified color and
    line width.

    You can change the color map to any palette supported by Matplotlib.
    A full list, including samples, is available at the following URL:

    https://matplotlib.org/tutorials/colors/colormaps.html

    You can also change the width of the lines.  This will be constant
    along the length of the trajectory.

    Arguments:
        trajectories {iterable} -- Trajectories to render.
        map_canvas {Matplotlib axes} -- Map to draw into.  This will usually
            come from ``tracktable.render.mapmaker``.

    Keyword Arguments:
        color_map {string or matplotlib.colors.Colormap} -- Colors for
            trajectories.  Each trajectory's color will start out at the
            beginning of the colormap and will end at the end of the colormap.
            (default: 'gist_heat')
        linewidth {integer} -- How wide the trajectories should be on the map.
            Measured in points.  (default: 1)

    Returns:
          List of actors added to the map canvase
    """

    return paths.draw_traffic(map_canvas,
                              trajectories,
                              color_map=color_map,
                              linewidth=linewidth)

# ---------------------------------------------------------------------


def trajectory_points_from_file(
      infile,
      object_id_column,
      timestamp_column,
      coordinate0_column,
      coordinate1_column,
      string_fields=None,
      real_fields=None,
      time_fields=None,
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

    Note: The function 'extract_field_assignments_from_arguments' will help
        you pull out rela_fields, string_fields, and time_fields from a
        set of parsed arguments.

    Arguments:
        infile {file-like object}: Data source for points
        object_id_column {int}: Column in file containing object ID
        timestamp_column {int}: Column in file containing timestamps for points
        coordinate0_column {int}: Column in file for x/longitude
        coordinate1_column {int}: Column in file for y/latitude

    Keyword Arguments:
        string_fields {dict, string->int}: Columns in the input file that we
            want to add to points as string properties.  The keys in this
            dict should be the name of the field and the values should be the
            integer column IDs (first column is 0).
        real_fields {dict, string->int}: Columns in the input file that we
            want to add to points as real-valued properties.  The keys in this
            dict should be the name of the field and the values should be the
            integer column IDs (first column is 0).
        time_fields {dict, string->int}: Columns in the input file that we
            want to add to points as timestamp-valued properties.  The keys in
            this dict should be the name of the field and the values should be
            the integer column IDs (first column is 0).
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
        Iterable of tracktable.domain.<domain>.TrajectoryPoints.
    """
    domain_module = domain_module_from_name(domain)
    reader_type = getattr(domain_module, 'TrajectoryPointReader')
    reader = reader_type()
    reader.input = infile
    reader.object_id_column = object_id_column
    reader.timestamp_column = timestamp_column
    reader.coordinates[0] = coordinate0_column
    reader.coordinates[1] = coordinate1_column
    reader.comment_character = comment_character
    reader.field_delimiter = field_delimiter

    return reader


# ----------------------------------------------------------------------


def main():
    logger = logging.getLogger(__name__)
    args = parse_args()

    #
    # Step 1: set up a canvas in Matplotlib.
    #
    logger.info('Initializing renderer.')
    figure_dimensions = [
        float(args.resolution[0]) / args.dpi,
        float(args.resolution[1]) / args.dpi
        ]
    figure = pyplot.figure(figsize=figure_dimensions,
                           facecolor='black',
                           edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    #
    # Step 2: Set up the input pipeline to load points and build trajectories.
    #
    point_filename = args.point_data_file[0]
    args_as_dict = vars(args)
    string_fields = extract_field_assignments_from_arguments(args_as_dict, 'string')
    real_fields = extract_field_assignments_from_arguments(args_as_dict, 'real')
    time_fields = extract_field_assignments_from_arguments(args_as_dict, 'time')

    with open(point_filename, 'r') as infile:
        logger.info('Initializing point source.')
        point_source = trajectory_points_from_file(
                          infile,
                          args.object_id_column,
                          args.timestamp_column,
                          args.coordinate0,
                          args.coordinate1,
                          string_fields=string_fields,
                          real_fields=real_fields,
                          time_fields=time_fields,
                          comment_character=args.comment_character,
                          field_delimiter=args.delimiter,
                          domain=args.domain)

        trajectory_source = trajectories_from_points(
            point_source,
            separation_distance=args.separation_distance,
            separation_time=datetime.timedelta(minutes=args.separation_time),
            minimum_length=args.minimum_length)

        # There is a sensible default map for terrestrial data -- the entire
        # world.  There is no such default for Cartesian data.  If the user
        # has not provided map bounds, we can compute them from the data itself
        # at the cost of loading all the trajectories into memory at once.
        if args.domain == 'cartesian2d':
            if args.map_bbox is None or len(args.map_bbox) == 0:
                # Pull all the trajectories into memory by
                # forcing assembly
                trajectory_source = list(trajectory_source)
                data_bbox = geomath.compute_bounding_box(
                    itertools.chain(trajectory_source)
                    )
                args.map_bbox[0] = data_bbox.min_corner[0]
                args.map_bbox[1] = data_bbox.max_corner[0]
                args.map_bbox[2] = data_bbox.min_corner[1]
                args.map_bbox[3] = data_bbox.max_corner[1]

        #
        # Step 3: Set up the map.
        #
        # There are a lot of keyword arguments for the map -- see
        # tracktable.script_helpers.argument_groups.mapmaker --
        # so rather than pull them out individually like we did for
        # the point reader we extract the whole dict using
        # tracktable.script_helpers.argument_groups.extract_arguments().
        logger.info('Initializing map canvas.')
        mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
        (mymap, artists) = mapmaker.mapmaker(**mapmaker_kwargs)

        #paths.draw_traffic(
        #  traffic_map=mymap,
        #  trajectory_iterable=trajectory_source,
        #  color_map=args.trajectory_colormap,
        #  linewidth=args.trajectory_linewidth
        #  )

        render_trajectories(trajectory_source,
                            mymap,
                            linewidth=args.trajectory_linewidth,
                            color_map=args.trajectory_colormap)

    # We're done operating on the trajectory data so we can finally exit the
    # with: block that opened the data file.

    print("STATUS: Saving figure to file")
    pyplot.savefig(args.image_file[0],
                   facecolor=figure.get_facecolor(),
                   figsize=figure_dimensions,
                   dpi=args.dpi,
                   frameon=False)

    pyplot.close()

    return 0

# ----------------------------------------------------------------------


if __name__ == '__main__':
    sys.exit(main())
