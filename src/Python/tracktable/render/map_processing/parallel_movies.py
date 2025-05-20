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

"""movie_processing.py - Functions for supporting rendering a parallel movie

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""

import logging
import os
import shlex
import subprocess

import matplotlib
import matplotlib.animation
from tracktable.render.map_processing import movies

matplotlib.use('Agg')

logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
    tqdm_installed = True
except ImportError:
    tqdm_installed = False

BATCH_RENDERER = None

# ---------------------------------------------------------------------

class BatchMovieRenderer(object):
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

    Note: This API is going to get cleaned up a lot as I refactor
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

        # Common Args
        self.trajectories = None
        self.trail_duration = None

        # Mapmaker Args
        self.domain = None
        self.map_canvas = None
        self.figure = None

        # Movie Args
        self.savefig_kwargs = None
        self.dpi = None
        self.axes = None
        self.fps = None
        self.temp_directory = None
        self.utc_offset = 0
        self.timezone_label = ""
        self.frame_duration = None
        self.first_frame_time = None
        self.codec = "ffv1"
        self.encoder = "ffmpeg"

        # Trajectory Rendering Args
        self.color_map = None
        self.decorate_head = None
        self.head_size = None
        self.head_color = None
        self.linewidth_style = None
        self.linewidth = None
        self.final_linewidth = None
        self.scalar = None
        self.scalar_min = None
        self.scalar_max = None
        self.zorder = None

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

        # TODO (mjfadem): Do we need to pass the movie title, artist and comment here?
        batch_writer = movies.setup_encoder(encoder=self.encoder,codec=self.codec,fps=self.fps)
        batch_filename = os.path.join(self.temp_directory, 'movie_chunk_{}.mkv'.format(batch_id))

        # Hand off to the parallel movie renderer to actually draw the trajectories
        parallel_movie_rendering(self.trajectories,

                                # Mapmaker kwargs
                                map_canvas=self.map_canvas,

                                # Trajectory Rendering kwargs
                                color_map = self.color_map,
                                decorate_head = self.decorate_head,
                                head_size = self.head_size,
                                head_color = self.head_color,
                                linewidth_style = self.linewidth_style,
                                linewidth = self.linewidth,
                                final_linewidth = self.final_linewidth,
                                scalar = self.scalar,
                                scalar_min = self.scalar_min,
                                scalar_max = self.scalar_max,
                                zorder = self.zorder,

                                # Movie kwargs
                                dpi=self.dpi,
                                figure=self.figure,
                                movie_writer=batch_writer,
                                filename=batch_filename,
                                first_frame=start_frame,
                                num_frames=num_frames,
                                frame_duration=self.frame_duration,
                                first_frame_time=self.first_frame_time,
                                trail_duration=self.trail_duration,

                                # SaveFig kwargs
                                savefig_kwargs=self.savefig_kwargs
                                )

        return batch_filename


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

    global BATCH_RENDERER
    return BATCH_RENDERER.render_frame_batch(batch)

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
    with open(recipe_filename, 'w') as outfile:
        for chunk_filename in chunk_filenames:
            outfile.write("file '{}'\n".format(chunk_filename))

    ffmpeg_args = [ 'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', recipe_filename,
                    '-c', 'copy',
                    os.path.join(tmpdir, 'assembled.mkv') ]

    subprocess.check_call(ffmpeg_args)
    os.remove(recipe_filename)

# ----------------------------------------------------------------------

def encode_final_movie(output_filename, tmpdir, encoder_args):
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

    if encoder_args is not None:
        encoder_args = shlex.split(encoder_args)
    else:
        encoder_args = [ "-c",  "copy" ]

    logger.debug("encode_final_movie: Extra encoder args are {}".format(encoder_args))

    # Now we re-encode the assembled movie to whatever specs the user wanted
    ffmpeg_args = [ 'ffmpeg', '-y', '-i', os.path.join(tmpdir, 'assembled.mkv') ]
    ffmpeg_args += encoder_args
    ffmpeg_args += [ os.path.abspath(output_filename) ]

    logger.debug("ffmpeg args for final encode: {}".format(ffmpeg_args))

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


# --------------------------------------------------------------------

def parallel_movie_rendering(trajectories,

                            # Mapmaker kwargs
                            map_canvas,

                            # Trajectory Rendering kwargs
                            color_map,
                            decorate_head,
                            head_size,
                            head_color,
                            linewidth_style,
                            linewidth,
                            final_linewidth,
                            scalar,
                            scalar_min,
                            scalar_max,
                            zorder,

                            # Movie kwargs
                            dpi,
                            figure,
                            movie_writer,
                            filename,
                            first_frame,
                            num_frames,
                            trail_duration,
                            frame_duration,
                            first_frame_time,

                            # SaveFig kwargs
                            savefig_kwargs):


    def frame_time(which_frame):
        return first_frame_time + which_frame * frame_duration

    with movie_writer.saving(figure, filename, dpi):
        if tqdm_installed:
            for i in tqdm(range(first_frame, first_frame+num_frames), desc="Rendering Frames", unit='frame'):
                current_time = frame_time(i)
                trail_start_time = frame_time(i) - trail_duration

                logger.info(
                    ('Rendering frame {}: current_time {}, '
                    'trail_start_time {}').format(
                        i,
                        current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        trail_start_time.strftime("%Y-%m-%d %H:%M:%S")))


                frame_trajectories = movies.clip_trajectories_to_interval(
                    trajectories,
                    start_time=trail_start_time,
                    end_time=current_time
                    )

                # TODO: Add in scalar accessor
                trajectory_artists = movies.render_annotated_trajectories(
                    frame_trajectories,
                    map_canvas,
                    color_map=color_map,
                    decorate_head=decorate_head,
                    head_size=head_size,
                    head_color=head_color,
                    linewidth_style=linewidth_style,
                    linewidth=linewidth,
                    final_linewidth=final_linewidth,
                    scalar=scalar,
                    scalar_min=scalar_min,
                    scalar_max=scalar_max,
                    zorder=zorder
                    )

                # TODO: here we could also render the clock
                movie_writer.grab_frame(**savefig_kwargs)

                # Clean up the figure for the next time around
                for artist in trajectory_artists:
                    artist.remove()

                current_time += frame_duration
                trail_start_time += frame_duration
        else:
            for i in range(first_frame, first_frame+num_frames):
                current_time = frame_time(i)
                trail_start_time = frame_time(i) - trail_duration

                logger.info(
                    ('Rendering frame {}: current_time {}, '
                    'trail_start_time {}').format(
                        i,
                        current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        trail_start_time.strftime("%Y-%m-%d %H:%M:%S")))

                frame_trajectories = movies.clip_trajectories_to_interval(
                    trajectories,
                    start_time=trail_start_time,
                    end_time=current_time
                    )

                # TODO: Add in scalar accessor
                trajectory_artists = movies.render_annotated_trajectories(
                    frame_trajectories,
                    map_canvas,
                    color_map=color_map,
                    decorate_head=decorate_head,
                    head_size=head_size,
                    head_color=head_color,
                    linewidth_style=linewidth_style,
                    linewidth=linewidth,
                    final_linewidth=final_linewidth,
                    scalar=scalar,
                    scalar_min=scalar_min,
                    scalar_max=scalar_max,
                    zorder=zorder
                    )

                # TODO: here we could also render the clock
                movie_writer.grab_frame(**savefig_kwargs)

                # Clean up the figure for the next time around
                for artist in trajectory_artists:
                    artist.remove()

                current_time += frame_duration
                trail_start_time += frame_duration
