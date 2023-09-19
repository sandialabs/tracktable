#
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

from __future__ import print_function

import sys
from six import StringIO
import datetime

from tracktable.core import geomath
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.cartesian2d import Trajectory as Cartesian2dTrajectory
from tracktable.domain.cartesian2d import TrajectoryPoint as Cartesian2dTrajectoryPoint

def create_point(lat, lon, id):

    point = TerrestrialTrajectoryPoint(lon, lat)
    point.object_id = id

    return point

def create_cart2_point(x, y, id):

    point = Cartesian2dTrajectoryPoint()
    point.object_id = id
    point[0] = x
    point[1] = y

    return point

def verify_result(expected, actual, test):
    if (geomath.distance(actual, expected) > .1):
        sys.stderr.write('ERROR: {} does not match. Expected centroid {}, but returned {}.\n'.format(test,expected,actual))
        return 1

    return 0


def test_convex_hull_centroid():

    print("Testing Convex Hull Centroid")

    error_count = 0;

    albuquerque = create_point(35.0844, -106.6504, "short_flight")
    denver = create_point(39.7392, -104.9903, "short_flight")
    el_paso = create_point(31.7619, -106.4850, "short_flight")
    san_francisco = create_point(37.7749, -122.4194, "long_flight")
    new_york = create_point(40.7128, -74.0060, "long_flight")
    london = create_point(51.5074, -0.1278, "long_flight")
    london = create_point(51.5074, -0.1278, "long_flight")
    point1 = create_cart2_point(0,0, "2d cartesian trajectory")
    point2 = create_cart2_point(0,1, "2d cartesian trajectory")
    point3 = create_cart2_point(1,1, "2d cartesian trajectory")
    point4 = create_cart2_point(1,0, "2d cartesian trajectory")

    short_trajectory = TerrestrialTrajectory.from_position_list([el_paso, albuquerque, denver])

    #Short trajectorty should have centroid around albuquerque
    expected_short_centroid = create_point(35.5314, -106.069, "short_flight_centroid")

    short_flight_centroid = geomath.convex_hull_centroid(short_trajectory)
    error_count += verify_result(expected_short_centroid, short_flight_centroid, "Short flight")

    long_trajectory = TerrestrialTrajectory.from_position_list([san_francisco, new_york, london])

    #/Longer flight should have larger centroid
    expected_long_centroid = create_point(55.4714, -72.1941, "long_flight_centroid")

    long_flight_centroid = geomath.convex_hull_centroid(long_trajectory)
    error_count += verify_result(expected_long_centroid, long_flight_centroid, "Long flight")

    combined_trajectory = TerrestrialTrajectory.from_position_list([el_paso, albuquerque, denver, san_francisco, new_york, london])

    #Combined flight should have slightly larger centroid since there are more points relatively further away
    expected_combined_centroid = create_point(53.0855, -79.1866, "combined_flight_centroid")

    combined_centroid = geomath.convex_hull_centroid(combined_trajectory)
    error_count += verify_result(expected_combined_centroid, combined_centroid, "Combined flight")

    #No points in a trajectory should return 0
    expected_no_point_centroid = create_point(0.0, 0.0, "no_point_centroid")

    no_points = TerrestrialTrajectory()
    no_point_centroid = geomath.convex_hull_centroid(no_points)
    error_count += verify_result(expected_no_point_centroid, no_point_centroid, "Empty flight")

    #One point in a trajectory should return 0
    expected_one_point_centroid = create_point(0.0, 0.0, "one_point_centroid")

    one_point = TerrestrialTrajectory.from_position_list([create_point(0.0, 0.0, "one_point_centroid")])

    one_point_centroid = geomath.convex_hull_centroid(one_point)
    error_count += verify_result(expected_one_point_centroid, one_point_centroid, "One point flight")

    #Test Cartesian for good measure
    expected_cartesian2d_centroid = create_cart2_point(0.5, 0.5, "four_point_centroid")

    cart_trajectory = Cartesian2dTrajectory.from_position_list([point1, point2, point3, point4])

    cart2d_centroid = geomath.convex_hull_centroid(cart_trajectory)
    error_count += verify_result(expected_cartesian2d_centroid, cart2d_centroid, "Four points cartesian")

    print("\n")
    return error_count

if __name__ == '__main__':
    sys.exit(test_convex_hull_centroid())