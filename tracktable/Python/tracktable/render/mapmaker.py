#
# Copyright (c) 2014-2017 National Technology and Engineering
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

"""tracktable.render.mapmaker - Convenience wrappers for geographic map creation and decoration
"""

from __future__ import print_function

from matplotlib import pyplot

from tracktable.info   import cities
from tracktable.render import maps
from tracktable.render import projection

def mapmaker(domain, **kwargs):
    if kwargs.get('map_bbox', None) is not None:
        map_bbox = kwargs['map_bbox']
    else:
        map_bbox = None

    if domain == 'terrestrial':
        if map_bbox is not None:
            try:
                # Convert to a native-typed bounding box
                from tracktable.domain.terrestrial import BoundingBox, BasePoint
                min_corner = BasePoint(map_bbox[0], map_bbox[1])
                max_corner = BasePoint(map_bbox[2], map_bbox[3])
                bbox = BoundingBox(min_corner, max_corner)
                kwargs['map_bbox'] = bbox
            except TypeError: # it's already a bbox
                pass
        return terrestrial_map(**kwargs)
    elif domain == 'cartesian' or domain == 'cartesian2d':
        if map_bbox is not None:
            try:
                # Convert to a native-typed bounding box
                from tracktable.domain.cartesian2d import BoundingBox, BasePoint
                min_corner = BasePoint(map_bbox[0], map_bbox[1])
                max_corner = BasePoint(map_bbox[2], map_bbox[3])
                bbox = BoundingBox(min_corner, max_corner)
                kwargs['map_bbox'] = bbox
            except TypeError: # it's already a bbox
                pass

        return cartesian_map(**kwargs)

# ----------------------------------------------------------------------

def cartesian_map(map_bbox=None,
                  gridline_spacing=None,
                  axes=None,
                  **kwargs):
    """Create a Cartesian map

    Since Cartesian space is flat and undistinguished, a "map" is just
    a display region.  You can also change the background color and
    draw axes/grid lines on the figure.
    """

    from tracktable.domain.cartesian2d import BoundingBox, BasePoint

    if axes is None:
        axes = pyplot.gca()

    print("DEBUG: cartesian_map: map_bbox is {}".format(map_bbox))

    (proj, artists) = projection.make_projection_cartesian2d()

    axes.set_aspect(kwargs.get('aspect', 'equal'))
    if map_bbox is not None:
        axes.set_xlim(left=map_bbox.min_corner[0],
                      right=map_bbox.max_corner[0])
        axes.set_ylim(bottom=map_bbox.min_corner[1],
                      top=map_bbox.max_corner[1])
        proj.bbox = map_bbox

    return (proj, artists)

# ----------------------------------------------------------------------

