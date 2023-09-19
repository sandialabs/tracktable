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


"""
tracktable.data_generators.heatmap point - Generating heatmap points around n largest cities.
"""
import csv
import datetime
import logging

from tracktable.data_generators import point
from tracktable.domain import terrestrial
from tracktable.feature import interleave_points
from tracktable.info import cities

logger = logging.getLogger(__name__)

def n_largest_cities(howmany):
    """
    n_largest_cities(howmany: int) -> list of CityInfo objects

    Retrieve a list of the N largest cities in the world (by
    population) sorted in descending order.
    """

    return cities.largest_cities_in_bbox(count=howmany)

# ----------------------------------------------------------------------

def point_radius_for_city(city):
    """point_radius_for_city(city: tracktable.info.cities.CityInfo) -> float(km)

    Return a radius proportional to a city's population.  Arbitrarily,
    a city with a population of 1 million will get a radius of 50 km.

    This has no particular real-world meaning.  It's just a way to
    scatter points around the city center.
    """

    return (city.population / 1000000) * 50.0

# ----------------------------------------------------------------------

def write_points_to_file(point_source, outfile):
    outfile.write('# object_id timestamp longitude latitude\n')
    writer = csv.writer(outfile, delimiter=',')

    for point in point_source:
        row = [ point.object_id, '2014-01-01 00:00:00', point[0], point[1] ]
        writer.writerow(row)

# ----------------------------------------------------------------------

def points_near_city(city, num_points):
    center = terrestrial.BasePoint()
    center[0] = city.longitude
    center[1] = city.latitude
    center.timestamp = datetime.datetime.now()
    center.object_id = 'ANON'

    max_radius = point_radius_for_city(city)

    return point.random_circle_linear_falloff(center, num_points, max_radius)

# ----------------------------------------------------------------------

def generate_heatmap_points(**kwargs):

    logger.info("Generating {} points around each of the {} largest cities in the world.".format(kwargs['num_points_per_city'], kwargs['num_cities']))
    heatmap_points = [ points_near_city(city, kwargs['num_points_per_city']) for city in n_largest_cities(kwargs['num_cities']) ]
    combined_point_source = interleave_points.interleave_points_by_timestamp(*heatmap_points)
    if kwargs['write_file']:
        with open(kwargs ['outfilename'], 'w') as outfile:
            write_points_to_file(combined_point_source, outfile)
    return heatmap_points
