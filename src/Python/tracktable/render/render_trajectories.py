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
tracktable.render.render_trajectories - render trajectories in python

This is a set of function that intend to allow user-friendly rendering
of trajectories. A user should be able to simply use the function
render_trajectories(trajs) passing a single parameter that is a list
of trajectories and get a rendering of those trajectories, whether
running as an interactive map inside of a noetbook or from the command
line and saved as a static image to a file.

In addition render_trajectories supports many parameters to enable
specifying a myriad of options for rendering the trajectories,
including allowing users to explicitly specify the rendering backend.
"""
import logging

from tracktable.core.geomath import simplify
from tracktable.render.backends import bokeh_backend, cartopy_backend, folium_backend, ipyleaflet_backend
from tracktable.render.map_processing import common_processing

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

def render_trajectories(trajectories, backend='', simplify_traj=False, simplify_tol=0.0001, **kwargs):
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
        simplify_traj (bool): Simplify trajectories prior to rendering them (Default: False)
        simplify_tol (float): Tolerance to use when simplifying trajectories (Default: 0.0001)
        map_canvas (map object for given backend): rather than create a new
            map, append to this given map
        obj_ids (str or list of str): only display trajecteories
            whose object id matches the given string or a string from
            the given list of strings.
        map_bbox ([minLon, minLat, maxLon, maxLat]): Bounding box for
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
        animate (bool): Animate the tracks. Used for Folium rendering only. (Default: False)
        anim_display_update_interval (timedelta): time between map updates (smaller values yields faster animation rates) (currently maps to Folium's TimestampedGeoJson transition_time). (Default: timedelta(microseconds=200000)=200 milliseconds)
        anim_timestamp_update_step (timedelta): time duration between updates (in the data time frame). The timestamp for the displayed data will increase by this amount every time the animation is updated.  (currently maps to Folium's TimestampedGeoJson period) (Default: timedelta(minutes=1))
        anim_trail_duration (timedelta): how long (in the data time frame) a trail should persist behind the most recent point (duration for features to remain on the map after "their time" has passed). If set to None features will persist indefinitely. (currently maps to Folium's TimestampedGeoJson duration) Example:timedelta(hours=1) (Default: None)
        anim_loop (bool): Whether the animation should loop and continue playing after the first time. (Default: True)
        use_markers (bool): Bool for using marker object instead of dots for airports and ports,
            used for Folium rendering only. (Default: False)
        popup_width (int): Size of the popup window that displays airport/port information, used for Folium rendering only (Default: 250)

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

        draw_arrows (bool): Whether or not to draw arrows from airport/port labels to dots, used for Cartopy rendering only. (Default: True)
        prefer_canvas (bool): Whether or not to prefer canvas rendering over SVG, used for Folium rendering only. (Default: False)

        draw_shorelines (bool): Whether or not to draw shorelines (Default: False)
        draw_rivers (bool): Whether or not to draw rivers (Default: False)
        draw_borders (bool): Whether or not to draw borders (Default: False)
        shoreline_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the shoreline (Default: 'red')
        river_color (name of standard color as string, hex color string or
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
        draw_all_shorelines (bool): Render all of the shorelines in the map_bbox, used for Cartopy rendering only. (Default: False)
        draw_all_rivers (bool): Render all of the rivers in the map_bbox, used for Cartopy rendering only. (Default: False)
        draw_all_borders (bool): Render all of the borders in the map_bbox, used for Cartopy rendering only. (Default: False)
    """

    render_function = folium_backend.render_trajectories

    if backend == 'folium':
        render_function = folium_backend.render_trajectories
    elif backend == 'cartopy':
        render_function = cartopy_backend.render_trajectories
    elif backend == 'ipyleaflet': # currently experimental
        logger.warn("ipyleaflet trajectory rendering backend is currently experimental, proceed with caution.")
        render_function = ipyleaflet_backend.render_trajectories
    elif backend == 'bokeh':  # currently experimental
        logger.warn("Bokeh trajectory rendering backend is currently experimental, proceed with caution.")
        render_function = bokeh_backend.render_trajectories
    else:
        if backend != '':
            logger.error("Error: Invalid backend specified in",
                  "render_trajectories.",
                  "Valid backends include: folium and cartopy",
                  "Defauting to folium backend")
        if common_processing.in_notebook():
            if type(trajectories) is not list or len(trajectories) <= 10000:
                render_function = folium_backend.render_trajectories
            else:
                logger.warn("Too many trajectories to plot with folium. Reverting to non-interactive backend. Override with backend='folium'")
                render_function = cartopy_backend.render_trajectories
        else:
            render_function = cartopy_backend.render_trajectories

    if simplify_traj:
        if type(trajectories) is not list:
            trajectories = simplify(trajectories, simplify_tol)
        else:
            for index, traj in enumerate(trajectories):
                trajectories[index] = simplify(traj, simplify_tol)

    return render_function(trajectories, **kwargs)

