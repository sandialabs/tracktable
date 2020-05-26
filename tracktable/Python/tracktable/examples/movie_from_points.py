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

"""movie_from_points.py - Example of how to render a movie of
trajectories built from points in a CSV file

"""

import tracktable.domain
from tracktable.feature import annotations

from tracktable.core import geomath
from tracktable.render import mapmaker, paths
from tracktable.script_helpers import argument_groups, argparse, n_at_a_time
from tracktable.source.trajectory import AssembleTrajectoryFromPoints

import datetime
import itertools
import logging
import numpy
import shlex
import sys

import matplotlib
from matplotlib import pyplot
import matplotlib.animation
matplotlib.use('Agg')


# ----------------------------------------------------------------------


def assemble_trajectories(point_source,
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


def clip_trajectories_to_interval(trajectories, start_time, end_time):
    trajectories_this_frame = [
        t for t in trajectories if trajectory_overlaps_interval(
            t, start_time, end_time)
    ]

    clipped_trajectories = (
        geomath.subset_during_interval(t, start_time, end_time)
        for t in trajectories_this_frame
        )

    return clipped_trajectories

# ----------------------------------------------------------------------


def compute_figure_dimensions(resolution, dpi):
    """Compute figure dimensions in inches given resolution and dots per inch

    Given an image of resolution X by Y pixels and D dots per inch,
    the figure's dimensions in inches are (X/D, Y/D).

    Arguments:
        resolution {list or tuple of 2 ints}: Image resolution in pixels
        dpi {int}: Dots per inch for image

    Returns:
        Tuple of two floats containing image size in inches
    """

    return (float(resolution[0])/dpi, float(resolution[1])/dpi)

# ---------------------------------------------------------------------


def compute_movie_time_bounds(trajectories, user_start_time, user_end_time):
    """Compute start and end time for a movie

    We have two ways to choose the start and end time of a movie:
    1.  User-specified values take precedence.
    2.  Absent a user preference, use the time bounds of the data.

    Use this function to compute that.

    Arguments:
        trajectories {iterable of Tracktable trajectories}: Trajectory data
            for movie
        user_start_time {datetime.datetime}: When the user wants the movie
            to start (can be None for 'don't care')
        user_end_time {datetime.datetime}: When the user wants the movie to
            end (can be None for 'don't care')

    Returns:
        (start_time, end_time), both as datetime.datetime objects

    Raises:
        ValueError: no trajectories and no user start/end time
    """

    start_time = None
    end_time = None
    for trajectory in trajectories:
        t_start = trajectory[0].timestamp
        t_end = trajectory[-1].timestamp
        if start_time is None or t_start < start_time:
            start_time = t_start
        if end_time is None or t_end > end_time:
            end_time = t_end

    # User preferences override the data
    if user_start_time is not None:
        start_time = user_start_time
    if user_end_time is not None:
        end_time = user_end_time

    return (start_time, end_time)

# --------------------------------------------------------------------


def extract_field_assignments(arg_dict):
    """Extract column->field assignments from arguments

    Field assignments are specified on the command line as arguments
    like '--real-field speed 12', meaning "take the contents
    of column 12 and add it to each point as a numeric field called
    speed".  This function iterates over the arguments and extracts
    all of those.

    Arguments:
        arg_dict {:obj:`dict`}: Command-line arguments to parse,
        specified as a :obj:`dict`.  To get a dictionary from the
        :obj:`Namespace` object returned by :code:`argparse.parse_args()`,
        call :code:`vars()` on the args object.

    Returns:
        Dictionary with three entries:
            'real': Dictionary mapping column names (strings) to
                    integer column IDs for real-valued fields
            'string': Dictionary mapping column names (strings) to
                    integer column IDs for string-valued fields
            'time': Dictionary mapping column names (strings) to
                    integer column IDs for timestamp-valued fields
    """

    return {
        'real': _extract_typed_field_assignments(arg_dict, 'real'),
        'string': _extract_typed_field_assignments(arg_dict, 'string'),
        'time': _extract_typed_field_assignments(arg_dict, 'time')
    }

# ----------------------------------------------------------------------


def initialize_canvas(resolution,
                      dpi=72,
                      facecolor='black'):
    """Set up Matplotlib canvas for rendering

    This function sets up a Matplotlib figure with specified resolution,
    DPI, and background/edge color.

    Since font sizes are specified in points, the combination of DPI and
    resolution determines how large a font will appear when text is
    rendered into the image.  One inch is 72 points, so a 12-point font
    will produce text where each line is (dpi / 6) pixels tall.

    Arguments:
        resolution {2 ints}: how large the images should be in pixels

    Keyword arguments:
        dpi {integer}: how many pixels per inch (pertains to text rendering).
            Defaults to 72.
        facecolor {string}: Default color for image background.  Can be
            specified as the name of a color ('black'), a float value for
            grays (0.75 == #B0B0B0), an RGBA tuple ((1, 0, 0, 1) is red),
            or an #RRGGBB string.  Defaults to 'black'.

    Returns:
        (figure, axes), where 'figure' is a Matplotlib figure and 'axes'
        are the default axes to render into.
    """

    figure_dimensions = compute_figure_dimensions(resolution, dpi)
    figure = pyplot.figure(figsize=figure_dimensions,
                           facecolor=facecolor)
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor=facecolor)
    axes.set_frame_on(False)

    return (figure, axes)

