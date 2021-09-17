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
from datetime import datetime

import folium as fol
import matplotlib
from folium.plugins import HeatMap
from matplotlib.colors import ListedColormap, hsv_to_rgb, rgb2hex
from tracktable.core.geomath import compute_bounding_box
from tracktable.render.map_decoration import coloring
from tracktable.render.map_processing import common_processing


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
        map_canvas = fol.Map(tiles=tiles, attr=attr, crs=crs,
                             control_scale = show_scale,
                             max_zoom=max_zoom)

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
                    filename = ''):
    """Creates an interactive heatmap visualization

    Args:
        points (list): list of points

    Keyword Arguments:
        trajectories: (Trajectoies) list of trajectories corresponding to the points,
            render trajectories if provided (Default: None)
        weights: (list) list of weights associated with each point (Default: None)
        color_map: (str) name of matplotlib colormap to use for the heatmap (Default: 'viridis')
        tiles (str): name of map tiling to use (Default: 'cartodbdark_matter')
        attr (str): folium specific parameter (Default: '.')
        crs (str): folium specific parameter (Default: "EPSG3857")
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

    Returns: an interactive heatmap
    """

    # lat, long, (optional weight) of points to render
    if weights is None:
        display_points = [[point[1], point[0]] for point in points]
    else:
        display_points = [[point[1], point[0], weight] for point, weight in zip(points, weights)]

    # create the heat map
    heat_map = fol.Map(tiles=tiles, zoom_start=4)
    gradient = coloring.matplotlib_cmap_to_dict(color_map)
    if trajectories is not None:
        heat_map = render_trajectories(trajectories, map=heat_map,
                                       line_color='grey', linewidth=0.5,
                                       tiles=tiles, attr=attr, crs=crs)
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

def bounding_box_for_folium(trajectories):
    """Translates a computed bounding box to the format needed by folium
    """
    raw_bbox = compute_bounding_box(itertools.chain(*trajectories))

    # folium needs two corner points [sw, ne], in (lat,lon) order
    box_for_folium = [(raw_bbox.min_corner[1], raw_bbox.min_corner[0]),
                      (raw_bbox.max_corner[1], raw_bbox.max_corner[0])]
    return box_for_folium