def terrestrial_map(map_name,
                    draw_coastlines=True,
                    draw_countries=True,
                    draw_states=True,
                    draw_lonlat=True,
                    land_color='#101010',
                    sea_color='#000000',
                    lonlat_spacing=10,
                    lonlat_color='#A0A0A0',
                    lonlat_linewidth=0.2,
                    lonlat_zorder=4,
                    coastline_color='#808080',
                    coastline_linewidth=1,
                    coastline_zorder=3,
                    country_color='#606060',
                    country_linewidth=0.5,
                    country_zorder=2,
                    state_color='#404040',
                    state_linewidth=0.3,
                    state_zorder=1,
                    draw_largest_cities=None,
                    draw_cities_larger_than=None,
                    city_label_size=12,
                    city_dot_size=2,
                    city_dot_color='white',
                    city_label_color='white',
                    border_resolution='i',
                    map_bbox=None,
                    map_projection=None,
                    map_scale_length=None,
                    region_size=None,
                    axes=None,
                    **kwargs):

    """Create and decorate a map

    Call the Basemap toolkit to create a map of some predefined area,
    up to and including the entire world.  The map will be decorated
    with some subset of coastlines, country borders, state/province
    borders and cities.

    Args:
      map_name:            Region name (one of the choices in
                           render.maps.available_maps()) or 'airport:XXX' or 'custom'
      draw_coastlines:     Whether or not to draw coastlines on the map
      draw_countries:      Whether or not to draw country borders on the map
      draw_states:         Whether or not to draw US/Canada state borders
      draw_lonlat:         Whether or not to draw longitude/latitude lines
      land_color:          Color name or hex string for land area
      sea_color:           Color name or hex string for sea area
      lonlat_spacing:      Distance in degrees between lon/lat lines
      lonlat_color:        Color name or hex string for longitude/latitude lines
      lonlat_linewidth:    Width (in point) for lon/lat lines
      lonlat_zorder:       Image layer for coastlines
      coastline_color:     Color name or hex string for coastlines
      coastline_linewidth: Width (in points) of coastlines
      coastline_zorder:    Image layer for coastlines
      country_color:       Color name or hex string for coastlines
      country_linewidth:   Width (in points) of coastlines
      country_zorder:      Image layer for coastlines
      state_color:         Color name or hex string for coastlines
      state_linewidth:     Width (in points) of coastlines
      state_zorder:        Image layer for coastlines
      draw_largest_cities: Draw the N largest cities on the map
      draw_cities_larger_than: Draw cities with populations greater than N
      city_label_size:     Size (in points) for city name labels
      city_dot_size:       Size (in points) for city markers
      city_dot_color:      Color name or hex string for city markers
      city_label_color:    Color name or hex string for city names
      border_resolution:   'c', 'i', 'h' or 'f' (in increasing order of complexity)
      axes:                Matplotlib axes to render into
      map_bbox:            Bounding box for custom map extent
      region_size:         Size of region depicted around an airport (km width x km height)
      map_projection:      Matplotlib string for map projection
      map_scale_length:    Length of map scale indicator (in km)

    Raises:
      KeyError: unknown map name

    Returns:
      (basemap, artist_list): Basemap instance and a list of Matplotlib artists that were rendered
    """

    if map_name == "custom":
        (mymap, artists) = maps.draw_custom_map(bounding_box=map_bbox,
                                                projection=map_projection,
                                                resolution=border_resolution,
                                                axes=axes)
    else:
        (mymap, artists) = draw_basemap(map_name,
                                        resolution=border_resolution,
                                        region_size=region_size,
                                        axes=axes
                                        )

    artists.extend(maps.fill_continents(mymap,
                                        land_color=land_color,
                                        sea_color=sea_color,
                                        zorder=0))
    if draw_coastlines:
        artists.extend(maps.draw_coastlines(mymap,
                                            linewidth=coastline_linewidth,
                                            color=coastline_color,
                                            zorder=coastline_zorder))

    if draw_countries:
        artists.extend(maps.draw_countries(mymap,
                                           linewidth=country_linewidth,
                                           color=country_color,
                                           zorder=country_zorder))

    if draw_states:
        artists.extend(maps.draw_states(mymap,
                                        linewidth=state_linewidth,
                                        color=state_color,
                                        zorder=state_zorder))

    if draw_lonlat:
        artists.extend(maps.draw_lonlat(mymap,
                                        spacing=lonlat_spacing,
                                        color=lonlat_color,
                                        linewidth=lonlat_linewidth,
                                        zorder=lonlat_zorder))

    if draw_largest_cities is not None:
        artists.extend(maps.draw_largest_cities(mymap,
                                                draw_largest_cities,
                                                dot_color=city_dot_color,
                                                dot_size=city_dot_size,
                                                label_color=city_label_color,
                                                label_size=city_label_size))

    if draw_cities_larger_than is not None:
        artists.extend(maps.draw_cities_larger_than(mymap,
                                                    draw_cities_larger_than,
                                                    dot_color=city_dot_color,
                                                    dot_size=city_dot_size,
                                                    label_color=city_label_color,
                                                    label_size=city_label_size))

    if map_scale_length is not None:
        artists.extend(maps.draw_scale(mymap,
                                       map_scale_length,
                                       label_color=city_label_color,
                                       label_size=city_label_size))

    from tracktable.domain.terrestrial import BoundingBox, BasePoint
    mymap.bbox = BoundingBox(
        BasePoint(mymap.llcrnrlon, mymap.llcrnrlat),
        BasePoint(mymap.urcrnrlon, mymap.urcrnrlat)
        )
    return (mymap, artists)



# ----------------------------------------------------------------------

def draw_basemap(which_map,
                 resolution='i',
                 axes=None,
                 **kwargs):

    """Set up Basemap projection for a named map

    This function calls out to tracktable.render.maps.predefined_map()
    to look up and configure the Basemap projection.  You can use a
    region name chosen from maps.available_maps() or a string of the
    form 'airport:XXX' where XXX is the 3- or 4-letter airport ID.

    Args:
       which_map (string): Name of map to draw.  See maps.available_maps() for a list of names.

    Keyword Args:
       resolution (character): One of None, 'c', 'l', 'i', 'h', 'f' indicating "coarse", "low", "intermediate", "high" and "full" resolution.  This affects the resolution of the shapefile with border and coastline information.  Higher values take more memory and time.
       axes (matplotlib Axes): Axes to render map information into.

    Returns:
       ( basemap, list(artists) )

    Raises:
       KeyError: You asked for a map that isn't defined.
    """

    if axes is None:
        axes = pyplot.gca()

    (mymap, artists) = maps.predefined_map(which_map, ax=axes, resolution=resolution, **kwargs)

    return (mymap, artists)
