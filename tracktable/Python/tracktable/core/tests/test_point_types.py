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
from datetime import datetime
import sys
import pickle
from six import StringIO


from tracktable.core import geomath
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.terrestrial import BasePoint as TerrestrialBasePoint

from tracktable.domain.cartesian2d import TrajectoryPoint as Cartesian2DTrajectoryPoint
from tracktable.domain.cartesian2d import BasePoint as Cartesian2DBasePoint

from tracktable.domain.cartesian3d import TrajectoryPoint as Cartesian3DTrajectoryPoint
from tracktable.domain.cartesian3d import BasePoint as Cartesian3DBasePoint

def verify_time(expected, actual, test_name):
    if(actual != expected):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def verify_trajectory_point(expected, actual, test_name):
    if (geomath.distance(actual, expected) > .1 or actual.timestamp != expected.timestamp or actual.property('speed') != expected.property('speed') or actual.property('heading') != expected.property('heading')):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def verify_base_point(expected, actual, test_name):
    if (geomath.distance(actual, expected) > .1):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def point_to_string(point):
    properties = []
    for thing in point.properties:
        properties.append( ( thing.key(), point.properties[thing.key()] ) )

    template_string = '[ lon: {} lat: {} altitude: {} speed: {} heading: {} id: {} timestamp: {} properties: {} ]\n'
    return template_string.format( point.longitude,
                                   point.latitude,
                                   point.altitude,
                                   point.speed,
                                   point.heading,
                                   point.object_id,
                                   point.timestamp,
                                   properties )
