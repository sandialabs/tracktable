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


from tracktable.script_helpers.argument_groups import create_argument_group
from tracktable.script_helpers.argument_groups import add_argument
from tracktable.render import maps

"""Command-line options for creating and decorating maps.

The Mapmaker argument group contains (almost) everything we think you
might need in order to draw a map of part of the Earth, including
decorating it with borders and cities.  It can also be used to specify
a map for a 2D Cartesian data set, albeit with some awkwardness.  This
will be fixed soon.

Arguments:

| ``--domain NAME``
|   Point domain for your data.  This will be one of 'terrestrial', 'cartesian2d', 'cartesian3d'.
|
| ``--map NAME``
|   Name of map that you want.  See tracktable.render.maps.available_maps() for options.  There is also a "custom" map type where you supply your own bounding box.
|
| ``--omit-coastlines``
|   Do not draw continent boundaries
|
| ``--omit-countries``
|   Do not draw country borders
|
| ``--omit-states``
|   Do not draw US/Canada state borders
|
| ``--omit-lonlat``
|   Do not draw longitude/latitude lines
|
| ``--lonlat-spacing NUMBER``
|   Spacing (in degrees) between longitude/latitude lines
|
| ``--draw-cities-larger-than NUMBER``
|   Draw all cities on the map with population larger than N
|
| ``--draw-largest-cities NUMBER``
|   Draw the largest N cities (by population) on the map
|
| ``--continent-color COLOR``
|   Color (name or hex string) for continental coastlines
|
| ``--continent-linewidth NUMBER``
|   Line width (in points) for continental coastlines
|
| ``--continent-zorder NUMBER``
|   Layer (Z-order, integer) for continental coastlines.  Higher numbers are drawn on top of lower numbers.
|
| ``--country-color COLOR``
|   Color (name or hex string) for country borders
|
| ``--country-linewidth NUMBER``
|   Line width (in points) for country borders
|
| ``--country-zorder NUMBER``
|   Label (Z-order, integer) for country borders. Higher numbers are drawn on top of lower numbers.
|
| ``--land-color COLOR``
|   Color (name or hex string) for land masses
|
| ``--sea-color COLOR``
|   Color (name or hex string) for bodies of water
|
| ``--state-color COLOR``
|   Color (name or hex string) for state borders
|
| ``--state-linewidth NUMBER``
|   Line width (in points) for state borders
|
| ``--state-zorder NUMBER``
|   Label (Z-order, integer) for state borders. Higher numbers are drawn on top of lower numbers.
|
| ``--city-label-size NUMBER``
|   Font size (in points) for city labels
|
| ``--city-dot-size NUMBER``
|   Size (in points) for dots representing cities on map
|
| ``--city-dot-color COLOR``
|   Color (name or hex string) for dots onmap representing cities
|
| ``--city-label-color COLOR``
|   Color (name or hex string) for city labels on map.
|
| ``--map-bbox X_MIN Y_MIN X_MAX Y_MAX``
|   Axis-aligned bounding box for map.
|
| ``--map-projection STRING``
|   Map projection string for Basemap.  Defaults to 'mill' (Miller cylindrical).

"""


"""example_movie_rendering - Parameters for movie encoding
"""

GROUP_INSTALLED = False


