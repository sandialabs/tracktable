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

import datetime
import itertools
import logging

import cartopy
import cartopy.crs
import matplotlib
import matplotlib.animation
from matplotlib import pyplot
from tracktable.core import geomath
from tracktable.render import render_map
from tracktable.render.map_processing.movie_processing import (
    clip_trajectories_to_interval, compute_movie_time_bounds,
    initialize_canvas, map_extent_as_bounding_box,
    render_annotated_trajectories, setup_encoder, trajectories_inside_box)

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
    # 4.  Add clock to map: TODO: I still need arguments to control whether the clock is included and, if so, where and how it's rendered.
    # 5.  Loop through frames

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
            itertools.chain(*trajectories))

    # Set up the map.
    logger.info('Initializing map canvas for rendering.')
    (figure, axes) = initialize_canvas(resolution, dpi)
    if map_canvas == None:
        (map_canvas, map_actors) = render_map.render_map(domain='terrestrial',
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