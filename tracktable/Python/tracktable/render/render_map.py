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
                    draw_largest_cities=None,
                    draw_cities_larger_than=None,
                    city_label_size=12,
                    city_dot_size=2,
                    city_dot_color='white',
                    city_label_color='white',
                    city_zorder=6,
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
                    axes=None,
                    tiles=None,
                    tiles_zoom_level=8,
                    **kwargs):
    """Create and decorate a terrestrial map

    Call the Cartopy toolkit to create a map of some predefined area,
    up to and including the entire world. The map will be decorated
    with some subset of coastlines, country borders, state/province
    borders and cities according to the keyword arguments you supply
    to mapmaker() or terrestrial_map().

    Args:
      map_name:            Region name ('region:XXX' or 'airport:XXX' or 'city:XXX' or 'custom'). Available regions are in tracktable.render.maps.available_maps().

    Keyword Args:
      draw_coastlines (bool):                       Whether or not to draw coastlines on the map (Default: True)
      draw_countries (bool):                        Whether or not to draw country borders on the map (Default: True)
      draw_states (bool):                           Whether or not to draw US/Canada state borders (Default: True)
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
      draw_largest_cities (int):                    Draw the N largest cities on the map (Default: None)
      draw_cities_larger_than (int):                Draw cities with populations greater than N (Default: None)
      city_label_size (int):                        Size (in points) for city name labels (Default: 12)
      city_dot_size (int):                          Size (in points) for city markers (Default: 2)
      city_dot_color (str):                         Color name or hex string for city markers (Default: 'white')
      city_label_color (str):                       Color name or hex string for city names (Default: 'white')
      city_zorder (int):                            Color name or hex string for city names (Default: 6)
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
      axes (GeoAxes):                               Matplotlib axes to render into (Default: None)
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
                color=lonlat_color,
                draw_labels=lonlat_labels,
                linewidth=lonlat_linewidth,
                zorder=lonlat_zorder
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