def install_group():
    """Register the Mapmaker argument group.

    This function is called when the argument_groups module is
    imported by dint of being listed in __init__.py.

    """

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True

    create_argument_group("mapmaker",
                          title="Create and annotate a geographic map",

                          description="Here you can set all of the options for creating and annotating your map.  These include asking for a predefined map of a region of the world, a map around an airport, a map of the whole world, whether or not to draw continents, country borders, state/province borders (in the US and Canada), cities and longitude/latitude lines.  The ability to specify a fully arbitrary map will come eventually.")

    add_argument("mapmaker", [ "--domain" ],
                 default="terrestrial",
                 help="Point domain for your data.  This should be 'terrestrial' if your points are in longitude/latitude format or 'cartesian' if your points are in regular 2D space.")

    add_argument("mapmaker", [ "--map" ],
                 default="region:world",
                 dest='map_name',
                 help="Which map do you want to use?  This must be one of {} or else a string of the form 'airport:XXX' where XXX is the 3- or 4-letter abbreviation for that airport.".format(list(maps.available_maps()) + ["custom"]))

    add_argument("mapmaker", [ "--omit-coastlines" ],
                 action='store_false',
                 dest='draw_coastlines',
                 help='Do not draw coastlines on the map (drawn by default)')

    add_argument("mapmaker", [ "--omit-countries" ],
                 action='store_false',
                 dest='draw_countries',
                 help='Do not draw country borders on the map (drawn by default)')

    add_argument("mapmaker", [ "--omit-states" ],
                 action='store_false',
                 dest='draw_states',
                 help='Do not draw US/Canada state borders on the map (drawn by default)')

    add_argument("mapmaker", [ '--omit-lonlat' ],
                 action='store_false',
                 dest='draw_lonlat',
                 help='Do not draw longitude/latitude lines (drawn by default)')

    add_argument("mapmaker", [ '--lonlat-spacing' ],
                 type=float,
                 default=10,
                 help="Spacing (in degrees) between longitude/latitude lines")

    add_argument("mapmaker", [ '--draw-largest-cities' ],
                 type=int,
                 help='Draw the N largest cities (by population) on the map')

    add_argument("mapmaker", [ '--draw-cities-larger-than' ],
                 type=int,
                 help='Draw all cities in the visible part of the map with population larger than N.')

    add_argument("mapmaker", [ '--city-label-size' ],
                 type=int,
                 default=12,
                 help='Size for city names (in points)')

    add_argument("mapmaker", [ '--city-dot-size' ],
                 type=float,
                 default=2,
                 help='Size for dots representing cities (in points)')

    add_argument("mapmaker", [ "--coastline-color" ],
                 default="#808080",
                 help="Color for coastlines (either color name or hex string)")

    add_argument("mapmaker", [ "--coastline-linewidth" ],
                 type=float,
                 default=1,
                 help="Width (in points) for coastlines")

    add_argument("mapmaker", [ "--coastline-zorder" ],
                 default=3,
                 help="Layer (z-order) for coastlines - higher layers are on top")

    add_argument("mapmaker", [ "--country-color" ],
                 default="#606060",
                 help="Color for country borders (either color name or hex string)")

    add_argument("mapmaker", [ "--country-linewidth" ],
                 type=float,
                 default=0.5,
                 help="Linewidth (in points) for country borders")

    add_argument("mapmaker", [ "--country-zorder" ],
                 default=2,
                 help="Layer (z-order) for coastlines - higher layers are on top")

    add_argument("mapmaker", [ "--land-color" ],
                 default="#303030",
                 help="Color for land masses (color name or hex string)")

    add_argument("mapmaker", [ "--sea-color" ],
                 default="#000000",
                 help="Color for bodies of water (color name or hex string)")

    add_argument("mapmaker", [ "--state-color" ],
                 default="#404040",
                 help="Color for state borders (either color name or hex string")

    add_argument("mapmaker", [ "--state-linewidth" ],
                 type=float,
                 default=0.3,
                 help="Line width (in points) for state borders")

    add_argument("mapmaker", [ "--state-zorder" ],
                 default=1,
                 help="Layer (z-order) for state borders - higher layers are on top")

    add_argument("mapmaker", [ '--city-label-size' ],
                           type=int,
                           default=12,
                           help='Size for city names (in points)')

    add_argument("mapmaker", [ '--city-dot-size' ],
                           type=float,
                           default=2,
                           help='Size for dots representing cities (in points)')

    add_argument("mapmaker", [ "--city-dot-color" ],
                 default="white",
                 help="Color (name or hex string) for cities on map")

    add_argument("mapmaker", [ "--city-label-color" ],
                 default="white",
                 help="Color (name or hex string) for city labels on map")

    add_argument("mapmaker", [ "--map-bbox" ],
                 type=float,
                 nargs=4,
                 help="Custom bounding box for map")

    add_argument("mapmaker", [ "--map-projection" ],
                 default="PlateCarree",
                 help="Custom projection for map")

    add_argument("mapmaker", [ "--map-scale-length" ],
                 type=float,
                 default=None,
                 help="Length of map scale indicator in km")

    add_argument("mapmaker", [ "--region-size" ],
                 type=float,
                 nargs=2,
                 default=None,
                 help="Width of box for maps near airport")
