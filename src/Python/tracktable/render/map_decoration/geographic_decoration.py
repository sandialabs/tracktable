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

"""Render cities, coastlines, etc onto maps"""

import logging

from typing import List, Tuple

import cartopy
import cartopy.crs
import cartopy.mpl.geoaxes

import matplotlib
import matplotlib.collections
import matplotlib.colors
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib import pyplot
from tracktable.core.geomath import longitude_degree_size
from tracktable.info import airports, borders, ports, rivers, shorelines
from tracktable.render.backends.patch_cartopy_download_url import \
    patch_cartopy_backend

logger = logging.getLogger(__name__)

cities = None

def _ensure_cities_loaded():
    global cities
    if cities is None:
        from tracktable.info import cities

def draw_largest_cities(map_axes,
                        num_cities,
                        label_size=10,
                        dot_size=2,
                        label_color='white',
                        dot_color='white',
                        zorder=10):
    """Decorate a map with the N largest cities

    Args:
       map_axes (GeoAxes): Map to decorate
       num_cities (int): Draw cities with at least this large a population

    Keyword Args:
       label_size (int): Font size (points) for label (Default: 10)
       dot_size (int): Size (in points) of dot marking city location (Default: 2)
       label_color (str): Color (name or hex string) for city labels (Default: 'white')
       dot_color (str): Color (name or hex string) for city markers (Default: 'white')
       zorder (int): Image layer (z-order) for cities (Default: 10)

    Returns:
       A list of artists added to the map

    """

#    map_extent = map_axes.get_extent(map_axes.tracktable_projection)
    map_extent = map_axes.get_extent()
    map_bbox_lowerleft = (map_extent[0], map_extent[2])
    map_bbox_upperright = (map_extent[1], map_extent[3])

    _ensure_cities_loaded()
    all_cities = cities.cities_in_bbox(map_bbox_lowerleft, map_bbox_upperright)

    def get_population(city): return city.population

    cities_to_draw = sorted(all_cities,
                            key=get_population,
                            reverse=True)[0:num_cities]

    return draw_cities(map_axes,
                       cities_to_draw,
                       label_size=label_size,
                       dot_size=dot_size,
                       label_color=label_color,
                       dot_color=dot_color,
                       zorder=zorder)

# ----------------------------------------------------------------------


def draw_cities_larger_than(map_axes,
                            minimum_population,
                            label_size=10,
                            dot_size=2,
                            label_color='white',
                            dot_color='white',
                            zorder=10,
                            axes=None):
    """Decorate a map with all cities larger than a given population

    Args:
       mymap (Basemap): Basemap instance to decorate
       minimum_population (int): Draw cities with at least this large a population

    Keyword Args:
       label_size (int): Font size (points) for label (Default: 10)
       dot_size (int): Size (in points) of dot marking city location (Default: 2)
       label_color (str): Color (name or hex string) for city labels (Default: 'white')
       dot_color (str): Color (name or hex string) for city markers (Default: 'white')
       zorder (int): Image layer (z-order) for cities (Default: 10)
       axes (Matplotlib axes): Matplotlib axes instance to render into (Default: None)

    Returns:
       A list of artists added to the axes

    """

    map_extent = map_axes.get_extent()
    map_bbox_lowerleft = (map_extent[0], map_extent[2])
    map_bbox_upperright = (map_extent[1], map_extent[3])
#    map_bbox_lowerleft = map_axes.viewLim[0]
#    map_bbox_upperright = map_axes.viewLim[1]
    _ensure_cities_loaded()
    all_cities = cities.cities_in_bbox(map_bbox_lowerleft, map_bbox_upperright)

    cities_to_draw = [
        city for city in all_cities if city.population > minimum_population
    ]

    return draw_cities(map_axes,
                       cities_to_draw,
                       label_size=label_size,
                       dot_size=dot_size,
                       label_color=label_color,
                       dot_color=dot_color)

# ----------------------------------------------------------------------


