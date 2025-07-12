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

def test_cartesian2d_distance():
    error_count = 0

    point00 = Cartesian2dTrajectoryPoint(0,0)
    point01 = Cartesian2dTrajectoryPoint(0,1)
    point11 = Cartesian2dTrajectoryPoint(1,1)
    point22 = Cartesian2dTrajectoryPoint(2,2)

    traj1 = Cartesian2dTrajectory.from_position_list([point00, point01])
    traj2 = Cartesian2dTrajectory.from_position_list([point11, point22])

    print("Testing Cartesian 2D Distance");

    expected = 1.0
    actual = geomath.distance(point00, point01)
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint to Cartesian2dTrajectoryPoint 1")

    expected = 1.414
    actual = geomath.distance(point00, point11)
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint to Cartesian2dTrajectoryPoint 2")

    expected = 1.0
    actual = geomath.distance(traj1, traj2)
    error_count += verify_result(actual, expected, "Cartesian2dTrajectory to Cartesian2dTrajectory")

    expected = 1.414
    actual = geomath.distance(point00, traj2)
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint to Cartesian2dTrajectory")

    actual = geomath.distance(traj2, point00)
    error_count += verify_result(actual, expected, "Cartesian2dTrajectory to Cartesian2dTrajectoryPoint")

    return error_count

#--------------------------------------------------------------------------

def test_cartesian3d_distance():
    error_count = 0

    point000 = Cartesian3dTrajectoryPoint(0,0,0)
    point001 = Cartesian3dTrajectoryPoint(0,0,1)
    point111 = Cartesian3dTrajectoryPoint(1,1,1)
    point222 = Cartesian3dTrajectoryPoint(2,2,2)

    traj1 = Cartesian3dTrajectory.from_position_list([point000, point001])
    traj2 = Cartesian3dTrajectory.from_position_list([point111, point222])

    print("Testing Cartesian 3D Distance");

    expected = 1.0
    actual = geomath.distance(point000, point001)
    error_count += verify_result(actual, expected, "Cartesian3dTrajectoryPoint to Cartesian3dTrajectoryPoint 1")

    expected = 1.732
    actual = geomath.distance(point000, point111)
    error_count += verify_result(actual, expected, "Cartesian3dTrajectoryPoint to Cartesian3dTrajectoryPoint 2")

    #Does not work due to boost not implementing disjoint for dimensions > 3 which is called by the distance function.
    #expected = 1.414
    #actual = geomath.distance(traj1, traj2)
    #error_count += verify_result(actual, expected, "Cartesian3dTrajectory to Cartesian3dTrajectory")

    expected = 1.732
    actual = geomath.distance(point000, traj2)
    error_count += verify_result(actual, expected, "Cartesian3dTrajectoryPoint to Cartesian3dTrajectory")

    actual = geomath.distance(traj2, point000)
    error_count += verify_result(actual, expected, "Cartesian3dTrajectory to Cartesian3dTrajectoryPoint")

    return error_count

#--------------------------------------------------------------------------

def test_terrestrial_distance():

    error_count = 0

    albuquerque = TerrestrialTrajectoryPoint(-106.6504, 35.0844)
    dallas = TerrestrialTrajectoryPoint(-96.8716, 32.8205)
    el_paso = TerrestrialTrajectoryPoint(-106.4850, 31.7619)
    san_antonio = TerrestrialTrajectoryPoint(-98.6544, 29.4813)
    houston = TerrestrialTrajectoryPoint(-74.0060, 29.8168)

    ep_to_dal = TerrestrialTrajectory.from_position_list([el_paso, dallas])
    sa_to_hou = TerrestrialTrajectory.from_position_list([san_antonio, houston])
    sa_to_abq = TerrestrialTrajectory.from_position_list([san_antonio, albuquerque])

    print("Testing Terrestrial Distance");

    expected = 369.764
    actual = geomath.distance(albuquerque, el_paso)
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint to TerrestrialTrajectoryPoint")

    expected = 349.276
    actual = geomath.distance(ep_to_dal, sa_to_hou)
    error_count += verify_result(actual, expected, "TerrestrialTrajectory to TerrestrialTrajectory")

    expected = 0.0
    actual = geomath.distance(ep_to_dal, sa_to_abq)
    error_count += verify_result(actual, expected, "TerrestrialTrajectory to TerrestrialTrajectory Intersecting")

    expected = 975.674
    actual = geomath.distance(albuquerque, sa_to_hou)
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint to TerrestrialTrajectory")

    actual = geomath.distance(sa_to_hou, albuquerque)
    error_count += verify_result(actual, expected, "TerrestrialTrajectory to TerrestrialTrajectoryPoint")

    return error_count

# ----------------------------------------------------------------------

def main():
    error_count = 0
    error_count += test_terrestrial_distance()
    error_count += test_cartesian2d_distance()
    error_count += test_cartesian3d_distance()

    return error_count

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