# ----------------------------------------------------------------------


def map_extent_as_bounding_box(axes, domain='terrestrial'):
    """Return a Tracktable bounding box for axes' drawable extent

    This is a convenience function to grab the bounding box for
    a set of Matplotlib axes and transform it to a Tracktable bounding
    box that can be used for intersection calculations.

    Note that this returns the extent of the drawable area itself without
    including the part of the canvas (if any) that containins decorations
    such as axis lines, ticks, and tick labels.

    Arguments:
        axes {Matplotlib axes}: Map for which you want the bounding box

    Keyword arguments:
        domain {string}: Coordinate domain for bounding box (default:
            'terrestrial')

    Returns:
        Tracktable bounding box from appropriate point domain

    Raises:
        KeyError: 'domain' must be one of 'cartesian2d' or 'terrestrial'
    """

    if domain not in ['terrestrial', 'cartesian2d']:
        raise KeyError(('map_extent_as_bounding_box: Domain must be '
                        'either "cartesian2d" or "terrestrial".  You '
                        'supplied "{}".').format(domain))

    # We use get_xlim() and get_ylim() instead of get_extent()
    # in order to get coordinates in data space instead of projected space.
    x_limits = axes.get_xlim()
    x_min = min(x_limits)
    x_max = max(x_limits)

    y_limits = axes.get_ylim()
    y_min = min(y_limits)
    y_max = max(y_limits)

    bbox_type = tracktable.domain.domain_class(domain, 'BoundingBox')

    return bbox_type((x_min, y_min), (x_max, y_max))

# ----------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description='Render a movie of traffic found in a delimited text file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("movie_rendering", parser)

    parser.add_argument('--trail-duration',
                        help=('How long should each object\'s trail last? '
                              '(seconds)'),
                        type=int,
                        default=300)

    parser.add_argument('point_data_file',
                        nargs=1,
                        help='Delimited text file containing point data')

    parser.add_argument('movie_file',
                        nargs=1,
                        help='Filename for trajectory movie')

    args = parser.parse_args()
    if args.resolution is None:
        args.resolution = [800, 600]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

# --------------------------------------------------------------------


