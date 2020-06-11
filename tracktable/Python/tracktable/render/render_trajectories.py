#
# Copyright (c) 2014-2020 National Technology and Engineering
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
of trajectories.  A user should be able to simply use the funection 
render_trajectories(trajs) passing a single parameter that is a list
of trajectories and get a rendering of those trajectories, whether 
running as an interactive map inside of a noetbook or from the command 
line and saved as a static image to a file.  

In addition render_trajectories supports many parameters to enable 
specifying a myriad of options for rendering the trajectories, 
including allowing users to explicitly specify the rendering backend.  
"""

import folium as fol
from tracktable.core.geomath import compute_bounding_box, distance
from tracktable.core.geomath import length, point_at_length_fraction
import itertools
import random
import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt
from tracktable.render.mapmaker import mapmaker
from tracktable.render import paths
from datetime import datetime
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv, to_rgb, rgb2hex
from math import ceil
#from math import pow
import math

import hashlib

# ----------------------------------------------------------------------

#todo should this return anything?
def render_trajectories_separate(trajectories, backend='', **kwargs):
    """Render a list of trajectories such that each trajectory is
    rendered separately in its own map.  See render_trajectories for 
    parameters"""
    for traj in trajectories:
        render_trajectories(traj, backend=backend, show=True, **kwargs)

# ----------------------------------------------------------------------


#TODO should we support iterables other than list?
#todo support list of linewidhts?  maybe just mapper
def render_trajectories(trajectories, backend='', **kwargs):
    """Render a list of trajectories
    This function renders a list of trajectories.  

    Arguments:
        trajectories {trajectory object or list of trajectory objects}: 
            A list of trajectories to render
    Keyword arguments:
        backend {string}: The backend to use for rendering
            default is folium if in a notebook and cartopy otherwise.
        map {map object for given backend}: rather than create a new 
            map, append to this given map
        obj_ids {string or list of strings}: only display trajecteories 
            whose object id matches the given string or a string from 
            the given list of strings.
        map_bbox {[minLon, maxLon, minLat, maxLat]}: bounding box for 
            custom map extent.  By default automatically set to 
            make all trajectories visible.
        show_lines {boolean}: whether or not to show the line segments
            of the trajecotry (defulat=True)
        gradient_hue {float or list of floats}: hue or list of hues 
            (one per trajectory) to be used in definig the gradient color
            map (dark to light) for the trajectories.  Only used if 
            line_color and color_map are not used (set to ''). 
            If line_color, color_map and gradient_hue are all unset the 
            default behavior is to set the gradient_hue based on a hash 
            of the object_id
        color_map {name of standard colormap as string or matplotlib 
            color_map object or list of either}: The color map to use 
            in rendering the segments of each trajectory. Overrides the
            gradient_hue value. Can be a list of color map objects or 
            a list of matplotlib color map name strings the same length 
            the length of the list of trajectories. Only used if 
            line_color is not used (set to '').
        line_color {name of standard color as string, hex color string
            or matplotlib color object, or list of any of these}: The 
            single color to use for all the segments in each trajectory. 
            Overrides color_map and gradient_hue values.  Can be a list 
            of matplotlib color name strings, hex color strings or 
            matplotlib color objects the same length as the length of 
            the list of trajectories.  
        linewidth {float}: Width of the trajectory segments. 
            (default folium 2.5, cartopy 2)
        show_points {boolean} whether or not to show the points along
            the trajecotry (defulat=False)
        point_size {float} radius of the points along the path 
            (default folium 0.6, cartopy 10.0)
        point_color = {name of standard color as string, hex color string
            or matplotlib color object, or list of any of these}: The 
            single color to use for all the points in each trajectory. 
            Can be a list of matplotlib color name strings, hex color 
            strings or matplotlib color objects the same length as the 
            length of the list of trajectories. If not specified, the 
            color matches the segment incident at the point.
        dot_size {float}: radius of a dot drawn at the latest point of 
            each trajectory (default folium 0.7, cartopy 10.0)
        dot_color {name of standard color as string, hex color string or 
            matplotlib color object} Color of spot that will be drawn at 
            the latest point of each trajecctory (default = 'white')
        trajectory_scalar_generator {function}: Function to generate 
            scalars for a trajectory 
            (default path_length_fraction_generator)
        trajectory_linewidth_generator {function}: Function to generate 
            path widths for a trajectory (default None)
        color_scale Linear or logarithmic scale 
            (default matplotlib.colors.Normalize(vmin=0, vmax=1)) 
            other options: LogNorm()
        show {boolean} whether or not to show the result (if possible) 
            (default True) if saving to a file, might not want to view.
        save {boolean} whether or not to save the result to a file.  
            For folium the results can be saved to an html file. For 
            cartopy the results can be saved as an image.  If no filename
            is given, a default filename including the timestamp is used.
            (default False) 
        filename {string} Path and filename to save the results to, if
            save is set to True. If no filename is given, a default 
            filename including the timestamp is used.

    Folium-specific Keyword Arguments:
        tiles {string} map tiles to use for folium. Can be a string name
            of a folium supported maptiles set or a Leaflet-style URL in 
            this format: http://{s}.yourtiles.com/{z}/{x}/{y}.png
            (default='cartodbdark_matter')
            Other options:
                "OpenStreetMap”
                “StamenTerrain” 
                "StamenToner"
                "StamenWatercolor"
                “CartoDBPositron”
                "CartoDBDark_Matter"
        attr {string} attribution string for custom tile set 
            (default "."),
        point_popup_properties {list of strings}: names of the properties
            to include in the popup which is displayed when clicking on 
            a point (when show_points==True).
        show_distance_geometry {boolean} whether or not to show the 
            distance geometry information for the trajectories 
            (default False)
        distance_geometry_depth {int} if show_distance_geometry is True,
            the depth of the distance geometry calculation (default=4)
        show_scale {boolean} whether or not to show the scale of the 
            current map in the lower-lefthand corner (default = True)
        max_zoom {int}: The maximum zoom level for the given map tiles
            this may need to be increased if there is a need to zoom in
            very close (default = 22)

    Cartopy-specific Keyword Arguments:
        map_projection {cartopy.crs projection object} Projection to use
            to display the map (default=cartopy.crs.Miller)
        transform {cartopy.crs projection object} the input projection 
            (default=Geodetic())
    """
    render_function = render_trajectories_folium

    if backend == 'folium':
        render_function = render_trajectories_folium
    elif backend == 'cartopy':
        render_function = render_trajectories_cartopy
    elif backend == 'ipyleaflet':
        render_function = render_trajectories_ipyleaflet
    elif backend == 'bokeh':  # currently for experimentation only
        render_function = render_trajectories_bokeh
    else:
        if backend != '':
            print("Error: Invalid backend specified in",
                  "render_trajectories.",
                  "Valid backends include: folium, and cartopy")
        if in_notebook():
            if type(trajectories) is not list or len(trajectories) <= 10000:
                render_function = render_trajectories_folium
            else:
                print("Too many trajectories to plot with folium.  Reverting to non-interactive backend.  Override with backend='folium'")
                render_function = render_trajectories_cartopy
        else:
            render_function = render_trajectories_cartopy

    return render_function(trajectories, **kwargs)

# ----------------------------------------------------------------------


def render_trajectory(trajectory, backend='', **kwargs):
    """Render a single trajectory
    This function allows users to render a single trajectory, and just
    calls render_trajectories, which also handles single trajectories.

    Arguments:
        trajectory -- The trajectory object to render

    Keyword Arguments:
        backend -- the rendering backend (cartopy, folium, etc)
            default is folium if in a notebook and cartopy otherwise.
        see render_trajectories for other arguments
    """
    render_trajectories(trajectory, backend, **kwargs)

# ----------------------------------------------------------------------


def path_length_fraction_generator(trajectory):
    """Generator to produce path length fraction scalars
    A genertor that given a trajectory will generate a scalar for each 
    point such that each scalar represents the fraction of the total 
    length along the path at the associated point.  
    """
    dist_fractions = []
    prev_point = trajectory[0]
    cum_distance = 0
    for point in trajectory[1:]:
        cum_distance += distance(prev_point,point) 
        dist_fractions.append(cum_distance)
        prev_point = point
    dist_fractions = [d / cum_distance for d in dist_fractions]
    return dist_fractions

# ----------------------------------------------------------------------


def get_constant_color_cmap(color):
    """Returns a colormap containing the single color given
    """
    if isinstance(color, str):
        return ListedColormap(np.array(matplotlib.colors.to_rgba(color)))
    else:
        return ListedColormap(np.array(color)) #TODO handle errors

# ----------------------------------------------------------------------
    

def progress_linewidth_generator(trajectory):
    """Generator to produce progress linewidth scalars
    A generator that given a trajectory will generate a scalar for each
    point such that each scalar represents a good width value for the 
    fraction of points that come before that point in the trajectory.
    """
    widths = []
    tlen = len(trajectory)
    for i, point in enumerate(trajectory[1:]):
        widths.append((((i+1)/tlen)*5.0)+0.37)
    return widths
    # anothr way:
    #annotator = tracktable.feature.annotations.retrieve_feature_function('progress')
    #annotator(trajectory)

# ----------------------------------------------------------------------


def get_color_mapper(color_scale, color_map):
    """Returns an object that can translate scalars into colors
       Returns an object that can produce for any scalar the correct RGBA
       color from the given color_map using the given color_scale.
    """
    cmap = plt.get_cmap(color_map)
    return matplotlib.cm.ScalarMappable(norm=color_scale, cmap=cmap)

# ----------------------------------------------------------------------


def hue_gradient_cmap(hue, chop_frac=.29):
    """Returns a color map which progresses from dark to light given a 
       specific hue

    Args:
       hue: the hue to generate the color map for.  (0 to 1)
       chop_frac: the fraction of the beginning and end of the total 
           gradient to chop off so as to not be too light or dark.

    Returns:
       color map object which can be passed to matplotlib's cmap param 
           or render_trajectories color_map
    """
    if isinstance(hue, str):
        hue = rgb_to_hsv(to_rgb(hue))[0]
    rgb = hsv_to_rgb([hue, 1.0, 1.0])
    N = 128
    vals = np.ones((N*2, 4))
    vals[:, 0] = np.concatenate([np.linspace(rgb[0]*chop_frac, rgb[0], N), np.linspace(rgb[0], 1.0-((1.0-rgb[0])*chop_frac), N)]) 
    vals[:, 1] = np.concatenate([np.linspace(rgb[1]*chop_frac, rgb[1], N), np.linspace(rgb[1], 1.0-((1.0-rgb[1])*chop_frac), N)])
    vals[:, 2] = np.concatenate([np.linspace(rgb[2]*chop_frac, rgb[2], N), np.linspace(rgb[2], 1.0-((1.0-rgb[2])*chop_frac), N)])
    return ListedColormap(vals)

# ----------------------------------------------------------------------


#todo some of this processing can be moved outside of the loop!
def setup_colors(line_color, color_map, gradient_hue, point_color,
                 color_scale, objid, i, linewidth_generator):
    """ Processes the color optins and returns the current color maps
    This function determines what the current color map should be for
    lines and points given the various releated parameters and returns
    color maps for points and for lines.  
    """
    if line_color != '' and line_color != []:
        if isinstance(line_color, list):
            current_cmap = ListedColormap([line_color[i]])
        else:
            current_cmap = ListedColormap([line_color])
    elif color_map != '' and color_map != []:
        if isinstance(color_map, list):
            current_cmap = color_map[i]
        else:
            current_cmap = color_map
    elif gradient_hue != None and gradient_hue != []:
        if isinstance(gradient_hue, list):
            current_cmap = hue_gradient_cmap(gradient_hue[i])
        else:
            current_cmap = hue_gradient_cmap(gradient_hue)
    else:
        current_cmap = hue_gradient_cmap(hash_short_md5(objid))

    if point_color != '':
        if isinstance(point_color, list):
            current_point_cmap = ListedColormap([point_color[i]])
        else:
            current_point_cmap = ListedColormap([point_color])
    else:
        current_point_cmap = hue_gradient_cmap(hash_short_md5(objid))

    # make color mapper if needed
    mapper = None
    point_mapper = None
    if type(current_cmap) is not ListedColormap \
       or len(current_cmap.colors) != 1 or linewidth_generator != None: 
        mapper = get_color_mapper(color_scale, current_cmap)
    if type(current_point_cmap) is not ListedColormap \
       or len(current_point_cmap.colors) != 1: 
        point_mapper = get_color_mapper(color_scale,
                                        current_cmap)

    return current_cmap, current_point_cmap, mapper, point_mapper
    
# ----------------------------------------------------------------------


def point_tooltip(current_point):
    """Formats the tooltip string for a point
    """
    return current_point.timestamp.strftime("%H:%M:%S")

# ----------------------------------------------------------------------


def point_popup(current_point, point_popup_properties):
    """Formats the popup string for a point
    """
    popup_str_point = str(current_point.object_id)+'<br>'+ \
        current_point.timestamp.strftime("%H:%M:%S")+'<br>Lat='+ \
        str(current_point[1])+'<br>Lon='+str(current_point[0])
    if point_popup_properties and point_popup_properties[0] == '*':
        for (name, value) in current_point.properties.items():
            popup_str_point += '<br>'+name+': '+str(value)
    else:
        for prop_str in point_popup_properties:
            if prop_str in current_point.properties:
                popup_str_point += '<br>'+prop_str+': '+ \
                    str(current_point.properties[prop_str])
    return popup_str_point

# ----------------------------------------------------------------------


def render_point_folium(current_point,
                        point_popup_properties, coord, point_radius,
                        point_color, map):
    """Renders a point to the folium map
    """
    tooltip_str_point = point_tooltip(current_point)
    popup_point = fol.Popup(point_popup(current_point,
                                        point_popup_properties),
                            max_width=450)
    fol.CircleMarker(coord, radius=point_radius, fill=True,
                     fill_opacity=1.0,
                     fill_color=point_color,
                     color=point_color,
                     tooltip=tooltip_str_point,
                     popup=popup_point).add_to(map)

# ----------------------------------------------------------------------


def render_distance_geometry_folium(distance_geometry_depth,
                                    traj, map):
    """Renders the distance geometry calculations to the folium map
    """
    #cp=control_point
    cp_colors = ['red', 'blue', 'yellow', 'purple']+ \
        [random_color() for i in range(4, distance_geometry_depth)]
    traj_length = length(traj)
    for num_cps in range(2,distance_geometry_depth+2):
        cp_increment = 1.0/(num_cps-1)
        cp_fractions = [cp_increment * i for i in range(num_cps)]
        cps = [point_at_length_fraction(traj, t) for t in cp_fractions]
        cp_coords = [(round(point[1],7), round(point[0],7)) for point in cps]
        for i, cp_coord in enumerate(cp_coords):
            normalization_term = traj_length*cp_increment
            control_color = cp_colors[num_cps-2]
            for j in range(len(cps)-1):
                line_coords = [(round(cps[j][1],7), round(cps[j][0],7)),
                               (round(cps[j+1][1],7), round(cps[j+1][0],7))]
                val = round(distance(cps[j], cps[j+1]) / normalization_term, 4)
                tooltip = str(j+1)+'/'+str(len(cps)-1)+' = '+str(val)
                fol.PolyLine(line_coords, color=control_color, weight=1,
                             tooltip=tooltip).add_to(map)
            popup=str(traj[0].object_id)+'<br>'+ \
                traj[i].timestamp.strftime("%H:%M:%S")+'<br>Latitude='+ \
                str(round(traj[i][1],7))+'<br>Longitude='+str(round(traj[i][0],7))
            fol.CircleMarker(cp_coord, radius=4, fill=True,
                             color=control_color,
                             tooltip=round(cp_fractions[i], 7),
                             popup=popup).add_to(map)    
    
# ----------------------------------------------------------------------


def hash_short_md5(string): 
    """Given any string, returns a number between 0 and 1.  The same 
       number is always returned given the same string. Internally uses
       hashlib.md5, but only uses the first quarter of the full hash
    """
    return int(hashlib.md5(string.encode('utf-8')).hexdigest()[:8],
               base=16)/((2**32)-1)
#perceived brightness (may be useful later)
# sqrt(R*R*.241 + G*G*.691 + B*B*.068)

# ----------------------------------------------------------------------


def common_processing(trajectories, obj_ids, line_color, color_map,
                      gradient_hue):
    #handle a single traj as input
    if type(trajectories) is not list: 
        trajectories = [trajectories]

    #filter trajectories list by obj_ids if specified
    if obj_ids != []:
        if type(obj_ids) is not list:
            trajectories = [traj for traj in trajectories \
                            if traj[0].object_id == obj_ids]
        else:
            filtered_trajs = []
            for obj_id in obj_ids:
                matched = [traj for traj in trajectories \
                            if traj[0].object_id == obj_id]
                filtered_trajs+=matched
            trajectories = filtered_trajs

    #now handle some color processing
        
    #translate strings into colormaps
    if type(color_map) is str and color_map != '':
        color_map = matplotlib.cm.get_cmap(color_map)
    elif type(color_map) is list:
        for i, cm in enumerate(color_map):
            if type(cm) is str:
                color_map[i] = matplotlib.cm.get_cmap(cm)

    #TODO make this into a function called 3 times
    # Handle too few colors
    if type(line_color) is list and len(trajectories) > len(line_color):
        times_to_repeat = ceil(len(trajectories)/len(line_color))
        line_color = line_color * times_to_repeat

    # Handle too few color maps
    if type(color_map) is list and len(trajectories) > len(color_map):
        times_to_repeat = ceil(len(trajectories)/len(color_map))
        color_map = color_map * times_to_repeat

    # Handle too few hews (say that 5 times fast) ;)
    if type(gradient_hue) is list and len(trajectories) > len(gradient_hue):
        times_to_repeat = ceil(len(trajectories)/len(gradient_hue))
        gradient_hue = gradient_hue * times_to_repeat
    
    return trajectories, line_color, color_map, gradient_hue
    
# ----------------------------------------------------------------------


# later can add multiple layers and switch between with:
#folium.TileLayer('cartodbdark_matter', attr='.').add_to(map)
#folium.TileLayer('CartoDBPositron', attr='.').add_to(map)
#folium.LayerControl().add_to(map)
#TODO add region specifications
#todo could have opacity, and point size  genertor?
#todo color_scale, can we remove min,max?
#TODO what if color map but no generator or vice versa
#todo add point_color_map?
#todo could customize choice of mapping hues to trajs
def render_trajectories_folium(trajectories,
                               #common arguments
                               map = None,
                               obj_ids = [],
                               #\/format [minLon, maxLon, minLat, maxLat]
                               map_bbox = None, 
                               show_lines = True,
                               gradient_hue = None,
                               color_map = '',
                               line_color = '',
                               linewidth = 2.4,
                               show_points = False,
                               point_size = 0.6,
                               point_color = '',
                               show_dot=True,
                               dot_size = 0.7,
                               dot_color = 'white',
                               trajectory_scalar_generator = path_length_fraction_generator,
                               trajectory_linewidth_generator = None, 
                               color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                               show = False,
                               save=False,
                               filename='',

                               #folium specific
                               tiles='cartodbdark_matter',
                               attr=".",
                               point_popup_properties = [],
                               show_distance_geometry = False,
                               distance_geometry_depth = 4,
                               show_scale = True,
                               max_zoom = 22,
                               fast=False,
                               **kwargs):
    """Render a list of trajectories using the folium backend
    This function renders a list of trajectories to a folium map.

    For documentation on the parameters, please see render_trajectories
    """
    if not fast:
        trajectories, line_color, color_map, gradient_hue \
            = common_processing(trajectories,
                                obj_ids,
                                line_color,
                                color_map,
                                gradient_hue)
    if not trajectories:
        return

    if map == None:
        map = fol.Map(tiles=tiles, attr=attr, control_scale = show_scale,
                      max_zoom=max_zoom)

    for i, trajectory in enumerate(trajectories):
        coordinates = [(point[1], point[0]) for point in trajectory]

        if not fast:
            #set up generators
            if trajectory_scalar_generator:
                scalars = trajectory_scalar_generator(trajectory)
            if trajectory_linewidth_generator:
                #Note: lines invisible below about .37
                widths = trajectory_linewidth_generator(trajectory) 

            current_color_map, current_point_cmap, mapper, point_mapper = \
                setup_colors(line_color, color_map, gradient_hue,
                             point_color, color_scale,
                             trajectory[0].object_id, i,
                             trajectory_linewidth_generator)
        else:
            rgb = hsv_to_rgb([hash_short_md5(trajectory[0].object_id), 1.0, 1.0])
            current_color_map = ListedColormap([rgb2hex(rgb)]) 

        if show_lines:
            popup_str = str(trajectory[0].object_id)+'<br>'+ \
                trajectory[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')+ \
                '<br> to <br>'+ \
                trajectory[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S')
            tooltip_str = str(trajectory[0].object_id)
            if fast or (type(current_color_map) is ListedColormap \
               and len(current_color_map.colors) == 1 \
               and trajectory_linewidth_generator == None): #Polyline ok
                fol.PolyLine(coordinates,
                             color=current_color_map.colors[0],
                             weight=linewidth, opacity=1,
                             tooltip=tooltip_str,
                             popup=popup_str).add_to(map)
            else: #mapped color (not solid)
                last_pos = coordinates[0]
                for i, pos in enumerate(coordinates[1:]):
                    weight = linewidth
                    if trajectory_linewidth_generator:
                        weight = widths[i]
                    segment_color = rgb2hex(mapper.to_rgba(scalars[i]))
                    fol.PolyLine([last_pos,pos],
                                 color=segment_color, weight=weight,
                                 opacity=1, tooltip=tooltip_str,
                                 popup=popup_str).add_to(map)
                    last_pos = pos
        if show_points:
            for i, c in enumerate(coordinates[:-1]): #all but last (dot)
                point_radius = point_size
                if type(current_point_cmap) is ListedColormap \
                   and len(current_point_cmap.colors) == 1: # one color 
                    current_point_color = current_point_cmap.colors[0]
                else:
                    current_point_color = \
                        rgb2hex(point_mapper.to_rgba(scalars[i]))
                    
                render_point_folium(trajectory[i],
                                    point_popup_properties, c,
                                    point_radius,
                                    current_point_color, map)
        if show_dot:
            render_point_folium(trajectory[-1],
                                point_popup_properties,
                                coordinates[-1], dot_size,
                                dot_color, map)

        if show_distance_geometry:
            render_distance_geometry_folium(distance_geometry_depth,
                                            trajectory,
                                            map)

    if map_bbox:
        map.fit_bounds([(map_bbox[2], map_bbox[0]),
                      (map_bbox[3], map_bbox[1])])
    else:
        map.fit_bounds(bounding_box_for_folium(trajectories))
    if save:  #saves as .html document
        #iframe = map._repr_html_()
        #html="<html><body>"+iframe+"</body></html>"
        if not filename:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            filename = "trajs-"+datetime_str+'.html'
        #with open(filename, 'w') as f:
        #    f.write(html)
        map.save(filename)
    if show:
        display(map)
    return map

# ----------------------------------------------------------------------

#The following is needed because ipyleaflet currently does not support
#fit_bounds

def transform(point, scale):
    EARTH_RADIUS = 6378137 #combine these to a global var
    transform_factor = 0.5 / (math.pi * EARTH_RADIUS)
    x = scale * ((transform_factor*point[0])+0.5)
    y = scale * ((-transform_factor*point[1])+0.5)
    return (x,y)

#spherical mercator projection #checked with https://epsg.io/transform#s_srs=4326&t_srs=3857
def project_spherical_mercator(latlng):
    EARTH_RADIUS = 6378137
    MAX_LATITUDE = 85.0511287798
    d = math.pi / 180.0
    max_lat = MAX_LATITUDE
    lat = max(min(max_lat, latlng[1]), -max_lat)
    sin = math.sin(lat * d)
    return (EARTH_RADIUS * latlng[0] * d, EARTH_RADIUS * math.log((1+sin) / (1-sin)) / 2)

def crs_zoom(scale):
    return math.log(scale / 256) / math.log(2)

def crs_scale(zoom):
    return 256 * math.pow(2, zoom)

#projects a geographical coordinate according to the projection of the map's CRS then scales it according to zoom and the CRS's Transformation.  The result is a poxel coord relative to the CRS origin
def project(latlng, zoom):
    #check zoom?
    projectedPoint = project_spherical_mercator(latlng)
    scale = crs_scale(zoom)
    return transform(projectedPoint, scale);

def get_scale_zoom(scale, from_zoom):
    zoom = crs_zoom(scale * crs_scale(from_zoom))
    return zoom # check for Nan?

#returns tne maximum zoom level on which the given bounds fit to the map vie in its entirety
def get_bounds_zoom(map, bounds, inside=True, size=[960,400], padding=[0,0]): #ignore padding for now #fix size
    #bounds is min_corner max_corner lon,lat
    #size = size=padding
    #boundsSize = toBounds(this.project(se, zoom), this.project(nw, zoom)).getSize()
    current_zoom = map.zoom
    nw = (bounds.min_corner[0], bounds.max_corner[1])
    se = (bounds.max_corner[0], bounds.min_corner[1])
    se_proj = project(se,current_zoom)
    nw_proj = project(nw,current_zoom)
    denx = abs(se_proj[0] - nw_proj[0])
    if denx != 0:
        scalex = size[0] / denx
    else:
        scalex = 1000000000 # what should this be TODO
    deny = abs(nw_proj[1] - se_proj[1])
    if deny !=0:
        scaley = size[1] / deny
    else:
        scaley = 1000000000 #Todo?
    scale = max(scalex, scaley)
    if inside:
        scale = min(scalex, scaley)
    
    zoom = get_scale_zoom(scale, current_zoom)
    
    #snap? could add later
    
    return max(map.min_zoom, min(map.max_zoom, zoom))



# ----------------------------------------------------------------------

def render_point_ipyleaflet(current_point,
                        point_popup_properties, coord, point_radius,
                        point_color, map):
    """Renders a point to the ipyleaflet map
    """
    import ipyleaflet as ipl #for now don't require unless using
    from ipywidgets import HTML # is this dependency okay?
    tooltip_str_point = point_tooltip(current_point)
    popup_point = point_popup(current_point,
                              point_popup_properties)

    marker = ipl.CircleMarker(location=coord, radius=int(point_radius+0.5),
                              stroke=False, fill=True, color=point_color,
                              fill_color=point_color, fill_opacity=1.0,
                              title=tooltip_str_point)
    popup_msg = HTML()
    popup_msg.value = popup_point
    marker.popup = popup_msg
    map.add_layer(marker)

# ----------------------------------------------------------------------

#todo should we add zoom parameter?
def render_trajectories_ipyleaflet(trajectories,
                               #common arguments
                               map = None,
                               obj_ids = [],
                               #\/format [minLon, maxLon, minLat, maxLat]
                               map_bbox = None, 
                               show_lines = True,
                               gradient_hue = None,
                               color_map = '',
                               line_color = '',
                               linewidth = 2.4,
                               show_points = False,
                               point_size = 0.6,
                               point_color = '',
                               show_dot=True,
                               dot_size = 0.7,
                               dot_color = 'white',
                               trajectory_scalar_generator = path_length_fraction_generator,
                               trajectory_linewidth_generator = None, 
                               color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                               show = False, #by default when map is returned it shows. #todo can we fix this?
                               save=False,
                               filename='',

                               #ipyleaflet specific
                               tiles='cartodbdark_matter',
                               attr=".",
                               point_popup_properties = [],
                               show_distance_geometry = False,
                               distance_geometry_depth = 4,
                               show_scale = True,
                               max_zoom = 22,
                               **kwargs):
    """Render a list of trajectories using the ipyleaflet backend
    This function renders a list of trajectories to a ipyleaflet map.

    For documentation on the parameters, please see render_trajectories
    """
    import ipyleaflet as ipl #for now don't require unless using
    from ipywidgets.embed import embed_minimal_html
    trajectories, line_color, color_map, gradient_hue \
        = common_processing(trajectories,
                            obj_ids,
                            line_color,
                            color_map,
                            gradient_hue)
    if not trajectories: #nothing to render
        return

    if map == None:
        basemap = ipl.basemaps.CartoDB.DarkMatter #added
        if tiles.startswith('http://') or tiles.startswith('https://'):
            basemap = dict(url=tiles,
                           max_zoom=max_zoom,
                           attribution=attr,
                           name='custom')
        else:
            if tiles == 'OpenStreetMaps':
                basemap = ipl.basemaps.OpenStreetMap.Mapnik   #todo consider using ipyleaflets strings not foliums
            elif tiles == 'StamenTerrain':
                basemap = ipl.basemaps.Stamen.Terrain
            elif tiles == 'StamenToner':
                basemap = ipl.basemaps.Stamen.Toner
            elif tiles == 'StamenWatercolor':
                basemap = ipl.basemaps.Stamen.Watercolor
            elif tiles == 'CartoDBPositron':
                basemap = ipl.basemaps.CartoDB.Positron
            #elif tiles == 'CartoDBDark_Matter' #default

        #others:
        #   basemap = ipl.basemaps.OpenStreetMap.BlackAndWhite
        #   basemap = ipl.basemaps.OpenStretMap.DE
        #   basemap = ipl.basemaps.OpenStreetMap.France
        #   basemap = ipl.basemaps.OpenStreetMap.HOT
        #   basemap = ipl.basemaps.OpenTopoMap
        #   basemap = ipl.basemaps.Hydda.Full
        #   basemap = ipl.basemaps.Hydda.Base
        #   basemap = ipl.basemaps.Esri.WorldStreetMap
        #   basemap = ipl.basemaps.Esri.DeLorme
        #   basemap = ipl.basemaps.Esri.WorldTopoMap
        #   basemap = ipl.basemaps.Esri.WorldImagery
        #   basemap = ipl.basemaps.Esri.NatGeoWorldMap
        #   basemap = ipl.basemaps.HikeBike.HikeBike
        #   basemap = ipl.basemaps.MtbMap
        #   basemap = ipl.basemaps.NASAGIBS.ModisTerraBands367CR
        #   basemap = ipl.basemaps.NASAGIBS.ModisTerraBands721CR
        #   basemap = ipl.basemaps.NASAGIBS.ModisAquaTrueColorCR
        #   basemap = ipl.basemaps.NASAGIBS.ModisAquaBands721CR
        #   basemap = ipl.basemaps.NASAGIBS.ViirsTrueColorCR
        #   basemap = ipl.basemaps.NASAGIBS.ViirsEarthAtNight2012
        #   basemap = ipl.basemaps.Strava.All
        #   basemap = ipl.basemaps.Strava.Ride
        #   basemap = ipl.basemaps.Strava.Run
        #   basemap = ipl.basemaps.Strava.Water
        #   basemap = ipl.basemaps.Strava.Winter

        map = ipl.Map(basemap=basemap, scroll_wheel_zoom=True, max_zoom=max_zoom)#changed #should we support disable scorlling?
        
        map.layout.width = '960px' #required to get fit bounds to work right #todo should be a parameter
        map.layout.height = '400px'

        if show_scale:
            map.add_control(ipl.ScaleControl(position='bottomleft'))

    for i, trajectory in enumerate(trajectories):
        coordinates = [(point[1], point[0]) for point in trajectory]

        #set up generators
        if trajectory_scalar_generator:
            scalars = trajectory_scalar_generator(trajectory)
        if trajectory_linewidth_generator:
            #Note: lines invisible below about .37
            widths = trajectory_linewidth_generator(trajectory) 

        current_color_map, current_point_cmap, mapper, point_mapper = \
            setup_colors(line_color, color_map, gradient_hue,
                         point_color, color_scale,
                         trajectory[0].object_id, i,
                         trajectory_linewidth_generator)

        if show_lines:
            #popup_str = str(trajectory[0].object_id)+'<br>'+ \
            #    trajectory[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')+ \
            #    '<br> to <br>'+ \
            #    trajectory[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S')
            #tooltip_str = str(trajectory[0].object_id)
            if type(current_color_map) is ListedColormap \
               and len(current_color_map.colors) == 1 \
               and trajectory_linewidth_generator == None: #Polyline ok
                line = ipl.Polyline(locations=coordinates,
                                    color=current_color_map.colors[0],
                                    weight = int(linewidth+0.5), opacity = 1,                                
                                    fill=False) #added
                map.add_layer(line)#changed
                #fol.PolyLine(coordinates,
                #             color=current_color_map.colors[0],
                #             weight=linewidth, opacity=1,
                #             tooltip=tooltip_str,
                #             popup=popup_str).add_to(map)
            else: #mapped color (not solid)
                last_pos = coordinates[0]
                for i, pos in enumerate(coordinates[1:]):
                    weight = linewidth
                    if trajectory_linewidth_generator:
                        weight = widths[i]
                    segment_color = rgb2hex(mapper.to_rgba(scalars[i]))
                    line = ipl.Polyline(locations=[last_pos, pos],
                                        color=segment_color,
                                        weight = int(weight+0.5), opacity = 1,                                
                                        fill=False) #added
                    map.add_layer(line)#changed
                    #fol.PolyLine([last_pos,pos],
                    #             color=segment_color, weight=weight,
                    #             opacity=1, tooltip=tooltip_str,
                    #             popup=popup_str).add_to(map)
                    last_pos = pos
        if show_points:
            for i, c in enumerate(coordinates[:-1]): #all but last (dot)
                point_radius = point_size*4
                if type(current_point_cmap) is ListedColormap \
                   and len(current_point_cmap.colors) == 1: # one color 
                    current_point_color = current_point_cmap.colors[0]
                else:
                    current_point_color = \
                        rgb2hex(point_mapper.to_rgba(scalars[i]))
                    
                render_point_ipyleaflet(trajectory[i],
                                        point_popup_properties, c,
                                        point_radius,
                                        current_point_color, map)
        if show_dot:
            render_point_ipyleaflet(trajectory[-1],
                                    point_popup_properties,
                                    coordinates[-1], dot_size,
                                    dot_color, map)

        if show_distance_geometry:
            render_distance_geometry_folium(distance_geometry_depth,
                                            trajectory,
                                            map)

    if map_bbox:
    #    map.fit_bounds([(map_bbox[2], map_bbox[0]),
    #                  (map_bbox[3], map_bbox[1])])
        #todo make a centroid function, unify with else code below
        center_lon = map_bbox[0]+((map_bbox[1]-map_bbox[0])/2.0) #added
        center_lat = map_bbox[2]+((map_bbox[3]-map_bbox[2])/2.0) #added
        map.center = (center_lat, center_lon)#added
        map.zoom=4 #get_bounds_zoom(map, map_bbox)-1 #hack #todo fix
    else:
        raw_bbox = compute_bounding_box(itertools.chain(*trajectories))
        center_lon = raw_bbox.min_corner[0] + ((raw_bbox.max_corner[0] - raw_bbox.min_corner[0])/2.0)
        center_lat = raw_bbox.min_corner[1] + ((raw_bbox.max_corner[1] - raw_bbox.min_corner[1])/2.0)
        map.center = (center_lat, center_lon)#added
        map.zoom=get_bounds_zoom(map, raw_bbox)-1 #hack
    #    map.fit_bounds(bounding_box_for_folium(trajectories))
    
    if save:  #saves as .html document
        if not filename:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            filename = "trajs-"+datetime_str+'.html'
        embed_minimal_html(filename, views=[map], title='Widgets export')
    if show:
        display(map)
    return map
#todo look into deckgl and tripslayer and mapbox. 
# ----------------------------------------------------------------------


def render_trajectories_bokeh(trajectories,
                              map = None,
                              obj_ids = [],
                              line_color = '',
                              show_lines = True,
                              show_points = False,
                              **kwargs):
    """Render a list of trajectories using the bokeh backend
    This function renders a list of trajectories to a bokeh map.

    Currently not officially supported.  Just for evaluation!
    """
    from bokeh.plotting import figure, show, output_file
    from bokeh.tile_providers import get_provider, Vendors
    from bokeh.io import output_notebook
    from pyproj import Proj, transform
    from bokeh.models import Slider, HoverTool
    from bokeh.models import ColumnDataSource
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    trajectories, line_color, color_map, gradient_hue = \
        common_processing(trajectories, obj_ids, line_color,
                          color_map,gradient_hue)
    if not trajectories:
        return
    
    if in_notebook():
        output_notebook()

    p = figure(x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(tile_provider)

    for trajectory in trajectories:
        data = {}
        data['x_values'] = []
        data['y_values'] = []
        data['timestamps'] = []
        for point in trajectory:
            wm_point = transform(Proj(init='epsg:4326'),
                                 Proj(init='epsg:3857'),
                                 point[0], point[1])
            data['x_values'].append(wm_point[0])
            data['y_values'].append(wm_point[1])
            fmt_str='%H:%M:%S'
            data['timestamps'].append(point.timestamp.strftime(fmt_str))
        source = ColumnDataSource(data=data)
        color = random_color()

        if show_lines:
            #could plot multilines instead? (may be faster?)
            line = p.line('x_values', 'y_values', source=source,
                          line_width=2, color=color)
            #may need to rework with multiple trajectories? TODO
            hover_tool = HoverTool(tooltips=trajectory[0].object_id,
                                   renderers=[line])  
            p.tools.append(hover_tool)
        if show_points:
            points = p.circle(x='x_values', y='y_values', source=source,
                              size=3, color=color)
            #may need to rework with multiple trajectories? TODO
            hover_tool_point = HoverTool(tooltips='@timestamps',
                                         renderers=[points])  
            p.tools.append(hover_tool_point)

    show(p)

# ----------------------------------------------------------------------


#TODO could implement show distance geometry
def render_trajectories_cartopy(trajectories,
                                #common arguments
                                map = None,
                                obj_ids = [],
                                map_bbox = [],
                                show_lines=True,   
                                gradient_hue = None,
                                color_map = '',
                                line_color = '',
                                linewidth=2.4,
                                show_points=False,
                                point_size = 0.6,
                                point_color='',
                                show_dot = True,
                                dot_size = 0.7,
                                dot_color = 'white',
                                trajectory_scalar_generator = path_length_fraction_generator,
                                trajectory_linewidth_generator = None, 
                                color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                                show = True,
                                save=False,
                                filename='',

                                #cartopy specific arguments
                                map_projection = None,
                                transform = None,
                                **kwargs):
    """Render a list of trajectories using the cartopy backend
    This function renders a list of trajectories to a cartopy map.

    For documentation on the parameters, please see render_trajectories
    """
    trajectories, line_color, color_map, gradient_hue = \
        common_processing(trajectories, obj_ids, line_color, color_map,
                          gradient_hue)
    if not trajectories:
        return

    if not show_dot:
        dot_size = 0
    
    if in_notebook():
        if show:
            #below effectively does %matplotlib inline (display inline)
            get_ipython().magic("matplotlib inline")   #TODO may casue issues may want to remove
            #TODO figure out how to get matplotlib not to show after
            #     executing code a second time.  
    figure = plt.figure(dpi=100, figsize=(12,6.75))
    if not map_bbox: #if it's empty
        map_bbox = compute_bounding_box(itertools.chain(*trajectories),
                                        buffer=(.1, .1))
    if not show_lines:
        linewidth=0

    color_maps = []

    for i, trajectory in enumerate(trajectories):
        if line_color != '':
            #call setup colors here insead at some point
            if isinstance(line_color, list):
                color_maps.append(get_constant_color_cmap(line_color[i]))
            else:
                color_maps.append(get_constant_color_cmap(line_color))
        elif color_map != '':
            if isinstance(color_map, list):
                color_maps.append(color_map[i])
            else:
                color_maps.append(color_map)
        elif gradient_hue != None:
            if isinstance(gradient_hue, list):
                color_maps.append(hue_gradient_cmap(gradient_hue[i]))
            else:
                color_maps.append(hue_gradient_cmap(gradient_hue))
        else:
           color_maps.append(hue_gradient_cmap(hash_short_md5(trajectory[0].object_id)))

    if map == None:   
        (map, map_actors) = mapmaker(domain='terrestrial',
                                     map_name='custom',
                                     map_bbox=map_bbox,
                                     map_projection = map_projection)

    #color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)
    #15 and .8 below accounts for differeing units in folium and cartopy
    paths.draw_traffic(traffic_map = map,
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
                       show_lines=show_lines)
    #Don't support: label_objects, label_generator, label_kwargs, axes, zorder

    if not in_notebook() or save:
        if filename:
            plt.savefig(filename)
        else:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            plt.savefig("trajs-"+datetime_str+".png")
    return map

# ----------------------------------------------------------------------


def random_hue():
    """Returns a random hue value (0 to 1)
    """
    return random.uniform(0,1)

# ----------------------------------------------------------------------


def random_color():
    """Returns a random RGB color in hex string format
    """
    r = lambda: random.randint(0,255)
    return '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

# ----------------------------------------------------------------------


def bounding_box_for_folium(trajectories):
    """Translates a computed bounding box to the format needed by folium
    """
    raw_bbox = compute_bounding_box(itertools.chain(*trajectories))
    #folium needs two corner points [sw, ne], with lat first, then lon
    # for each
    box_for_folium = [(raw_bbox.min_corner[1], raw_bbox.min_corner[0]),
                      (raw_bbox.max_corner[1], raw_bbox.max_corner[0])]
    return box_for_folium

# ----------------------------------------------------------------------


def in_notebook():
    """Returns True if run within a Jupyter notebook, and false otherwise
    """
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip == None:
            return False
        if 'IPKernelApp' not in ip.config:
            return False
    except ImportError:
        return False
    return True

