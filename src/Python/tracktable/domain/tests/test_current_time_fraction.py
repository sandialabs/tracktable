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
from datetime import datetime
from tracktable.core import geomath
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.cartesian2d import Trajectory as Cartesian2dTrajectory
from tracktable.domain.cartesian2d import TrajectoryPoint as Cartesian2dTrajectoryPoint

def verify_result(actual, expected, test_name):
    if (abs(expected - actual) >= .001):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def test_cartesian2d_current_time_fraction():
    error_count = 0

    point00 = Cartesian2dTrajectoryPoint(0,0)
    point00.timestamp = datetime.strptime("2020-09-03 05:00:00", "%Y-%m-%d %H:%M:%S")
    point01 = Cartesian2dTrajectoryPoint(0,1)
    point01.timestamp = datetime.strptime("2020-09-03 06:00:00", "%Y-%m-%d %H:%M:%S")
    point03 = Cartesian2dTrajectoryPoint(0,3)
    point03.timestamp = datetime.strptime("2020-09-03 08:00:00", "%Y-%m-%d %H:%M:%S")
    point04 = Cartesian2dTrajectoryPoint(0,4)
    point04.timestamp = datetime.strptime("2020-09-03 09:00:00", "%Y-%m-%d %H:%M:%S")

    traj = Cartesian2dTrajectory.from_position_list([point00, point01, point03, point04])
    print("Testing Cartesian 2D Current Time Fraction");

    expected = 0.0
    actual = geomath.current_time_fraction(traj[0])
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint 0")

    expected = 0.25
    actual = geomath.current_time_fraction(traj[1])
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint 1")

    expected = 0.75
    actual = geomath.current_time_fraction(traj[2])
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint 2")

    expected = 1.0
    actual = geomath.current_time_fraction(traj[3])
    error_count += verify_result(actual, expected, "Cartesian2dTrajectoryPoint 3")

    return error_count

#--------------------------------------------------------------------------

def test_terrestrial_current_time_fraction():
    error_count = 0

    point0 = TerrestrialTrajectoryPoint(35,-105)
    point0.timestamp = datetime.strptime("2020-09-03 05:00:00", "%Y-%m-%d %H:%M:%S")
    point1 = TerrestrialTrajectoryPoint(35,-106)
    point1.timestamp = datetime.strptime("2020-09-03 06:00:00", "%Y-%m-%d %H:%M:%S")
    point2 = TerrestrialTrajectoryPoint(35,-108)
    point2.timestamp = datetime.strptime("2020-09-03 08:00:00", "%Y-%m-%d %H:%M:%S")
    point3 = TerrestrialTrajectoryPoint(35,-109)
    point3.timestamp = datetime.strptime("2020-09-03 09:00:00", "%Y-%m-%d %H:%M:%S")

    traj = TerrestrialTrajectory.from_position_list([point0, point1, point2, point3])
    print("Testing Terrestrial Current Time Fraction");

    expected = 0.0
    actual = geomath.current_time_fraction(traj[0])
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint 0")

    expected = 0.25
    actual = geomath.current_time_fraction(traj[1])
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint 1")

    expected = 0.75
    actual = geomath.current_time_fraction(traj[2])
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint 2")

    expected = 1.0
    actual = geomath.current_time_fraction(traj[3])
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint 3")

    return error_count

# ----------------------------------------------------------------------

def main():
    error_count = 0
    error_count += test_terrestrial_current_time_fraction()
    error_count += test_cartesian2d_current_time_fraction()

    return error_count

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
