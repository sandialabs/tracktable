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
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
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

"""Convenience wrappers for geographic map creation and decoration
"""

import logging

import cartopy
import cartopy.crs
from matplotlib import pyplot
from tracktable.render.map_decoration import geographic_decoration as decoration
from tracktable.render.map_processing import maps


def render_map(domain='terrestrial', *args, **kwargs):
    """Generate a map for a given domain

    Keyword Args:
        domain (str): Domain to create the map in (Default: 'terrestrial')
        args (tuple): Arguments to be passed to specific map creation (Default: tuple)
        kwargs (dict): Any other arguments to customize the generated map (Default: dict)

    Returns:
        A terrestrial or cartesian domain map

    """

    if kwargs.get('map_bbox', None) is not None:
        kwargs['map_bbox'] = _make_bounding_box(kwargs['map_bbox'], domain)

    if domain == 'terrestrial':
        return terrestrial_map(*args, **kwargs)
    elif domain == 'cartesian' or domain == 'cartesian2d':
        return cartesian_map(*args, **kwargs)
    else:
        raise ValueError(('render_map only works on the terrestrial and '
                          ' cartesian2d domains, not "{}".').format(domain))

# ----------------------------------------------------------------------

def cartesian_map(map_bbox=None,
                  gridline_spacing=None,
                  axes=None,
                  **kwargs):
    """Create a Cartesian map

    Since Cartesian space is flat and undistinguished, a "map" is just
    a display region. You can also change the background color and
    draw axes/grid lines on the figure.

    Keyword Args:
        map_bbox ([minLon, minLat, maxLon, maxLat]): bounding box for
            custom map extent. By default automatically set to
            make all trajectories visible. (Default: None)
        gridline_spacing (int): Spaceing to put between grid lines (Default: None)
        axes (GeoAxes): Domain to create the map in (Default: None)
        kwargs (dict): Any other arguments to customize the generated map (Default: dict)

    Returns:
        A cartesian domain map

    """

    if axes is None:
        axes = pyplot.axes(projection=cartopy.crs.PlateCarree())

    logging.getLogger(__name__).debug(
        "cartesian_map: map_bbox is {}".format(map_bbox))

    axes.set_aspect(kwargs.get('aspect', 'equal'))
    if map_bbox is not None:
        axes.set_xlim(left=map_bbox.min_corner[0],
                      right=map_bbox.max_corner[0])
        axes.set_ylim(bottom=map_bbox.min_corner[1],
                      top=map_bbox.max_corner[1])

    return (axes, list())

# ----------------------------------------------------------------------

from cartopy.io.img_tiles import GoogleWTS
class Tiles(GoogleWTS):
    def __init__(self, url):
        """
        Set up a new instance to retrieve tiles from a map tiles URL.

        Parameters
        ----------
        url
            url template with locations for z (zoom), x, and y identified

        """
        self.url = url
        super(Tiles, self).__init__()

    def _image_url(self, tile):
        x, y, z = tile
        return self.url.format(z=z, y=y, x=x)

# ----------------------------------------------------------------------

