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
import logging

from tracktable.core.geomath import simplify
from tracktable.render.backends import ffmpeg_backend

logger = logging.getLogger(__name__)

def render_trajectory_movie(trajectories, backend='', simplify_traj=False, simplify_tol=0.0001, **kwargs):

    # TODO: Update this comment for the movie rendering
    """Render a list of trajectories interactively or as a static image

    This function will render a list of trajectories using Folium (for
    interactive display) if you are in a Jupyter notebook or using Cartopy
    (for a static image) if you are running from a script.

    Args:
        trajectories (single Tracktable trajectory or list of trajectories):
            Trajectories to render

    Keyword Arguments:
        backend (str): Which back end to use.  This can be 'folium' to force
            Folium interactive rendering or 'cartopy' to force static images.
            Defaults to None, which lets the renderer select automatically.
        simplify_traj (bool): Simplify trajectories prior to rendering them
        simplify_tol (float): Tolerance to use when simplifying trajectories,
            default is 0.0001
        map_canvas (map object for given backend): rather than create a new
            map, append to this given map
        obj_ids (str or list of str): only display trajecteories
            whose object id matches the given string or a string from
            the given list of strings.
        map_bbox ([minLon, minLat, maxLon, maxLat]): bounding box for
            custom map extent. By default automatically set to
            make all trajectories visible.
        show_lines (bool): whether or not to show the line segments
            of the trajecotry (Default: True)
        gradient_hue (float or list of floats): hue or list of hues
            (one per trajectory) to be used in definig the gradient color
            map (dark to light) for the trajectories. Only used if
            line_color and color_map are not used (set to '').
            If line_color, color_map and gradient_hue are all unset the
            default behavior is to set the gradient_hue based on a hash
            of the object_id
        color_map (name of standard colormap as string or matplotlib
            color_map object or list of either): The color map to use
            in rendering the segments of each trajectory. Overrides the
            gradient_hue value. Can be a list of color map objects or
            a list of matplotlib color map name strings the same length
            the length of the list of trajectories. Only used if
            line_color is not used (set to '').
        line_color (name of standard color as string, hex color string
            or matplotlib color object, or list of any of these): The
            single color to use for all the segments in each trajectory.
            Overrides color_map and gradient_hue values. Can be a list
            of matplotlib color name strings, hex color strings or
            matplotlib color objects the same length as the length of
            the list of trajectories.
        linewidth (float): Width of the trajectory segments.
            (Default: folium 2.5, cartopy 2)
        show_points (bool): whether or not to show the points along
            the trajecotry (Default: False)
        point_size (float): radius of the points along the path
            (Default: folium 0.6, cartopy 10.0)
        point_color = (name of standard color as string, hex color string
            or matplotlib color object, or list of any of these): The
            single color to use for all the points in each trajectory.
            Can be a list of matplotlib color name strings, hex color
            strings or matplotlib color objects the same length as the
            length of the list of trajectories. If not specified, the
            color matches the segment incident at the point.
        dot_size (float): radius of a dot drawn at the latest point of
            each trajectory (Default: folium 0.7, cartopy 10.0)
        dot_color (name of standard color as string, hex color string or
            matplotlib color object): Color of spot that will be drawn at
            the latest point of each trajecctory (Default: 'white')
        trajectory_scalar_generator (function): Function to generate
            scalars for a trajectory
            (Default: path_length_fraction_generator)
        trajectory_linewidth_generator (function): Function to generate
            path widths for a trajectory (Default: None)
        color_scale (matplotlib.colors.Normalize() or LogNorm()): Linear or logarithmic scale
            (Default: matplotlib.colors.Normalize(vmin=0, vmax=1))
        show (bool): whether or not to show the result (if possible)
            (default True) if saving to a file, might not want to view.
        save (bool): whether or not to save the result to a file.
            For folium the results can be saved to an html file. For
            cartopy the results can be saved as an image. If no filename
            is given, a default filename including the timestamp is used.
            (default False)
        filename (str): Path and filename to save the results to, if
            save is set to True. If no filename is given, a default
            filename including the timestamp is used.
        map_projection (Cartopy CRS): Cartopy CRS projection object (optional), used for Cartopy rendering only. (Default: None)
        transform: Matplotlib axes to render into, used for Cartopy rendering only. (Default: cartopy.crs.PlateCarree())
        tiles (str): Map tiles to use during image generation, the name
            or server url can be used. Options include OpenStreetMaps,
            StamenTerrain, StamenToner, StamenWatercolor, CartoDBPositron
            CartoDBDark_Matter, used for Folium rendering only. (Default: 'cartodbdark_matter')
        attr (str): Map tile attribution; only required if passing custom tile URL,
            used for Folium rendering only. (Default: ".")
        crs (str): Defines coordinate reference systems for projecting geographical
            points into pixel (screen) coordinates and back,
            used for Folium rendering only. (Default: "EPSG3857")
        point_popup_properties (list): Point properties, used for Folium rendering only.
        show_distance_geometry (bool): Boolean to enable displaying distance geometry for a given
            trajectory, used for Folium rendering only. (Default: False)
        distance_geometry_depth (int): Level of distance geometry to display, used for Folium rendering only. (Default: 4)
        show_scale (bool): Boolean to draw the distance scale of the map, used for Folium rendering only. (Default: True)
        max_zoom (int): Maximum allowed zoom level for the tile layer that is created, used for Folium rendering only. (Default: 22)
        fast (bool): Bool for reduced/faster processing of the folium map, used for Folium rendering only. (Default: False)

    """

    if backend == 'ffmpeg':
        render_function = ffmpeg_backend.render_trajectory_movie
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