# Copyright (c) 2014, Sandia Corporation.  All rights
# reserved.
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


# generate_heatmap_sample_data - Generate the data file points_near_big_cities.tsv
#

# Our heatmap sample data file contains points sampled randomly in the
# vicinity of large cities.  If you want to generate a similar file
# with different parameters or just want to know how it works, use and
# modify this script.
#
# The example data in tracktable/Examples/Data/HeatmapSamplePoints.tsv
# was generated with the following command line:
#
# python generate_heatmap_sample_data.py 500 100 HeatmapSamplePoints.tsv
#

import csv
import math
import random
import sys

from tracktable.core import geomath
from tracktable.info import cities
from tracktable.source import random_point_source, combine

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
    writer = csv.writer(outfile, delimiter='\t')

    for point in point_source:
        point.object_id = 'ANON'
        row = [ point.object_id, '2014-01-01 00:00:00', point.longitude, point.latitude ]
        writer.writerow(row)

# ----------------------------------------------------------------------

def points_near_city(city, num_points):
    center = ( city.longitude, city.latitude )
    radius = point_radius_for_city(city)

    source = random_point_source.ConePointsNearPosition()
    source.center = center
    source.max_radius = geomath.km_to_radians(radius)
    source.num_points = num_points

    return source.points()

# ----------------------------------------------------------------------

def main():
    argv = sys.argv
    if len(argv) != 4:
        sys.stderr.write('usage: {} num_cities num_points_per_city outfile.tsv\n'.format(argv[0]))
        return 1

    num_cities = int(argv[1])
    num_points_per_city = int(argv[2])
    outfilename = argv[3]

    print("INFO: Generating {} points around each of the {} largest cities in the world.".format(num_points_per_city, num_cities))

    all_sources = [ points_near_city(city, num_points_per_city) for city in n_largest_cities(num_cities) ]
    combined_point_source = combine.concatenate_sources(*all_sources)

    with open(outfilename, 'wb') as outfile:
        write_points_to_file(combined_point_source, outfile)

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