def render_annotated_trajectories(trajectories,
                                  axes,
                                  color_map='plasma',
                                  decorate_head=False,
                                  head_size=2,
                                  head_color='white',
                                  linewidth_style='taper',
                                  linewidth=0.5,
                                  final_linewidth=0.01,
                                  scalar='progress',
                                  scalar_min=0,
                                  scalar_max=1,
                                  zorder=10):
    """Render decorated trajectories (with scalars) onto a map.

    Given a map instance and an iterable containing trajectories,
    draw the trajectories onto the map with the specified appearance
    parameters.  You can control the trajectory color, linewidth,
    z-order and whether or not a dot is drawn at the head of each
    path.

    The "annotated" part of render_annotated_trajectories refers to
    per-point scalar metadata on each trajectory.  For example, if your
    trajectories have a property "speed" at each point, you could render
    a movie where trajectories being displayed are color-coded by speed.
    If you supply the name of a property for the `scalar_property`
    argument, that property will be used along with `colormap` to determine
    color.  If you don't specify a property, trajectories will be colored
    so that traverse the entire colormap from start to finish.

    Arguments:
        axes {matplotlib Axes}: Axes to render into
        trajectories {iterable of Tracktable trajectories}: trajectories
            to render

    Keyword Arguments:
        color_map {name of colormap or :obj:`matplotlib.colors.Colormap`}:
            Trajectory scalars will be mapped to this color map.  (default:
            'plasma')
        decorate_head {boolean}: If true, a dot will be drawn at the current
            position of each object on the screen.  (default: False)
        head_size {float}: How large the dot should be for decorated
            trajectories, measured in points.  (default: 2)
        head_color {string or tuple}: What color the head dot should be for
            decorated trajectories.  Can be any Matplotlib color specification
            such as a color name, an '#RRGGBB' string, or a tuple of RGB or
            RGBA values.  The value 'scalar' means to use the scalar value
            at the head of the trajectory so that the dot is the same color
            as its trail.
        linewidth_style {string}: Either 'constant', in which case the lines
            for each trajectory will have constant width (see the `linewidth`
            parameter); or 'taper', in which case the line width will vary
            smoothly from `linewidth` at the object's current position to
            `final_linewidth` at the oldest end of the trail. (default:
            'taper')
        linewidth {float}: Width of trajectory trail subject to
            `linewidth_style`. (default: 0.5)
        final_linewidth {float}: Width of oldest end of trajectory trail.
            Only used when `linewidth_style` is 'taper'.
        scalar {string}: Real-valued property to be used to determine
            trajectory color.  You must make sure that this property is present
            at all points in the trajectory data.  The default 'progress'
            scalar is added automatically. (default: 'progress')
        scalar_min {float}: Bottom of range of scalar values that you care
            about. If your scalars are outside the range (0,1), you should set
            this.  Values below this will be treated as the minimum value.
            (default: 0)
        scalar_max {float}: Top of range of scalar values that you care about.
            If your scalars are outside the range (0,1), you should set this.
            Values above this will be treated as the maximum value.
            (default: 1)
        zorder {integer}: Z-order for drawn items.  Items with a higher
            Z-order will appear on top of items with a lower Z-order.  This is
            Matplotlib-specific. (default: 10)

    Returns:
        List of Matplotlib artists added to the figure.

    Raises:
        KeyError: The desired scalar is not present
        ValueError: linewidth_style is neither 'constant' nor 'taper'

    NOTE: A gallery of Matplotlib colormaps can be found at
          https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
    """

    if linewidth_style not in ['constant', 'taper']:
        raise ValueError(('Trajectory linewidth must be either "constant" or '
                          '"taper".  You supplied "{}".').format(
                          linewidth_style))
    if linewidth_style == 'taper':
        linewidths_for_trajectory = _make_tapered_linewidth_generator(
                                linewidth, final_linewidth)
    else:
        linewidths_for_trajectory = _make_constant_linewidth_generator(linewidth)

    if not decorate_head:
        head_size = 0
        head_color = 'white'

    logger = logging.getLogger(__name__)

    def scalars_for_trajectory(trajectory):
        result = [0] * len(trajectory)
        try:
            for (i, point) in enumerate(trajectory):
                value = point.properties[scalar]
                if value is not None:
                    result[i] = value
        except KeyError:
            logger.error(('One or more points in trajectory do not have '
                          'the scalar field "{}".').format(scalar))

        return result

    return paths.draw_traffic(axes,
                              trajectories,
                              color_map=color_map,
                              trajectory_scalar_generator=scalars_for_trajectory,
                              trajectory_linewidth_generator=linewidths_for_trajectory,
                              zorder=zorder,
                              color_scale=matplotlib.colors.Normalize(vmin=scalar_min, vmax=scalar_max),
                              dot_size=head_size,
                              dot_color=head_color)

