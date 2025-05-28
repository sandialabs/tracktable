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
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
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

"""
tracktable.render.heatmaps - render heatmaps in python

This is a set of functions that intend to allow user-friendly rendering
of heatmaps. A user should be able to simply use the function
render_heatmap(points) passing a single parameter that is a list
of points and get a rendering of those points, whether
running as an interactive map inside of a notebook or from the command
line and saved as a static image to a file.
"""

import logging

from tracktable.render.backends import cartopy_backend, folium_backend
from tracktable.render.map_processing import common_processing

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

def render_heatmap(points, backend='', trajectories=None, **kwargs):
    """Render a list of trajectories interactively or as a static image

    This function will render a list of trajectories using Folium (for
    interactive display) if you are in a Jupyter notebook or using Cartopy
    (for a static image) if you are running from a script.

    Args:
        points (single points or list of points):
            Points to render

    Keyword Arguments:
        backend (str): Which back end to use.  This can be 'folium' to force
            Folium interactive rendering or 'cartopy' to force static images.
            Defaults to None, which lets the renderer select automatically.
        trajectories (Trajectory): list of trajectories corresponding to the points,
            render trajectories if provided. (Default: None)
        simplify_traj (bool): Simplify trajectories prior to rendering them (Default: False)
        simplify_tol (float): Tolerance to use when simplifying trajectories (Default: 0.0001)
        weights: (list) list of weights associated with each point (Default: None)
        color_map: (str) name of matplotlib colormap to use for the heatmap (Default: 'viridis')
        tiles (str): name of map tiling to use (Default: 'cartodbdark_matter')
        attr (str): folium specific parameter (Default: '.')
        crs (str): folium specific parameter (Default: "EPSG3857")
        show (bool): whether or not to show the result (if possible)
            (default: True) if saving to a file, might not want to view.
        save (bool): whether or not to save the result to a file.
            For folium the results can be saved to an html file. For
            cartopy the results can be saved as an image. If no filename
            is given, a default filename including the timestamp is used.
            (default: False)
        filename (str): Path and filename to save the results to, if
            save is set to True. If no filename is given, a default
            filename including the timestamp is used.
        map_projection (GeoAxes): Map to render onto
        point_source (iterable): Sequence of 2D points. This will
          be traversed only once.
        bounding_box (point2d): Bounding box of area to generate histogram
        bin_size (int): Boundary size for bins (Default: 1)
        colormap (str or Colormap): Colors to use for histogram (Default: 'gist_heat')
        colorscale (matplotlib.colors.Normalize or subclass): Mapping from bin counts to color. Useful values are matplotlib.colors.Normalize() and matplotlib.colors.LogNorm(). (Default: matplotlib.colors.Normalize())
        zorder (int): Image priority for rendering. Higher values will be rendered on top of actors with lower z-order. (Default: 10)
        draw_cities (bool): Render the cities within the given bounding box. (Default: False)

        draw_airports (bool): Whether or not to draw airports (Default: False)
        draw_all_airports (bool): Render all of the ports in the map_bbox, used for Cartopy rendering only. (Default: False)
        airport_list (list(str)): IATA code of airports to render onto the map (Default: [])
        airport_bounding_box (BoundingBox or tuple/list of points): Bounding box for
            rendering airports within. (Default: None)
        airport_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the airport dot or marker (Default: 'red')
        airport_label_size (int): Size (in points) for airport name labels, used for Cartopy rendering only. (Default: 12)
        airport_dot_size (float): Radius of a airport dot (Default: folium 1, cartopy 2)
        airport_label_color (str): Color name or hex string for airport names, used for Cartopy rendering only. (Default: 'white')
        airport_zorder (int): Color name or hex string for airport names, used for Cartopy rendering only. (Default: 6)

        draw_ports (bool): Whether or not to draw ports (Default: False)
        draw_all_ports (bool): Render all of the ports in the map_bbox, used for Cartopy rendering only. (Default: False)
        port_list (list(str)): Name or WPI index number of ports to render onto the map (Default: [])
        port_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the port dot or marker (Default: 'blue')
        port_country (str): Name of country to render ports in. (Default: None)
        port_water_body (str): Name of body of water to render ports on. (Default: None)
        port_wpi_region (str): Name of WPI region to render ports in. (Default: None)
        port_bounding_box (BoundingBox or tuple/list of points): Bounding box for
            rendering ports within. (Default: None)
        port_and_country_seperate (bool): Bool for searching the ports database for a port and not considering it's
            country to see if it's rendered. i.e. You want to render a port in the U.K. while rendering all ports in
            Japan. (Default: False)
        port_label_size (int): Size (in points) for port name labels, used for Cartopy rendering only. (Default: 12)
        port_dot_size (float): radius of a port dot (Default: folium 1, cartopy 2)
        port_label_color (str): Color name or hex string for port names, used for Cartopy rendering only. (Default: 'white')
        port_zorder (int): Color name or hex string for port names, used for Cartopy rendering only. (Default: 6)

        draw_arrows (bool): Whether or not to draw arrows from airport/port labels to dots (Default: True)

        draw_shorelines (bool): Whether or not to draw shorelines (Default: False)
        draw_rivers (bool): Whether or not to draw rivers (Default: False)
        draw_borders (bool): Whether or not to draw borders (Default: False)
        shoreline_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the shoreline (Default: 'red')
        river_color_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the river (Default: 'blue')
        border_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the border (Default: 'green')
        shoreline_fill_polygon (bool): Whether or not to fill in the inside of the shoreline polygon (Default: True)
        shoreline_fill_color (name of standard color as string, hex color string or
            matplotlib color object): Fill color of the shoreline (Default: 'red')
        popup_width (int): Size of the popup window that displays airport/port information, used for Folium rendering only (Default: 375)
        shoreline_list (list(int)): GSHHS index number of the shoreline polygons to render (Default: [])
        river_list (list(int)): WDBII index number of the river polygons to render (Default: [])
        border_list (list(int)): WDBII index number of the border polygons to render (Default: [])
        shoreline_bounding_box (BoundingBox): Bounding box for
            rendering shorelines within. (Default: None)
        river_bounding_box (BoundingBox): Bounding box for
            rendering rivers within. (Default: None)
        border_bounding_box (BoundingBox): Bounding box for
            rendering borders within. (Default: None)
        shoreline_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
        shoreline_level (string): See the docstring for build_shoreline_dict() for more information about levels. (Default: "L1")
        river_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
        river_level (string): See the docstring for build_river_dict() for more information about levels. (Default: "L01")
        border_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
        border_level (string): See the docstring for build_border_dict() for more information about levels. (Default: "L1")
        display_polygon_tooltip (bool): Whether or not to display the tooltip when hovering over a polygon,
            used for folium rendering only (Default: True)
    """

    render_function = folium_backend.render_heatmap

    if backend == 'folium':
        render_function = folium_backend.render_heatmap
    elif backend == 'cartopy':
        render_function = cartopy_backend.render_heatmap
    elif backend == 'ipyleaflet': # currently not implemented
        raise NotImplementedError("ipyleaflet heatmap rendering backend is currently unavailable.")
    elif backend == 'bokeh':  # currently not implemented
        raise NotImplementedError("Bokeh heatmap rendering backend is currently unavailable.")
    else:
        if backend != '':
            logger.error("Error: Invalid backend specified in",
                  "render_heatmap.",
                  "Valid backends include: folium and cartopy.",
                  "Defauting to folium backend")
        if common_processing.in_notebook():
            if type(trajectories) is not list or len(trajectories) <= 10000:
                render_function = folium_backend.render_heatmap
            else:
                logger.warning("Too many trajectories to plot with folium. Reverting to non-interactive backend. Override with backend='folium'")
                render_function = cartopy_backend.render_heatmap
        else:
            render_function = cartopy_backend.render_heatmap

    return render_function(points, trajectories=trajectories, **kwargs)
