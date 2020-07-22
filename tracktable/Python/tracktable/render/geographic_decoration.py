"""Render cities, coastlines, etc onto maps"""

from __future__ import print_function, absolute_import, division

import cartopy
cities = None


def _ensure_cities_loaded():
    global cities
    if cities is None:
        from ..info import cities

def draw_largest_cities(map_axes,
                        num_cities,
                        label_size=10,
                        dot_size=2,
                        label_color='white',
                        dot_color='white',
                        zorder=10):
    """Decorate a map with the N largest cities

    Args:
       map_axes:           Map to decorate
       minimum_population: Draw cities with at least this large a population
       label_size:         Font size (points) for label
       dot_size:           Size (in points) of dot marking city location
       label_color:        Color (name or hex string) for city labels
       dot_color:          Color (name or hex string) for city markesr
       zorder:             Image layer (z-order) for cities

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
                       dot_color=dot_color,
                       axes=axes)

# ----------------------------------------------------------------------


def draw_cities(map_axes,
                cities_to_draw,
                label_size=12,
                dot_size=2,
                label_color='white',
                dot_color='white',
                zorder=10,
                transform = None):

    if transform is None:
        transform = cartopy.crs.Geodetic()

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
                xy=(longitude, latitude),
                xytext=(6, 0),
                textcoords="offset points",
                s=city.name,
                fontsize=label_size,
                color=label_color,
                ha="left",
                va="center",
                zorder=zorder,
                transform=transform
            )
            artists.append(text_artist)

    return artists

# ----------------------------------------------------------------------


def draw_countries(map_axes,
                   linewidth=0.5,
                   zorder=4,
                   edgecolor='#606060',
                   resolution='10m',
                   **kwargs):

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
       map_axes: GeoAxes from mapmaker

    Keyword Args:
       border_color (colorspec): Color for coastlines (default #808080, a medium gray)
       resolution (string): Resolution for coastlines.  A value of None means 'don't draw'.  The values '110m', '50m' and '10m' specify increasingly detailed coastlines.  Defaults to '110m'.
       linewidth (float): Stroke width in points for coastlines.  Defaults to 0.2.
       zorder (int): Drawing layer for coastlines.  Layers with higher Z-order are drawn on top of those with lower Z-order.

    Returns:
       A list of Matplotlib artists added to the map.
    """

    coastlines = cartopy.feature.NaturalEarthFeature(
        name='coastline',
        category='physical',
        scale=resolution,
        edgecolor=edgecolor,
        facecolor='none',
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
      land_color (string): Color specification for land.  Can be either a common name or a 6-digit hex string.
      linewidth (float): Stroke width (in points) for coastlines
      zorder (integer or None): Image layer for coastlines

    TODO:
      Is this the method that mapmaker actually uses?

    """

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
      resolution (string): One of '110m', '50m' or '10m' in increasing order of fidelity
      water_color (string): Color specification for water.  Can be either a common name or a 6-digit hex string.
      zorder (integer or None): Image layer for coastlines

    TODO:
      Does this also fill lakes?  Apparently not.
    """

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
      resolution (string): One of '110m', '50m' or '10m' in increasing order of fidelity
      facecolor (string): Color specification for water.  Can be either a common name or a 6-digit hex string.
      zorder (integer or None): Image layer for coastlines
    """

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
                linewidth=0.25,
                color='#C0C0C0'):

    artist = map_axes.gridlines(
        color=color,
        linewidth=linewidth,
        zorder=zorder
        )

    return [artist]

# ----------------------------------------------------------------------

def draw_scale(mymap,
               length_in_km,
               label_color,
               label_size,
               linewidth=1,
               zorder=20):

    raise NotImplementedError(
      ("tracktable.render.geographic_decoration.draw_scale has not "
       "been ported to Cartopy"))
    
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



# ----------------------------------------------------------------------

def fill_background(mymap, border_color='#000000', bgcolor='#000000', linewidth=1):
    raise NotImplementedError(
      ("tracktable.render.geographic_decoration: fill_background has not "
       "been ported to Cartopy"))
    
    result = mymap.drawmapboundary(color=border_color, fill_color=bgcolor, linewidth=linewidth)
    return result
