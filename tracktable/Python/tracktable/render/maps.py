#
# Copyright (c) 2014-2017 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.

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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


#
# tracktable/render/maps.py - Friendly interface around Basemap
#
# The functions in this file make it easy to draw maps of various
# interesting places around the world.

# TODO:
#
# map_for_country?
#
# australia_map
# north_america_map

from __future__ import print_function, division

import itertools
import math
import matplotlib
import numpy
import pprint
import string
import sys

from mpl_toolkits.basemap import Basemap
from matplotlib import pyplot
from ..info import airports, cities
from . import paths

CONVENIENCE_MAPS = {
    'conus': {
        'projection': 'mill',
        'llcrnrlon': -130,
        'llcrnrlat': 22,
        'urcrnrlon': -65,
        'urcrnrlat': 50
    },

    'europe': {
        'projection': 'mill',
        'llcrnrlon': -11,
        'llcrnrlat': 34,
        'urcrnrlon': 35,
        'urcrnrlat': 72
    },

    'north_america': {
        'projection': 'stere',
        'width': 8000000,
        'height': 8000000,
        'lat_ts': 45,
        'lat_0': 45,
        'lon_0': -107
    },

    'south_america': {
        'projection': 'mill',
        'llcrnrlon': -85,
        'llcrnrlat': -60,
        'urcrnrlon': -30,
        'urcrnrlat': 35
    },

    'australia': {
        'projection': 'mill',
        'llcrnrlon': 110,
        'llcrnrlat': -45,
        'urcrnrlon': 155,
        'urcrnrlat': -10
    },

    'world': {
        'projection': 'mill',
        'llcrnrlon': -180,
        'llcrnrlat': -90,
        'urcrnrlon': 180,
        'urcrnrlat': 90
    }
}

# ----------------------------------------------------------------------

def available_maps():
    global CONVENIENCE_MAPS
    return CONVENIENCE_MAPS.keys()

# ----------------------------------------------------------------------

def _flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

# ----------------------------------------------------------------------

def map_for_airport(airport_code,
                    region_size=(200,200),
                    projection='mill',
                    **kwargs):

    """Draw a map for a region surrounding an airport.

    map_for_airport(airport_code, (string - example 'ORD' or 'KORD' for O'Hare
                    region_size = (200,200)
                    projection='mill') -> Basemap map instance

    Create a map for the region surrounding the requested airport.

    The region will be a rectangle in lon/lat space with the specified
    width and height in KM.  We'll do our best to convert those into a
    lat/lon bounding box.

    We default to the Miller Cylindrical projection.  It does a pretty
    good job of showing the world in familiar shapes although
    distortion sets in above/below about 50 degrees.  Fortunately,
    things are still quite recognizable.  If you would prefer a
    different projection then change the value of projection from
    'mill' to something else.

    This function returns the artists from matplotlib and draws the
    map as a side effect.
    """

    # TODO: Not all Basemap projections take the parameters we supply
    # here.  Find out which ones do and enforce the choice of one of
    # them.

    airport_info = airports.airport_information(airport_code)
    if airport_info is None:
        sys.stderr.write("ERROR: Can't find information for airport '%s'!\n" % airport_code)
        return None

    width = region_size[0]
    height = region_size[1]

    airport_location = airport_info.position

    latitude_span = height / _latitude_degree_width(airport_location[1])

    bottom_latitude = airport_location[1] - latitude_span / 2
    top_latitude = airport_location[1] + latitude_span / 2

    # Allow for the possibility that we've gone past the poles
    if top_latitude > 90:
        top_latitude = 90 - top_latitude
    if bottom_latitude < -90:
        bottom_latitude = -180 - bottom_latitude

    longitude_width_at_top = max(_longitude_degree_width(top_latitude), 1)
    longitude_width_at_bottom = max(_longitude_degree_width(bottom_latitude), 1)

    # This could go wrong at very high latitudes but seems OK for now
    longitude_span = width / min(longitude_width_at_top, longitude_width_at_bottom)

    mymap = Basemap(projection=projection,
                    resolution='h',
                    llcrnrlon = airport_location[0] - longitude_span/2,
                    llcrnrlat = bottom_latitude,
                    urcrnrlon = airport_location[0] + longitude_span/2,
                    urcrnrlat = top_latitude,
                    **kwargs)

    return (mymap, [])

# ----------------------------------------------------------------------