def draw_cities(map_axes,
                cities_to_draw,
                label_size=12,
                dot_size=2,
                label_color='white',
                dot_color='white',
                zorder=10,
                transform=None,
                map_name=None,
                map_bbox=None,
                country=None,
                location=None):
    """Decorate a map with specified number of cities

    Args:
       map_axes (GeoAxes): Map to decorate
       cities_to_draw (int): Draw specified amount of cities

    Keyword Args:
       label_size (int): Font size (points) for label (Default: 10)
       dot_size (int): Size (in points) of dot marking city location (Default: 2)
       label_color (str): Color (name or hex string) for city labels (Default: 'white')
       dot_color (str): Color (name or hex string) for city markers (Default: 'white')
       zorder (int): Image layer (z-order) for cities (Default: 10)
       transform (cartopy crs object): Transform the corrdinate system (Default: None)

    Returns:
       A list of artists added to the axes

    """

    # TODO (mjfadem): draw_cities needs to be updated to function like draw_ports and draw_airports
    # along with keeping it's existing functionality

    # TODO: Transform is kwarg here but doesn't exist in the params
    # for draw_cities_larger_than() and draw_largest_cities() which
    # call this function
    if transform is None:
        transform = cartopy.crs.PlateCarree()

    artists = []
    if cities_to_draw and len(cities_to_draw) > 0:
        city_longitudes = [city.longitude for city in cities_to_draw]
        city_latitudes = [city.latitude for city in cities_to_draw]

        artists.append(
            map_axes.scatter(
                city_longitudes,
                city_latitudes,
                s=dot_size,
                color=dot_color,
                zorder=zorder,
                transform=transform
            ))

        # Label them with their names
        for city in cities_to_draw:
            longitude = city.longitude
            latitude = city.latitude
            text_artist = map_axes.annotate(
                text=city.name,
                xy=(longitude, latitude),
                xytext=(6, 0),
                textcoords="offset points",
                fontsize=label_size,
                color=label_color,
                ha="left",
                va="center",
                zorder=zorder,
                xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
            )
            artists.append(text_artist)

    return artists

# ----------------------------------------------------------------------


def draw_airports(map_axes,
                airport_list=[],
                label_size=12,
                dot_size=2,
                label_color='white',
                dot_color='red',
                zorder=10,
                transform=cartopy.crs.PlateCarree(),
                map_name=None,
                map_bbox=None,
                airport_bounding_box=None,
                draw_all_airports=False,
                draw_arrows=True):
    """Decorate a map with airports

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       airport_list (list(str)): IATA code of airports to render onto the map (Default: [])
       label_size (int): Font size (points) for label (Default: 10)
       dot_size (int): Size (in points) of dot marking airport location (Default: 2)
       label_color (str): Color (name or hex string) for airport labels (Default: 'white')
       dot_color (str): Color (name or hex string) for airport markers (Default: 'white')
       zorder (int): Image layer (z-order) for airports (Default: 10)
       transform (cartopy crs object): Transform the corrdinate system (Default: cartopy.crs.PlateCarree())
       map_name (str): Name of the map to draw on (Default: None)
       map_bbox (BoundingBox): Bounding box of the map being decorated (Default: None)
       airport_bounding_box (BoundingBox or tuple/list of points): bounding box for
            rendering airports within. (Default: None)
       draw_all_airports (bool): Draw all of the airports in the bounding box (Default: False)
       draw_arrows (bool): Whether or not to draw arrows from airport labels to corresponding dots (Default: True)

    Returns:
       A list of artists added to the axes

    """

    artists = []
    if map_name and map_name != "custom" and map_name.split(':')[0].lower() == "airport": # We're rendering an airport specifc map
        airport_code = map_name.split(':')[1]
        airport = airports.airport_information(airport_code)
        longitude = airport.position[0]
        latitude = airport.position[1]

        artists.append(
            map_axes.scatter(
                longitude,
                latitude,
                s=dot_size,
                color=dot_color,
                zorder=zorder,
                transform=transform
            )
        )

        if draw_arrows:
            text_artist = map_axes.annotate(
                text=airport_code,
                xy=(longitude, latitude),
                xytext=(-20, 20),
                textcoords="offset points",
                fontsize=label_size,
                color=label_color,
                ha="left",
                va="bottom",
                zorder=zorder,
                xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
                arrowprops=dict(color=label_color,
                                arrowstyle="->")
            )
        else:
            text_artist = map_axes.annotate(
                text=airport_code,
                xy=(longitude, latitude),
                xytext=(-10, 5),
                textcoords="offset points",
                fontsize=label_size,
                color=label_color,
                ha="left",
                va="bottom",
                zorder=zorder,
                xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
            )

        artists.append(text_artist)

    else: # We're rendering a custom map
        display_all_airports = True
        all_airports = []

        if draw_all_airports and not airport_bounding_box:
            display_all_airports = False
            for airport_name, airport in airports.all_airports_within_bounding_box(map_bbox).items():
                all_airports.append(airport)

        elif airport_bounding_box and not draw_all_airports:
            display_all_airports = False
            for airport_name, airport in airports.all_airports_within_bounding_box(airport_bounding_box).items():
                all_airports.append(airport)

        elif airport_bounding_box and draw_all_airports:
            logger.info("`airport_bounding_box` and `draw_all_airports` both provided, using `map_bbox`.")
            display_all_airports = False
            for airport_name, airport in airports.all_airports_within_bounding_box(map_bbox).items():
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
            longitude = airport.position[0]
            latitude = airport.position[1]

            artists.append(
                map_axes.scatter(
                    longitude,
                    latitude,
                    s=dot_size,
                    color=dot_color,
                    zorder=zorder,
                    transform=transform
                )
            )

            if draw_arrows:
                text_artist = map_axes.annotate(
                    text=airport.name,
                    xy=(longitude, latitude),
                    xytext=(-20, 20),
                    textcoords="offset points",
                    fontsize=label_size,
                    color=label_color,
                    ha="left",
                    va="bottom",
                    zorder=zorder,
                    xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
                    arrowprops=dict(color=label_color,
                                    arrowstyle="->")
                )
            else:
                text_artist = map_axes.annotate(
                    text=airport.name,
                    xy=(longitude, latitude),
                    xytext=(-10, 5),
                    textcoords="offset points",
                    fontsize=label_size,
                    color=label_color,
                    ha="left",
                    va="bottom",
                    zorder=zorder,
                    xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
                )

            artists.append(text_artist)

    return artists

