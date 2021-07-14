#
# Copyright (c) 2014-2021 National Technology and Engineering
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

"""movie_from_points.py - Render a movie of trajectories

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""

import tracktable.domain

from tracktable.core import geomath
from tracktable.render import mapmaker, paths
from tracktable.script_helpers import argument_groups, argparse, n_at_a_time
from tracktable.analysis.assemble_trajectories import AssembleTrajectoryFromPoints

import datetime
import itertools
import logging
import numpy
import shlex

import cartopy
import cartopy.crs

import matplotlib
from matplotlib import pyplot
import matplotlib.animation
matplotlib.use('Agg')

try:
    from tqdm import tqdm
    tqdm_installed = True
except ImportError:
    tqdm_installed = False

def render_trajectory_movie(trajectories,
                            map_projection = cartopy.crs.PlateCarree(),
                            map_canvas = None,
                            trail_duration=datetime.timedelta(seconds=300),
                            figure=None,
                            dpi=100,
                            filename='movie.mp4',
                            start_time=None,
                            end_time=None,
                            utc_offset=0,
                            timezone_label=None,
                            domain='terrestrial',
                            map_bbox=[],
                            resolution=[800, 600],
                            encoder="ffmpeg",
                            duration=60,
                            fps=30,
                            codec=None,
                            encoder_args=None,
                            movie_title='Tracktable Movie',
                            movie_artist='Tracktable Trajectory Toolkit',
                            movie_comment='',
                            draw_lonlat=True,
                            fill_land=True,
                            fill_water=True,
                            draw_coastlines=True,
                            draw_countries=True,
                            draw_states=True,
                            tiles=None,
                            decorate_trajectory_head=False,
                            trajectory_head_color="white",
                            trajectory_head_dot_size=2,
                            trajectory_colormap="gist_heat",
                            trajectory_color="progress",
                            scalar_min=0,
                            scalar_max=1,
                            trajectory_linewidth=0.5,
                            trajectory_initial_linewidth=0.5,
                            trajectory_final_linewidth=0.01,
                            savefig_kwargs=None,
                            **kwargs):

    # Steps:
    # 1.  Cull trajectories that are entirely outside the map
    # 2.  Annotate trajectories with scalars needed for color
    # 3.  Compute frame duration
    # 4.  Add clock to map
    # 5.  Loop through frames
    #
    # TODO: I still need arguments to control whether the clock is included and, if so, where and how it's rendered.
    logger = logging.getLogger(__name__)

    #tiles override cartopy map features
    if tiles != None:
        fill_land=False
        fill_water=False
        draw_coastlines=False
        draw_countries=False
        draw_states=False

    num_frames = fps * duration

    # We can compute the bounding box for Cartesian data automatically.
    # We don't need to do so for terrestrial data because the map will
    # default to the whole world.
    if (domain == 'cartesian2d' and
        (map_bbox is None or len(map_bbox) == 0)):

        map_bbox = geomath.compute_bounding_box(
            itertools.chain(*trajectories)
            )

    # Set up the map.
    logger.info('Initializing map canvas for rendering.')
    (figure, axes) = initialize_canvas(resolution, dpi)
    if map_canvas == None:
        (map_canvas, map_actors) = mapmaker(domain='terrestrial',
                                            map_name='custom',
                                            map_bbox=map_bbox,
                                            map_projection=map_projection,
                                            draw_lonlat=draw_lonlat,
                                            draw_coastlines=draw_coastlines,
                                            draw_countries=draw_countries,
                                            draw_states=draw_states,
                                            fill_land=fill_land,
                                            fill_water=fill_water,
                                            tiles=tiles,
                                            **kwargs)

    # Set up the video encoder.
    movie_writer = setup_encoder(encoder=encoder,
                                codec=codec,
                                encoder_args=encoder_args,
                                movie_title=movie_title,
                                movie_artist=movie_artist,
                                movie_comment=movie_comment,
                                fps=fps,
                                **kwargs)

    #
    # Lights! Camera! Action!
    #
    if trajectory_linewidth == 'taper':
        linewidth_style = 'taper'
        linewidth = trajectory_initial_linewidth
        final_linewidth = trajectory_final_linewidth
    else:
        linewidth_style = 'constant'
        linewidth = trajectory_linewidth
        final_linewidth = linewidth


    # This set of arguments will be passed to the savefig() call that
    # grabs the latest movie frame.  This is the place to put things
    # like background color, tight layout and friends.
    if savefig_kwargs == None:
        savefig_kwargs = {'facecolor': figure.get_facecolor(), 'bbox_inches':'tight'}

    # Eventually we will be able to use argument_groups.extract_arguments() for
    # this, but right now it's broken.  Not all of the parameters in the
    # trajectory rendering argument group are supported and some of the names
    # have changed.
    #
    trajectory_rendering_kwargs = {
        'decorate_head': decorate_trajectory_head,
        'head_color': trajectory_head_color,
        'head_size': trajectory_head_dot_size,
        'color_map': trajectory_colormap,
        'scalar': trajectory_color,
        'scalar_min': scalar_min,
        'scalar_max': scalar_max,
        'linewidth_style': linewidth_style,
        'linewidth': linewidth,
        'final_linewidth': final_linewidth
    }

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
        if tqdm_installed:
            for i in tqdm(range(int(num_frames)), desc="Rendering Frames", unit='frame'):
                current_time = frame_time(i)
                trail_start_time = frame_time(i) - trail_duration

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
                movie_writer.grab_frame(**savefig_kwargs)

                # Clean up the figure for the next time around
                for artist in trajectory_artists:
                    artist.remove()
        else:
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
                movie_writer.grab_frame(**savefig_kwargs)

                # Clean up the figure for the next time around
                for artist in trajectory_artists:
                    artist.remove()


# ----------------------------------------------------------------------

def assemble_trajectories(point_source,
                          separation_distance=1000,
                          separation_time=datetime.timedelta(hours=24),
                          minimum_length=2):
    """Assemble a sequence of points into trajectories

    This function will instantiate and configure a `tracktable.analysis.
    assemble_trajectories.AssembleTrajectoryFromPoints` to convert a sequence
    of points into a sequence of trajectories.

    You must specify an iterable of points.  You can also specify
    parameters that determine when a series of points with the
    same object ID will be cut into separate trajectories and the
    minimum number of points a trajectory must have in order to
    be worthy of consideration.

    Note:
        This function does not actually build the trajectories.  It
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
        resolution (2 ints): how large the images should be in pixels

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

    Note:
        A gallery of Matplotlib colormaps can be found at
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
                              dot_color=head_color,
                              transform=cartopy.crs.PlateCarree())

# ---------------------------------------------------------------------


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
    """

    def linewidth_generator(trajectory):
        scalars = numpy.zeros(len(trajectory))
        scalars += float(linewidth)
        return scalars

    return linewidth_generator

# ----------------------------------------------------------------------

