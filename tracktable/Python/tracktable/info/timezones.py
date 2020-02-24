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

from __future__ import print_function, division, absolute_import

import logging
import os.path
import pytz
import shapefile

from shapely.geometry.polygon import Polygon
from shapely.geometry import Point, MultiPolygon
from six.moves import range


TIMEZONE_BOUNDARIES = None
TIMEZONE_STRUCTS = dict()

def load_timezone_shapefile():
    raise NotImplementedError("load_timezone_shapefile needs a shapefile reader!")
    global TIMEZONE_BOUNDARIES
    logger = logging.getLogger(__name__)
    full_path = os.path.join(os.path.dirname(__file__), 'data', 'tz_world')
    logger.debug('Loading timezone shapefile from {}'.format(full_path))
    reader = shapefile.Reader(full_path)
    timezone_names = [ record[0] for record in reader.records() ]
    shapes = reader.shapes()

    split_names = [ tz.split('/') for tz in timezone_names ]
    names_and_zones = zip(shapes, split_names)

    america_timezones = [thing for thing in names_and_zones if thing[1][0] == 'America']
    canada_timezones = [ thing for thing in names_and_zones if thing[1][0] == 'Canada' ]
    all_other_timezones = [ thing for thing in names_and_zones if (thing[1][0] != 'Canada' and thing[1][0] != 'America') ]

    sorted_timezones = america_timezones + canada_timezones + all_other_timezones

    boundaries = []
    logger.debug("Converting shapefile to polygons")

    TIMEZONE_BOUNDARIES = []
    for named_shape in sorted_timezones:
        shape = named_shape[0]
        name_list = named_shape[1]
        joined_name = '/'.join(name_list)

        polygons = []

        num_polys = len(shape.parts)
        for i in range(num_polys):
            poly_start = shape.parts[i]
            poly_end = shape.parts[i+1] if (i+1) < num_polys else -1
            poly_points = shape.points[poly_start:poly_end]
            next_polygon = Polygon(poly_points)
            polygons.append(next_polygon)

        TIMEZONE_BOUNDARIES.append((MultiPolygon(polygons), joined_name))


# ----------------------------------------------------------------------

def find_containing_timezone(longitude, latitude):
    global TIMEZONE_BOUNDARIES, TIMEZONE_STRUCTS
    if not TIMEZONE_BOUNDARIES:
        load_timezone_shapefile()
        assert TIMEZONE_BOUNDARIES

    lonlat_point = Point(longitude, latitude)
    for (boundary, name) in TIMEZONE_BOUNDARIES:
        if boundary.contains(lonlat_point):
            if name in TIMEZONE_STRUCTS:
                return TIMEZONE_STRUCTS[name]
            else:
                TIMEZONE_STRUCTS[name] = pytz.timezone(name)
                return TIMEZONE_STRUCTS[name]

    return None

# ----------------------------------------------------------------------

def print_file():
    print("__file__: %s" % __file__)

def retrieve_file():
    return __file__

def local_time_for_position(position):
    timezone = find_containing_timezone(position.longitude, position.latitude)
    if timezone:
        return position.timestamp.astimezone(timezone)
    else:
        return position.timestamp