# ----------------------------------------------------------------------


def draw_ports(map_axes,
                port_list=[],
                label_size=12,
                dot_size=2,
                label_color='white',
                dot_color='blue',
                zorder=10,
                transform=cartopy.crs.PlateCarree(),
                map_name=None,
                map_bbox=None,
                country=None,
                port_country=None,
                port_water_body=None,
                port_wpi_region=None,
                port_bounding_box=None,
                port_and_country_seperate=False,
                draw_all_ports=False,
                draw_arrows=True):
    """Decorate a map with specified number of ports

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       port_list (list(str)): Name or WPI index number of ports to render onto the map (Default: [])
       label_size (int): Font size (points) for label (Default: 10)
       dot_size (int): Size (in points) of dot marking port location (Default: 2)
       label_color (str): Color (name or hex string) for port labels (Default: 'white')
       dot_color (str): Color (name or hex string) for port markers (Default: 'white')
       zorder (int): Image layer (z-order) for ports (Default: 10)
       transform (cartopy crs object): Transform the corrdinate system (Default: cartopy.crs.PlateCarree())
       map_name (str): Name of the map to draw on (Default: None)
       map_bbox (BoundingBox): Bounding box of the map being decorated (Default: None)
       country (str): Name of the country the port is located in (Default: None)
       port_country (str): Name of country to render ports in. (Default: None)
       port_water_body (str): Name of body of water to render ports on. (Default: None)
       port_wpi_region (str): Name of WPI region to render ports in. (Default: None)
       port_bounding_box (BoundingBox or tuple/list of points): bounding box for rendering ports within. (Default: None)
       port_and_country_seperate (bool): Bool for searching the ports database for a port and not considering it's country to see if it's rendered. i.e. You want to render a port in the U.K. while rendering all ports in Japan. (Default: False)
        draw_arrows (bool): Whether or not to draw arrows from airport labels to corresponding dots (Default: True)

    Returns:
       A list of artists added to the axes

    """

    artists = []
    if map_name and map_name != "custom" and map_name.split(':')[0].lower() == "port": # We're rendering an port specifc map
        port_name = map_name.split(':')[1]
        port = ports.port_information(port_name, country=country)
        port_name = port.name
        longitude = port.position[0]
        latitude = port.position[1]

        artists.append(
            map_axes.scatter(
                longitude,
                latitude,
                s=dot_size,
                color=dot_color,
                zorder=zorder,
                transform=transform
            )
        )

        if draw_arrows:
            text_artist = map_axes.annotate(
                text=port_name,
                xy=(longitude, latitude),
                xytext=(-20, 20),
                textcoords="offset points",
                fontsize=label_size,
                color=label_color,
                ha="left",
                va="bottom",
                zorder=zorder,
                xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
                arrowprops=dict(color=label_color,
                                arrowstyle="->")
            )
        else:
            text_artist = map_axes.annotate(
                text=port_name,
                xy=(longitude, latitude),
                xytext=(-10, 5),
                textcoords="offset points",
                fontsize=label_size,
                color=label_color,
                ha="left",
                va="bottom",
                zorder=zorder,
                xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
            )

        artists.append(text_artist)

    else: # We're rendering a custom map
        display_all_ports = True
        all_ports = []

        if draw_all_ports and not port_bounding_box:
            display_all_ports = False
            for port_index, port in ports.all_ports_within_bounding_box(map_bbox).items():
                all_ports.append(port)

        elif port_bounding_box and not draw_all_ports:
            display_all_ports = False
            for port_index, port in ports.all_ports_within_bounding_box(port_bounding_box).items():
                all_ports.append(port)

        elif port_bounding_box and draw_all_ports:
            logger.info("`airport_bounding_box` and `draw_all_ports` both provided, using `map_bbox`.")
            display_all_ports = False
            for port_index, port in ports.all_ports_within_bounding_box(map_bbox).items():
                all_ports.append(port)

        if port_water_body:
            display_all_ports = False
            for port_index, port in ports.all_ports_by_water_body(port_water_body).items():
                all_ports.append(port)

        if port_wpi_region:
            display_all_ports = False
            for port_index, port in ports.all_ports_by_wpi_region(port_wpi_region).items():
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
            longitude = port.position[0]
            latitude = port.position[1]

            artists.append(
                map_axes.scatter(
                    longitude,
                    latitude,
                    s=dot_size,
                    color=dot_color,
                    zorder=zorder,
                    transform=transform
                )
            )

            if draw_arrows:
                text_artist = map_axes.annotate(
                    text=port.name,
                    clip_on=True,
                    xy=(longitude, latitude),
                    xytext=(-20, 20),
                    textcoords="offset points",
                    fontsize=label_size,
                    color=label_color,
                    ha="left",
                    va="bottom",
                    zorder=zorder,
                    xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
                    arrowprops=dict(color=label_color,
                                    arrowstyle="->")
                )
            else:
                text_artist = map_axes.annotate(
                    text=port.name,
                    clip_on=True,
                    xy=(longitude, latitude),
                    xytext=(-10, 5),
                    textcoords="offset points",
                    fontsize=label_size,
                    color=label_color,
                    ha="left",
                    va="bottom",
                    zorder=zorder,
                    xycoords=transform._as_mpl_transform(map_axes), # https://stackoverflow.com/a/25421922, the given transformation gets destroyed by annotate
                )

            artists.append(text_artist)

    return artists


