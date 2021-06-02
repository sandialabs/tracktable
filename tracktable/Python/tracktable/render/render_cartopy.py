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
tracktable.render.cartopy - render trajectories in using the cartopy backend
"""

import itertools
from datetime import datetime

import cartopy
import cartopy.crs
import matplotlib
import matplotlib.pyplot as plt
from tracktable.core.geomath import compute_bounding_box
from tracktable.render import coloring, common_processing, paths
from tracktable.render.mapmaker import mapmaker

# from IPython import get_ipython


def render_trajectories_cartopy(trajectories,

                                #common arguments
                                map_canvas = None,
                                obj_ids = [],
                                map_bbox = [],
                                show_lines = True,
                                gradient_hue = None,
                                color_map = '',
                                line_color = '',
                                linewidth = 0.8,
                                show_points = False,
                                point_size = 0.2,
                                point_color = '',
                                show_dot = True,
                                dot_size = 0.23,
                                dot_color = 'white',
                                trajectory_scalar_generator = common_processing.path_length_fraction_generator,
                                trajectory_linewidth_generator = None,
                                color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                                show = True,
                                save = False,
                                filename = '',
                                tiles=None,
                                show_distance_geometry = False,
                                distance_geometry_depth = 4,
                                zoom_frac = [0,1], #undocumented feature, for now

                                #cartopy specific arguments
                                draw_lonlat=True,
                                fill_land=True,
                                fill_water=True,
                                draw_coastlines=True,
                                draw_countries=True,
                                draw_states=True,
                                map_projection = None,
                                transform = cartopy.crs.PlateCarree(),
                                figsize=(4,2.25),
                                dpi=300,
                                bbox_buffer=(.3,.3),
                                **kwargs): #kwargs are for mapmaker
    """Render a list of trajectories using the cartopy backend

        For documentation on the parameters, please see render_trajectories
    """
    #tiles override cartopy map features
    if tiles != None:
        fill_land=False
        fill_water=False
        draw_coastlines=False
        draw_countries=False
        draw_states=False

    trajectories, line_color, color_map, gradient_hue = \
        common_processing.common_processing(trajectories, obj_ids, line_color, color_map,
                          gradient_hue)
    if not trajectories:
        return

    if not show_dot:
        dot_size = 0

    if common_processing.in_notebook():
        if show:
            # below effectively does %matplotlib inline (display inline)
            get_ipython().magic("matplotlib inline")   # TODO may casue issues may want to remove
            # TODO figure out how to get matplotlib not to show after executing code a second time.
    figure = plt.figure(dpi=dpi, figsize=figsize)
    if not map_bbox: #if it's empty
        if zoom_frac != [0,1]:
            sub_trajs = common_processing.sub_trajs_from_frac(trajectories, zoom_frac)
            map_bbox = compute_bounding_box(itertools.chain(*sub_trajs),
                                            buffer=bbox_buffer)
        else:
            map_bbox = compute_bounding_box(itertools.chain(*trajectories),
                                            buffer=bbox_buffer)
    if not show_lines:
        linewidth=0

    color_maps = []

    for i, trajectory in enumerate(trajectories):
        if line_color != '':
            # call setup colors here insead at some point
            if isinstance(line_color, list):
                color_maps.append(coloring.get_constant_color_cmap(line_color[i]))
            else:
                color_maps.append(coloring.get_constant_color_cmap(line_color))
        elif color_map != '':
            if isinstance(color_map, list):
                color_maps.append(color_map[i])
            else:
                color_maps.append(color_map)
        elif gradient_hue != None:
            if isinstance(gradient_hue, list):
                color_maps.append(coloring.hue_gradient_cmap(gradient_hue[i]))
            else:
                color_maps.append(coloring.hue_gradient_cmap(gradient_hue))
        else:
           color_maps.append(coloring.hue_gradient_cmap(common_processing.hash_short_md5(trajectory[0].object_id)))

    if map_canvas == None:
        (map_canvas, map_actors) = mapmaker(domain='terrestrial',
                                            map_name='custom',
                                            map_bbox=map_bbox,
                                            map_projection = map_projection,
                                            draw_lonlat=draw_lonlat,
                                            draw_coastlines=draw_coastlines,
                                            draw_countries=draw_countries,
                                            draw_states=draw_states,
                                            fill_land=fill_land,
                                            fill_water=fill_water,
                                            tiles=tiles,
                                            **kwargs)

    # `dot_size*15` andl `inewidth*0.8` below accounts for differing units between folium and cartopy
    paths.draw_traffic(traffic_map = map_canvas,
                       trajectory_iterable = trajectories,
                       color_map = color_maps,
                       color_scale = color_scale,
                       trajectory_scalar_generator = trajectory_scalar_generator,
                       trajectory_linewidth_generator=trajectory_linewidth_generator,
                       linewidth=linewidth*0.8,
                       dot_size=dot_size*15,
                       dot_color=dot_color,
                       show_points = show_points,
                       point_size = point_size*15,
                       point_color=point_color,
                       show_lines=show_lines,
                       transform=transform)
    # Don't support: label_objects, label_generator, label_kwargs, axes, zorder

    if show_distance_geometry:
        common_processing.render_distance_geometry('cartopy', distance_geometry_depth,
                                 trajectory, map_canvas)

    if not common_processing.in_notebook() or save:
        if filename:
            #plt.tight_layout()  #was giving warnings
            plt.savefig(filename)
        else:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            #plt.tight_layout()
            plt.savefig("trajs-"+datetime_str+".png")
    return map_canvas
