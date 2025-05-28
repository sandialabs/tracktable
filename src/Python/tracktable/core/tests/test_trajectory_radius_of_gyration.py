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

import pickle
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
    if (abs(actual - expected) > .1):
        sys.stderr.write('ERROR: {} does not match. Expected radius of gyration {}, but returned {}.\n'.format(test,expected,actual))
        return 1

    return 0


def test_radius_of_gyration():

    print("Testing Radius of Gyration")

    error_count = 0;

    albuquerque = create_point(35.0844, -106.6504, "short_flight")
    denver = create_point(39.7392, -104.9903, "short_flight")
    el_paso = create_point(31.7619, -106.4850, "short_flight")
    san_francisco = create_point(37.7749, -122.4194, "long_flight")
    new_york = create_point(40.7128, -74.0060, "long_flight")
    london = create_point(51.5074, -0.1278, "long_flight")
    point1 = create_cart2_point(0,0, "2d cartesian trajectory")
    point2 = create_cart2_point(0,1, "2d cartesian trajectory")
    point3 = create_cart2_point(1,0, "2d cartesian trajectory")
    point4 = create_cart2_point(1,1, "2d cartesian trajectory")

    short_trajectory = TerrestrialTrajectory.from_position_list([el_paso, albuquerque, denver])

    #Short trajectorty should have small radius
    expected_short_radius = 0.0580509 * 6371.0

    short_flight_radius = geomath.radius_of_gyration(short_trajectory)
    error_count += verify_result(expected_short_radius, short_flight_radius, "Short flight")

    long_trajectory = TerrestrialTrajectory.from_position_list([san_francisco, new_york, london])

    #/Longer flight should have larger radius
    expected_long_radius = 0.581498 * 6371.0

    long_flight_radius = geomath.radius_of_gyration(long_trajectory)
    error_count += verify_result(expected_long_radius, long_flight_radius, "Long flight")

    combined_trajectory = TerrestrialTrajectory.from_position_list([el_paso, albuquerque, denver, san_francisco, new_york, london])

    #Combined flight should have smaller radius since there are more points relatively clustered together
    expected_combined_radius = 0.523586 * 6371.0

    combined_radius = geomath.radius_of_gyration(combined_trajectory)
    error_count += verify_result(expected_combined_radius, combined_radius, "Combined flight")

    #No points in a trajectory should return 0
    expected_no_point_radius = 0.0

    no_points = TerrestrialTrajectory()
    no_point_radius = geomath.radius_of_gyration(no_points)
    error_count += verify_result(expected_no_point_radius, no_point_radius, "Empty flight")

    #One point in a trajectory should return 0
    expected_one_point_radius = 0.0

    one_point = TerrestrialTrajectory.from_position_list([el_paso])

    one_point_radius = geomath.radius_of_gyration(one_point)
    error_count += verify_result(expected_one_point_radius, one_point_radius, "One point flight")

    #Test Cartesian for good measure
    expected_cartesian2d_radius = 0.707

    cart_trajectory = Cartesian2dTrajectory.from_position_list([point1, point2, point3, point4])

    cart2d_radius = geomath.radius_of_gyration(cart_trajectory)
    error_count += verify_result(expected_cartesian2d_radius, cart2d_radius, "Four points cartesian")

    print("\n")
    return error_count

if __name__ == '__main__':
    sys.exit(test_radius_of_gyration())