# ----------------------------------------------------------------------

def draw_shorelines(map_axes,
                    zorder=7,
                    map_bbox=None,
                    shoreline_list=[],
                    shoreline_color='red',
                    shoreline_fill_polygon=True,
                    shoreline_fill_color='red',
                    shoreline_bounding_box=None,
                    shoreline_resolution='low',
                    shoreline_level='L1',
                    draw_all_shorelines=False,
                    transform=cartopy.crs.PlateCarree()):
    """Decorate a map with shorelines

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       map_name (str): Name of the map to draw on (Default: None)
       map_bbox (BoundingBox): Bounding box of the map being decorated (Default: None)
       zorder (int): Image layer (z-order) for shorelines (Default: 10)
       shoreline_list (list(int)): GSHHS index number of the shoreline polygons to render (Default: [])
       shoreline_color (name of standard color as string, hex color string or matplotlib color object): Color of the shoreline (Default: 'red')
       shoreline_zorder (int): Image layer for shorelines (Default: 7)
       shoreline_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
       shoreline_level (string): See the docstring for build_shoreline_dict() for more information about levels. (Default: "L1")
       shoreline_bounding_box (BoundingBox): Bounding box for rendering shorelines within. (Default: None)
       shoreline_fill_polygon (bool): Whether or not to fill in the inside of the shoreline polygon (Default: True)
       shoreline_fill_color (name of standard color as string, hex color string or
            matplotlib color object): Fill color of the shoreline (Default: 'red')
       transform (cartopy crs object): Transform the corrdinate system (Default: cartopy.crs.PlateCarree())

    Returns:
       A list of artists added to the axes

    """

    artists = []
    display_all_shorelines = True
    all_shorelines = []

    if draw_all_shorelines and not shoreline_bounding_box:
        display_all_shorelines = False
        for shoreline_name, shoreline in shorelines.all_shorelines_within_bounding_box(map_bbox, resolution=shoreline_resolution, level=shoreline_level).items():
            all_shorelines.append(shoreline)

    elif shoreline_bounding_box and not draw_all_shorelines:
        display_all_shorelines = False
        for shoreline_name, shoreline in shorelines.all_shorelines_within_bounding_box(shoreline_bounding_box, resolution=shoreline_resolution, level=shoreline_level).items():
            all_shorelines.append(shoreline)

    elif shoreline_bounding_box and draw_all_shorelines:
        logger.info("`shoreline_bounding_box` and `draw_all_shorelines` both provided, using `map_bbox`.")
        display_all_shorelines = False
        for shoreline_name, shoreline in shorelines.all_shorelines_within_bounding_box(map_bbox, resolution=shoreline_resolution, level=shoreline_level).items():
            all_shorelines.append(shoreline)

    if len(shoreline_list) > 0:
        display_all_shorelines = False
        for shoreline in shoreline_list:
            all_shorelines.append(shorelines.shoreline_information(shoreline, resolution=shoreline_resolution, level=shoreline_level))

    if display_all_shorelines:
        all_shorelines = shorelines.all_shorelines(resolution=shoreline_resolution, level=shoreline_level)
    else:
        # Remove duplicates since there is a chance you'll double up on ports with how this code is structured
        all_shorelines = list(set(all_shorelines))

    if shoreline_fill_polygon:
        artists.append(
            map_axes.add_geometries([shoreline.polygon for shoreline in all_shorelines],
                                    crs = transform,
                                    edgecolor=shoreline_color,
                                    zorder = zorder,
                                    facecolor=shoreline_fill_color)
        )
    else:
        artists.append(
            map_axes.add_geometries([shoreline.polygon for shoreline in all_shorelines],
                                    crs = transform,
                                    edgecolor=shoreline_color,
                                    zorder = zorder,
                                    facecolor='none')
        )

    return artists