def map_parameters_for_airport(airport_code,
                               region_size=(200,200),
                               **kwargs):

    width = region_size[0]
    height = region_size[1]

    airport_info = airports.airport_information(airport_code)
    if airport_info is None:
        raise KeyError("ERROR: Can't find information for airport '{}'".format(airport_code))

    airport_location = airport_info.position

    latitude_span = height / _latitude_degree_width(airport_location[1])

    bottom_latitude = airport_location[1] - latitude_span / 2
    top_latitude = airport_location[1] + latitude_span / 2

    # Allow for the possibility that we've gone past the poles
    if top_latitude > 90:
        top_latitude = 90 - top_latitude
    if bottom_latitude < -90:
        bottom_latitude = -180 - bottom_latitude

    longitude_width_at_top = max(_longitude_degree_width(top_latitude), 1)
    longitude_width_at_bottom = max(_longitude_degree_width(bottom_latitude), 1)

    # This could go wrong at very high latitudes but seems OK for now
    longitude_span = width / min(longitude_width_at_top, longitude_width_at_bottom)

    basemap_kwargs = { 'projection': 'mill',
                       'llcrnrlon': airport_location[0] - longitude_span/2,
                       'llcrnrlat': bottom_latitude,
                       'urcrnrlon': airport_location[0] + longitude_span/2,
                       'urcrnrlat': top_latitude }
    basemap_kwargs.update(kwargs)

    return basemap_kwargs

# ----------------------------------------------------------------------

def draw_custom_map(projection,
                    bounding_box,
                    resolution='i',
                    axes=None):
    """Draw a map with custom projection and bounding box.

    Args:
      projection (string): One of Basemap's projection strings
      bounding_box (4 floats): (ll_longitude, ll_latitude, ur_longitude, ur_latitude)
      resolution (character in [ 'c', 'l', 'i', 'h', 'f' or None ]): resolution for boundary data
      ax (matplotlib.Axes): axes into which to render
    """

    mymap = Basemap(projection=projection,
                    llcrnrlon=bounding_box.min_corner[0],
                    llcrnrlat=bounding_box.min_corner[1],
                    urcrnrlon=bounding_box.max_corner[0],
                    urcrnrlat=bounding_box.max_corner[1],
                    resolution=resolution,
                    ax=axes)

    return (mymap, list())

# ----------------------------------------------------------------------

def predefined_map(mapname,
                   resolution='i',
                   ax=None,
                   region_size=None,
                   **kwargs):
    """Convenient wrapper function to create a map of one of several familiar regions in the world.

    Args:
      mapname: String naming which predefined map you want
      resolution: One of 'c', 'l', 'i', 'h', 'f' specifying coastline resolution from low to high
      ax: Matplotlib axes object to attah to map


    Keyword args:
      region_size: How wide map should be in map's distance units

    Returns:
      (projection, list(artists))

    You can either request a geographic map (see available_maps() for
    a list of names) or a map around an airport.  For the airport,
    specify the name 'airport:XXX' where XXX is the airport's 3-letter
    identifier.  For example, Atlanta Hartsfield-Jackson Airport is
    ATL.  London's Heathrow airport is LHR.
    """

    my_kwargs = dict(kwargs)
    if region_size is not None:
        my_kwargs['region_size'] = region_size

    global CONVENIENCE_MAPS

    map_parameters = {}

    if mapname.lower().startswith('airport:'):
        map_parameters = map_parameters_for_airport(mapname.upper().split(':')[1], **my_kwargs)
    else:
        if mapname not in CONVENIENCE_MAPS:
            raise KeyError("Map name '{}' is not in the list of convenience maps.  Legal values: {}".format(mapname, CONVENIENCE_MAPS.keys()))

        map_parameters = dict(CONVENIENCE_MAPS[mapname])

    if resolution:
        map_parameters['resolution'] = resolution
    if ax:
        map_parameters['ax'] = ax

    mymap = Basemap(**map_parameters)
    return (mymap, [])

# ----------------------------------------------------------------------


# ----------------------------------------------------------------------

def add_coastlines(mymap,
                   border_color='#808080',
                   resolution='i',
                   linewidth=0.2,
                   zorder=None,
                   **kwargs):
    """Draw coastlines onto a Basemap instance

    Args:
       mymap (Basemap): Map projection

    Keyword Args:
       border_color (colorspec): Color for coastlines (default #808080, a medium gray)
       resolution (string): Resolution for coastlines.  A value of None means 'don't draw'.  The values 'c', 'l', 'i', 'h' and 'f' specify increasingly detailed coastlines ('c' is for Coarse, 'f' is for Full detail).  Defaults to 'i'.
       linewidth (float): Stroke width in points for coastlines.  Defaults to 0.2.
       zorder (int): Drawing layer for coastlines.  Layers with higher Z-order are drawn on top of those with lower Z-order.

    Returns:
       A list of Matplotlib artists added to the map.
    """

    result = mymap.drawcoastlines(linewidth=linewidth, color=border_color, zorder=zorder)
    return [ result ]

