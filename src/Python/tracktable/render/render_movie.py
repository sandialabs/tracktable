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

"""render_movie.py - Render a movie of trajectories

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""
import logging

from tracktable.core.geomath import simplify
from tracktable.render.backends import ffmpeg_backend

logger = logging.getLogger(__name__)

def render_trajectory_movie(trajectories, backend='', simplify_traj=False, simplify_tol=0.0001, parallel=False, **kwargs):

    """Render a list of trajectories into a matplotlib animation/movie

        This function will render a list of trajectories using ffmpeg through the
        matplotlib animation library.

        Args:
            trajectories (single Tracktable trajectory or list of trajectories):
                Trajectories to render

        Keyword Arguments:
            backend (str): Which rendering back end to use. Currently the only available move renderer is FFMPEG. Defaults to None, which lets the renderer select automatically.
            simplify_traj (bool): Simplify trajectories prior to rendering them (Default: False)
            simplify_tol (float): Tolerance to use when simplifying trajectories (Default: 0.0001)
            parallel (bool): Wheather to generate the movie's frames in parallel, this may not be faster than using a single process. (Default: False)

            domain (str): Domain to create the map in (Default: 'terrestrial')
            map_name: Region name ('region:<region>' or 'airport:<airport>' or 'port:<port>' or 'city:<city>' or 'custom'). Available regions are in tracktable.render.map_processing.maps.available_maps().
            draw_coastlines (bool): Whether or not to draw coastlines on the map (Default: True)
            draw_countries (bool): Whether or not to draw country borders on the map (Default: True)
            draw_states (bool): Whether or not to draw US/Canada state borders (Default: True)
            draw_lonlat (bool): Whether or not to draw longitude/latitude lines (Default: True)
            map_bbox ([minLon, minLat, maxLon, maxLat]): Bounding box for custom map extent (Default: None)
            map_projection (Cartopy CRS): Cartopy CRS projection object (optional) (Default: None)
            fill_land (bool): Whether or not to fill in the land areas (Default: True)
            fill_water (bool): Whether or not to fill in the land areas (Default: True)

            trajectory_color (string): Scalar to apply to the trajectories (default: progress)
            trajectory_colormap (name of colormap or :obj:`matplotlib.colors.Colormap`): Trajectory scalars will be mapped to this color map.  (default: 'plasma')
            decorate_trajectory__head (boolean): If true, a dot will be drawn at the current
                position of each object on the screen.  (default: False)
            trajectory_head_size (float): How large the dot should be for decorated
                trajectories, measured in points.  (default: 2)
            trajectory_head_color (string or tuple): What color the head dot should be for
                decorated trajectories.  Can be any Matplotlib color specification
                such as a color name, an '#RRGGBB' string, or a tuple of RGB or
                RGBA values.  The value 'scalar' means to use the scalar value
                at the head of the trajectory so that the dot is the same color
                as its trail.
            trajectory_linewidth_style (string): Either 'constant', in which case the lines
                for each trajectory will have constant width (see the `linewidth`
                parameter); or 'taper', in which case the line width will vary
                smoothly from `linewidth` at the object's current position to
                `final_linewidth` at the oldest end of the trail. (default:
                'taper')
            trajectory_linewidth (float): Width of trajectory trail subject to
                `linewidth_style`. (default: 0.5)
            trajectory_final_linewidth (float): Width of oldest end of trajectory trail.
                Only used when `linewidth_style` is 'taper'.
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
            trajectory_zorder (integer): Z-order for drawn items.  Items with a higher
                Z-order will appear on top of items with a lower Z-order.  This is
                Matplotlib-specific. (default: 10)
            trail_duration (datetime timedelta): Amount of time in seconds to retain trajectories
                tail (default: datetime.timedelta(seconds=300))

            filename (string): User-specified filename for the finished movie (Default: 'movie.mp4')
            movie_writer (Matplotlib animation objec): video encoder (Default)
            encoder (string): Name of encoder.  This must be one of the
                values in ``matplotlib.animation.writers.list``.
                Default: 'ffmpeg' (requires that you have FFmpeg installed
                on your system)
            codec (string): Name of specific encoding algorithm to use.
                This is specific to the encoder you choose.  Default:
                None (whatever the encoder prefers)
            encoder_args (list of strings): Any arguments you wish to
                provide to the encoder.  These are passed through
                to the underlying Matplotlib implementation as
                ``extra_args``.  More information about the
                encoder args can be found here:
                https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FFMpegWriter.html#matplotlib-animation-ffmpegwriter
            movie_title (string): Title string to be embedded in the
                movie's metadata.  This is not rendered on screen.
                Default: "Tracktable Movie"
            movie_artist (string): Movie creator to be embedded in the
                movie's metadata.  This is not rendered on screen.
                Default: "Tracktable Trajectory Toolkit"
            movie_comment (string): Any other comments you want to
                embed in metadata.  (Default: empty string)
            fps (int): Desired frames per second for the result. (Default: 30)

    """

    render_function = ffmpeg_backend.render_trajectory_movie

    if backend == 'ffmpeg' and parallel == False:
        render_function = ffmpeg_backend.render_trajectory_movie
    elif backend == 'ffmpeg' and parallel == True:
        render_function = ffmpeg_backend.render_trajectory_movie_parallel
    # elif backend != 'ffmpeg' and parallel == True:
        # TODO mjfadem: Our parallel code has a bunch of spots of ffmpeg hardcoded values, we'll
        # need to update that before we can support other encoder parallel processing
    else:
        if backend != '':
            logger.error("Error: Invalid backend specified in",
                        "render_movie.",
                        "Valid backends include: ffmpeg",
                        "Defauting to ffmpeg backend")
        else:
            render_function = ffmpeg_backend.render_trajectory_movie

    if simplify_traj:
        if type(trajectories) is not list:
            trajectories = simplify(trajectories, simplify_tol)
        else:
            for index, traj in enumerate(trajectories):
                trajectories[index] = simplify(traj, simplify_tol)

    render_function(trajectories, **kwargs)