# ----------------------------------------------------------------------

def draw_rivers(map_axes,
                    zorder=7,
                    map_bbox=None,
                    river_list=[],
                    river_color='blue',
                    river_bounding_box=None,
                    river_resolution='low',
                    river_level='L01',
                    draw_all_rivers=False,
                    transform=cartopy.crs.PlateCarree()):
    """Decorate a map with rivers

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       map_name (str): Name of the map to draw on (Default: None)
       map_bbox (BoundingBox): Bounding box of the map being decorated (Default: None)
       zorder (int): Image layer (z-order) for rivers (Default: 10)
       river_list (list(int)): GSHHS index number of the river polygons to render (Default: [])
       river_color (name of standard color as string, hex color string or matplotlib color object): Color of the river (Default: 'blue')
       river_zorder (int): Image layer for rivers (Default: 7)
       river_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
       river_level (string): See the docstring for build_river_dict() for more information about levels. (Default: "L1")
       river_bounding_box (BoundingBox): Bounding box for rendering rivers within. (Default: None)
       transform (cartopy crs object): Transform the corrdinate system (Default: cartopy.crs.PlateCarree())

    Returns:
       A list of artists added to the axes

    """
    artists = []
    display_all_rivers = True
    all_rivers = []

    if draw_all_rivers and not river_bounding_box:
        display_all_rivers = False
        for river_name, river in rivers.all_rivers_within_bounding_box(map_bbox, resolution=river_resolution, level=river_level).items():
            all_rivers.append(river)

    elif river_bounding_box and not draw_all_rivers:
        display_all_rivers = False
        for river_name, river in rivers.all_rivers_within_bounding_box(river_bounding_box, resolution=river_resolution, level=river_level).items():
            all_rivers.append(river)

    elif river_bounding_box and draw_all_rivers:
        logger.info("`river_bounding_box` and `draw_all_rivers` both provided, using `map_bbox`.")
        display_all_rivers = False
        for river_name, river in rivers.all_rivers_within_bounding_box(map_bbox, resolution=river_resolution, level=river_level).items():
            all_rivers.append(river)

    if len(river_list) > 0:
        display_all_rivers = False
        for river in river_list:
            all_rivers.append(rivers.river_information(river, resolution=river_resolution, level=river_level))

    if display_all_rivers:
        all_rivers = rivers.all_rivers(resolution=river_resolution, level=river_level)
    else:
        # Remove duplicates since there is a chance you'll double up on ports with how this code is structured
        all_rivers = list(set(all_rivers))

    artists.append(
        map_axes.add_geometries([river.polygon for river in all_rivers],
                                crs = transform,
                                edgecolor=river_color,
                                zorder = zorder,
                                facecolor='none')
    )

    return artists

# ----------------------------------------------------------------------

