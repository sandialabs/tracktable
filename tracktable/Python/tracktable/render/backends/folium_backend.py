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
tracktable.render.folium - render trajectories in using the folium backend
"""

import itertools
import logging
from datetime import datetime, timedelta

import matplotlib
from matplotlib.colors import ListedColormap, hsv_to_rgb, rgb2hex
from tracktable.core.geomath import compute_bounding_box
from tracktable.info import airports, borders, ports, rivers, shorelines
from tracktable.render.map_decoration import coloring
from tracktable.render.map_processing import common_processing

from tracktable.render.backends import folium_proxy

fol = folium_proxy.import_folium()
fol_heat_map = folium_proxy.import_folium("plugins.heat_map")

logger = logging.getLogger(__name__)

# later can add multiple layers and switch between with:
# folium.TileLayer('cartodbdark_matter', attr='.').add_to(map)
# folium.TileLayer('CartoDBPositron', attr='.').add_to(map)
# folium.LayerControl().add_to(map)
# TODO add region specifications
# TODO could have opacity, and point size  genertor?
# TODO color_scale, can we remove min,max?
# TODO what if color map but no generator or vice versa
# TODO add point_color_map?
# TODO could customize choice of mapping hues to trajs

def timedelta_to_iso8601_duration(td: timedelta) -> str:
    """Convert a datetime.timedelta to ISO8601 Duration format

    This function converts a duration specified as a ``datetime.timedelta``
    to ISO 8601 string format.  Fractional seconds will be rounded to the nearest second.

    Arguments:
        td (datetime.timedelta): Interval to convert

    Returns:
        Duration represented as a string in ISO8601 format (without fractional seconds)
    """
    #Adapted from isodate's _strfduration method.
    ret = []
    usecs = abs(
        (td.days * 24 * 60 * 60 + td.seconds) * 1000000 + td.microseconds
    )
    seconds, usecs = divmod(usecs, 1000000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days:
        ret.append("%sD" % days)
    if hours or minutes or seconds or usecs:
        ret.append("T")
        if hours:
            ret.append("%sH" % hours)
        if minutes:
            ret.append("%sM" % minutes)
        if seconds or usecs:
            if usecs:
                seconds = seconds + int(round(usecs/1000000)) #we don't want fractional seconds
            ret.append("%dS" % seconds)
    if len(ret) == 0:     # at least one component has to be there, if not 0D
        return "P0D"
    else:
        return "P"+"".join(ret)


def render_trajectories(trajectories,

                        #common arguments
                        map_canvas = None,
                        obj_ids = [],
                        map_bbox = None,
                        show_lines = True,
                        gradient_hue = None,
                        color_map = '',
                        line_color = '',
                        linewidth = 2.4,
                        show_points = False,
                        point_size = 0.6,
                        point_color = '',
                        show_dot = True,
                        dot_size = 0.7,
                        dot_color = 'white',
                        trajectory_scalar_generator = common_processing.path_length_fraction_generator,
                        trajectory_linewidth_generator = None,
                        color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                        show = False,
                        save = False,
                        filename = '',

                        # folium specific args
                        tiles = 'cartodbdark_matter',
                        attr = ".",
                        crs = "EPSG3857",
                        point_popup_properties = [],
                        show_distance_geometry = False,
                        distance_geometry_depth = 4,
                        zoom_frac = [0,1], #undocumented feature, for now
                        show_scale = True,
                        max_zoom = 22,
                        fast = False,
                        animate = False,
                        anim_display_update_interval=timedelta(microseconds=200000),
                        anim_timestamp_update_step=timedelta(minutes=1),
                        anim_trail_duration=None,
                        anim_loop=True,

                        # Airport and poirt specific args
                        draw_airports=False,
                        draw_ports=False,
                        airport_color='red',
                        port_color='blue',
                        airport_dot_size = 1,
                        port_dot_size = 1,
                        use_shapefile=False,
                        use_markers=False,
                        popup_width=250,
                        airport_list=[],
                        port_list=[],
                        airport_bounding_box=None,
                        port_country=None,
                        port_water_body=None,
                        port_wpi_region=None,
                        port_bounding_box=None,
                        port_and_country_seperate=False,
                        prefer_canvas=False,

                        # Shoreline, River and Border specific args
                        draw_shorelines=False,
                        draw_rivers=False,
                        draw_borders=False,
                        shoreline_color='red',
                        river_color='blue',
                        border_color='green',
                        shoreline_fill_polygon=True,
                        shoreline_fill_color='red',
                        shoreline_list=[],
                        river_list=[],
                        border_list=[],
                        shoreline_bounding_box=None,
                        river_bounding_box=None,
                        border_bounding_box=None,
                        shoreline_resolution="low",
                        shoreline_level="L1",
                        river_resolution="low",
                        river_level="L01",
                        border_resolution="low",
                        border_level="L1",
                        **kwargs):
    """Render a list of trajectories using the folium backend

        For documentation on the parameters, please see render_trajectories
    """

    if not fast:
        trajectories, line_color, color_map, gradient_hue \
            = common_processing.common_processing(trajectories,
                                                  obj_ids,
                                                  line_color,
                                                  color_map,
                                                  gradient_hue)
    if not trajectories:
        return

    if map_canvas == None:
        map_canvas = fol.Map(tiles=tiles,
                            attr=attr,
                            crs=crs,
                            control_scale=show_scale,
                            max_zoom=max_zoom,
                            prefer_canvas=prefer_canvas)

    if animate:
        from folium import plugins # to not require it always. Reconsider moving to top?
        segments = []
        anim_points = []

    render_airports_and_ports(map_canvas,
                        draw_airports=draw_airports,
                        draw_ports=draw_ports,
                        airport_color=airport_color,
                        port_color=port_color,
                        airport_dot_size = airport_dot_size,
                        port_dot_size = port_dot_size,
                        use_shapefile=use_shapefile,
                        use_markers=use_markers,
                        popup_width=popup_width,
                        airport_list=airport_list,
                        port_list=port_list,
                        airport_bounding_box=airport_bounding_box,
                        port_country=port_country,
                        port_water_body=port_water_body,
                        port_wpi_region=port_wpi_region,
                        port_bounding_box=port_bounding_box,
                        port_and_country_seperate=port_and_country_seperate)

    render_shorelines_rivers_borders(map_canvas,
                                draw_shorelines=draw_shorelines,
                                draw_rivers=draw_rivers,
                                draw_borders=draw_borders,
                                shoreline_color=shoreline_color,
                                river_color=river_color,
                                border_color=border_color,
                                shoreline_fill_polygon=shoreline_fill_polygon,
                                shoreline_fill_color=shoreline_fill_color,
                                shoreline_list=shoreline_list,
                                river_list=river_list,
                                border_list=border_list,
                                shoreline_bounding_box=shoreline_bounding_box,
                                river_bounding_box=river_bounding_box,
                                border_bounding_box=border_bounding_box,
                                shoreline_resolution=shoreline_resolution,
                                shoreline_level=shoreline_level,
                                river_resolution=river_resolution,
                                river_level=river_level,
                                border_resolution=border_resolution,
                                border_level=border_level)

    for i, trajectory in enumerate(trajectories):
        coordinates = [(point[1], point[0]) for point in trajectory]
        if animate:
            times = [point.timestamp.strftime('%Y-%m-%d %H:%M:%S') for point in trajectory]


        if not fast:
            # set up generators
            if trajectory_scalar_generator:
                scalars = trajectory_scalar_generator(trajectory)
            if trajectory_linewidth_generator:
                # NOTE: lines invisible below about .37
                widths = trajectory_linewidth_generator(trajectory)

            current_color_map, current_point_cmap, mapper, point_mapper = \
                coloring.setup_colors(line_color, color_map, gradient_hue,
                                      point_color, color_scale,
                                      trajectory[0].object_id, i,
                                      trajectory_linewidth_generator)
        else:
            rgb = hsv_to_rgb([common_processing.hash_short_md5(trajectory[0].object_id), 1.0, 1.0])
            current_color_map = ListedColormap([rgb2hex(rgb)])

        solid = (type(current_color_map) is ListedColormap \
               and len(current_color_map.colors) == 1 \
               and trajectory_linewidth_generator == None)
        if show_lines:
            popup_str = str(trajectory[0].object_id)+'<br>'+ \
                trajectory[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')+ \
                '<br> to <br>'+ \
                trajectory[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S')
            tooltip_str = str(trajectory[0].object_id)
            if fast or (solid and not animate): # Polyline ok
                fol.PolyLine(coordinates,
                             color=current_color_map.colors[0],
                             weight=linewidth, opacity=1,
                             tooltip=tooltip_str,
                             popup=popup_str).add_to(map_canvas)
            else: # mapped color (not solid) or animate
                last_pos = coordinates[0]
                for i, pos in enumerate(coordinates[1:]):
                    weight = linewidth
                    if trajectory_linewidth_generator:
                        weight = widths[i]
                    if solid:
                        segment_color = current_color_map.colors[0]
                    else:
                        segment_color = rgb2hex(mapper.to_rgba(scalars[i]))
                    if animate:
                        segments.append({'coordinates': [[last_pos[1], last_pos[0]], [pos[1], pos[0]]],
                                         'times': [times[i], times[i+1]], #i is off by one, so in first iter times[0] is the previous time
                                         'color': segment_color,
                                         'weight': weight
                                     })
                    else:
                        fol.PolyLine([last_pos,pos],
                                     color=segment_color, weight=weight,
                                     opacity=1, tooltip=tooltip_str,
                                     popup=popup_str).add_to(map_canvas)
                    last_pos = pos
        if show_points:
            for coord_ind, c in enumerate(coordinates[:-1]): # all but last (dot)
                point_radius = point_size
                if type(current_point_cmap) is ListedColormap \
                   and len(current_point_cmap.colors) == 1: # one color
                    current_point_color = current_point_cmap.colors[0]
                else:
                    current_point_color = \
                        rgb2hex(point_mapper.to_rgba(scalars[coord_ind]))
                if animate:
                    anim_points.append({'coordinates': [c[1],c[0]], 'time': times[coord_ind], 'color': current_point_color, 'radius':  point_radius, 'popup_str': common_processing.point_popup(trajectory[coord_ind], point_popup_properties)}) #swap lat/lon c[1],c[0]
                else:
                    render_point(trajectory[coord_ind],
                                 point_popup_properties, c,
                                 point_radius,
                                 current_point_color, map_canvas)
        if show_dot:
            render_point(trajectory[-1],
                                point_popup_properties,
                                coordinates[-1], dot_size,
                                dot_color, map_canvas)

        if show_distance_geometry:
            common_processing.render_distance_geometry('folium', distance_geometry_depth,
                                     trajectory, map_canvas)
    if animate:
        #linestrings/track
        features = [{"type": "Feature",
                     "geometry": {
                         "type": "LineString",
                         "coordinates": seg["coordinates"],
                     },
                     "properties": {
                         "times": seg["times"],
                         "style": {
                             "color": seg["color"],
                             "weight": seg["weight"]
                         },
                     },
                 } for seg in segments ]
        if show_points:
            features+=[{"type": "Feature",
                              "geometry": {
                                  "type": "Point",
                                  "coordinates": point["coordinates"],
                              },
                              "properties": {
                                  "time": point["time"],
                                  "popup": point["popup_str"],
                                  "icon": 'circle',
                                  "style": {
                                      "color": point["color"],
                                  },
                                  'iconstyle': {
                                      'fillOpacity': 1.0,
                                      'radius': point['radius'],
                                  },
                              },
            } for point in anim_points ]

        if anim_trail_duration != None:
            anim_trail_duration = timedelta_to_iso8601_duration(anim_trail_duration)
        anim_timestamp_update_step = timedelta_to_iso8601_duration(anim_timestamp_update_step)

        plugins.TimestampedGeoJson({"type":"FeatureCollection",
                                    "features": features}, add_last_point=False,
                                   transition_time=anim_display_update_interval.microseconds // 1000,
                                   period=anim_timestamp_update_step,
                                   duration=anim_trail_duration,
                                   time_slider_drag_update=True,
                                   loop_button=True, loop=anim_loop).add_to(map_canvas)# need to set period automatically or allow users to set.
    if map_bbox:
        map_canvas.fit_bounds([(map_bbox[1], map_bbox[0]),
                      (map_bbox[3], map_bbox[2])])
    else:
        if zoom_frac != [0,1]:
            sub_trajs = common_processing.sub_trajs_from_frac(trajectories, zoom_frac)
            map_canvas.fit_bounds(bounding_box_for_folium(sub_trajs))
        else:
            map_canvas.fit_bounds(bounding_box_for_folium(trajectories))
    if save:  # saves as .html document
        if not filename:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            filename = "trajs-"+datetime_str+'.html'
        map_canvas.save(filename)
    if show:
        display(map_canvas)
    return map_canvas

# ----------------------------------------------------------------------

def render_heatmap(points,
                    trajectories=None,
                    weights=None,
                    color_map='viridis',
                    tiles='cartodbdark_matter',
                    attr='.',
                    crs="EPSG3857",
                    show = False,
                    save = False,
                    filename = '',
                    show_scale = True,
                    max_zoom = 22,

                    # Airport and poirt specific args
                    draw_airports=False,
                    draw_ports=False,
                    airport_color='red',
                    port_color='blue',
                    airport_dot_size = 1,
                    port_dot_size = 1,
                    use_shapefile=False,
                    use_markers=False,
                    popup_width=250,
                    airport_list=[],
                    port_list=[],
                    airport_bounding_box=None,
                    port_country=None,
                    port_water_body=None,
                    port_wpi_region=None,
                    port_bounding_box=None,
                    port_and_country_seperate=False,
                    prefer_canvas=False,

                    # Shoreline, River and Border specific args
                    draw_shorelines=False,
                    draw_rivers=False,
                    draw_borders=False,
                    shoreline_color='red',
                    river_color='blue',
                    border_color='green',
                    shoreline_fill_polygon=True,
                    shoreline_fill_color='red',
                    shoreline_list=[],
                    river_list=[],
                    border_list=[],
                    shoreline_bounding_box=None,
                    river_bounding_box=None,
                    border_bounding_box=None,
                    shoreline_resolution="low",
                    shoreline_level="L1",
                    river_resolution="low",
                    river_level="L01",
                    border_resolution="low",
                    border_level="L1",
                    **kwargs):
    """Creates an interactive heatmap visualization using the folium backend

        For documentation on the parameters, please see render_heatmap
    """

    # lat, long, (optional weight) of points to render
    if weights is None:
        display_points = [[point[1], point[0]] for point in points]
    else:
        display_points = [[point[1], point[0], weight] for point, weight in zip(points, weights)]

    # create the heat map
    heat_map = fol.Map(tiles=tiles,
                        zoom_start=4,
                        attr=attr,
                        crs=crs,
                        control_scale=show_scale,
                        max_zoom=max_zoom,
                        prefer_canvas=prefer_canvas)

    render_airports_and_ports(heat_map,
                            draw_airports=draw_airports,
                            draw_ports=draw_ports,
                            airport_color=airport_color,
                            port_color=port_color,
                            airport_dot_size = airport_dot_size,
                            port_dot_size = port_dot_size,
                            use_shapefile=use_shapefile,
                            use_markers=use_markers,
                            popup_width=popup_width,
                            airport_list=airport_list,
                            port_list=port_list,
                            airport_bounding_box=airport_bounding_box,
                            port_country=port_country,
                            port_water_body=port_water_body,
                            port_wpi_region=port_wpi_region,
                            port_bounding_box=port_bounding_box,
                            port_and_country_seperate=port_and_country_seperate)

    render_shorelines_rivers_borders(heat_map,
                                draw_shorelines=draw_shorelines,
                                draw_rivers=draw_rivers,
                                draw_borders=draw_borders,
                                shoreline_color=shoreline_color,
                                river_color=river_color,
                                border_color=border_color,
                                shoreline_fill_polygon=shoreline_fill_polygon,
                                shoreline_fill_color=shoreline_fill_color,
                                shoreline_list=shoreline_list,
                                river_list=river_list,
                                border_list=border_list,
                                shoreline_bounding_box=shoreline_bounding_box,
                                river_bounding_box=river_bounding_box,
                                border_bounding_box=border_bounding_box,
                                shoreline_resolution=shoreline_resolution,
                                shoreline_level=shoreline_level,
                                river_resolution=river_resolution,
                                river_level=river_level,
                                border_resolution=border_resolution,
                                border_level=border_level)

    gradient = coloring.matplotlib_cmap_to_dict(color_map)
    if trajectories:
        heat_map = render_trajectories(trajectories, map_canvas=heat_map,
                                       line_color='grey', linewidth=0.5,
                                       tiles=tiles, attr=attr, crs=crs,
                                       prefer_canvas=prefer_canvas)
    fol_heat_map.HeatMap(display_points, gradient=gradient).add_to(heat_map)
    if save:  # saves as .html document
        if not filename:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            filename = "heatmap-"+datetime_str+'.html'
        heat_map.save(filename)
    if show:
        display(heat_map)
    return heat_map

# ----------------------------------------------------------------------

def render_point(current_point,
                point_popup_properties, coord, point_radius,
                point_color, map_canvas):
    """Renders a point to the folium map

    Args:
        current_point (point): Current point of the trajectory
        point_popup_properties (list): Point properties
        coord (tuple): Coordinates to render point
        point_radius (int): Size of the point to render
        point_color (str): Color of the point to render
        map (Basemap): Folium map

    Returns:
        No return value

    """

    tooltip_str_point = common_processing.point_tooltip(current_point)
    popup_point = fol.Popup(common_processing.point_popup(current_point,
                                        point_popup_properties),
                            max_width=450)
    fol.CircleMarker(coord, radius=point_radius, fill=True,
                     fill_opacity=1.0,
                     fill_color=point_color,
                     color=point_color,
                     tooltip=tooltip_str_point,
                     popup=popup_point).add_to(map_canvas)

# ----------------------------------------------------------------------

def render_airports_and_ports(map_canvas,
                            draw_airports=False,
                            draw_ports=False,
                            airport_color='red',
                            port_color='blue',
                            airport_dot_size = 1,
                            port_dot_size = 1,
                            use_shapefile=False, # Undocumented for now
                            use_markers=False,
                            popup_width=250,
                            airport_list=[],
                            port_list=[],
                            airport_bounding_box=None,
                            port_country=None,
                            port_water_body=None,
                            port_wpi_region=None,
                            port_bounding_box=None,
                            port_and_country_seperate=False,
                            **kwargs):

    """Renders airports and/or ports to the folium map

    Args:
        map_canvas (folium map object): Canvas to draw the airports/ports on

    Keyword Arguments:
        draw_airports (bool): Whether or not to draw airports (Default: False)
        draw_ports (bool): Whether or not to draw ports (Default: False)
        airport_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the airport dot or marker (Default: 'red')
        port_color (name of standard color as string, hex color string or
            matplotlib color object): Color of the port dot or marker (Default: 'blue')
        airport_dot_size (float): Radius of a airport dot (Default: 1)
        port_dot_size (float): radius of a port dot (Default: 1)
        use_markers (bool): Bool for using marker object instead of dots for airports and prots,
            used for Folium rendering only. (Default: False)
        popup_width (int): Size of the popup window that displays airport/port information, used for Folium rendering only (Default: 250)
        airport_list (list(str)): IATA code of airports to render onto the map (Default: [])
        port_list (list(str)): Name or WPI index number of ports to render onto the map (Default: [])
        airport_bounding_box (BoundingBox or tuple/list of points): bounding box for
            rendering airports within. (Default: None)
        port_bounding_box (BoundingBox or tuple/list of points): bounding box for
            rendering ports within. (Default: None)
        port_country (str): Name of country to render ports in. (Default: None)
        port_water_body (str): Name of body of water to render ports on. (Default: None)
        port_wpi_region (str): Name of WPI region to render ports in. (Default: None)
        port_and_country_seperate (bool): Bool for searching the ports database for a port and not considering it's
            country to see if it's rendered. i.e. You want to render a port in the U.K. while rendering all ports in
            Japan. (Default: False)

    Returns:
        No return value

    """

    if use_shapefile:
            logger.warning("Using a shapefile is currently unsupported for rendering airports and ports.")

    if use_markers:
            logger.warning("Using `markers` causes a considerable performance decrease, ensure `prefer_canvas=True` is set for the Folium map to help performance.")

    if draw_airports:
        display_all_airports = True
        all_airports = []

        if airport_bounding_box:
            display_all_airports = False
            for airport_name, airport in airports.all_airports_within_bounding_box(airport_bounding_box).items():
                all_airports.append(airport)

        if len(airport_list) > 0:
            display_all_airports = False
            for airport in airport_list:
                all_airports.append(airports.airport_information(airport))

        if display_all_airports:
            all_airports = airports.all_airports()
        else:
            # Remove duplicates since there is a chance you'll double up on ports with how this code is structured
            all_airports = list(set(all_airports))

        for airport in all_airports:
            airport_properties = "Airport = " + airport.name + \
                                    "<br>City = " + airport.city + \
                                    "<br>Country = " + airport.country + \
                                    "<br>Lat = " + str(airport.position[1]) + \
                                    "<br>Lon = " + str(airport.position[0]) + \
                                    "<br>Alt = " + str(airport.position[2]) + " ft | " + str(round(airport.position[2]/3.281, 2)) + " m" + \
                                    "<br>IATA Code = " + str(airport.iata_code) + \
                                    "<br>ICAO Code = " + str(airport.icao_code) + \
                                    "<br>UTC Offset = " + str(airport.utc_offset) + \
                                    "<br>Daylight Savings = " + airport.daylight_savings
            if use_markers:
                fol.Marker(location=[airport.position[1], airport.position[0]], tooltip=airport.name,
                        popup=fol.Popup(airport_properties, max_width=popup_width, min_width=popup_width), icon=fol.Icon(color=airport_color, icon='fa-plane', prefix='fa')).add_to(map_canvas)
            else:
                fol.CircleMarker((airport.position[1], airport.position[0]), radius=airport_dot_size, fill=True,
                        fill_opacity=1.0,
                        fill_color=airport_color,
                        color=airport_color,
                        tooltip=airport.name,
                        popup=fol.Popup(airport_properties, max_width=popup_width, min_width=popup_width)).add_to(map_canvas)

    if draw_ports:
        display_all_ports = True
        all_ports = []

        if port_water_body:
            display_all_ports = False
            for port_index, port in ports.all_ports_by_water_body(port_water_body).items():
                all_ports.append(port)

        if port_wpi_region:
            display_all_ports = False
            for port_index, port in ports.all_ports_by_wpi_region(port_wpi_region).items():
                all_ports.append(port)

        if port_bounding_box:
            display_all_ports = False
            for port_index, port in ports.all_ports_within_bounding_box(port_bounding_box).items():
                all_ports.append(port)

        if len(port_list) > 0:
            display_all_ports = False
            if port_and_country_seperate:
                if port_country:
                    for port_index, port in ports.all_ports_by_country(port_country).items():
                        all_ports.append(port)
                else:
                    logger.info("No `port_country` specified only ports listed in `port_list` will be rendered.")
                for port in port_list:
                    all_ports.append(ports.port_information(port))
            else:
                for port in port_list:
                    all_ports.append(ports.port_information(port, country=port_country))

            flatten_all_ports = []
            for port in all_ports: # Since port_information can return lists we need to flatten the all_ports list
                if type(port) is list:
                    for i in port:
                        flatten_all_ports.append(i)
                else:
                    flatten_all_ports.append(port)

            all_ports = flatten_all_ports

        if len(port_list) == 0 and port_country:
            display_all_ports = False
            for port_index, port in ports.all_ports_by_country(port_country).items():
                all_ports.append(port)

        if display_all_ports:
            all_ports = ports.all_ports()
        else:
            # Remove duplicates since there is a chance you'll double up on ports with how this code is structured
            all_ports = list(set(all_ports))

        for port in all_ports:
            port_properties = "Port = " + port.name + \
                                "<br>Alternate Port Name = " + port.alternate_name + \
                                "<br>Country = " + port.country + \
                                "<br>Lat = " + str(port.position[1]) + \
                                "<br>Lon = " + str(port.position[0]) + \
                                "<br>Region = " + port.region + \
                                "<br>Water Body = " + port.water_body + \
                                "<br>UN/LOCODE = " + str(port.un_locode) + \
                                "<br>World Port Index Number = " + str(port.world_port_index_number)

            # TODO (mjfadem): It appears that the WPI.shp file is made up of coordinates and not polygon lists so
            # it's no different then the CSV data we use as a baseline. This needs a bit more investigation.
            # if use_shapefile:
                # sf = shapefile.Reader("tracktable/Python/tracktable/info/data/WPI.shp")
                # for record in sf.shapeRecords():
                #     fol.GeoJson(shape(record.shape.__geo_interface__)).add_to(map_canvas)

            if use_markers:
                fol.Marker(location=[port.position[1], port.position[0]], tooltip=port.name,
                        popup=fol.Popup(port_properties, max_width=popup_width, min_width=popup_width),
                        icon=fol.Icon(color=port_color, icon='fa-ship', prefix='fa')).add_to(map_canvas)
            else:
                fol.CircleMarker((port.position[1], port.position[0]), radius=port_dot_size, fill=True,
                        fill_opacity=1.0,
                        fill_color=port_color,
                        color=port_color,
                        tooltip=port.name,
                        popup=fol.Popup(port_properties, max_width=popup_width, min_width=popup_width)).add_to(map_canvas)

# ----------------------------------------------------------------------

def render_shorelines_rivers_borders(map_canvas,
                            draw_shorelines=False,
                            draw_rivers=False,
                            draw_borders=False,
                            shoreline_color='red',
                            river_color='blue',
                            border_color='green',
                            shoreline_fill_polygon=True,
                            shoreline_fill_color='red',
                            popup_width=375,
                            shoreline_list=[],
                            river_list=[],
                            border_list=[],
                            shoreline_bounding_box=None,
                            river_bounding_box=None,
                            border_bounding_box=None,
                            shoreline_resolution="low",
                            shoreline_level="L1",
                            river_resolution="low",
                            river_level="L01",
                            border_resolution="low",
                            border_level="L1",
                            display_polygon_tooltip=True,
                            **kwargs):

    """Renders shorelines, rivers and/or borders to the folium map

    Args:
        map_canvas (folium map object): Canvas to draw the shorelines/rivers/borders on

    Keyword Arguments:
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
        shoreline_bounding_box (BoundingBox): bounding box for
            rendering shorelines within. (Default: None)
        river_bounding_box (BoundingBox): bounding box for
            rendering rivers within. (Default: None)
        border_bounding_box (BoundingBox): bounding box for
            rendering borders within. (Default: None)
        shoreline_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
        shoreline_level (string): See the docstring for build_shoreline_dict() for more information about levels. (Default: "L1")
        river_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
        river_level (string): See the docstring for build_river_dict() for more information about levels. (Default: "L01")
        border_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
        border_level (string): See the docstring for build_border_dict() for more information about levels. (Default: "L1")
        display_polygon_tooltip (bool): Whether or not to display the tooltip when hovering over a polygon. (Default: True)

    Returns:
        No return value

    """

    if draw_shorelines:
        display_all_shorelines = True
        all_shorelines = []

        if shoreline_bounding_box:
            display_all_shorelines = False
            for shoreline_index, shoreline in shorelines.all_shorelines_within_bounding_box(shoreline_bounding_box, resolution=shoreline_resolution, level=shoreline_level).items():
                all_shorelines.append(shoreline)

        if len(shoreline_list) > 0:
            display_all_shorelines = False
            for shoreline in shoreline_list:
                all_shorelines.append(shorelines.shoreline_information(shoreline, resolution=shoreline_resolution, level=shoreline_level))

        if display_all_shorelines:
            all_shorelines = shorelines.all_shorelines(resolution=shoreline_resolution, level=shoreline_level)
        else:
            # Remove duplicates since there is a chance you'll double up on shorelines with how this code is structured
            all_shorelines = list(set(all_shorelines))

        for shoreline in all_shorelines:
            shoreline_properties = f"GSHHS Index = {shoreline.index} <br>Bounding Box = {shoreline.shape_bbox} <br>Centroid = {shoreline.shape_centroid} <br>GSHHS Level = {shoreline.level} <br>Resolution = {shoreline.resolution}"
            if shoreline_fill_polygon:
                if display_polygon_tooltip:
                    fol_geojson_obj = fol.GeoJson(data=shoreline.geojson,
                                        tooltip=shoreline.index,
                                        style_function=lambda x: {'fillColor': shoreline_fill_color, 'color': shoreline_color})
                else:
                    fol_geojson_obj = fol.GeoJson(data=shoreline.geojson,
                                        style_function=lambda x: {'fillColor': shoreline_fill_color, 'color': shoreline_color})
            else:
                if display_polygon_tooltip:
                    fol_geojson_obj = fol.GeoJson(data=shoreline.geojson,
                                        tooltip=shoreline.index,
                                        style_function=lambda x: {'fillColor': 'none', 'color': shoreline_color})
                else:
                    fol_geojson_obj = fol.GeoJson(data=shoreline.geojson,
                                        style_function=lambda x: {'fillColor': 'none', 'color': shoreline_color})

            fol.Popup(shoreline_properties, max_width=popup_width, min_width=popup_width).add_to(fol_geojson_obj)
            fol_geojson_obj.add_to(map_canvas)

    if draw_rivers:
        display_all_rivers = True
        all_rivers = []

        if river_bounding_box:
            display_all_rivers = False
            for river_index, river in rivers.all_rivers_within_bounding_box(river_bounding_box, resolution=river_resolution, level=river_level).items():
                all_rivers.append(river)

        if len(river_list) > 0:
            display_all_rivers = False
            for river in river_list:
                all_rivers.append(rivers.river_information(river, resolution=river_resolution, level=river_level))

        if display_all_rivers:
            all_rivers = rivers.all_rivers(resolution=river_resolution, level=river_level)
        else:
            # Remove duplicates since there is a chance you'll double up on rivers with how this code is structured
            all_rivers = list(set(all_rivers))

        for river in all_rivers:
            river_properties = f"WBDII River Index = {river.index} <br>Bounding Box = {river.shape_bbox} <br>Centroid = {river.shape_centroid} <br>WBDII Level = {river.level} <br>Resolution = {river.resolution}"
            if display_polygon_tooltip:
                fol_geojson_obj = fol.GeoJson(data=river.geojson,
                            tooltip=river.index,
                            style_function=lambda x: {'fillColor': 'none', 'color': river_color})
            else:
                fol_geojson_obj = fol.GeoJson(data=river.geojson,
                                style_function=lambda x: {'fillColor': 'none', 'color': river_color})

            fol.Popup(river_properties, max_width=popup_width, min_width=popup_width).add_to(fol_geojson_obj)
            fol_geojson_obj.add_to(map_canvas)

    if draw_borders:
        display_all_borders = True
        all_borders = []

        if border_bounding_box:
            display_all_borders = False
            for border_index, border in borders.all_borders_within_bounding_box(border_bounding_box, resolution=border_resolution, level=border_level).items():
                all_borders.append(border)

        if len(border_list) > 0:
            display_all_borders = False
            for border in border_list:
                all_borders.append(borders.border_information(border, resolution=border_resolution, level=border_level))

        if display_all_borders:
            all_borders = borders.all_borders(resolution=border_resolution, level=border_level)
        else:
            # Remove duplicates since there is a chance you'll double up on borders with how this code is structured
            all_borders = list(set(all_borders))

        for border in all_borders:
            border_properties = f"WBDII Border Index = {border.index} <br>Bounding Box = {border.shape_bbox} <br>Centroid = {border.shape_centroid} <br>WBDII Level = {border.level} <br>Resolution = {border.resolution}"
            if display_polygon_tooltip:
                fol_geojson_obj = fol.GeoJson(data=border.geojson,
                                tooltip=border.index,
                                style_function=lambda x: {'fillColor': 'none', 'color': border_color})
            else:
                fol_geojson_obj = fol.GeoJson(data=border.geojson,
                                style_function=lambda x: {'fillColor': 'none', 'color': border_color})

            fol.Popup(border_properties, max_width=popup_width, min_width=popup_width).add_to(fol_geojson_obj)
            fol_geojson_obj.add_to(map_canvas)

# ----------------------------------------------------------------------

def bounding_box_for_folium(trajectories):
    """Translates a computed bounding box to the format needed by folium
    """
    raw_bbox = compute_bounding_box(itertools.chain(*trajectories))

    # folium needs two corner points [sw, ne], in (lat,lon) order
    box_for_folium = [(raw_bbox.min_corner[1], raw_bbox.min_corner[0]),
                      (raw_bbox.max_corner[1], raw_bbox.max_corner[0])]
    return box_for_folium


