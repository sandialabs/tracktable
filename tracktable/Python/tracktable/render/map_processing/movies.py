#
# Copyright (c) 2014-2023 National Technology and Engineering
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

"""movie_processing.py - Functions for supporting rendering a movie

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""

import logging
import shlex

import cartopy
import cartopy.crs
import matplotlib
import matplotlib.animation
import numpy
import tracktable.domain
from matplotlib import pyplot
from tracktable.core import geomath
from tracktable.render.map_processing import paths

matplotlib.use('Agg')

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

        Args::
            axes (matplotlib Axes): Axes to render into
            trajectories (iterable of Tracktable trajectories): trajectories to render

        Keyword Arguments:
            color_map (name of colormap or :obj:`matplotlib.colors.Colormap`): Trajectory scalars will be mapped to this color map.  (default: 'plasma')
            decorate_head (boolean): If true, a dot will be drawn at the current position of each object on the screen.  (default: False)
            head_size (float): How large the dot should be for decorated trajectories, measured in points.  (default: 2)
            head_color (string or tuple): What color the head dot should be for
                decorated trajectories.  Can be any Matplotlib color specification
                such as a color name, an '#RRGGBB' string, or a tuple of RGB or
                RGBA values.  The value 'scalar' means to use the scalar value
                at the head of the trajectory so that the dot is the same color
                as its trail.
            linewidth_style (string): Either 'constant', in which case the lines
                for each trajectory will have constant width (see the `linewidth`
                parameter); or 'taper', in which case the line width will vary
                smoothly from `linewidth` at the object's current position to
                `final_linewidth` at the oldest end of the trail. (default:
                'taper')
            linewidth (float): Width of trajectory trail subject to `linewidth_style`. (default: 0.5)
            final_linewidth (float): Width of oldest end of trajectory trail. Only used when `linewidth_style` is 'taper'.
            scalar (string): Real-valued property to be used to determine
                trajectory color.  You must make sure that this property is present
                at all points in the trajectory data.  The default 'progress'
                scalar is added automatically. (default: 'progress')
            scalar_min (float): Bottom of range of scalar values that you care
                about. If your scalars are outside the range (0,1), you should set
                this.  Values below this will be treated as the minimum value.
                (default: 0)
            scalar_max (float): Top of range of scalar values that you care about.
                If your scalars are outside the range (0,1), you should set this.
                Values above this will be treated as the maximum value.
                (default: 1)
            zorder (integer): Z-order for drawn items.  Items with a higher
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
        encoder (string): Name of encoder.  This must be one of the
            values in :code:`matplotlib.animation.writers.list`.
            Default: 'ffmpeg' (requires that you have FFmpeg installed
            on your system)
        codec (string): Name of specific encoding algorithm to use.
            This is specific to the encoder you choose.  Default:
            None (whatever the encoder prefers)
        encoder_args (list of strings): Any arguments you wish to
            provide to the encoder.  These are passed through
            to the underlying Matplotlib implementation as
            :code:`extra_args`.  More information about the
            encoder args can be found here:
            https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FFMpegWriter.html#matplotlib-animation-ffmpegwriter
        movie_title (string): Title string to be embedded in the
            movie's metadata.  This is not rendered on screen.
            Default: "Tracktable Movie"
        movie_artist (string): Movie creator to be embedded in the
            movie's metadata.  This is not rendered on screen.
            Default: "Tracktable Trajectory Toolkit"
        movie_comment (string): Any other comments you want to
            embed in metadata.  Default: empty string
        fps (int): Desired frames per second for the result.
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
