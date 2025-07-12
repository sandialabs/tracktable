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
import pytz

from tracktable.core import geomath
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.cartesian3d import BasePoint as CartesianPoint3D


def verify_result(expected, actual, test_name):
    if(geomath.distance(actual, expected) > .1):
        print(geomath.distance(actual, expected))
        sys.stderr.write('ERROR: {} does not match. Expected ECEF {}, but returned actual ECEF {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def run_test():

    print("Testing ECEF function")
    error_count = 0

    lonlatzero = TerrestrialTrajectoryPoint(0.0, 0.0)
    equatorpoint = TerrestrialTrajectoryPoint(90.0, 0.0)
    northpole = TerrestrialTrajectoryPoint(0.0, 90.0)
    northpole2 = TerrestrialTrajectoryPoint(-135.0, 90.0)
    northpole2.set_property("altitude",100)
    albuquerque = TerrestrialTrajectoryPoint(-106.6504, 35.0844)

    expected = CartesianPoint3D(6378.137, 0.0, 0.0)
    actual = geomath.ECEF(lonlatzero);
    error_count += verify_result(actual, expected, "LonLatZero");

    expected = CartesianPoint3D(0.0, 6378.137, 0.0)
    actual = geomath.ECEF(equatorpoint);
    error_count += verify_result(actual, expected, "EquatorPoint");

    expected = CartesianPoint3D(0.0, 0.0, 6356.75231)
    actual = geomath.ECEF(northpole);
    error_count += verify_result(actual, expected, "NorthPole");

    expected = CartesianPoint3D(0.0, 0.0, 6456.75231)
    actual = geomath.ECEF(northpole2, 1, "altitude");
    error_count += verify_result(actual, expected, "NorthPole2");

    expected = CartesianPoint3D(-1497.14022, -5005.96887, 3645.53304)
    actual = geomath.ECEF(albuquerque);
    error_count += verify_result(actual, expected, "Albuquerque");

    print("Testing ECEF_from_meters")

    albuquerque.set_property("altitude", 1000);
    actual = geomath.ECEF_from_meters(albuquerque)
    expected = CartesianPoint3D(-1497.375, -5006.753, 3646.108)
    error_count += verify_result(actual, expected, "AlbuquerqueMetters")

    albuquerque.set_property("height", 1000)
    actual = geomath.ECEF_from_feet(albuquerque, "height")
    expected = CartesianPoint3D(-1497.212, -5006.208, 3645.708)
    error_count += verify_result(actual, expected, "AlbuquerqueFeet");

    if error_count == 0:
        print("Trajectory ECEF passed all tests.")

    return error_count

# ----------------------------------------------------------------------

def test_ecef():
    error_count = run_test()
    print("\n")

    return error_count

if __name__ == '__main__':
    sys.exit(test_ecef())