# ----------------------------------------------------------------------

#todo should this return anything?
def render_trajectories_separate(trajectories, backend='', **kwargs):
    """Render a list of trajectories such that each trajectory is
    rendered separately in its own map. See render_trajectories for
    parameters

    Args:
        trajectories (Tracktable trajectory or list of trajectory objects):
            List of trajectories to render

    Keyword Args:
        backend (str): The backend to use for rendering default is folium if in a notebook and cartopy otherwise.
        kwargs (dict): Additional parameters to customize the rendered trajectory

    Returns:
        No return value

    """

    for traj in trajectories:
        render_trajectories(traj, backend=backend, show=True, **kwargs)

# ----------------------------------------------------------------------

def render_trajectory(trajectory, backend='', **kwargs):
    """Render a single trajectory
    This function allows users to render a single trajectory, and just
    calls render_trajectories, which also handles single trajectories.

    Arguments:
        trajectory (Trajectory): The trajectory object to render

    Keyword Arguments:
        backend (str): the rendering backend (cartopy, folium, etc)
            default is folium if in a notebook and cartopy otherwise.
        kwargs (dict): see render_trajectories for other arguments

    Returns:
        No return value

    """

    render_trajectories(trajectory, backend, **kwargs)

# ----------------------------------------------------------------------

def render_trajectories_for_print(trajectories, filename,
                                  land_fill_color='white',
                                  water_fill_color='#EEEEEE',
                                  color_map='viridis',
                                  dot_color='grey',
                                  linewidth=1.5,
                                  figsize=(6,4),
                                  save=True,
                                  **kwargs):
    """Render a list of trajectories with print-friendly defaults

    This function will render a list of trajectories using Cartopy
    in a way this is more appropriate for use in printed media.
    """

    if not 'gradient_hue' in kwargs:
        kwargs['color_map']=color_map  #make this the default, but let it be supersceded by gradient_hue

    render_trajectories(trajectories, backend='cartopy', land_fill_color=land_fill_color,
                                water_fill_color=water_fill_color, dot_color=dot_color,
                                linewidth=linewidth, figsize=figsize, save=save,
                                filename=filename, **kwargs)

# ----------------------------------------------------------------------

def render_trajectories_for_print_using_tiles(trajectories, filename,
                                              color_map='viridis',
                                              dot_color='grey', linewidth=1.5,
                                              figsize=(6,4),
                                              save=True,
                                              tiles='https://basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png',
                                              fill_land=False,
                                              fill_water=False,
                                              draw_coastlines=False,
                                              draw_countries=False,
                                              draw_states=False,
                                              **kwargs):
    """Render a list of trajectories with print-friendly defaults
       but using tiles as the basemap.

    This function will render a list of trajectories using Cartopy
    in a way this is more appropriate for use in printed media.
    """

    if not 'gradient_hue' in kwargs:
        kwargs['color_map']=color_map  #make this the default, but let it be supersceded by gradient_hue

    render_trajectories(trajectories, backend='cartopy', dot_color=dot_color, linewidth=linewidth,
                                figsize=figsize, save=save, filename=filename,
                                tiles=tiles, fill_land=fill_land, fill_water=fill_water,
                                draw_coastlines=draw_coastlines, draw_countries=draw_countries,
                                draw_states=draw_states, **kwargs)