# ---------------------------------------------------------------------


def render_trajectory_movie(movie_writer,
                            axes,
                            trajectories,
                            num_frames,
                            trail_duration,
                            figure=None,
                            dpi=100,
                            filename='movie.mp4',
                            start_time=None,
                            end_time=None,
                            savefig_kwargs=None,
                            trajectory_rendering_kwargs=None,
                            utc_offset=0,
                            timezone_label=None,
                            domain='terrestrial'):

    # Steps:
    # 1.  Cull trajectories that are entirely outside the map
    # 2.  Annotate trajectories with scalars needed for color
    # 3.  Compute frame duration
    # 4.  Add clock to map
    # 5.  Loop through frames
    #
    # I still need arguments to control whether the clock is included and,
    # if so, where and how it's rendered.
    logger = logging.getLogger(__name__)

    if savefig_kwargs is None:
        savefig_kwargs = dict()
    if trajectory_rendering_kwargs is None:
        trajectory_rendering_kwargs = dict()
    (movie_start_time, movie_end_time) = compute_movie_time_bounds(
        trajectories, start_time, end_time)

    map_bbox = map_extent_as_bounding_box(axes, domain=domain)

    # Cull out trajectories that do not overlap the map.  We do not
    # clip them (at least not now) since that would affect measures
    # like progress along the path.
    trajectories_on_map = list(trajectories_inside_box(trajectories, map_bbox))
    if len(trajectories_on_map) == 0:
        raise ValueError(
            ('No trajectories intersect the map bounding box '
             '(({} {}) - ({} {})).  Is the '
             'bounding box correct?').format(map_bbox.min_corner[0],
                                             map_bbox.min_corner[1],
                                             map_bbox.max_corner[0],
                                             map_bbox.max_corner[1]))

    logger.info('Movie covers time span from {} to {}'.format(
        movie_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        movie_end_time.strftime("%Y-%m-%d %H:%M:%S")))

    frame_duration = ((movie_end_time - movie_start_time) /
                      num_frames)
    first_frame_time = movie_start_time + trail_duration

    def frame_time(which_frame):
        return first_frame_time + which_frame * frame_duration

    if figure is None:
        figure = pyplot.gcf()

    with movie_writer.saving(figure, filename, dpi):
        for i in range(0, num_frames):
            current_time = frame_time(i)
            trail_start_time = frame_time(i) - trail_duration

            logger.info(
                ('Rendering frame {}: current_time {}, '
                 'trail_start_time {}').format(
                    i,
                    current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    trail_start_time.strftime("%Y-%m-%d %H:%M:%S")))

            frame_trajectories = clip_trajectories_to_interval(
                trajectories_on_map,
                start_time=trail_start_time,
                end_time=current_time
                )

            # TODO: Add in scalar accessor
            trajectory_artists = render_annotated_trajectories(
                frame_trajectories,
                axes,
                **trajectory_rendering_kwargs
                )

            # TODO: here we could also render the clock
            #
            movie_writer.grab_frame(**savefig_kwargs)

            # Clean up the figure for the next time around
            for artist in trajectory_artists:
                artist.remove()


# ----------------------------------------------------------------------