draw_coastlines = add_coastlines

# ----------------------------------------------------------------------

def fill_continents(mymap,
                    land_color='#303030',
                    sea_color='#000000',
                    linewidth=0.1,
                    zorder=None):
    """Fill in land and sea on a map instance

    Given a Basemap instance, draw borders of continents and then fill
    both land and sea with user-specified colors.

    Args:
      mymap (mpl_toolkits.basemap.Basemap): Map instance to render onto

    Keyword Args:
      land_color (string): Color specification for land.  Can be either a common name or a 6-digit hex string.
      sea_color (string): Color specification for oceans.  Can be either a common name or a 6-digit hex string.
      linewidth (float): Stroke width (in points) for coastlines
      zorder (integer or None): Image layer for coastlines

    TODO:
      If we're using a Basemap then we also need an Axes optional argument.

    TODO:
      We're missing an argument for the border color.

    TODO:
      Is this the method that mapmaker actually uses?
    """

    fill_background(mymap,
                    bgcolor=sea_color,
                    linewidth=linewidth)
    return mymap.fillcontinents(color=land_color,
                                lake_color=sea_color,
                                zorder=zorder)


# ----------------------------------------------------------------------

def fill_background(mymap, border_color='#000000', bgcolor='#000000', linewidth=1):
    result = mymap.drawmapboundary(color=border_color, fill_color=bgcolor, linewidth=linewidth)
    return result



# ----------------------------------------------------------------------

def _latitude_degree_width(latitude):
    """
    _latitude_degree_width(latitude: float between -90 and 90) -> float (in km)

    Compute the distance between adjacent degrees of latitude centered
    on a given parallel.  This measurement is 111.694km at the equator
    and 110.574km at the poles.  This is a small enough variation that
    we'll just use linear interpolation.
    """

    return (math.fabs(latitude) / 90) * (110.574 - 111.694) + 111.594

# ----------------------------------------------------------------------

def _longitude_degree_width(latitude):
    """*
    _longitude_degree_width(longitude: float between -90 and 90) -> float (in km)

    Compute the difference between adjacent degrees of longitude at a
    given latitude.  This varies from 111.32km at the equator to 0 at
    the poles and decreases as the cosine of increasing latitude.
    """

    def d2r(d):
        return math.pi * d / 180

    return 111.32 * math.cos(d2r(math.fabs(latitude)))

# ----------------------------------------------------------------------


def draw_largest_cities(mymap,
                        num_cities,
                        label_size=10,
                        dot_size=2,
                        label_color='white',
                        dot_color='white',
                        zorder=10,
                        axes=None):
    """Decorate a map with the N largest cities

    Args:
       mymap:              Basemap instance to decorate
       minimum_population: Draw cities with at least this large a population
       label_size:         Font size (points) for label
       dot_size:           Size (in points) of dot marking city location
       label_color:        Color (name or hex string) for city labels
       dot_color:          Color (name or hex string) for city markesr
       zorder:             Image layer (z-order) for cities
       axes:               Matplotlib axes instance to render into

    Returns:
       A list of artists added to the axes
    """

    map_bbox_lowerleft = ( mymap.llcrnrlon, mymap.llcrnrlat )
    map_bbox_upperright = ( mymap.urcrnrlon, mymap.urcrnrlat )
    all_cities = cities.cities_in_bbox(map_bbox_lowerleft, map_bbox_upperright)

    def get_population(city): return city.population

    cities_to_draw = sorted(all_cities, key=get_population, reverse=True)[0:num_cities]

    return draw_cities(mymap,
                       cities_to_draw,
                       label_size=label_size,
                       dot_size=dot_size,
                       label_color=label_color,
                       dot_color=dot_color,
                       zorder=zorder,
                       axes=axes)

# ----------------------------------------------------------------------