def draw_borders(map_axes,
                    zorder=7,
                    map_bbox=None,
                    border_list=[],
                    border_color='green',
                    border_bounding_box=None,
                    border_resolution='low',
                    border_level='L1',
                    draw_all_borders=False,
                    transform=cartopy.crs.PlateCarree()):
    """Decorate a map with borders

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       map_name (str): Name of the map to draw on (Default: None)
       map_bbox (BoundingBox): Bounding box of the map being decorated (Default: None)
       zorder (int): Image layer (z-order) for borders (Default: 10)
       border_list (list(int)): GSHHS index number of the border polygons to render (Default: [])
       border_color (name of standard color as string, hex color string or matplotlib color object): Color of the border (Default: 'green')
       border_zorder (int): Image layer for borders (Default: 7)
       border_resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
       border_level (string): See the docstring for build_border_dict() for more information about levels. (Default: "L1")
       border_bounding_box (BoundingBox): Bounding box for rendering borders within. (Default: None)
       transform (cartopy crs object): Transform the corrdinate system (Default: cartopy.crs.PlateCarree())

    Returns:
       A list of artists added to the axes

    """

    artists = []
    display_all_borders = True
    all_borders = []

    if draw_all_borders and not border_bounding_box:
        display_all_borders = False
        for border_name, border in borders.all_borders_within_bounding_box(map_bbox, resolution=border_resolution, level=border_level).items():
            all_borders.append(border)

    elif border_bounding_box and not draw_all_borders:
        display_all_borders = False
        for border_name, border in borders.all_borders_within_bounding_box(border_bounding_box, resolution=border_resolution, level=border_level).items():
            all_borders.append(border)

    elif border_bounding_box and draw_all_borders:
        logger.info("`border_bounding_box` and `draw_all_borders` both provided, using `map_bbox`.")
        display_all_borders = False
        for border_name, border in borders.all_borders_within_bounding_box(map_bbox, resolution=border_resolution, level=border_level).items():
            all_borders.append(border)

    if len(border_list) > 0:
        display_all_borders = False
        for border in border_list:
            all_borders.append(borders.border_information(border, resolution=border_resolution, level=border_level))

    if display_all_borders:
        all_borders = borders.all_borders(resolution=border_resolution, level=border_level)
    else:
        # Remove duplicates since there is a chance you'll double up on ports with how this code is structured
        all_borders = list(set(all_borders))

    artists.append(
        map_axes.add_geometries([border.polygon for border in all_borders],
                                crs = transform,
                                edgecolor=border_color,
                                zorder = zorder,
                                facecolor='none')
    )

    return artists

# ----------------------------------------------------------------------

def draw_countries(map_axes,
                   linewidth=0.5,
                   zorder=4,
                   edgecolor='#606060',
                   resolution='10m',
                   **kwargs):
    """Decorate a map with countries

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       linewidth (float): Width of the country borders (Default: 0.5)
       zorder (int): Image layer (z-order) for countries (Default: 4)
       edgecolor (str): Color (name or hex string) for country borders (Default: '#606060')
       resolution (str): Detail of country borders (Default: '10m')
       kwargs (dict): Arguments to be passed to Matplotlib text renderer for label (Default: dict())

    Returns:
       A list of Matplotlib artists added to the figure.

    """

    patch_cartopy_backend()

    country_borders = cartopy.feature.NaturalEarthFeature(
        'cultural',
        'admin_0_boundary_lines_land',
        resolution
        )

    map_axes.add_feature(country_borders,
                         edgecolor=edgecolor,
                         facecolor='none',
                         linewidth=linewidth,
                         zorder=zorder)


    return [country_borders]

# ----------------------------------------------------------------------

def draw_states(map_axes,
                resolution='10m',
                linewidth=0.25,
                zorder=3,
                facecolor='#606060',
                edgecolor='#A0A0A0',
                **kwargs):
    """Decorate a map with states

    Args:
       map_axes (GeoAxes): Map to decorate

    Keyword Args:
       resolution (str): Detail of state borders (Default: '10m')
       linewidth (float): Width of the state borders (Default: 0.25)
       zorder (int): Image layer (z-order) for countries (Default: 3)
       facecolor (str): Color (name or hex string) for states (Default: '#606060')
       edgecolor (str): Color (name or hex string) for state borders (Default: '#A0A0A0')
       kwargs (dict): Arguments to be passed to Matplotlib text renderer for label (Default: dict())

    Returns:
       A list of Matplotlib artists added to the figure.

    """

    patch_cartopy_backend()

    return [map_axes.add_feature(
        cartopy.feature.STATES.with_scale(resolution),
        linewidth=linewidth,
        zorder=zorder,
        facecolor=facecolor,
        edgecolor=edgecolor,
        **kwargs)]


# ----------------------------------------------------------------------

def draw_coastlines(map_axes,
                    edgecolor='#808080',
                    resolution='50m',
                    linewidth=0.2,
                    zorder=5,
                    **kwargs):
    """Draw coastlines onto a GeoAxes instance

    Args:
       map_axes (GeoAxes): GeoAxes from mapmaker

    Keyword Args:
       border_color (colorspec): Color for coastlines (Default: #808080, Medium Gray)
       resolution (str): Resolution for coastlines.  A value of None means 'don't draw'.  The values '110m', '50m' and '10m' specify increasingly detailed coastlines. (Default: '50m')
       linewidth (float): Stroke width in points for coastlines.  (Defaults: 0.2)
       zorder (int): Drawing layer for coastlines.  Layers with higher Z-order are drawn on top of those with lower Z-order. (Default: 5)
       kwargs (dict): Arguments to be passed to Matplotlib text renderer for label (Default: dict())

    Returns:
       A list of Matplotlib artists added to the map.

    """

    patch_cartopy_backend()

    coastlines = cartopy.feature.NaturalEarthFeature(
        name='coastline',
        category='physical',
        scale=resolution,
        edgecolor=edgecolor,
        facecolor='none',
        linewidth=linewidth,
        zorder=zorder)

    map_axes.add_feature(coastlines)
    return [coastlines]