def setup_encoder(encoder='ffmpeg',
                  codec=None,
                  encoder_args=None,
                  movie_title='Tracktable Movie',
                  movie_artist='Tracktable Trajectory Toolkit',
                  movie_comment='',
                  fps=30,
                  **kwargs):
    """Instantiate and configure a video encoder

    Matplotlib supports video encoding with a writer interface that
    takes several arguments including which program to use to do
    the encoding and what parameters the encoder needs.  This
    function is a convenience interface to that.

    Keyword Arguments:
        encoder {string}: Name of encoder.  This must be one of the
            values in :code:`matplotlib.animation.writers.list`.
            Default: 'ffmpeg' (requires that you have FFmpeg installed
            on your system)
        codec {string}: Name of specific encoding algorithm to use.
            This is specific to the encoder you choose.  Default:
            None (whatever the encoder prefers)
        encoder_args {list of strings}: Any arguments you wish to
            provide to the encoder.  These are passed through
            to the underlying Matplotlib implementation as
            :code:`extra_args`.  TODO: get a reference to a
            documentation page in Matplotlib that explains what
            these do
        movie_title {string}: Title string to be embedded in the
            movie's metadata.  This is not rendered on screen.
            Default: "Tracktable Movie"
        movie_artist {string}: Movie creator to be embedded in the
            movie's metadata.  This is not rendered on screen.
            Default: "Tracktable Trajectory Toolkit"
        movie_comment {string}: Any other comments you want to
            embed in metadata.  Default: empty string
        fps {int}: Desired frames per second for the result.
            Default: 30

    Returns:
        Matplotlib animation object configured with supplied parameters

    Raises:
        KeyError: You have requested an encoder that is not available
            on this system
    """

    if encoder_args is None:
        encoder_args = list()

    if encoder not in matplotlib.animation.writers.list():
        raise KeyError((
            'Movie encoder {} is not available.  This system '
            'has the following encoders available: {}').format(
                encoder, matplotlib.animation.writers.list()))

    movie_metadata = {'title': movie_title,
                      'artist': movie_artist,
                      'comment': movie_comment}

    # The encoder args are passed to FFmpeg as if they were command-line
    # parameters.
    #
    # TODO: what do other encoders expect as encoder_args?
    if type(encoder_args) is str:
        encoder_args = shlex.split(encoder_args)

    writer = matplotlib.animation.writers[encoder](fps=fps,
                                                   codec=codec,
                                                   metadata=movie_metadata,
                                                   extra_args=encoder_args)

    return writer

# --------------------------------------------------------------------


