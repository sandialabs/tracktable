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

import sys
from tracktable.core import geomath
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.cartesian2d import Trajectory as Cartesian2dTrajectory
from tracktable.domain.cartesian2d import TrajectoryPoint as Cartesian2dTrajectoryPoint
from tracktable.domain.cartesian3d import Trajectory as Cartesian3dTrajectory
from tracktable.domain.cartesian3d import TrajectoryPoint as Cartesian3dTrajectoryPoint

def verify_result(actual, expected, test_name):
    if (abs(expected - actual) >= .001):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

#--------------------------------------------------------------------------

def test_kms_to_lon():
    error_count = 0

    km_per_lon_at_lat_0 = 111.320
    km_per_lon_at_lat_30 = 96.40594794928371
    km_per_lon_at_lat_60 = 55.660
    km_per_lon_at_lat_89 = 1.9428018845983854

    print("Testing representing 1 kilometer as degrees-longitude, at various latitudes");

    expected = 1.0 / km_per_lon_at_lat_0
    actual = geomath.kms_to_lon(1.0,0.0)
    error_count += verify_result(actual, expected, "1 Degree Longitude in km, at Latitude 0 N")

    expected = 1.0 / km_per_lon_at_lat_30
    actual = geomath.kms_to_lon(1.0,30.0)
    error_count += verify_result(actual, expected, "1 Degree Longitude in km, at Latitude 30 N")

    expected = 1.0 / km_per_lon_at_lat_60
    actual = geomath.kms_to_lon(1.0,60.0)
    error_count += verify_result(actual, expected, "1 Degree Longitude in km, at Latitude 60 N")

    expected = 1.0 / km_per_lon_at_lat_89
    actual = geomath.kms_to_lon(1.0,89.0)
    error_count += verify_result(actual, expected, "1 Degree Longitude in km, at Latitude 89 N")

    return error_count

#--------------------------------------------------------------------------

def test_kms_to_lat():
    error_count = 0

    km_per_lat_at_lat_0  = 111.594
    km_per_lat_at_lat_30 = 111.22066666666666
    km_per_lat_at_lat_60 = 110.84733333333332
    km_per_lat_at_lat_89 = 110.48644444444443

    print("Testing representing 1 kilometer as degrees-latitude, at various latitudes");

    expected = 1.0 / km_per_lat_at_lat_0
    actual = geomath.kms_to_lat(1.0,0.0)
    error_count += verify_result(actual, expected, "1 Degree Latitude in km, at Latitude 0 N")

    expected = 1.0 / km_per_lat_at_lat_30
    actual = geomath.kms_to_lat(1.0,30.0)
    error_count += verify_result(actual, expected, "1 Degree Latitude in km, at Latitude 30 N")

    expected = 1.0 / km_per_lat_at_lat_60
    actual = geomath.kms_to_lat(1.0,60.0)
    error_count += verify_result(actual, expected, "1 Degree Latitude in km, at Latitude 60 N")

    expected = 1.0 / km_per_lat_at_lat_89
    actual = geomath.kms_to_lat(1.0,89.0)
    error_count += verify_result(actual, expected, "1 Degree Latitude in km, at Latitude 89 N")

    return error_count

# ----------------------------------------------------------------------

def main():
    error_count = 0
    error_count += test_kms_to_lon()
    error_count += test_kms_to_lat()

    return error_count

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