# ----------------------------------------------------------------------


def fill_land(map_axes,
              edgecolor='none',
              facecolor='#303030',
              linewidth=0.1,
              resolution='110m',
              zorder=None):
    """Fill in land (continents and islands)

    Given a GeoAxes instance, fill in the land on a map with a
    specified color.

    Args:
      map_axes (GeoAxes): Map instance to render onto

    Keyword Args:
       edgecolor (str): Color (name or hex string) for land borders (Default: 'none')
       facecolor (str): Color (name or hex string) for land (Default: '#303030')
       linewidth (float): Width of the land borders (Default: 0.1)
       resolution (str): Detail of land borders (Default: '110m')
       zorder (int): Image layer (z-order) for countries (Default: None)

    Returns:
       A list of Matplotlib artists added to the map.

    """

    patch_cartopy_backend()

    landmass = cartopy.feature.NaturalEarthFeature(
        name='land',
        category='physical',
        scale=resolution,
        edgecolor=edgecolor,
        facecolor=facecolor
        )
    map_axes.add_feature(landmass)
    return [landmass]


# ----------------------------------------------------------------------


def fill_oceans(map_axes,
                facecolor='#101020',
                resolution='110m',
                zorder=None):
    """Fill in oceans

    Given a GeoAxes instance, fill in the oceans on a map with a
    specified color.

    Args:
      map_axes (GeoAxes): Map instance to render onto

    Keyword Args:
      facecolor (str): Color (name or hex string) for ocean (Default: '#101020')
      resolution (str): Detail of ocean borders (Default: '110m')
      zorder (int): Image layer (z-order) for oceans (Default: None)

    Returns:
       A list of Matplotlib artists added to the map.

    """

    patch_cartopy_backend()

    oceans = cartopy.feature.NaturalEarthFeature(
        name='ocean',
        category='physical',
        scale=resolution,
        edgecolor='none',
        facecolor=facecolor
        )
    map_axes.add_feature(oceans)
    return [oceans]


# ----------------------------------------------------------------------


def fill_lakes(map_axes,
               edgecolor='none',
               facecolor='#101020',
               resolution='110m',
               zorder=None):
    """Fill in lakes

    Given a GeoAxes instance, fill in the lakes on a map with a
    specified color.

    Args:
      map_axes (GeoAxes): Map instance to render onto

    Keyword Args:
      edgecolor (str): Color (name or hex string) for lake borders (Default: 'none')
      facecolor (str): Color (name or hex string) for lakes (Default: '#101020')
      resolution (str): Detail of lake borders (Default: '110m')
      zorder (int): Image layer (z-order) for lake (Default: None)

    Returns:
       A list of Matplotlib artists added to the map.

    """

    patch_cartopy_backend()
    lakes = cartopy.feature.NaturalEarthFeature(
        name='lakes',
        category='physical',
        scale=resolution,
        edgecolor=edgecolor,
        facecolor=facecolor
        )
    map_axes.add_feature(lakes)
    return [lakes]

# ----------------------------------------------------------------------


def draw_lonlat(map_axes,
                spacing=10,
                zorder=5,
                draw_labels=False,
                linewidth=0.25,
                color='#C0C0C0'):
    """Fill in lonlat

    Given a GeoAxes instance, fill in the lonlat lines on a map with a
    specified color.

    Args:
      map_axes (GeoAxes): Map instance to render onto

    Keyword Args:
      spacing (int): Spacing between the lon lat lines (Default: 10)
      zorder (int): Image layer (z-order) for lonlat lines (Default: 5)
      linewidth (float): Width of the lonlat lines (Default: 0.25)
      color (str): Color (name or hex string) for lonlat lines (Default: '#C0C0C0')

    Returns:
       A list of Matplotlib artists added to the map.

    """

    artist = map_axes.gridlines(
        draw_labels=draw_labels,
        color=color,
        linewidth=linewidth,
        zorder=zorder
        )

    if draw_labels:
        artist.xformatter = LONGITUDE_FORMATTER
        artist.yformatter = LATITUDE_FORMATTER

    return [artist]

# ----------------------------------------------------------------------

def draw_scale(mymap,
               length_in_km=10,
               label_color='#C0C0C0',
               label_size=10,
               linewidth=1,
               zorder=20):
    """ Fill in map scale

    Given a GeoAxes instance, fill in a scale on a map.

    Args:
      map_axes (GeoAxes): Map instance to render onto

    Keyword Args:
      length_in_km (int): Scale's representative length (Default: 10)
      label_color (str): Color (name or hex string) for scale (Default: '#C0C0C0')
      label_size (str): Size of the scale label (Default: 10)
      linewidth (float): Width of the scale (Default: 1)
      zorder (int): Image layer (z-order) for scale (Default: 20)

    Returns:
       A list of Matplotlib artists added to the map.
    """

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