def draw_cities_larger_than(mymap,
                            minimum_population,
                            label_size=10,
                            dot_size=2,
                            label_color='white',
                            dot_color='white',
                            zorder=10,
                            axes=None):
    """Decorate a map with all cities larger than a given population

    Args:
       mymap:              Basemap instance to decorate
       minimum_population: Draw cities with at least this large a population
       label_size:         Font size (points) for label
       dot_size:           Size (in points) of dot marking city location
       label_color:        Color (name or hex string) for city labels
       dot_color:          Color (name or hex string) for city markesr
       zorder:             Image layer (z-order) for cities
       axes:               Matplotlib axes instance to render into

    Returns:
       A list of artists added to the axes

    """

    map_bbox_lowerleft = ( mymap.llcrnrlon, mymap.llcrnrlat )
    map_bbox_upperright = ( mymap.urcrnrlon, mymap.urcrnrlat )
    all_cities = cities.cities_in_bbox(map_bbox_lowerleft, map_bbox_upperright)

    cities_to_draw = [ city for city in all_cities if city.population > minimum_population ]

    return draw_cities(mymap,
                       cities_to_draw,
                       label_size=label_size,
                       dot_size=dot_size,
                       label_color=label_color,
                       dot_color=dot_color,
                       axes=axes)

# ----------------------------------------------------------------------

def draw_cities(mymap,
                cities_to_draw,
                label_size=12,
                dot_size=2,
                label_color='white',
                dot_color='white',
                zorder=10,
                axes=None):

    map_span = (mymap.urcrnrlon - mymap.llcrnrlon)
    artists = []
    if cities_to_draw and len(cities_to_draw) > 0:
        city_longitudes = [ city.longitude for city in cities_to_draw ]
        city_latitudes = [ city.latitude for city in cities_to_draw ]
        (city_x, city_y) = mymap(city_longitudes, city_latitudes)
        artists.append(mymap.scatter(city_x, city_y, s=dot_size, color=dot_color, zorder=zorder, axes=axes))

        # Label them with their names
        for city in cities_to_draw:
            longitude = city.longitude + 0.01 * map_span
            latitude = city.latitude
            (x, y) = mymap(longitude, latitude)
            artists.append(pyplot.text(x, y, city.name, fontsize=label_size, color=label_color, ha='left', va='center', zorder=zorder, axes=axes))

    return artists

# ----------------------------------------------------------------------

def draw_coastlines(mymap,
                    linewidth=1,
                    zorder=4,
                    color='#606060'):

    return [ mymap.drawcoastlines(color=color, linewidth=linewidth, zorder=zorder) ]

# ----------------------------------------------------------------------

def draw_countries(mymap,
                   linewidth=0.5,
                   zorder=3,
                   color='#606060'):

    return [ mymap.drawcountries(color=color, linewidth=linewidth, zorder=zorder) ]

# ----------------------------------------------------------------------

def draw_states(mymap,
                linewidth=0.25,
                zorder=2,
                color='#606060'):

    return [ mymap.drawstates(color=color, linewidth=linewidth, zorder=zorder) ]

# ----------------------------------------------------------------------

def draw_lonlat(mymap,
                spacing=10,
                zorder=5,
                linewidth=0.25,
                color='#C0C0C0'):

    parallels = numpy.arange(-90, 90, spacing)
    meridians = numpy.arange(-180, 180, spacing)
    artists = []

    parallel_artists =  mymap.drawparallels(parallels,
                                             labels=[False, False, False, False],
                                             linewidth=linewidth,
                                             zorder=zorder,
                                             color=color)

    meridian_artists = mymap.drawmeridians(meridians,
                                           labels=[False, False, False, False],
                                           linewidth=linewidth,
                                           zorder=zorder,
                                           color=color)

    for artist_list_pair in parallel_artists.values():
        artists.extend(artist_list_pair[0])
        artists.extend(artist_list_pair[1])

    for artist_list_pair in meridian_artists.values():
        artists.extend(artist_list_pair[0])
        artists.extend(artist_list_pair[1])

    return artists

# ----------------------------------------------------------------------

def draw_scale(mymap,
               length_in_km,
               label_color,
               label_size,
               linewidth=1,
               zorder=20):

    artists = []

    artists.append(
        _draw_map_scale_line(mymap,
                             length_in_km,
                             color=label_color,
                             linewidth=linewidth,
                             zorder=zorder)
        )

    artists.append(
        _draw_map_scale_label(mymap,
                              length_in_km,
                              color=label_color,
                              fontsize=label_size,
                              zorder=zorder)
        )

    return artists


# ----------------------------------------------------------------------