def trajectories_from_point_file(infile,
                                 object_id_column=0,
                                 timestamp_column=1,
                                 coordinate0_column=2,
                                 coordinate1_column=3,
                                 string_fields=None,
                                 real_fields=None,
                                 time_fields=None,
                                 comment_character='#',
                                 field_delimiter=',',
                                 separation_distance=None,
                                 separation_time=None,
                                 minimum_length=2,
                                 domain='terrestrial'):
    """Load points from a file and assemble them into trajectories

    This function encapsulates the pipeline that loads points from a
    delimited text file, turns them into TrajectoryPoints, then
    assembles trajectories from those points.

    Note that timestamps must have the format "YYYY-mm-dd HH:MM:SS".
    For example, December 10, 2001 at 12:34:56 PM would be
    "2001-12-10 12:34:56".

    Arguments:
        infile {file-like object} -- Input source for points

    Keyword Arguments:
        object_id_column {integer} -- Column in file containing
            object ID (default: 0)
        timestamp_column {integer} -- Column in file containing
            timestamp (default: 1)
        coordinate0_column {integer} -- Column in file containing
            longitude or X coordinate (default: 2)
        coordinate1_column {integer} -- Column in file containing
            latitude or Y coordinate (default: 3)
        string_fields {dict} -- Mapping from field name to column
            number for columns containing string metadata (default: None)
        real_fields {dict} -- Mapping from field name to column
            number for columns containing numeric metadata (default: None)
        time_fields {dict} -- Mapping from field name to column number
            for columns containing timestamp metadata (default: None)
        comment_character {str} -- Lines in the input file that start
            with this character will be ignored (default: '#')
        field_delimiter {str} -- This character will be used as the
            separator between fields in a file (default: ',')
        domain {str} -- Point domain for data to be rendered.  Must be
            either 'terrestrial' or 'cartesian2d'.  (default: 'terrestrial')

    Returns:
        Iterable of trajectories.

    Raises:
        ValueError: comment character string or field delimiter string are
            not 1 character long, or domain is not 'terrestrial' or
            'cartesian2d'
    """

    if len(comment_character) != 1:
        raise ValueError(('trajectories_from_point_file: Comment character '
                          'string must be 1 character long.  You supplied'
                          '"{}".'.format(comment_character)))
    if len(field_delimiter) != 1:
        raise ValueError(('trajectories_from_point_file: Field delimiter '
                          'string must be 1 character long.  You supplied '
                          '"{}".').format(field_delimiter))
    if domain not in ['terrestrial', 'cartesian2d']:
        raise ValueError(('trajectories_from_point_file: Point domain must '
                          'be either "terrestrial" or "cartesian2d".  You '
                          'supplied "{}".').format(domain))

    point_source = trajectory_points_from_file(
                          infile,
                          object_id_column,
                          timestamp_column,
                          coordinate0_column,
                          coordinate1_column,
                          string_fields=string_fields,
                          real_fields=real_fields,
                          time_fields=time_fields,
                          comment_character=comment_character,
                          field_delimiter=field_delimiter,
                          domain=domain)

    trajectory_source = assemble_trajectories(
            point_source,
            separation_distance=separation_distance,
            separation_time=separation_time,
            minimum_length=minimum_length)

    return trajectory_source


# ---------------------------------------------------------------------


def trajectories_inside_box(trajectories, bounding_box):
    """Filter trajectories to include only those inside a bounding box

    We can speed up rendering quite a bit if we discard trajectories
    that do not intersect the image being rendered.  This function
    compares each trajectory against a user-supplied bounding box
    (presumably the bounds for the map) and returns only those trajectories
    that fall within the box.

    Arguments:
        trajectories {iterable of Tracktable trajectories}: Data
            to test against bounding box
        bounding_box {Tracktable bounding box}: box to test

    Returns:
        Iterable of trajectories that intersect the bounding box

    Raises:
        ValueError: bounding box must not be None
    """

    if bounding_box is None:
        raise ValueError(('trajectories_inside_box: Bounding box must '
                          'not be None.'))
    return (t for t in trajectories if geomath.intersects(t, bounding_box))


# --------------------------------------------------------------------


def trajectory_overlaps_interval(trajectory, start_time, end_time):
    """Does a trajectory overlap a time interval?

    For a trajectory to overlap a time interval, it cannot be the case
    that it begins after the interval ends or ends before the interval
    begins.

    Arguments:
        trajectory {Tracktable trajectory}: trajectory to test
        start_time {datetime.datetime}: Beginning of interval
        end_time {datetime.datetime}: End of interval

    Returns:
        Boolean: true if overlap, false if disjoint
    """
    return not (trajectory[0].timestamp > end_time or
                trajectory[-1].timestamp < start_time)

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
    domain_module = tracktable.domain.domain_module_from_name(domain)
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


