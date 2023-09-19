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

"""ffmpeg_backend.py - Render a movie of trajectories using ffmpeg

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""

import datetime
import itertools
import logging
import multiprocessing
import os
import platform
import subprocess
import tempfile

import matplotlib
import matplotlib.animation
from matplotlib import pyplot
from tracktable.core import geomath
from tracktable.render import render_map
from tracktable.render.map_processing.movies import (
    clip_trajectories_to_interval, compute_movie_time_bounds,
    initialize_canvas, map_extent_as_bounding_box,
    render_annotated_trajectories, setup_encoder, trajectories_inside_box)
from tracktable.render.map_processing.parallel_movies import (
    BatchMovieRenderer, concatenate_movie_chunks, encode_final_movie,
    remove_movie_chunks)

matplotlib.use('Agg')

logger = logging.getLogger(__name__)

# In order to keep ffmpeg a soft dependency we check that ffmpeg is installed and fail accordingly.
# Also need to make sure that we don't internally call the render_movie functions.
try:
    if platform.system() == "Windows":
        subprocess.check_output(['where', 'ffmpeg'])
    if platform.system() == "Darwin" or platform.system() == "Linux":
        subprocess.check_output(['which', 'ffmpeg'])
except Exception as e:
    raise ImportError("ffmpeg isn't installed on this system, unable to generate a Tracktable movie. Please install ffmpeg.")

try:
    from tqdm import tqdm
    tqdm_installed = True
except ImportError:
    tqdm_installed = False

# ---------------------------------------------------------------------

def render_trajectory_movie(trajectories,

                            # Mapmaker kwargs
                            domain='terrestrial',
                            map_name="region:world",
                            draw_coastlines=True,
                            draw_countries=True,
                            draw_states=True,
                            draw_lonlat=True,
                            map_bbox=[],
                            map_projection = None,
                            map_canvas = None,
                            figure=None,
                            fill_land=True,
                            fill_water=True,
                            tiles=None,

                            # Trajectory Rendering kwargs
                            trajectory_color_type="scalar",
                            trajectory_color="progress",
                            trajectory_colormap="gist_heat",
                            trajectory_zorder=10,
                            decorate_trajectory_head=False,
                            trajectory_head_dot_size=2,
                            trajectory_head_color="white",
                            trajectory_linewidth_style="constant",
                            trajectory_linewidth=0.5,
                            trajectory_initial_linewidth=0.5,
                            trajectory_final_linewidth=0.01,
                            scalar_min=0,
                            scalar_max=1,
                            trail_duration=datetime.timedelta(seconds=300),

                            # Movie kwargs
                            movie_writer=None,
                            codec=None,
                            encoder="ffmpeg",
                            encoder_args="-c:v mpeg4 -q:v 5",
                            duration=60,
                            fps=30,
                            resolution=[800, 600],
                            dpi=100,
                            start_time=None,
                            end_time=None,
                            filename='movie.mp4',
                            movie_title='Tracktable Movie',
                            movie_artist='Tracktable Trajectory Toolkit',
                            movie_comment='',
                            utc_offset=None,
                            timezone_label=None,

                            # SaveFig kwargs
                            savefig_kwargs=None,

                            # Additional args for Render Map
                            **kwargs):

    """Render a list of trajectories into a movie

        For documentation on the parameters, please see render_movie
    """

    # Steps:
    # 1.  Cull trajectories that are entirely outside the map
    # 2.  Annotate trajectories with scalars needed for color
    # 3.  Compute frame duration
    # 4.  Add clock to map: TODO: I still need arguments to control whether the clock is
    #                       included and, if so, where and how it's rendered.
    # 5.  Loop through frames

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
    if (domain == 'cartesian2d' and (map_bbox is None or len(map_bbox) == 0)):
        map_bbox = geomath.compute_bounding_box(itertools.chain(*trajectories))

    # Set up the map.
    logger.info('Initializing map canvas for rendering.')
    (figure, axes) = initialize_canvas(resolution, dpi)
    if map_canvas == None:
        (map_canvas, map_actors) = render_map.render_map(domain=domain,
                                            map_name=map_name,
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

    map_bbox = map_extent_as_bounding_box(map_canvas, domain=domain)

    # Set up the video encoder.
    if movie_writer is None:
        movie_writer = setup_encoder(encoder=encoder,
                                codec=codec,
                                encoder_args=encoder_args,
                                movie_title=movie_title,
                                movie_artist=movie_artist,
                                movie_comment=movie_comment,
                                fps=fps,
                                **kwargs)

    # Setup trajectory render style
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
        savefig_kwargs = {'facecolor': figure.get_facecolor()}

    # This a known issue in matplotlib that was never fixed so we're on the
    # hook to ensure that we don't pass the bbox_inches param to ffmpeg
    if "bbox_inches" in savefig_kwargs and encoder == 'ffmpeg':
        logger.warn('The `bbox_inches` save argument is incompatiable with ffmpeg, argument will be removed from `savefig_kwargs`.')
        savefig_kwargs.pop("bbox_inches")

    (movie_start_time, movie_end_time) = compute_movie_time_bounds(
        trajectories, start_time, end_time)

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

    counter = 0
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
                    map_canvas,
                    color_map=trajectory_colormap,
                    decorate_head=decorate_trajectory_head,
                    head_size=trajectory_head_dot_size,
                    head_color=trajectory_head_color,
                    linewidth_style=linewidth_style,
                    linewidth=linewidth,
                    final_linewidth=final_linewidth,
                    scalar=trajectory_color,
                    scalar_min=scalar_min,
                    scalar_max=scalar_max,
                    zorder=trajectory_zorder
                    )

                # pyplot.savefig('image_'+str(counter)+'.jpg', **savefig_kwargs)
                counter+=1

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
                    map_canvas,
                    color_map=trajectory_colormap,
                    decorate_head=decorate_trajectory_head,
                    head_size=trajectory_head_dot_size,
                    head_color=trajectory_head_color,
                    linewidth_style=linewidth_style,
                    linewidth=trajectory_linewidth,
                    final_linewidth=final_linewidth,
                    scalar=trajectory_color,
                    scalar_min=scalar_min,
                    scalar_max=scalar_max,
                    zorder=trajectory_zorder
                    )

                # TODO: here we could also render the clock
                movie_writer.grab_frame(**savefig_kwargs)

                # Clean up the figure for the next time around
                for artist in trajectory_artists:
                    artist.remove()

# --------------------------------------------------------------------

def render_trajectory_movie_parallel(trajectories,

                                    # Mapmaker kwargs
                                    domain='terrestrial',
                                    map_name="region:world",
                                    draw_coastlines=True,
                                    draw_countries=True,
                                    draw_states=True,
                                    draw_lonlat=True,
                                    map_bbox=[],
                                    map_projection = None,
                                    map_canvas = None,
                                    figure=None,
                                    fill_land=True,
                                    fill_water=True,
                                    tiles=None,

                                    # Trajectory Rendering kwargs
                                    trajectory_color_type="scalar",
                                    trajectory_color="progress",
                                    trajectory_colormap="gist_heat",
                                    trajectory_zorder=10,
                                    decorate_trajectory_head=False,
                                    trajectory_head_dot_size=2,
                                    trajectory_head_color="white",
                                    trajectory_linewidth_style="constant",
                                    trajectory_linewidth=0.5,
                                    trajectory_initial_linewidth=0.5,
                                    trajectory_final_linewidth=0.01,
                                    scalar_min=0,
                                    scalar_max=1,
                                    trail_duration=datetime.timedelta(seconds=300),

                                    # Movie kwargs
                                    codec="ffv1",
                                    encoder="ffmpeg",
                                    encoder_args="-c:v mpeg4 -q:v 5",
                                    duration=60,
                                    fps=30,
                                    resolution=[800, 600],
                                    dpi=100,
                                    start_time=None,
                                    end_time=None,
                                    filename='movie.mp4',
                                    movie_title='Tracktable Movie',
                                    movie_artist='Tracktable Trajectory Toolkit',
                                    movie_comment='',
                                    utc_offset=None,
                                    timezone_label=None,
                                    frame_batch_size = 500,

                                    # SaveFig kwargs
                                    savefig_kwargs=None,

                                    # Parallel kwargs
                                    processors=0,

                                    # Additional args for Render Map
                                    **kwargs):

    """Render a list of trajectories into a movie in parallel

        For documentation on the parameters, please see render_movie
    """

    # Steps:
    # 1.  Cull trajectories that are entirely outside the map
    # 2.  Annotate trajectories with scalars needed for color
    # 3.  Split trajectories into equal sized batches
    # 4.  Add clock to map: TODO: I still need arguments to control whether the clock is
    #                       included and, if so, where and how it's rendered.
    # 5.  Generate a movie for each batch of trajectories using multiprocessing pool
    # 6.  Splice movies together into a single movie

    # Configure the batch renderer
    renderer = BatchMovieRenderer()

    global BATCH_RENDERER
    BATCH_RENDERER = renderer

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
    if (domain == 'cartesian2d' and (map_bbox is None or len(map_bbox) == 0)):
        map_bbox = geomath.compute_bounding_box(itertools.chain(*trajectories))

    # Set up the map.
    logger.info('Initializing map canvas for rendering.')
    (figure, axes) = initialize_canvas(resolution, dpi)
    if map_canvas == None:
        (map_canvas, map_actors) = render_map.render_map(domain=domain,
                                            map_name=map_name,
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

    map_bbox = map_extent_as_bounding_box(map_canvas, domain=domain)

    # Setup trajectory render style
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
        savefig_kwargs = {'facecolor': figure.get_facecolor()}

    # This a known issue in matplotlib that was never fixed so we're on the
    # hook to ensure that we don't pass the bbox_inches param to ffmpeg
    if "bbox_inches" in savefig_kwargs and encoder == 'ffmpeg':
        logger.warn('The `bbox_inches` save argument is incompatiable with ffmpeg, argument will be removed from `savefig_kwargs`.')
        savefig_kwargs.pop("bbox_inches")

    (movie_start_time, movie_end_time) = compute_movie_time_bounds(
        trajectories, start_time, end_time)

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

    total_frame_count = num_frames

    if figure is None:
        figure = pyplot.gcf()

    # Setup the temp dir needed to store the movie parts
    tmpdir = tempfile.mkdtemp(prefix='movie_parts')

    # Setup the renderers args
    # Common Args
    renderer.trajectories = trajectories_on_map
    renderer.trail_duration = trail_duration

    # Mapmaker Args
    renderer.domain = domain
    renderer.map_canvas = map_canvas
    renderer.figure = figure

    # Movie Args
    renderer.savefig_kwargs = savefig_kwargs
    renderer.dpi = dpi
    renderer.axes = axes
    renderer.fps = fps
    renderer.temp_directory = tmpdir
    if utc_offset:
        renderer.utc_offset = int(utc_offset)
    if timezone_label:
        renderer.timezone_label = timezone_label
    renderer.frame_duration = frame_duration
    renderer.first_frame_time = first_frame_time
    renderer.codec = codec
    renderer.encoder = encoder

    renderer.color_map=trajectory_colormap
    renderer.decorate_head=decorate_trajectory_head
    renderer.head_size=trajectory_head_dot_size
    renderer.head_color=trajectory_head_color
    renderer.linewidth_style=linewidth_style
    renderer.linewidth=linewidth
    renderer.final_linewidth=final_linewidth
    renderer.scalar=trajectory_color
    renderer.scalar_min=scalar_min
    renderer.scalar_max=scalar_max
    renderer.zorder=trajectory_zorder

    # Figure out how many batches we're going to need
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

    # Setup the number of thread processors
    if processors == 0:
        processors = None

    pool = multiprocessing.Pool(processes=processors)
    result = pool.map_async(renderer.render_frame_batch, frame_batches)
    batch_result = result.get()

    logger.info("Combining movie parts into raw footage file")
    concatenate_movie_chunks(batch_result, tmpdir)

    logger.info("Encoding raw footage file to final movie")
    encode_final_movie(filename, tmpdir, encoder_args)

    logger.info("Cleaning up temporary files")
    remove_movie_chunks(tmpdir, batch_result)

    os.rmdir(tmpdir)