def terrestrial_map(map_name,
                    draw_coastlines=True,
                    draw_countries=True,
                    draw_states=True,
                    draw_airports = False,
                    draw_ports = False,
                    draw_cities = False,
                    draw_largest_cities=None,
                    draw_cities_larger_than=None,
                    draw_lonlat=True,
                    draw_scale=True,
                    fill_land=True,
                    fill_water=True,
                    land_fill_color='#101010',
                    water_fill_color='#000000',
                    land_zorder=4,
                    water_zorder=4,
                    lonlat_spacing=10,
                    lonlat_color='#A0A0A0',
                    lonlat_linewidth=0.2,
                    lonlat_zorder=6,
                    scale_length_in_km=20,
                    scale_label_color='white',
                    scale_label_size=10,
                    scale_linewidth=1,
                    scale_zorder=6,
                    lonlat_labels=False,
                    coastline_color='#808080',
                    coastline_linewidth=1,
                    coastline_zorder=5,
                    country_color='#606060',
                    country_fill_color='#303030',
                    country_linewidth=0.5,
                    country_zorder=3,
                    state_color='#404040',
                    state_fill_color='none',
                    state_linewidth=0.3,
                    state_zorder=2,
                    city_label_size=12,
                    city_dot_size=2,
                    city_dot_color='white',
                    city_label_color='white',
                    city_zorder=6,
                    airport_list=[],
                    airport_label_size=12,
                    airport_dot_size=2,
                    airport_color='red',
                    airport_label_color='white',
                    airport_zorder=7,
                    airport_bounding_box=None,
                    port_list=[],
                    port_label_size=12,
                    port_dot_size=2,
                    port_color='blue',
                    port_label_color='white',
                    port_zorder=8,
                    port_country=None,
                    port_water_body=None,
                    port_wpi_region=None,
                    port_bounding_box=None,
                    port_and_country_seperate=False,
                    country_resolution='10m',
                    state_resolution='10m',
                    coastline_resolution='50m',
                    land_resolution='110m',
                    ocean_resolution='110m',
                    lake_resolution='110m',
                    map_bbox=None,
                    map_global=False,
                    map_projection=None,
                    region_size=None,
                    country=None,
                    location=None,
                    axes=None,
                    tiles=None,
                    tiles_zoom_level=8,
                    draw_all_ports=False,
                    draw_all_airports=False,
                    cities_to_draw=5,
                    draw_arrows=True,
                    **kwargs):
    """Create and decorate a terrestrial map

    Call the Cartopy toolkit to create a map of some predefined area,
    up to and including the entire world. The map will be decorated
    with some subset of coastlines, country borders, state/province
    borders and cities according to the keyword arguments you supply
    to render_map() or terrestrial_map().

    Args:
      map_name:            Region name ('region:<region>' or 'airport:<airport>' or 'port:<port>' or 'city:<city>' or 'custom'). Available regions are in tracktable.render.map_processing.maps.available_maps().

    Keyword Args:
      draw_coastlines (bool):                       Whether or not to draw coastlines on the map (Default: True)
      draw_countries (bool):                        Whether or not to draw country borders on the map (Default: True)
      draw_states (bool):                           Whether or not to draw US/Canada state borders (Default: True)
      draw_airports (bool):                         Whether or not to draw airports (Default: False)
      draw_ports (bool):                            Whether or not to draw ports (Default: False)
      draw_cities (bool):                           Whether or not to draw cities (Default: False)
      draw_largest_cities (int):                    Draw the N largest cities on the map (Default: None)
      draw_cities_larger_than (int):                Draw cities with populations greater than N (Default: None)
      draw_lonlat (bool):                           Whether or not to draw longitude/latitude lines (Default: True)
      draw_scale (bool):                            Whether or not to draw scale (Default: True)
      fill_land (bool):                             Whether or not to fill in the land areas (Default: True)
      fill_water (bool):                            Whether or not to fill in the land areas (Default: True)
      land_fill_color (str):                        Color name or hex string for land area (Default: '#101010')
      water_fill_color (str):                       Color name or hex string for sea area (Default: '#000000')
      land_zorder (int):                            Image layer for land (Default: 4)
      water_zorder (int):                           Image layer for sea (Default: 4)
      lonlat_spacing (int):                         Distance in degrees between lon/lat lines (Default: 10)
      lonlat_color (str):                           Color name or hex string for longitude/latitude lines (Default: '#A0A0A0')
      lonlat_linewidth (float):                     Width (in point) for lon/lat lines (Default: 0.2)
      lonlat_zorder (int):                          Image layer for coastlines (Default: 6)
      scale_length_in_km (int)                      Scale's representative length (Default: 10)
      scale_label_color (str):                      Color (name or hex string) for scale (Default: '#C0C0C0')
      scale_label_size (int):                       Size of the scale label (Default: 10)
      scale_linewidth (int):                        Width of the scale (Default: 1)
      scale_zorder (int):                           Image layer (z-order) for scale (Default: 20)
      lonlat_labels (bool):                         If True, draw lon/lat values at edges. (only for PlateCarree and Mercator)
      coastline_color (str):                        Color name or hex string for coastlines (Default: '#808080')
      coastline_linewidth (float):                  Width (in points) of coastlines (Default: 1)
      coastline_zorder (int):                       Image layer for coastlines (Default: 5)
      country_color (str):                          Color name or hex string for coastlines (Default: '#606060')
      country_fill_color (str):                     Color name or hex string for coastlines (Default:'#303030' )
      country_linewidth (float):                    Width (in points) of coastlines (Default: 0.5)
      country_zorder (int):                         Image layer for coastlines (Default: 3)
      state_color (str):                            Color name or hex string for coastlines (Default: '#404040')
      state_fill_color (str):                       Color name or hex string for coastlines (Default: 'none')
      state_linewidth (float):                      Width (in points) of coastlines (Default: 0.3)
      state_zorder (int):                           Image layer for coastlines (Default: 2)
      city_label_size (int):                        Size (in points) for city name labels (Default: 12)
      city_dot_size (int):                          Size (in points) for city markers (Default: 2)
      city_dot_color (str):                         Color name or hex string for city markers (Default: 'white')
      city_label_color (str):                       Color name or hex string for city names (Default: 'white')
      city_zorder (int):                            Color name or hex string for city names (Default: 6)
      airport_list (list(str)): IATA code of airports to render onto the map (Default: [])
      airport_label_size (int):                     Size (in points) for airport name labels (Default: 12)
      airport_dot_size (float):                     Radius of a airport dot (Default: 2)
      airport_color (name of standard color as string, hex color string or matplotlib color object): Color of the airport dot (Default: 'red')
      airport_label_color (str):                    Color name or hex string for airport names (Default: 'white')
      airport_zorder (int):                         Color name or hex string for airport names (Default: 6)
      port_bounding_box (BoundingBox or tuple/list of points): bounding box for rendering airports within. (Default: None)
      port_list (list(str)):                        Name or WPI index number of ports to render onto the map (Default: [])
      port_label_size (int):                        Size (in points) for port name labels (Default: 12)
      port_dot_size (int):                          radius of a port dot (Default: 2)
      port_color (name of standard color as string, hex color string or matplotlib color object): Color of the port dot (Default: 'blue')
      port_label_color (str):                       Color name or hex string for port names (Default: 'white')
      port_zorder (int):                            Color name or hex string for port names (Default: 6)
      port_country (str):                           Name of country to render ports in. (Default: None)
      port_water_body (str):                        Name of body of water to render ports on. (Default: None)
      port_wpi_region (str):                        Name of WPI region to render ports in. (Default: None)
      port_bounding_box (BoundingBox or tuple/list of points): bounding box for rendering ports within. (Default: None)
      port_and_country_seperate (bool):             Bool for searching the ports database for a port and not considering it's
                                                    country to see if it's rendered. i.e. You want to render a port in the U.K. while rendering all ports in
                                                    Japan. (Default: False)
      country_resolution (str):                     Detail of country borders (Default: '10m')
      state_resolution (str):                       Detail of state borders (Default: '10m')
      coastline_resolution (str):                   Detail of coastlines (Default: '500m')
      land_resolution (str):                        Detail of land (Default: '110m')
      ocean_resolution (str):                       Detail of oceans (Default: '110m')
      lake_resolution (str):                        Detail of lakes (Default: '110m')
      map_bbox ([minLon, minLat, maxLon, maxLat]):  Bounding box for custom map extent (Default: None)
      map_projection (Cartopy CRS):                 Cartopy CRS projection object (optional) (Default: None)
      map_global (bool):                            If True overrides map_bbox and uses the limits of the projection
      map_scale_length (float):                     Length of map scale indicator (in km) (Default: None)
      region_size (float):                          Size of region depicted around an airport (km width x km height) (Default: None)
      country (str):                                Two character country code for city maps, full country name for port maps. Required if a port or city name matches multiple items.  (Default: None).
      location (tuple, TrajectoryPoint, BasePoint): Location to search near, exclusively used for city maps (Default: None).
      region_size (float):                          Size of region depicted around an airport (km width x km height) (Default: None)
      axes (GeoAxes):                               Matplotlib axes to render into (Default: None)
      cities_to_draw (int):                         Number of cities to draw (Default: 5)
      draw_all_airports (bool):                     Draw all of the airports in the bounding box (Default: False)
      draw_all_ports (bool):                        Draw all of the ports in the bounding box (Default: False)
      draw_arrows (bool):                            Whether or not to draw arrows from airport/port labels to corresponding dots (Default: True)
      kwargs (dict):                                Any other arguments to customize the generated map (Default: dict)

    Raises:
      KeyError: unknown map name

    Returns:
      (GeoAxes, artist_list): Cartopy instance and a list of Matplotlib artists that were rendered
    """

    if map_global:
        map_axes = maps.instantiate_map_global(
            projection=map_projection
            )

    elif map_name == "custom":
        map_axes = maps.instantiate_map(
            min_corner=map_bbox.min_corner,
            max_corner=map_bbox.max_corner,
            projection=map_projection
            )

    else:
        map_axes = maps.predefined_map(
            map_name,
            country=country,
            location=location,
            region_size=region_size,
            projection=map_projection
            )
    artists = []

    if tiles != None:
        tiler = Tiles(tiles)
        map_axes.add_image(tiler, tiles_zoom_level)

    if draw_coastlines:
        artists.extend(
            decoration.draw_coastlines(
                map_axes,
                edgecolor=coastline_color,
                resolution=coastline_resolution,
                linewidth=coastline_linewidth,
                zorder=coastline_zorder
            ))

    if fill_land:
        artists.extend(
            decoration.fill_land(
                map_axes,
                facecolor=land_fill_color,
                resolution=land_resolution,
                zorder=land_zorder
                ))

    if fill_water:
        water_actors = decoration.fill_oceans(
            map_axes,
            facecolor=water_fill_color,
            resolution=ocean_resolution,
            zorder=water_zorder
            )
        lake_actors = decoration.fill_lakes(
            map_axes,
            facecolor=water_fill_color,
            resolution=lake_resolution,
            zorder=water_zorder
            )
        artists.extend(water_actors)
        artists.extend(lake_actors)

    if draw_countries:
        artists.extend(
            decoration.draw_countries(
                map_axes,
                linewidth=country_linewidth,
                zorder=country_zorder,
                edgecolor=country_color,
                resolution=country_resolution,
                facecolor=country_fill_color #TODO this doesn't appear to be used. (set to none)
                ))

    if draw_states:
        artists.extend(
            decoration.draw_states(
                map_axes,
                resolution=state_resolution,
                edgecolor=state_color,
                facecolor=state_fill_color,
                linewidth=state_linewidth,
                zorder=state_zorder
                ))

    if draw_lonlat:
        artists.extend(
            decoration.draw_lonlat(
                map_axes,
                spacing=lonlat_spacing,
                color=lonlat_color,
                draw_labels=lonlat_labels,
                linewidth=lonlat_linewidth,
                zorder=lonlat_zorder
                ))

    if draw_airports:
        artists.extend(
            decoration.draw_airports(
                map_axes,
                airport_list=airport_list,
                label_size=airport_label_size,
                dot_size=airport_dot_size,
                label_color=airport_label_color,
                dot_color=airport_color,
                zorder=airport_zorder,
                map_name=map_name,
                map_bbox=map_bbox,
                airport_bounding_box=airport_bounding_box,
                draw_all_airports=draw_all_airports,
                draw_arrows=draw_arrows
            ))

    if draw_ports:
        artists.extend(
            decoration.draw_ports(
                map_axes,
                port_list=port_list,
                label_size=port_label_size,
                dot_size=port_dot_size,
                label_color=port_label_color,
                dot_color=port_color,
                zorder=port_zorder,
                map_name=map_name,
                map_bbox=map_bbox,
                country=port_country,
                port_country=port_country,
                port_water_body=port_water_body,
                port_wpi_region=port_wpi_region,
                port_bounding_box=port_bounding_box,
                port_and_country_seperate=port_and_country_seperate,
                draw_all_ports=draw_all_ports,
                draw_arrows=draw_arrows
            ))

    if draw_cities:
        artists.extend(
            decoration.draw_cities(
                map_axes,
                cities_to_draw,
                label_size=city_label_size,
                dot_size=city_dot_size,
                label_color=city_label_color,
                dot_color=city_dot_color,
                zorder=city_zorder,
                map_name=map_name,
                map_bbox=map_bbox,
                country=country,
                location=location
            ))

    if draw_largest_cities is not None:
        artists.extend(
            decoration.draw_largest_cities(
                map_axes,
                draw_largest_cities,
                dot_color=city_dot_color,
                dot_size=city_dot_size,
                label_color=city_label_color,
                label_size=city_label_size
            ))

    if draw_cities_larger_than is not None:
        artists.extend(
            decoration.draw_cities_larger_than(
                map_axes,
                draw_cities_larger_than,
                dot_color=city_dot_color,
                dot_size=city_dot_size,
                label_color=city_label_color,
                label_size=city_label_size
            ))

    if draw_scale:
        artists.extend(
            decoration.draw_scale(
                map_axes,
                length_in_km=scale_length_in_km,
                label_color=scale_label_color,
                label_size=scale_label_size,
                linewidth=scale_linewidth,
                zorder=scale_zorder
            ))

    return (map_axes, artists)


def _make_bounding_box(bbox_args, domain):
    """Make a sensible bounding box out of whatever the user gave us."""

    # Case 1: Is it a list of coordinates from the command line?
    if type(bbox_args) is list and len(bbox_args) == 4:
        if domain == 'terrestrial':
            from tracktable.domain.terrestrial import \
                BoundingBox as TerrestrialBoundingBox
            min_corner = (bbox_args[0], bbox_args[1])
            max_corner = (bbox_args[2], bbox_args[3])
            return TerrestrialBoundingBox(min_corner, max_corner)
        elif domain == 'cartesian2d':
            from tracktable.domain.cartesian2d import \
                BoundingBox as Cartesian2DBoundingBox
            min_corner = (bbox_args[0], bbox_args[1])
            max_corner = (bbox_args[2], bbox_args[3])
            return Cartesian2DBoundingBox(min_corner, max_corner)
        else:
            raise ValueError('Custom bounding box for domain {} is not defined.'.format(domain))
    # Case 2: is it a bbox already?
    else:
        # just hope for the best
        return bbox_args