def trajectory_time_bounds(trajectories):
    """Compute the collective start and end time of a set of trajectories

    Arguments:
        trajectories {iterable of Tracktable trajectories}: trajectories
            whose bounds you want

    Returns:
        Pair of Python datetimes.  The first element is the earliest
            timestamp in any of the trajectories.  The second element is
            the latest timestamp.

    Raises:
        ValueError: input sequence is empty
    """

    start_time = None
    end_time = None
    for t in trajectories:
        this_start_time = t[0].timestamp
        this_end_time = t[-1].timestamp
        if start_time is None:
            start_time = this_start_time
        else:
            start_time = min(this_start_time, start_time)
        if end_time is None:
            end_time = this_end_time
        else:
            this_end_time = min(this_end_time, end_time)

    if start_time is None:
        raise ValueError('trajectory_time_bounds: Input sequence is empty')
    else:
        return (start_time, end_time)

# ---------------------------------------------------------------------


def _make_tapered_linewidth_generator(initial_linewidth,
                                      final_linewidth):

    """Create a function that will make a tapered line width for a trajectory

    In order to render tapered trajectories whose lines get thinner as
    they get older, we need to generate a scalar array with as many
    components as the trajectory has segments.  The first entry in
    this array (corresponding to the OLDEST point) should have the
    value 'final_linewidth'.  The last entry (corresponding to the
    NEWEST point) should have the value 'initial_linewidth'.

    Args:
       initial_linewidth:  Width (in points) at the head of the trajectory
       final_linewidth:    Width (in points) at the tail of the trajectory

    Returns:
       A function that takes in a trajectory as an argument and
       returns an array of linewidths

    TODO: There might be an off-by-one error in here: we generate
    len(trajectory) scalars but the geometry has len(trajectory)-1
    segments.  Check to see if draw_traffic in paths.py corrects for
    this.
    """

    def linewidth_generator(trajectory):
        return numpy.linspace(final_linewidth, initial_linewidth, len(trajectory))

    return linewidth_generator

# ----------------------------------------------------------------------


def _make_constant_linewidth_generator(linewidth):

    """Create a function that will make a constant line width for a trajectory

    Args:
       linewidth:  Width (in points) along the trajectory

    Returns:
       A function that takes in a trajectory as an argument and
       returns an array of linewidths

    TODO: There might be an off-by-one error in here: we generate
    len(trajectory) scalars but the geometry has len(trajectory)-1
    segments.  Check to see if draw_traffic in paths.py corrects for
    this.
    """

    def linewidth_generator(trajectory):
        scalars = numpy.zeros(len(trajectory))
        scalars += float(linewidth)
        return scalars

    return linewidth_generator

# ----------------------------------------------------------------------