def test_point_type():
    print("Testing point type")

    error_count = 0

    point1 = TerrestrialBasePoint(45, 45)
    point2 = TerrestrialBasePoint(135, 45)

    print("Testing terrestrial base point interpolate, 0.5")
    result = geomath.interpolate(point1, point2, 0.5)
    expected = TerrestrialBasePoint(90, 54.7356)
    error_count += verify_base_point(expected, result, "Terrestrial Base Point Interpolate 0.5")

    print("Testing terrestrial base point interpolate, 0.3")
    result = geomath.interpolate(point1, point2, 0.3)
    expected = TerrestrialBasePoint(69.7884, 53.0018)
    error_count += verify_base_point(expected, result, "Terrestrial Base Point Interpolate 0.3")

    print("Testing terrestrial base point interpolate, 1")
    result = geomath.interpolate(point1, point2, 1)
    error_count += verify_base_point(point2, result, "Terrestrial Base Point Interpolate 1")

    print("Testing terrestrial base point extrapolate, 2")
    result = geomath.extrapolate(point1, point2, 2)
    expected = TerrestrialBasePoint(180, 0)
    error_count += verify_base_point(expected, result, "Terrestrial Base Point Extrapolate 2")

    point3 = Cartesian2DBasePoint(0,0)
    point4 = Cartesian2DBasePoint(10,10)

    print("Testing cartesian2d base point interpolate, 0.5")
    result = geomath.interpolate(point3, point4, 0.5)
    expected = Cartesian2DBasePoint(5,5)
    error_count += verify_base_point(expected, result, "Cartesian2D Base Point Interpolate 0.5")

    print("Testing cartesian2d base point interpolate, 0.3")
    result = geomath.interpolate(point3, point4, 0.3)
    expected = Cartesian2DBasePoint(3,3)
    error_count += verify_base_point(expected, result, "Cartesian2D Base Point Interpolate 0.3")

    print("Testing cartesian2d base point interpolate, 1")
    result = geomath.interpolate(point3, point4, 1)
    error_count += verify_base_point(point4, result, "Cartesian2D Base Point Interpolate 1")

    print("Testing cartesian2d base point extrapolate, 1.5")
    result = geomath.extrapolate(point3, point4, 1.5)
    expected = Cartesian2DBasePoint(15,15)
    error_count += verify_base_point(expected, result, "Cartesian2D Base Point Extrapolate 1.5")

    point5 = Cartesian3DBasePoint(0,0,0)
    point6 = Cartesian3DBasePoint(10,10,10)

    print("Testing cartesian3d base point interpolate, 0.5")
    result = geomath.interpolate(point5, point6, 0.5)
    expected = Cartesian3DBasePoint(5,5,5)
    error_count += verify_base_point(expected, result, "Cartesian3D Base Point Interpolate 0.5")

    print("Testing cartesian3d base point interpolate, 0.3")
    result = geomath.interpolate(point5, point6, 0.3)
    expected = Cartesian3DBasePoint(3,3,3)
    error_count += verify_base_point(expected, result, "Cartesian3D Base Point Interpolate 0.3")

    print("Testing cartesian3d base point interpolate, 1")
    result = geomath.interpolate(point5, point6, 1)
    error_count += verify_base_point(point6, result, "Cartesian3D Base Point Interpolate 1")

    print("Testing cartesian3d base point extrapolate, 1.5")
    result = geomath.extrapolate(point5, point6, 1.5)
    expected = Cartesian3DBasePoint(15,15,15)
    error_count += verify_base_point(expected, result, "Cartesian3D Base Point Extrapolate 1.5")

    point7 = TerrestrialTrajectoryPoint(10, 30)
    point7.timestamp = datetime.strptime("2020-12-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    point7.object_id = 'FOO'
    point7.set_property('speed', 100.0)
    point7.set_property('heading', 0.0)

    point8 = TerrestrialTrajectoryPoint(14.6929, 35.1023)
    point8.timestamp = datetime.strptime("2020-12-01 00:30:00", "%Y-%m-%d %H:%M:%S")
    point8.object_id = 'FOO'
    point8.set_property('speed', 150.0)
    point8.set_property('heading', 90.0)

    point9 = TerrestrialTrajectoryPoint(20, 40)
    point9.timestamp = datetime.strptime("2020-12-01 01:00:00", "%Y-%m-%d %H:%M:%S")
    point9.object_id = 'FOO'
    point9.set_property('speed', 200.0)
    point9.set_property('heading', 180.0)

    print("Testing terrestrial trajectory point interpolate, 0.5")
    result = geomath.interpolate(point7, point9, 0.5)
    error_count += verify_trajectory_point(point8, result, "Terrestrial Trajectory Point Interpolate 0.5")

    print("Testing terrestrial trajectory point extrapolate, 2")
    result = geomath.extrapolate(point7, point8, 2)
    error_count += verify_trajectory_point(point9, result, "Terrestrial Trajectory Point Extrapolate 2")

    point10 = Cartesian2DTrajectoryPoint(5, 5)
    point10.timestamp = datetime.strptime("2020-12-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    point10.object_id = 'FOO'
    point10.set_property('speed', 10.0)
    point10.set_property('heading', 0.0)

    point11 = Cartesian2DTrajectoryPoint(10, 10)
    point11.timestamp = datetime.strptime("2020-12-01 00:30:00", "%Y-%m-%d %H:%M:%S")
    point11.object_id = 'FOO'
    point11.set_property('speed', 15.0)
    point11.set_property('heading', 90.0)

    point12 = Cartesian2DTrajectoryPoint(15, 15)
    point12.timestamp = datetime.strptime("2020-12-01 01:00:00", "%Y-%m-%d %H:%M:%S")
    point12.object_id = 'FOO'
    point12.set_property('speed', 20.0)
    point12.set_property('heading', 180.0)

    print("Testing cartesian2d trajectory point interpolate, 0.5")
    result = geomath.interpolate(point10, point12, 0.5)
    error_count += verify_trajectory_point(point11, result, "Cartesian2D Trajectory Point Interpolate 0.5")

    print("Testing cartesian2d trajectory point extrapolate, 2")
    result = geomath.extrapolate(point10, point11, 2)
    error_count += verify_trajectory_point(point12, result, "Cartesian2D Trajectory Point Extrapolate 2")

    point13 = Cartesian3DTrajectoryPoint(5, 5, 5)
    point13.timestamp = datetime.strptime("2020-12-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    point13.object_id = 'FOO'
    point13.set_property('speed', 10.0)
    point13.set_property('heading', 0.0)

    point14 = Cartesian3DTrajectoryPoint(10, 10, 10)
    point14.timestamp = datetime.strptime("2020-12-01 00:30:00", "%Y-%m-%d %H:%M:%S")
    point14.object_id = 'FOO'
    point14.set_property('speed', 15.0)
    point14.set_property('heading', 90.0)

    point15 = Cartesian3DTrajectoryPoint(15, 15, 15)
    point15.timestamp = datetime.strptime("2020-12-01 01:00:00", "%Y-%m-%d %H:%M:%S")
    point15.object_id = 'FOO'
    point15.set_property('speed', 20.0)
    point15.set_property('heading', 180.0)

    print("Testing cartesian3d trajectory point interpolate, 0.5")
    result = geomath.interpolate(point13, point15, 0.5)
    error_count += verify_trajectory_point(point14, result, "Cartesian3D Trajectory Point Interpolate 0.5")

    print("Testing cartesian3d trajectory point extrapolate, 2")
    result = geomath.extrapolate(point13, point14, 2)
    error_count += verify_trajectory_point(point15, result, "Cartesian3D Trajectory Point Extrapolate 2")

    return error_count


# ----------------------------------------------------------------------

def test_point_types():
    error_count = test_point_type()

    print("test_point_types: error count is {}".format(error_count))

    return error_count


if __name__ == '__main__':
    sys.exit(test_point_types())

