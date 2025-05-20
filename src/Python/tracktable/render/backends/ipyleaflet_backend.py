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
tracktable.render.ipyleaflet - render trajectories in using the ipyleaflet backend
"""

import itertools
import math
from datetime import datetime

import matplotlib
from matplotlib.colors import ListedColormap, rgb2hex
from tracktable.core.geomath import compute_bounding_box
from tracktable.render.map_decoration import coloring
from tracktable.render.map_processing import common_processing

EARTH_RADIUS = 6378137
MAX_LATITUDE = 85.0511287798

#todo should we add zoom parameter?
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
                               show_dot=True,
                               dot_size = 0.7,
                               dot_color = 'white',
                               trajectory_scalar_generator = common_processing.path_length_fraction_generator,
                               trajectory_linewidth_generator = None,
                               color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                               show = False, #by default when map is returned it shows. #todo can we fix this?
                               save=False,
                               filename='',

                               # ipyleaflet specific args
                               tiles='cartodbdark_matter',
                               attr=".",
                               point_popup_properties = [],
                               show_distance_geometry = False,
                               distance_geometry_depth = 4,
                               show_scale = True,
                               max_zoom = 22,
                               **kwargs):
    """Render a list of trajectories using the ipyleaflet backend

        For documentation on the parameters, please see render_trajectories

        Currently not officially supported. Just for experimentation!
    """

    # Don't require dependencies unless using this backend
    import ipyleaflet as ipl
    from ipywidgets.embed import embed_minimal_html

    trajectories, line_color, color_map, gradient_hue \
        = common_processing.common_processing(trajectories,
                            obj_ids,
                            line_color,
                            color_map,
                            gradient_hue)

    if not trajectories: #nothing to render
        return

    if map_canvas == None:
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

        map_canvas = ipl.Map(basemap=basemap, scroll_wheel_zoom=True, max_zoom=max_zoom)#changed #should we support disable scorlling?

        map_canvas.layout.width = '960px' #required to get fit bounds to work right #todo should be a parameter
        map_canvas.layout.height = '400px'

        if show_scale:
            map_canvas.add_control(ipl.ScaleControl(position='bottomleft'))

    for i, trajectory in enumerate(trajectories):
        coordinates = [(point[1], point[0]) for point in trajectory]

        #set up generators
        if trajectory_scalar_generator:
            scalars = trajectory_scalar_generator(trajectory)
        if trajectory_linewidth_generator:
            #Note: lines invisible below about .37
            widths = trajectory_linewidth_generator(trajectory)

        current_color_map, current_point_cmap, mapper, point_mapper = \
            coloring.setup_colors(line_color, color_map, gradient_hue,
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
                map_canvas.add_layer(line)#changed
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
                    map_canvas.add_layer(line)#changed
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
                                        current_point_color, map_canvas)
        if show_dot:
            render_point_ipyleaflet(trajectory[-1],
                                    point_popup_properties,
                                    coordinates[-1], dot_size,
                                    dot_color, map_canvas)

        if show_distance_geometry:
            common_processing.render_distance_geometry('folium', distance_geometry_depth,
                                     trajectory, map_canvas)

    if map_bbox:
    #    map.fit_bounds([(map_bbox[1], map_bbox[0]),
    #                  (map_bbox[3], map_bbox[2])])
        #todo make a centroid function, unify with else code below
        center_lon = map_bbox[0]+((map_bbox[2]-map_bbox[0])/2.0) #added
        center_lat = map_bbox[1]+((map_bbox[3]-map_bbox[1])/2.0) #added
        map.center = (center_lat, center_lon)#added
        map.zoom=4 #get_bounds_zoom(map, map_bbox)-1 #hack #todo fix
    else:
        raw_bbox = compute_bounding_box(itertools.chain(*trajectories))
        center_lon = raw_bbox.min_corner[0] + ((raw_bbox.max_corner[0] - raw_bbox.min_corner[0])/2.0)
        center_lat = raw_bbox.min_corner[1] + ((raw_bbox.max_corner[1] - raw_bbox.min_corner[1])/2.0)
        map_canvas.center = (center_lat, center_lon)#added
        map_canvas.zoom=get_bounds_zoom(map_canvas, raw_bbox)-1 #hack
    #    map.fit_bounds(bounding_box_for_folium(trajectories))

    if save:  #saves as .html document
        if not filename:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            filename = "trajs-"+datetime_str+'.html'
        embed_minimal_html(filename, views=[map_canvas], title='Widgets export')
    if show:
        display(map_canvas)
    return map_canvas
#todo look into deckgl and tripslayer and mapbox.

# ----------------------------------------------------------------------

def render_point_ipyleaflet(current_point,
                            point_popup_properties, coord, point_radius,
                            point_color, map_canvas):
    """Renders a point to the ipyleaflet map.

    Currently not officially supported. Just for experimentation!

    Args:
        current_point (point): Current point of the trajectory
        point_popup_properties (list): Point properties
        coord (tuple): Coordinates to render point
        point_radius (int): Size of the point to render
        point_color (str): Color of the point to render
        map (Basemap): ipyleaflet map

    Returns:
        No return value

    """
    # Don't require dependencies unless using this backend
    import ipyleaflet as ipl
    from ipywidgets import HTML

    tooltip_str_point = common_processing.point_tooltip(current_point)
    popup_point = common_processing.point_popup(current_point,
                              point_popup_properties)

    marker = ipl.CircleMarker(location=coord, radius=int(point_radius+0.5),
                              stroke=False, fill=True, color=point_color,
                              fill_color=point_color, fill_opacity=1.0,
                              title=tooltip_str_point)
    popup_msg = HTML()
    popup_msg.value = popup_point
    marker.popup = popup_msg
    map_canvas.add_layer(marker)

# ----------------------------------------------------------------------

#The following is needed because ipyleaflet currently does not support
#fit_bounds

def transform(point, scale):
    """ Transform the given point based on the scale factor

    Args:
        point (point): Point transform
        scale (int): Scale factor to transform by

    Return:
        Scaled (x,y) values

    """
    transform_factor = 0.5 / (math.pi * EARTH_RADIUS)
    x = scale * ((transform_factor*point[0])+0.5)
    y = scale * ((-transform_factor*point[1])+0.5)
    return (x,y)

# ----------------------------------------------------------------------

#spherical mercator projection #checked with https://epsg.io/transform#s_srs=4326&t_srs=3857
def project_spherical_mercator(latlng):
    """ Project the spherical mercator for a given lat long value

    Args:
        latlng (point): Point transform

    Return:
        Projection of spherical mercator

    """
    d = math.pi / 180.0
    lat = max(min(MAX_LATITUDE, latlng[1]), -MAX_LATITUDE)
    sin = math.sin(lat * d)
    return (EARTH_RADIUS * latlng[0] * d, EARTH_RADIUS * math.log((1+sin) / (1-sin)) / 2)

# ----------------------------------------------------------------------

def crs_zoom(scale):
    """ Zoom the CRS based on scale factor
    """
    return math.log(scale / 256) / math.log(2)

# ----------------------------------------------------------------------

def crs_scale(zoom):
    """ Scale the CRS based on zoom factor
    """
    return 256 * math.pow(2, zoom)

# ----------------------------------------------------------------------

def project(latlng, zoom):
    """ Projects a geographical coordinate according to the projection of the map's CRS then scales it according to zoom and the CRS's Transformation

    Args:
        latlng (point): Point to project
        zoom (int): Zoom value to scale by

    Returns:
        Pixel coord relative to the CRS origin
    """
    #check zoom?
    projectedPoint = project_spherical_mercator(latlng)
    scale = crs_scale(zoom)
    return transform(projectedPoint, scale)

# ----------------------------------------------------------------------

def get_scale_zoom(scale, from_zoom):
    """ Get zoom scale factor
    """
    zoom = crs_zoom(scale * crs_scale(from_zoom))
    return zoom # check for Nan?

# ----------------------------------------------------------------------

def get_bounds_zoom(map_canvas, bounds, inside=True, size=[960,400], padding=[0,0]): #ignore padding for now #fix size
    """ Get the zoom if the bounding box corners

    Args:
        map (Basemap): Map containing bounding box
        bounds (point): Long-Lat point of the bounding box corners

    Keyword Arguments:
        inside (bool): Flag to indicate inside of the bounding box
        size (list): Size of the bouning box
        padding (list): Padding of boundries

    Returns:
        The maximum zoom level on which the given bounds fit to the map vie in its entirety

    """

    #bounds is min_corner max_corner lon,lat
    #size = size=padding
    #boundsSize = toBounds(this.project(se, zoom), this.project(nw, zoom)).getSize()
    current_zoom = map_canvas.zoom
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

    return max(map_canvas.min_zoom, min(map_canvas.max_zoom, zoom))
