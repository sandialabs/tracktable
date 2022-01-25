#
# Copyright (c) 2014-2022 National Technology and Engineering
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
from datetime import datetime

import folium as fol
import matplotlib
from folium.plugins import HeatMap
from matplotlib.colors import ListedColormap, hsv_to_rgb, rgb2hex
from tracktable.core.geomath import compute_bounding_box
from tracktable.info import airports, ports
from tracktable.render.map_decoration import coloring
from tracktable.render.map_processing import common_processing

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

    for i, trajectory in enumerate(trajectories):
        coordinates = [(point[1], point[0]) for point in trajectory]

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

        if show_lines:
            popup_str = str(trajectory[0].object_id)+'<br>'+ \
                trajectory[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')+ \
                '<br> to <br>'+ \
                trajectory[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S')
            tooltip_str = str(trajectory[0].object_id)
            if fast or (type(current_color_map) is ListedColormap \
               and len(current_color_map.colors) == 1 \
               and trajectory_linewidth_generator == None): # Polyline ok
                fol.PolyLine(coordinates,
                             color=current_color_map.colors[0],
                             weight=linewidth, opacity=1,
                             tooltip=tooltip_str,
                             popup=popup_str).add_to(map_canvas)
            else: # mapped color (not solid)
                last_pos = coordinates[0]
                for i, pos in enumerate(coordinates[1:]):
                    weight = linewidth
                    if trajectory_linewidth_generator:
                        weight = widths[i]
                    segment_color = rgb2hex(mapper.to_rgba(scalars[i]))
                    fol.PolyLine([last_pos,pos],
                                 color=segment_color, weight=weight,
                                 opacity=1, tooltip=tooltip_str,
                                 popup=popup_str).add_to(map_canvas)
                    last_pos = pos
        if show_points:
            for i, c in enumerate(coordinates[:-1]): # all but last (dot)
                point_radius = point_size
                if type(current_point_cmap) is ListedColormap \
                   and len(current_point_cmap.colors) == 1: # one color
                    current_point_color = current_point_cmap.colors[0]
                else:
                    current_point_color = \
                        rgb2hex(point_mapper.to_rgba(scalars[i]))

                render_point(trajectory[i],
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

    gradient = coloring.matplotlib_cmap_to_dict(color_map)
    if trajectories:
        heat_map = render_trajectories(trajectories, map_canvas=heat_map,
                                       line_color='grey', linewidth=0.5,
                                       tiles=tiles, attr=attr, crs=crs,
                                       prefer_canvas=prefer_canvas)
    HeatMap(display_points, gradient=gradient).add_to(heat_map)
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

            # TODO (mjfadem): It appears that the WIP.shp file is made up of coordinates and not polygon lists so
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

def bounding_box_for_folium(trajectories):
    """Translates a computed bounding box to the format needed by folium
    """
    raw_bbox = compute_bounding_box(itertools.chain(*trajectories))

    # folium needs two corner points [sw, ne], in (lat,lon) order
    box_for_folium = [(raw_bbox.min_corner[1], raw_bbox.min_corner[0]),
                      (raw_bbox.max_corner[1], raw_bbox.max_corner[0])]
    return box_for_folium


