#
# Copyright (c) 2014-2019 National Technology and Engineering
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

"""
tracktable.source.scatter - Ways to generate points around a seed point
"""

from __future__ import division, print_function, absolute_import

import math
import random
from six.moves import range


def random_box_uniform(min_corner, max_corner, num_points=100):
    """Generate points uniformly within a bounding box

    This will generate points according to a uniform random 
    distribution within a specified bounding box.

    Note that the uniformity is with respect to each dimension,
    not the underlying metric.  You will only get spatially uniform
    points if (1) the bounding box is square and (2) the coordinate 
    system is isotropic with respect to the underlying surface.  
    Cartesian coordinate systems are such.  Geographic coordinates
    (longitude/latitude) are not -- the width of 1 degree of
    longitude changes as a function of latitude.

    Arguments:
        min_corner (Tracktable point type): lower left / SW corner of 
           bounding box
        max_corner (Tracktable point type): upper right / NE corner of
           bounding box
        num_points (int): How many points you want
    Returns:
        Iterable of points
    """

    num_coords = len(min_corner)
    point_type = min_corner.__class__
    def generate_point():
        new_coords = [random.uniform(min_corner[i], max_corner[i])
                      for i in range(num_coords)]
        return point_type(*new_coords)

    return (generate_point() for j in range(num_points))


def random_circle_linear_falloff(seed_point,
                                 num_points=100,
                                 max_radius_km=100):
    """Generate points within a certain radius of a seed point

    Point density falls off linearly with distance from the seed
    point.

    NOTE: Right now this function is specialized for terrestrial
          coordinates.  That will be fixed in an upcoming point
          release.

    Args:
       seed_point (tracktable.domain.terrestrial.BasePoint): Center of 
           point cloud
       num_points (integer, default 100): Number of points to generate
       max_radius (float, non-negative): How far the points can be from 
           the center (default 100km)

    Returns:
       Iterable of points of same type as seed point

    Note:
       Formula from www.movable-type.co.uk/scripts/latlong.html

    """

    def d2r(degrees):
        return (degrees / 180.0) * math.pi

    def r2d(radians):
        return (radians / math.pi) * 180.0

    start_lon = d2r(seed_point[0])
    start_lat = d2r(seed_point[1])

    def triangle_variate(max=1):
        """Generate a value drawn from the triangular distribution with mode at 0 and p=0 at 1"""
        return max * (
            1 - math.sqrt(random.uniform(0, 1))
            )


    def generate_nearby_point():
        bearing = random.uniform(0, 2.0 * math.pi)
        # 6371km is the radius of the earth
        distance = triangle_variate(max=max_radius_km) / 6371.0

        end_lat = math.asin(
            math.sin(start_lat) * math.cos(distance) +
            math.cos(start_lat) * math.sin(distance) * math.cos(bearing)
        )
        end_lon = start_lon + math.atan2(
            math.sin(bearing) * math.sin(distance) * math.cos(start_lat),
            math.cos(distance) - math.sin(start_lat) * math.sin(end_lat)
        )

        new_point = seed_point.__class__()
        try:
            new_point.object_id = seed_point.object_id
            new_point.timestamp = seed_point.timestamp
        except AttributeError:
            pass
        new_point[0] = r2d(end_lon)
        new_point[1] = r2d(end_lat)

        return new_point

    return (generate_nearby_point() for i in range(num_points))
