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

# -*- encoding: utf-8; -*-

"""
cities.py - Locations and population values for many cities of the world
"""

#
# This code is derived from a list of cities provided by MaxMind at
# http://www.maxmind.com/en/worldcities.  Here is the license under
# which we use and redistribute the data:
#
# OPEN DATA LICENSE for MaxMind WorldCities and Postal Code Databases
#
# Copyright (c) 2008 MaxMind Inc.  All Rights Reserved.
#
# The database uses toponymic information, based on the Geographic
# Names Data Base, containing official standard names approved by the
# United States Board on Geographic Names and maintained by the
# National Geospatial-Intelligence Agency. More information is
# available at the Maps and Geodata link at www.nga.mil. The National
# Geospatial-Intelligence Agency name, initials, and seal are
# protected by 10 United States Code Section 445.
#
# It also uses free population data from Stefan Helders www.world-gazetteer.com.
# Visit his website to download the free population data.  Our database
# combines Stefan's population data with the list of all cities in the world.
#
# All advertising materials and documentation mentioning features or
# use of this database must display the following acknowledgment:
# "This product includes data created by MaxMind, available from
# http://www.maxmind.com/"
#
# Redistribution and use with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. Redistributions must retain the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# 2. All advertising materials and documentation mentioning features or use of
# this database must display the following acknowledgement:
# "This product includes data created by MaxMind, available from
# http://www.maxmind.com/"
#
# 3. "MaxMind" may not be used to endorse or promote products derived from this
# database without specific prior written permission.
#
# THIS DATABASE IS PROVIDED BY MAXMIND.COM ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL MAXMIND.COM BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS DATABASE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function, absolute_import, division

import operator

from tracktable.core.geomath import latitude, longitude
from tracktable.core import logging

CITY_TABLE = None
CITY_HEADERS = None

# ----------------------------------------------------------------------

class CityInfo(object):
    """Brief information about a city.

    Attributes:
      country_code (string): 2-character abbreviation for country
      name (string): City name
      population (integer): Estimated population
      latitude (float): Latitude of city location
      longitude (float): Longitude of city location
    """

    def __init__(self):
        """Initialize an empty city."""
        self.country_code = None
        self.name = None
        self.population = None
        self.latitude = None
        self.longitude = None

# ----------------------------------------------------------------------

def cities_in_bbox(bbox_min=(-180, -90),
                   bbox_max=(180, 90),
                   minimum_population=0):
    """Return all the cities in a bounding box.

    Kwargs:
      bbox_min (TrajectoryPoint): Southwest corner of bounding box,
         default (-180, -90)
      bbox_max (TrajectoryPoint): Northeast corner of bounding box,
         default (180, 90)
      minimum_population (integer): Cities with lower population than
         this will not be returned.  Default 0.

    Returns:
      List of CityInfo objects.
    """

    global CITY_TABLE
    if not CITY_TABLE:
        from tracktable.info.data.city_table import city_table as cities
        CITY_TABLE = cities

    result = []

    logger = logging.getLogger(__name__)
    logging.trace(logger, ("cities_in_bbox: bbox_min is {}, "
                           "bbox_max is {}".format(bbox_min, bbox_max)))
  
    logging.trace(
      logger, 
      ("DEBUG: min_longitude is {}, min_latitude is {}, "
       "max_longitude is {}, max_latitude is {}").format(
            longitude(bbox_min),
            latitude(bbox_min),
            longitude(bbox_max),
            latitude(bbox_max)))

    min_longitude = longitude(bbox_min)
    max_longitude = longitude(bbox_max)
    min_latitude = latitude(bbox_min)
    max_latitude = latitude(bbox_max)
    
    for row in CITY_TABLE:
        lat = row[3]
        lon = row[4]
        if ( lon >= min_longitude and
             lon <= max_longitude and
             lat >= min_latitude and
             lat <= max_latitude and
             ((not minimum_population) or (row[2] >= minimum_population)) ):

            info = CityInfo()
            info.country_code = row[0]
            info.name = row[1]
            info.population = row[2]
            info.latitude = row[3]
            info.longitude = row[4]
            result.append(info)

    return result


# ----------------------------------------------------------------------

def largest_cities_in_bbox(bbox_min=(-180, -90),
                           bbox_max=(180, 90),
                           count=10):
    """Return the largest N cities in a bounding box.

    A city's size is measured by its population.

    Args:
      bbox_min (TrajectoryPoint): Southwest corner of bounding box.
        Defaults to (-180, -90).
      bbox_max (TrajectoryPoint): Northeast corner of bounding box.
        Defaults to (180, 90).
      count (integer): How many cities to return.  Defaults to 10.

    Returns:
      A list of CityInfo objects.
    """

    all_cities = cities_in_bbox(bbox_min, bbox_max)
    sorted_cities = sorted(all_cities, 
                           key=lambda city: city.population, 
                           reverse=True)
    return sorted_cities[0:count]


HEADINGS = [ u"Country",u"AccentCity",'Population','Latitude','Longitude' ]
