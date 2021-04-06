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

"""movie_from_csv.py - Example of how to render a movie of a bunch of trajectories from a .traj file
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.animation
from matplotlib import pyplot

import csv
import datetime
import numpy
import os
import shlex
import sys

#import example_point_reader
#mport example_trajectory_builder
#import example_trajectory_rendering
#import example_movie_rendering

from tracktable.feature               import annotations
from tracktable.filter.trajectory     import ClipToTimeWindow as ClipTrajectoryToTimeWindow, FilterByBoundingBox as FilterTrajectoriesByBoundingBox
from tracktable.render                import colormaps, mapmaker, paths
from tracktable.core                  import geomath
from tracktable.script_helpers        import argument_groups, argparse

# ----------------------------------------------------------------------

# Note: There is more work to do here to expose options for the
# linewidths, line colors, Z-order and background color for the map.
# That work will happen once we get this script up and running in the
# first place.

def parse_args():
    parser = argparse.ArgumentParser(description='Render a movie of traffic found in a delimited text file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("movie_rendering", parser)

    parser.add_argument('--trail-duration',
                        help="How long should each object's trail last? (seconds)",
                        type=int,
                        default=300)

    parser.add_argument('trajectory_data_file',
                        nargs=1,
                        help='Delimited text file containing trajectory data')

    parser.add_argument('movie_file',
                        nargs=1,
                        help='Filename for trajectory movie')


    args = parser.parse_args()
    if args.resolution is None:
        args.resolution = [ 800, 600 ]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

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

def setup_trajectory_source(filename, args):
    if args.domain == 'terrestrial':
        from tracktable.domain.terrestrial import TrajectoryReader
    else:
        from tracktable.domain.cartesian2d import TrajectoryReader

    infile = open(filename, 'rb')
    return TrajectoryReader(infile)


# ----------------------------------------------------------------------

def main():
    args = parse_args()

    dpi = args.dpi
    image_resolution = args.resolution
    if image_resolution is None:
        image_resolution = [ 800, 600 ]
    figure_dimensions = [ float(image_resolution[0]) / dpi, float(image_resolution[1]) / dpi ]


    print("STATUS: Initializing canvas")
    figure = pyplot.figure(figsize=figure_dimensions, facecolor='black', edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    print("STATUS: Initializing trajectory source")
    trajectory_source = setup_trajectory_source(args.trajectory_data_file[0], args)

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
    data_bbox = None
    if args.domain == 'cartesian2d' and args.map_bbox is None:
        print("STATUS: Collecting points to compute bounding box")
        all_points = itertools.chain(list(trajectory_source))
        data_bbox = geomath.compute_bounding_box(all_points)
        point_source = all_points

    print("STATUS: Initializing map projection")
    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    (mymap, base_artists) = mapmaker.mapmaker(computed_bbox=data_bbox, **mapmaker_kwargs)

    print("STATUS: Collecting all trajectories")
    all_trajectories = list(trajectory_source)

    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
    movie_writer = setup_encoder(**movie_kwargs)

    # This set of arguments will be passed to the savefig() call that
    # grabs the latest movie frame.  This is the place to put things
    # like background color, tight layout and friends.
    savefig_kwargs = { 'facecolor': figure.get_facecolor() }

    trajectory_kwargs = argument_groups.extract_arguments("trajectory_rendering", args)

    render_trajectory_movie(
        movie_writer,
        map_projection=mymap,
        trajectories=all_trajectories,
        dpi=args.dpi,
        figure=figure,
        filename=args.movie_file[0],
        num_frames=movie_kwargs['fps'] * movie_kwargs['duration'],
        start_time=movie_kwargs['start_time'],
        end_time=movie_kwargs['end_time'],
        trail_duration = datetime.timedelta(seconds=args.trail_duration),
        savefig_kwargs=savefig_kwargs,
        axes=axes,
        trajectory_rendering_args=trajectory_kwargs
    )

    pyplot.close()

    logger.info("Movie render complete. File saved to {}".format(args.movie_file[0]))

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