def _extract_typed_field_assignments(arguments,
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

    NOTE: Don't call this function directly unless you need the field
        assignments for one specific data type.  Instead, call
        `extract_field_assignments`.
    """

    if field_type not in ['string', 'real', 'time']:
        raise ValueError(('Field type ({}) must be one of "string", '
                          '"real", or "time".  Case matters').format(
                                field_type))

    arg_name = '{}_field_column'.format(field_type)
    field_assignments = dict()
    definition_list = arguments.get(arg_name, None)
    if definition_list is not None:
        if len(definition_list) > 0:
            for (field_name, column) in n_at_a_time(definition_list, 2):
                field_assignments[field_name] = int(column)

    return field_assignments

# --------------------------------------------------------------------


def main():
    logger = logging.getLogger(__name__)

    # Step 0: Parse the command line arguments and grab sets we will need
    # later.
    args = parse_args()
    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
#   Some of the keyword arguments for trajectory rendering have been renamed.
#   For now, we'll extract them by hand farther down in this function.
#    trajectory_rendering_kwargs = argument_groups.extract_arguments(
#                                    "trajectory_rendering", args)

    # Step 1: Load all the trajectories into memory.
    point_filename = args.point_data_file[0]
    field_assignments = extract_field_assignments(vars(args))

    with open(point_filename, 'r') as infile:
        logger.info('Loading points and building trajectories.')
        trajectories = list(
            trajectories_from_point_file(
                infile,
                object_id_column=args.object_id_column,
                timestamp_column=args.timestamp_column,
                coordinate0_column=args.coordinate0,
                coordinate1_column=args.coordinate1,
                string_fields=field_assignments['string'],
                real_fields=field_assignments['real'],
                time_fields=field_assignments['time'],
                comment_character=args.comment_character,
                field_delimiter=args.delimiter,
                separation_distance=args.separation_distance,
                separation_time=datetime.timedelta(minutes=args.separation_time),
                minimum_length=args.minimum_length,
                domain=args.domain)
            )
        # Add the 'progress' annotation to all of our trajectories so
        # we have some way to color them
        trajectories = [annotations.progress(t) for t in trajectories]

    # We can compute the bounding box for Cartesian data automatically.
    # We don't need to do so for terrestrial data because the map will
    # default to the whole world.
    if (args.domain == 'cartesian2d' and
            (args.map_bbox is None or
             len(args.map_bbox) == 0)):

        args.map_bbox = geomath.compute_bounding_box(
            itertools.chain(*trajectories)
            )

    #
    # Step 3: Set up the map.
    #
    # There are a lot of keyword arguments for the map -- see
    # tracktable.script_helpers.argument_groups.mapmaker --
    # so rather than pull them out individually like we did for
    # the point reader we extract the whole dict using
    # tracktable.script_helpers.argument_groups.extract_arguments().

    logger.info('Initializing map canvas for rendering.')
    (figure, axes) = initialize_canvas(args.resolution,
                                       args.dpi)
    (mymap, map_artists) = mapmaker.mapmaker(**mapmaker_kwargs)

    #
    # Step 4: Set up the video encoder.
    #
    #
    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
    movie_writer = setup_encoder(**movie_kwargs)

    # This set of arguments will be passed to the savefig() call that
    # grabs the latest movie frame.  This is the place to put things
    # like background color, tight layout and friends.
    savefig_kwargs = {'facecolor': figure.get_facecolor(),
                      'figsize': compute_figure_dimensions(args.resolution,
                                                           args.dpi),
                      'frameon': False}

    #
    # Lights! Camera! Action!
    #
    if args.trajectory_linewidth == 'taper':
        linewidth_style = 'taper'
        linewidth = args.trajectory_initial_linewidth
        final_linewidth = args.trajectory_final_linewidth
    else:
        linewidth_style = 'constant'
        linewidth = args.trajectory_linewidth
        final_linewidth = linewidth

    # Eventually we will be able to use argument_groups.extract_arguments() for
    # this, but right now it's broken.  Not all of the parameters in the
    # trajectory rendering argument group are supported and some of the names
    # have changed.
    #
    trajectory_rendering_kwargs = {
        'decorate_head': args.decorate_trajectory_head,
        'head_color': args.trajectory_head_color,
        'head_size': args.trajectory_head_dot_size,
        'color_map': args.trajectory_colormap,
        'scalar': args.trajectory_color,
        'scalar_min': args.scalar_min,
        'scalar_max': args.scalar_max,
        'linewidth_style': linewidth_style,
        'linewidth': linewidth,
        'final_linewidth': final_linewidth
    }

    render_trajectory_movie(
        movie_writer,
        axes=mymap,
        trajectories=trajectories,
        dpi=args.dpi,
        figure=figure,
        filename=args.movie_file[0],
        num_frames=movie_kwargs['fps'] * movie_kwargs['duration'],
        start_time=movie_kwargs['start_time'],
        end_time=movie_kwargs['end_time'],
        trail_duration=datetime.timedelta(seconds=args.trail_duration),
        savefig_kwargs=savefig_kwargs,
        trajectory_rendering_kwargs=trajectory_rendering_kwargs,
        domain=args.domain
    )

    pyplot.close()

    logger.info("Movie render complete. File saved to {}".format(args.movie_file[0]))

    return 0

# ----------------------------------------------------------------------


if __name__ == '__main__':
    sys.exit(main())
