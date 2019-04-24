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


"""example_trajectory_rendering - Arguments and code for drawing trajectories

Once we have a set of trajectories in memory we can make decisions
about how they should look on screen.  That includes...

* How should the line segments in the trajectory be colored?

* What should the line width for each segment be?

* Should there be a dot at the head of the trajectory?  What size and
  color?

* What layer (Z-order) should the trajectories live in?

The convenience methods in this file will render a single group of
trajectories.  You can render several groups by instantiating several
of them.
"""

from __future__ import division, absolute_import, print_function

import matplotlib
matplotlib.use('Agg')

import matplotlib.animation
from matplotlib import pyplot

import csv
import datetime
import multiprocessing
import numpy
import os.path
import shlex
import subprocess
import sys
import tempfile

import example_point_reader
import example_trajectory_builder
import example_trajectory_rendering
import example_movie_rendering


from tracktable.feature               import annotations
from tracktable.filter.trajectory     import ClipToTimeWindow as ClipTrajectoryToTimeWindow, FilterByBoundingBox as FilterTrajectoriesByBoundingBox
from tracktable.render                import colormaps, mapmaker, paths
from tracktable.core                  import geomath, Timestamp
from tracktable.script_helpers        import argument_groups, argparse

CHUNK_RENDERER = None

class MovieChunkRenderer(object):
    """Render a single batch of frames for a movie.

    We parallelize movie rendering by chopping the movie up into small
    batches of frames, placing those batches into a queue and then
    allowing one or more render processes to perform tasks from that
    queue.  This allows us to trade off the need for load balancing
    (so that all worker processes stay busy) with the overhead of
    encoding a movie stream.

    This class encapsulates all the information we need to go out and
    render a single batch.  Our intent is to make this process
    thread-safe although it may be some time before an implementation
    using threads instead of processes is efficient.

    \note This API is going to get cleaned up a lot as I refactor
          movie-making to support different types of movies (heatmap
          especially).

    Attributes:
      basemap (mpl_toolkits.basemap.Basemap): Map instance to render into
      trajectories (list): Reusable sequence of Trajectory objects
      trail_duration (int): Length of trail to draw behind moving objects (seconds)
      figure (matplotlib.Figure): Top-level image container
      dpi (int): Dots per inch to use when rendering text into figure
      savefig_kwargs (dict): Any extra arguments to pass to Matplotlib's savefig() such as border size or tight_layout parameters
      trajectory_rendering_kwargs (dict): Any extra arguments to pass to the trajectory renderer such as linewidth, annotation functions or z-order
      axes (matplotlib.axes.Axes): Axes to which actors will be added
      fps (integer): Frames per second for movie
      all_args (argparse.Namespace): All arguments from command line
      temp_directory (path): Destination for encoded frame batches
      start_time (datetime):  Data before this time will not be in the movie
      end_time (datetime): Data after this time will not be in the movie
      movie_kwargs (dict): Extra arguments (such as metadata) to pass to movie encoding
      num_frames_overall (integer): Number of frames in entire movie, not just each chunk
      utc_offset (integer): Argument to pass to clock rendered on map
      timezone_label (string): Text annotation to be added to clock
    """

    def __init__(self):
        """Instantiate an unconfigured chunk renderer."""

        self.basemap = None
        self.trajectories = None
        self.trail_duration = None
        self.figure = None
        self.dpi = None
        self.savefig_kwargs = None
        self.trajectory_rendering_kwargs = None
        self.axes = None
        self.fps = None
        self.all_args = None
        self.temp_directory = None
        self.start_time = None
        self.end_time = None
        self.movie_kwargs = None
        self.num_frames_overall=None
        self.utc_offset = 0
        self.timezone_label = ""

    def render_frame_batch(self, batch_info):
        """Render a single group of frames.

        In order to preserve maximum image quality, we encode each
        movie chunk with FFMPEG's 'ffv1' lossless codec.  We will
        maintain lossless encoding until right at the end when we
        encode the final movie with the user's desired compression
        parameters.

        Args:
          batch_info (list): Group of ( numeric_id, start_frame_number, num_frames, temp_directory )

        Returns:
          Filename (with path) for encoded movie fragment
        """

        batch_id = batch_info[0]
        start_frame = batch_info[1]
        num_frames = batch_info[2]
        self.temp_directory = batch_info[3]

        chunk_writer = example_movie_rendering.setup_encoder(encoder='ffmpeg',
                                                             codec='ffv1',
                                                             fps=self.fps)
        chunk_filename = os.path.join(self.temp_directory, 'movie_chunk_{}.mkv'.format(batch_id))

        # hand off to the movie renderer to draw them
        example_movie_rendering.render_trajectory_movie(chunk_writer,
                                                        self.basemap,
                                                        self.trajectories,
                                                        first_frame=start_frame,
                                                        num_frames=num_frames,
                                                        num_frames_overall=self.num_frames_overall,
                                                        trail_duration=self.trail_duration,
                                                        figure=self.figure,
                                                        dpi=self.dpi,
                                                        filename=chunk_filename,
                                                        start_time=self.start_time,
                                                        end_time=self.end_time,
                                                        savefig_kwargs=self.savefig_kwargs,
                                                        trajectory_rendering_args=self.trajectory_rendering_kwargs,
                                                        frame_batch_size=100,
                                                        axes=self.axes,
                                                        utc_offset=self.utc_offset,
                                                        timezone_label=self.timezone_label,
                                                        batch_id=batch_id)
        return chunk_filename


