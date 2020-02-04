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

import matplotlib
import matplotlib.animation

import datetime
import itertools
import logging
import shlex
import six
import sys

from tracktable.domain import domain_module_from_name
from tracktable.feature import annotations
from tracktable.filter.trajectory import ClipToTimeWindow as ClipTrajectoryToTimeWindow, FilterByBoundingBox as FilterTrajectoriesByBoundingBox
from tracktable.render import colormaps, mapmaker, paths
from tracktable.core import geomath
from tracktable.script_helpers import argument_groups, argparse
from tracktable.source.trajectory import AssembleTrajectoryFromPoints

matplotlib.use('Agg')
from matplotlib import pyplot  # noqa

# ----------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description='Render a movie of traffic found in a delimited text file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("movie_rendering", parser)

    parser.add_argument('--trail-duration',
                        help=("How long should each object's trail last? "
                              "(seconds)"),
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
        args.resolution = [ 800, 600 ]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args


# --------------------------------------------------------------------


def extract_field_assignments_from_arguments(arguments,
                                             field_type):
    """Helper function for configuring point reader

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

# ----------------------------------------------------------------------

def setup_video_encoder(encoder='ffmpeg',
                        codec=None,
                        encoder_args=list(),
                        movie_title='Tracktable Movie',
                        movie_artist='Tracktable Trajectory Toolkit',
                        movie_comment='',
                        fps=20,
                        **kwargs):
    """Set up a video encoder for movie rendering

    Matplotlib provides classes that allow us to write an animation to
    disk by saving one frame at a time.  This function configures one
    of those encoder back ends.

    Common back ends include 'pillow', 'ffmpeg', 'imagemagick', and
    'html' as of Matplotlib 3.  Your installation may vary.

    Keyword Arguments:
        encoder {str} -- Which Matplotlib video back-end to use.  Must
            be one of the values in matplotlib.animation.writers.list().
            (default: {'ffmpeg'})
        codec {str} -- Video encoding algorithm to use.  This is specific to
            the back end.  For FFmpeg, use the command 'ffmpeg -codecs'
            to get a list.  'h264' is a widely used choice.  (default:
            value of Matplotlib 'animation.codec' RC parameter)
        encoder_args {list of strings} -- Extra arguments to be passed to the
            underlying video encoder.  (default: empty list)
        movie_title {str} -- Title to be saved in the movie's metadata 
            (default: {'Tracktable Movie'})
        movie_artist {str} -- Author information to be saved in the movie's
            metadata (default: {'Tracktable Trajectory Toolkit'})
        movie_comment {str} -- Any comment you want to save in the movie's
            metadata (default: {''})
        fps {number} -- Desired frames per second for the movie (default: {20})

    Returns:
        matplotlib.animation.Animation object - sink for video frames

    Raises:
        KeyError: user requested an unavailable video encoder
    """
    if encoder not in matplotlib.animation.writers.list():
        raise KeyError(("Video encoder {} is not available.  This system "
                        "has the following encoders available: {}").format(
                            encoder, 
                            matplotlib.animation.writers.list()
                            ))

    movie_metadata = { 
        'title': movie_title,
        'artist': movie_artist,
        'comment': movie_comment 
        }

    encoder_args = maybe_split_string(encoder_args)

    writer = matplotlib.animation.writers[encoder](fps=fps,
                                                   codec=codec,
                                                   metadata=movie_metadata,
                                                   extra_args=encoder_args)
    return writer

# ----------------------------------------------------------------------


def maybe_split_string(maybe_string):
    """Split a string with shell-like quoting; leave lists alone

    Utility function for splitting up arguments to the video codec.
    If we get argumnts from the command line they are likely to
    come in as one long string and will probably have quotes in them.
    This function tries to split up strings using shell-style quoting
    but leaves lists alone.

    Arguments:
        maybe_string {sequence} -- String or list
    """

    if isinstance(maybe_string, six.text_type):
        return shlex.split(maybe_string)
    else:
        return maybe_string

# ----------------------------------------------------------------------


# ----------------------------------------------------------------------

def render_trajectory_movie(axes,
                            trajectories,
                            num_frames,
                            trail_duration,
                            first_frame=0,
                            num_frames_overall=None,
                            figure=None,
                            dpi=100,
                            filename='movie.mp4',
                            start_time=None,
                            end_time=None,
                            savefig_kwargs=dict(),
                            trajectory_rendering_args=dict(),
                            frame_batch_size=100,
                            batch_id='0'):

  # XXX YOU ARE HERE
  # 
    local_savefig_kwargs = dict(savefig_kwargs)
    local_trajectory_rendering_args = dict(trajectory_rendering_args)

    # Cull out trajectories that do not overlap the map.  We do not
    # clip them (at least not now) since that would affect measures
    # like progress along the path.
    try:
        map_bbox = map_projection.bbox
        trajectories_on_map = [ traj for traj in trajectories if geomath.intersects(traj, map_bbox) ]
    except AttributeError:
        print("INFO: Map does not contain a bbox attribute.  Trajectory culling will be skipped.")
        trajectories_on_map = list(trajectories)

    if len(trajectories_on_map) == 0:
        print("ERROR: No trajectories intersect the map bounding box ({}).  Is the bounding box set correctly?")
        return

    global ANNOTATED_TRAJECTORIES
    if not ANNOTATED_TRAJECTORIES:
        print("Annotating trajectories (should only happen once)")
        annotated_trajectories = list(annotate_trajectories(trajectories_on_map,
                                                            **local_trajectory_rendering_args))
        ANNOTATED_TRAJECTORIES = annotated_trajectories
    else:
        print("Re-using trajectory annotations")
        annotated_trajectories = ANNOTATED_TRAJECTORIES

    print("Annotated trajectories retrieved.")

    if local_trajectory_rendering_args['trajectory_color_type'] == 'static':
        local_trajectory_rendering_args['trajectory_colormap'] = example_trajectory_rendering.make_constant_colormap(local_trajectory_rendering_args['trajectory_color'])

    (data_start_time, data_end_time) = compute_trajectory_time_bounds(trajectories_on_map)
    if end_time is None:
        end_time = data_end_time
    else:
        end_time = Timestamp.from_any(end_time)
    if start_time is None:
        start_time = data_start_time
    else:
        start_time = Timestamp.from_any(start_time)

    print("INFO: Movie covers time span from {} to {}".format(
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S")))
    print("INFO: Data set covers time span from {} to {}".format(
        data_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        data_end_time.strftime("%Y-%m-%d %H:%M:%S")))

    if num_frames_overall is None:
        num_frames_overall = num_frames

        frame_duration_seconds = (end_time - start_time).total_seconds() / num_frames_overall
        frame_duration = datetime.timedelta(seconds=frame_duration_seconds)

    first_frame_time = start_time + trail_duration

    if (local_trajectory_rendering_args['trajectory_color_type'] == 'scalar' and
        local_trajectory_rendering_args.get('trajectory_color', None) is not None):
        scalar_accessor = annotations.retrieve_feature_accessor(local_trajectory_rendering_args['trajectory_color'])
    else:
        scalar_accessor = None

    # We've handled these args ourselves - don't pass them on
    del local_trajectory_rendering_args['trajectory_color_type']
    del local_trajectory_rendering_args['trajectory_color']

    if scalar_accessor is not None:
        local_trajectory_rendering_args['trajectory_scalar_accessor'] = scalar_accessor

    def frame_time(which_frame):
        return first_frame_time + which_frame * frame_duration


    def my_format_time(timestamp):
        minutes = timestamp.time().minute
        minutes = 15 * int(minutes / 15)
        local_timezone = SimpleTimeZone(hours=utc_offset)
        newtime = timestamp.replace(minute=minutes).astimezone(local_timezone)

        timestring = Timestamp.to_string(newtime, format_string='%Y-%m-%d\n%H:%M {}'.format(
            timezone_label), include_tz=False)

        return timestring



    ## TODO Add arguments to control this
    clock_artist = clock.digital_clock(frame_time(0),
                                       my_format_time,
                                       (0.95, 0.85),
                                       ha='right',
                                       va='baseline',
                                       color='white',
                                       size=18,
                                       backgroundcolor='black',
                                       zorder=20)[0]

    if figure is None:
        figure = pyplot.gcf()

    print("Rendering to {}".format(filename))
    current_trajectory_batch = None

    # Matplotlib's file animation writers save all of the frames for
    # the movie-in-progress to the current directory.  This is a bit
    # untidy; worse, it meanst hat multiple movies rendering in one
    # directory will stomp on one another's frames.  We use
    # frame_prefix to try to keep them apart.
    frame_prefix = "movie_chunk_{}".format(batch_id)
#    with movie_writer.saving(figure, filename, dpi, frame_prefix=frame_prefix):
    with movie_writer.saving(figure, filename, dpi):

        for i in range(first_frame, first_frame+num_frames):

            current_time = frame_time(i)
            trail_start_time = frame_time(i) - trail_duration

            print("Rendering frame {}: current_time {}, trail_start_time {}".format(
                i,
                current_time.strftime("%Y-%m-%d %H:%M:%S"),
                trail_start_time.strftime("%Y-%m-%d %H:%M:%S")))

            current_trajectory_batch = list(trajectories_on_map)

            frame_data = render_trajectories_for_frame(
                frame_time=current_time,
                trail_start_time=trail_start_time,
                trajectories=current_trajectory_batch,
                basemap=map_projection,
                axes=axes,
                render_args=local_trajectory_rendering_args,
                frame_number=i
                )

            clock_artist.set_text(my_format_time(current_time))

            next_filename = 'test_frame_{}.png'.format(i)
            movie_writer.grab_frame(**local_savefig_kwargs)
            cleanup_frame(frame_data)

            current_time += frame_duration
            trail_start_time += frame_duration

# -----------------------------------------------------------------------
def main():
    logger = logging.getLogger(__name__)
    args = parse_args()

    dpi = args.dpi
    image_resolution = args.resolution
    if image_resolution is None:
        image_resolution = [800, 600]
    figure_dimensions = [
        float(image_resolution[0]) / dpi,
        float(image_resolution[1]) / dpi
        ]

    # Step 1: set up a canvas in Matplotlib.
    logger.info('Initializing renderer.')
    figure = pyplot.figure(
        figsize=figure_dimensions,
        facecolor='black',
        edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    #
    # Step 2: Set up the input pipeline to load points and build trajectories.
    #
    point_filename = args.point_data_file[0]
    args_as_dict = vars(args)
    string_fields = extract_field_assignments_from_arguments(args_as_dict,
                                                             'string')
    real_fields = extract_field_assignments_from_arguments(args_as_dict,
                                                           'real')
    time_fields = extract_field_assignments_from_arguments(args_as_dict,
                                                           'time')

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

        # We need all of the trajectories in movie for each frame, so we might
        # as well read them now and get it over with.
        all_trajectories = list(trajectory_source)

    # We're done reading data at this point.

    # If the user is rendering Cartesian data and did not supply a bounding
    # box we will compute one ourselves.
    if args.domain == 'cartesian2d':
        if args.map_bbox is None or len(args.map_bbox) == 0:
            data_bbox = geomath.compute_bounding_box(
                itertools.chain(*all_trajectories)
                )
            args.map_bbox = [
                data_bbox.min_corner[0],
                data_bbox.max_corner[0],
                data_bbox.min_corner[1],
                data_bbox.max_corner[1]
                ]

    #
    # Step 3: Set up the map.
    #
    # There are a lot of keyword arguments for the map -- see
    # tracktable.script_helpers.argument_groups.mapmaker --
    # so rather than pull them out individually like we did for
    # the point reader we extract the whole dict using
    # tracktable.script_helpers.argument_groups.extract_arguments().
    #
    logger.info('Initializing map canvas.')
    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    (mymap, artists) = mapmaker.mapmaker(**mapmaker_kwargs)

    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
    movie_writer = setup_video_encoder(**movie_kwargs)

    # This set of arguments will be passed to the savefig() call that
    # grabs the latest movie frame.  This is the place to put things
    # like background color, tight layout and friends.
    savefig_kwargs = {
        'facecolor': figure.get_facecolor(),
        'figsize': figure_dimensions,
        'frameon': False
        }

    trajectory_kwargs = argument_groups.extract_arguments("trajectory_rendering", args)

    example_movie_rendering.render_trajectory_movie(
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

    print("Movie render complete. File saved to {}".format(args.movie_file[0]))

    return 0

# ----------------------------------------------------------------------


if __name__ == '__main__':
    sys.exit(main())