def _find_map_scale_endpoints(mymap, scale_length_in_km):
    longitude_span = mymap.urcrnrlon - mymap.llcrnrlon
    latitude_span = mymap.urcrnrlat - mymap.llcrnrlat

    # Position the scale 5% up from the bottom of the figure
    scale_latitude = mymap.llcrnrlat + 0.05 * latitude_span

    scale_length_in_degrees = scale_length_in_km / _longitude_degree_width(scale_latitude)

    if scale_length_in_degrees > 0.9 * longitude_span:
        raise RuntimeError("draw_scale: Requested map scale size ({} km) is too large to fit on map ({} km near bottom).".format(length_in_km, longitude_span * _longitude_degree_width(scale_latitude)))

    # Position the scale 5% in from the left edge of the map
    scale_longitude_start = mymap.llcrnrlon + 0.05 * longitude_span
    scale_longitude_end = scale_longitude_start + scale_length_in_degrees

    return [ (scale_longitude_start, scale_latitude), (scale_longitude_end, scale_latitude) ]

# ----------------------------------------------------------------------

def _find_map_scale_tick_endpoints(mymap, scale_length_in_km):
    longitude_span = mymap.urcrnrlon - mymap.llcrnrlon
    latitude_span = mymap.urcrnrlat - mymap.llcrnrlat

    scale_endpoints = _find_map_scale_endpoints(mymap, scale_length_in_km)

    tick_height = 0.025 * latitude_span
    tick1_endpoints = [ (scale_endpoints[0][0], scale_endpoints[0][1] - 0.5 * tick_height),
                        (scale_endpoints[0][0], scale_endpoints[0][1] + 0.5 * tick_height) ]
    tick2_endpoints = [ (scale_endpoints[1][0], scale_endpoints[1][1] - 0.5 * tick_height),
                        (scale_endpoints[1][0], scale_endpoints[1][1] + 0.5 * tick_height) ]

    return (tick1_endpoints, tick2_endpoints)

# ----------------------------------------------------------------------

def _draw_map_scale_line(mymap,
                         scale_length_in_km,
                         axes=None,
                         color='#FFFFFF',
                         linewidth=1,
                         zorder=10):

    if axes is None:
        axes = pyplot.gca()

    longitude_span = mymap.urcrnrlon - mymap.llcrnrlon
    latitude_span = mymap.urcrnrlat - mymap.llcrnrlat

    world_scale_endpoints = _find_map_scale_endpoints(mymap, scale_length_in_km)
    world_tick_endpoints = _find_map_scale_tick_endpoints(mymap, scale_length_in_km)

    screen_scale_endpoints = [ mymap(*world_scale_endpoints[0]),
                               mymap(*world_scale_endpoints[1]) ]
    screen_tick_endpoints = [ (mymap(*world_tick_endpoints[0][0]), mymap(*world_tick_endpoints[0][1])),
                              (mymap(*world_tick_endpoints[1][0]), mymap(*world_tick_endpoints[1][1])) ]

    # Assemble line segments
    # We could also use paths.points_to_segments to do this
    segments = [
        screen_tick_endpoints[0],
        ( screen_scale_endpoints[0], screen_scale_endpoints[1] ),
        screen_tick_endpoints[1]
        ]

    linewidths = [ linewidth ] * len(segments)
    colors = [ color ] * len(segments)
    map_scale_segments = matplotlib.collections.LineCollection(
        segments,
        zorder=zorder,
        colors=colors,
        linewidths=linewidths
    )

    axes.add_artist(map_scale_segments)
    return map_scale_segments

# ----------------------------------------------------------------------

def _draw_map_scale_label(mymap,
                          scale_length_in_km,
                          axes=None,
                          color='#FFFFFF',
                          fontsize=12,
                          zorder=10):

    if axes is None:
        axes = pyplot.gca()

    longitude_span = mymap.urcrnrlon - mymap.llcrnrlon
    latitude_span = mymap.urcrnrlat - mymap.llcrnrlat

    world_scale_endpoints = _find_map_scale_endpoints(mymap, scale_length_in_km)

    longitude_center = 0.5 * (world_scale_endpoints[0][0] + world_scale_endpoints[1][0])

    text_centerpoint_world = ( longitude_center, world_scale_endpoints[0][1] + 0.01 * latitude_span )
    text_centerpoint_screen = mymap(*text_centerpoint_world)

    text_artist = pyplot.text(
        text_centerpoint_screen[0], text_centerpoint_screen[1],
        '{} km'.format(int(scale_length_in_km)),
        fontsize=fontsize,
        color=color,
        horizontalalignment='center',
        verticalalignment='bottom'
        )

    axes.add_artist(text_artist)

    return text_artist