# ----------------------------------------------------------------------

def parse_args():
    """Set up an argparse instance for parallel movie rendering.

    This function will appear in just about every non-trivial script
    that uses Tracktable.  The argparse module makes it much easier
    to handle command-line arguments than if we had to parse the
    entire command line ourselves.
    """

    parser = argparse.ArgumentParser(description='Render a movie of traffic found in a delimited text file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("movie_rendering", parser)
    argument_groups.use_argument_group("parallel", parser)


    parser.add_argument('--trail-duration',
                        help="How long should each object's trail last? (seconds)",
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




# ----------------------------------------------------------------------

def setup_matplotlib_figure(args, renderer):
    """Instantiate and configure a Matplotlib figure.

    This sets up high-level properties of the rendered figure such as
    its resolution, DPI and background color.

    Args:
      args (argparse.Namespace): Arguments parsed from command line
      renderer (MovieChunkRenderer): Object that will manage the rendering process

    Side Effects:
      Pointers to the figure and axes as well as the image resolution,
      DPI and arguments for saving images will be stored in the
      renderer.
    """


    # Set up the matplotlib figure
    dpi = args.dpi
    image_resolution = args.resolution
    if image_resolution is None:
        image_resolution = [ 800, 600 ]
    figure_dimensions = [ float(image_resolution[0]) / dpi, float(image_resolution[1]) / dpi ]
    figure = pyplot.figure(figsize=figure_dimensions, facecolor='black', edgecolor='black')

    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    renderer.dpi = dpi
    renderer.figure = figure
    renderer.axes = axes
    renderer.savefig_kwargs = { 'facecolor': figure.get_facecolor(),
                                'figsize': figure_dimensions,
                                'frameon': False }


# ----------------------------------------------------------------------

def setup_basemap(args, renderer):
    """Call Mapmaker to set up our map projection.

    Args:
      args (argparse.Namespace): Arguments parsed from command line
      renderer (MovieChunkRenderer): Render manager

    Side Effects:
      A pointer to the Basemap instance will be saved in the renderer.

    Known Bugs:
      The list of artists that are added to the map as decorations is
      being ignored.
    """

    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    (mymap, base_artists) = mapmaker.terrestrial_map(**mapmaker_kwargs)
    renderer.basemap = mymap

# ----------------------------------------------------------------------

def setup_point_source(filename, args):
    """Instantiate and configure a point reader.

    This function will set up a pipeline to read points from a text
    file with a DelimitedTextPointReader including the underlying
    Python CSV reader and the field map that tells the reader how to
    populate each point.

    Args:
      filename (string): Filename for point data
      args (argparse.Namespace): Arguments parsed from command line

    Yields:
      TrajectoryPoint objects
    """

    config_reader = example_point_reader.configure_point_reader
    field_map = {}
    for column_name in [ 'object_id',
                         'timestamp',
                         'longitude',
                         'latitude',
                         'altitude',
                         'speed',
                         'heading' ]:

        field_name_in_args = '{}_column'.format(column_name)
        if hasattr(args, field_name_in_args):
            field_map[column_name] = getattr(args, field_name_in_args)

    infile = open(filename, 'rb')
    point_source = config_reader(infile,
                                 delimiter=args.delimiter,
                                 comment_character=args.comment_character,
                                 field_map=field_map)

    return point_source.points()


# ----------------------------------------------------------------------

def setup_trajectory_source(point_source, args):
    """Set up pipeline to assemble points into trajectories

    Before you call this function you must have an iterable of
    TrajectoryPoint objects.  We will configure an
    AssembleTrajectoriesFromPoints source and return a generator for its results.
    its results.

    Args:
      point_source (iterable): Sequence of TrajectoryPoint objects
      args (argparse.Namespace): Arguments parsed from command line

    Yields:
      Trajectory objects
    """

    args = argument_groups.extract_arguments("trajectory_assembly", args)

    source = example_trajectory_builder.configure_trajectory_builder(**args)
    source.input = point_source

    return source.trajectories()


# ----------------------------------------------------------------------

def collect_trajectories(args):
    """Load all trajectories from disk into a list.

    This function sets up and runs the input pipeline: load points
    from disk, assemble them into trajectories, collect those
    trajectories into a list and return them to the user.

    \note All trajectories that are not discarded as too short will be
    in memory after this function returns.  We load everything so that
    we can re-use the data on successive batches of frames instead of
    having to re-load from scratch.

    Args:
      args (argparse.Namespace): Arguments parsed from command line

    Returns:
      List of Trajectory objects.
    """

    print("STATUS: Initializing point source")
    filename = os.path.expanduser(os.path.expandvars(args.point_data_file[0]))
    point_source = setup_point_source(filename, args)

    print("STATUS: Initializing trajectory source")
    trajectory_source = setup_trajectory_source(point_source, args)

    print("STATUS: Collecting all trajectories")
    all_trajectories = list(trajectory_source)

    return all_trajectories

# ----------------------------------------------------------------------

def setup_chunk_renderer(args):
    """Instantiate and configure the render manager

    This function sets up a MovieChunkRenderer so that it's all ready
    to start processing batches of frames.  This includes setting up
    Matplotlib and Basemap, loading trajectory data from disk and
    storing information in the renderer that does not change between
    frames.

    Args:
      args (argparse.Namespace): All arguments parsed from command line

    Side Effects:
      The renderer is stored in the global variable CHUNK_RENDERER.

    Known Bugs:
      Global variables are not thread-safe.
    """

    renderer = MovieChunkRenderer()
    global CHUNK_RENDERER
    CHUNK_RENDERER = renderer

    renderer.all_args = args
    setup_matplotlib_figure(args, CHUNK_RENDERER)
    setup_basemap(args, CHUNK_RENDERER)

    all_trajectories = collect_trajectories(args)
    renderer.trajectories = all_trajectories

    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
    trajectory_kwargs = argument_groups.extract_arguments("trajectory_rendering", args)

    renderer.trajectory_rendering_kwargs = trajectory_kwargs
    renderer.movie_kwargs = movie_kwargs
    renderer.trail_duration = datetime.timedelta(seconds=args.trail_duration)
    renderer.start_time = args.start_time
    renderer.end_time = args.end_time
    renderer.fps = args.fps
    renderer.num_frames_overall = renderer.fps * args.duration
    if renderer.utc_offset:
        renderer.utc_offset = int(args.utc_offset)
    if args.timezone_label:
        renderer.timezone_label = args.timezone_label

# ----------------------------------------------------------------------

def setup_chunk_encoder(encoder='ffmpeg',
                        fps=20,
                        **kwargs):

    """Set up an encoder for a chunk of the overall movie.

    Args:
       encoder (string): one of the encoders supported by the current Matplotlib install
       codec (string): Which video codec to use to encode chunks
       fps (int): frames per second for the encoder
       kwargs (dict): any other argument_groups

    Returns:
       Matplotlib movie writer
    """

    if encoder not in matplotlib.animation.writers.list():
        raise KeyError("Movie encoder {} is not available.  This system has the following encoders available: {}".format(encoder, matplotlib.animation.writers.list()))

#    encoder_args = [ '-c:v', 'mpeg4' ]

    writer = matplotlib.animation.writers[encoder]( fps=fps, metadata={'title': 'Foo!'}, extra_args=[ '-v', 'verbose' ] )

    return writer


# ----------------------------------------------------------------------

def render_frame_batch(batch):
    """Worker function to hand off a frame batch to the renderer.

    This is a convenient wrapper that lets us use
    multiprocessing.map_async() to process frame batches.

    Args:
      batch (list): Frame batch information for renderer

    Returns:
      Whatever comes back from the batch renderer (generally a filename)
    """

    global CHUNK_RENDERER
    return CHUNK_RENDERER.render_frame_batch(batch)

# ----------------------------------------------------------------------

def concatenate_movie_chunks(chunk_filenames, tmpdir):
    """Assemble individual movie chunks into a single movie

    In addition to encoding, decoding and multiplexing media streams,
    FFMPEG has a convenient mode called "concat" that will append one
    bitstream to another without re-encoding.  We take advantage of
    that to assemble the frame batches into a single movie.

    Args:
      chunk_filenames (list): Filenames of movie batches.  These batches must be in order.
      tmpdir (string): Path to directory where raw footage should be stored.

    Side Effects:
      * Individual frame batches will be concatenated into a movie
        called 'assembled.mkv' in the temporary directory.
      * Frame batches will be removed after concatenation.
      * A temporary file 'concat_recipe' will be created when this function is called and removed after encoding is complete.
    """

    recipe_filename = os.path.join(tmpdir, 'concat_recipe.txt')
    with open(recipe_filename, 'wb') as outfile:
        for chunk_filename in chunk_filenames:
            outfile.write("file '{}'\n".format(chunk_filename))

    ffmpeg_args = [ 'ffmpeg',
                    '-f', 'concat',
                    '-i', recipe_filename,
                    '-c', 'copy',
                    os.path.join(tmpdir, 'assembled.mkv') ]

    subprocess.check_call(ffmpeg_args)
    os.remove(recipe_filename)

# ----------------------------------------------------------------------

def encode_final_movie(output_filename, tmpdir, args):
    """Re-encode the finished movie to user specifications.

    We generate the movie originally using a lossless encoding.  This
    results in a very large file.  Typically the user will want it in
    a different format that's easier to move around.  This function
    does that with a call to ffmpeg.

    Args:
      output_filename (string): User-specified filename for the finished movie
      tmpdir (string): Path to work directory
      args (argparse.Namespace): All arguments parsed from command line

    Side Effects:
      Movie will be transcoded from its intermediate format and written to the output file.
    """

    movie_kwargs = argument_groups.extract_arguments('movie_rendering', args)
    if movie_kwargs.get('encoder_args', None) is not None:
        encoder_args = shlex.split(movie_kwargs['encoder_args'])
    else:
        encoder_args = [ "-c",  "copy" ]

#    print("DEBUG: encode_final_movie: Extra encoder args are {}".format(encoder_args))

    # Now we re-encode the assembled movie to whatever specs the user wanted
    ffmpeg_args = [ 'ffmpeg',
                    '-i', os.path.join(tmpdir, 'assembled.mkv') ]
    ffmpeg_args += encoder_args
    ffmpeg_args += [ os.path.abspath(output_filename) ]

#    print("DEBUG: ffmpeg args for final encode: {}".format(ffmpeg_args))

    subprocess.check_call(ffmpeg_args)

# ----------------------------------------------------------------------

def remove_movie_chunks(tmpdir, filenames):
    """Clean up intermediate movies.

    Remove the individual movie chunks as well as the assembled raw
    footage.

    Args:
      tmpdir (string): Path to work directory
      filenames (list): List of filenames for intermediate footage
    """

    for filename in filenames:
        os.remove(filename)
    os.remove(os.path.join(tmpdir, 'assembled.mkv'))

# ----------------------------------------------------------------------

def remove_tmpdir(pathname):
    """Remove the temporary work directory.

    Args:
      pathname (string): Directory to remove
    """
    os.rmdir(pathname)

# ----------------------------------------------------------------------

def main():
    """Make a trajectory movie using several processes in parallel.

    We do very little actual work here: we ask for the command line
    arguments, compute the bounds for the frame batches and set up
    multiprocessing.  Apart from that everything happens in the other
    functions in this file.
    """

    args = parse_args()

    print("utc_offset: {} timezone_label: {}".format(args.utc_offset, args.timezone_label))

    total_frame_count = int(args.fps) * int(args.duration)
    frame_batch_size = 20

    tmpdir = tempfile.mkdtemp(prefix='movie_parts')
    start_frame = 0
    batch_id = 0
    frame_batches = []
    while start_frame < total_frame_count:
        last_frame = min(total_frame_count, start_frame + frame_batch_size)
        num_frames = (last_frame - start_frame) + 1
        frame_batches.append(( batch_id,
                               start_frame,
                               num_frames,
                               tmpdir ))
        start_frame += frame_batch_size
        batch_id += 1


    if args.processors == 0:
        processors = None
    else:
        processors = args.processors

    pool = multiprocessing.Pool(processes=processors,
                                initializer=setup_chunk_renderer,
                                initargs=[ args ])
    result = pool.map_async(render_frame_batch, frame_batches)
    chunk_result = result.get()

    print("STATUS: Combining movie parts into raw footage file")
    concatenate_movie_chunks(chunk_result, tmpdir)
    print("STATUS: Encoding raw footage file to final movie")
    movie_filename = os.path.expanduser(os.path.expandvars(args.movie_file[0]))
    encode_final_movie(movie_filename, tmpdir, args)
    print("STATUS: Cleaning up temporary files")
    remove_movie_chunks(tmpdir, chunk_result)
    remove_tmpdir(tmpdir)

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