def _find_map_scale_endpoints(extent: Tuple[float, float, float, float], scale_length_in_km: float):
    min_lon, max_lon, min_lat, max_lat = extent

    longitude_span = max_lon - min_lon
    latitude_span = max_lat - min_lat

    # Position the scale 5% up from the bottom of the figure
    scale_latitude = min_lat + 0.05 * latitude_span

    scale_length_in_degrees = scale_length_in_km / longitude_degree_size(scale_latitude)
    if scale_length_in_degrees > 0.9 * longitude_span:
        raise RuntimeError("draw_scale: Requested map scale size ({} km) is too large to fit on map ({} km near bottom).".format(scale_length_in_km, longitude_span * longitude_degree_size(scale_latitude)))

    # Position the scale 5% in from the left edge of the map
    scale_longitude_start = min_lon + 0.05 * longitude_span
    scale_longitude_end = scale_longitude_start + scale_length_in_degrees

    return [ (scale_longitude_start, scale_latitude), (scale_longitude_end, scale_latitude) ]

# ----------------------------------------------------------------------

def _find_map_scale_tick_endpoints(extent: Tuple[float, float, float, float], scale_length_in_km: float):
    min_lon, max_lon, min_lat, max_lat = extent

    latitude_span = max_lat - min_lat

    scale_endpoints = _find_map_scale_endpoints(extent, scale_length_in_km)

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

    geodetic_projection = cartopy.crs.PlateCarree()
    geodetic_extent = mymap.get_extent(crs=geodetic_projection)

    world_scale_endpoints = _find_map_scale_endpoints(geodetic_extent, scale_length_in_km)
    world_tick_endpoints = _find_map_scale_tick_endpoints(geodetic_extent, scale_length_in_km)

    screen_scale_endpoints = [ world_scale_endpoints[0], world_scale_endpoints[1] ]
    screen_tick_endpoints = [ (world_tick_endpoints[0][0], world_tick_endpoints[0][1]),
                              (world_tick_endpoints[1][0], world_tick_endpoints[1][1]) ]

    # Assemble line segments
    # We could also use paths.points_to_segments to do this
    segments = [ screen_tick_endpoints[0], (screen_scale_endpoints[0], screen_scale_endpoints[1]),
        screen_tick_endpoints[1] ]

    linewidths = [ linewidth ] * len(segments)
    colors = [ color ] * len(segments)
    map_scale_segments = matplotlib.collections.LineCollection(
        segments,
        zorder=zorder,
        colors=colors,
        linewidths=linewidths,
        transform=geodetic_projection)

    axes.add_artist(map_scale_segments)
    return [map_scale_segments]

# ----------------------------------------------------------------------

def _draw_map_scale_label(mymap,
                          scale_length_in_km,
                          axes=None,
                          color='#FFFFFF',
                          fontsize=12,
                          zorder=10):

    if axes is None:
        axes = pyplot.gca()


    original_projection = mymap.projection

    # We use PlateCarree when we're getting the map extent because it uses
    # geodetic coordinates.
    geodetic_projection = cartopy.crs.PlateCarree()
    geodetic_extent = mymap.get_extent(crs=geodetic_projection)

    min_lon, max_lon, min_lat, max_lat = geodetic_extent

    longitude_span = max_lon - min_lon
    latitude_span = max_lat - min_lat

    world_scale_endpoints = _find_map_scale_endpoints(geodetic_extent, scale_length_in_km)

    longitude_center = 0.5 * (world_scale_endpoints[0][0] + world_scale_endpoints[1][0])

    text_centerpoint_world = ( longitude_center, world_scale_endpoints[0][1] + 0.01 * latitude_span )
    text_centerpoint_screen = text_centerpoint_world

    text_artist = pyplot.text(
        text_centerpoint_screen[0], text_centerpoint_screen[1],
        '{} km'.format(int(scale_length_in_km)),
        fontsize=fontsize,
        color=color,
        horizontalalignment='center',
        verticalalignment='bottom',
        transform=geodetic_projection
        )

    axes.add_artist(text_artist)

    return text_artist



# ----------------------------------------------------------------------

def fill_background(mymap, border_color='#000000', bgcolor='#000000', linewidth=1):
    """ fill_background has not been implemented yet
    """
    raise NotImplementedError(
      ("tracktable.render.geographic_decoration: fill_background has not "
       "been ported to Cartopy"))

    result = mymap.drawmapboundary(color=border_color, fill_color=bgcolor, linewidth=linewidth)
    return result
