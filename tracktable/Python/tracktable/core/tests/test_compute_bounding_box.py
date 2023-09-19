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


# Use a back end for matplotlib that does not require access to a
# windowing system
import matplotlib
matplotlib.use('Agg')

import sys
import os
import traceback
from tracktable.core import geomath
from tracktable.feature.interpolated_points import TrajectoryPointSource
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint
from tracktable.domain.cartesian2d import Trajectory as Cartesian2dTrajectory
from tracktable.domain.cartesian2d import TrajectoryPoint as Cartesian2dTrajectoryPoint

#from tracktable.render.mapmaker import mapmaker
#from matplotlib import pyplot
#from matplotlib import colors

def verify_result(expected, actual, test_name):
    if (expected.min_corner[0] != actual.min_corner[0] or
        expected.min_corner[1] != actual.min_corner[1] or
        expected.max_corner[0] != actual.max_corner[0] or
        expected.max_corner[1] != actual.max_corner[1]):
        sys.stderr.write('ERROR: {} does not match. Expected ({}{}), but returned ({}{}).\n'.format(test_name,expected.min_corner,expected.max_corner,actual.min_corner,actual.max_corner))
        return 1
    return 0

def test_compute_bounding_box():

    error_count = 0

    bbox_type = TerrestrialTrajectoryPoint.domain_classes['BoundingBox']
    expected_min_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    expected_max_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()

    albuquerque = TerrestrialTrajectoryPoint(-106.6504, 35.0844)
    san_francisco = TerrestrialTrajectoryPoint( -122.4194, 37.7749)
    tokyo = TerrestrialTrajectoryPoint(-221.6917, 35.6895)

    small_traj = TrajectoryPointSource()
    small_traj.start_point = albuquerque
    small_traj.end_point = san_francisco
    small_traj.num_points = 2

    long_traj = TrajectoryPointSource()
    long_traj.start_point = tokyo
    long_traj.end_point = san_francisco
    long_traj.num_points = 2

    #Test smallish basic bounding box
    expected_min_corner[0] = san_francisco[0]
    expected_min_corner[1] = albuquerque[1]
    expected_max_corner[0] = albuquerque[0]
    expected_max_corner[1] = san_francisco[1]
    expected = bbox_type(expected_min_corner, expected_max_corner)

    map_bbox = geomath.compute_bounding_box(small_traj.points())
    error_count += verify_result(expected, map_bbox, "Basic small box")


    #Test larger basic bounding box
    expected_min_corner[0] = tokyo[0]
    expected_min_corner[1] = tokyo[1]
    expected_max_corner[0] = san_francisco[0]
    expected_max_corner[1] = san_francisco[1]
    expected = bbox_type(expected_min_corner, expected_max_corner)

    map_bbox = geomath.compute_bounding_box(long_traj.points())
    error_count += verify_result(expected, map_bbox, "Basic large box")

    #Test smallish bounding box with buffer
    lon_buffer = .2
    lat_buffer = .5
    expected_min_corner[0] = san_francisco[0] - ((albuquerque[0] - san_francisco[0]) * lon_buffer)
    expected_min_corner[1] = albuquerque[1] - ((san_francisco[1] - albuquerque[1]) * lat_buffer)
    expected_max_corner[0] = albuquerque[0] + ((albuquerque[0] - san_francisco[0]) * lon_buffer)
    expected_max_corner[1] = san_francisco[1] + ((san_francisco[1] - albuquerque[1]) * lat_buffer)
    expected = bbox_type(expected_min_corner, expected_max_corner)

    map_bbox = geomath.compute_bounding_box(small_traj.points(),(lon_buffer,lat_buffer))
    error_count += verify_result(expected, map_bbox, "Buffered small box")

    #Test larger basic bounding box with buffer
    lon_buffer = .2
    lat_buffer = .1
    expected_min_corner[0] = tokyo[0] - ((san_francisco[0] - tokyo[0]) * lon_buffer)
    expected_min_corner[1] = tokyo[1] - ((san_francisco[1] - tokyo[1]) * lat_buffer)
    expected_max_corner[0] = san_francisco[0] + ((san_francisco[0] - tokyo[0]) * lon_buffer)
    expected_max_corner[1] = san_francisco[1] + ((san_francisco[1] - tokyo[1]) * lat_buffer)
    expected = bbox_type(expected_min_corner, expected_max_corner)

    map_bbox = geomath.compute_bounding_box(long_traj.points(),(lon_buffer,lat_buffer))
    error_count += verify_result(expected, map_bbox, "Buffered large box")

    #Test cartesian based boxes
    c_bbox_type = Cartesian2dTrajectoryPoint.domain_classes['BoundingBox']
    c_expected_min_corner = Cartesian2dTrajectoryPoint.domain_classes['BasePoint']()
    c_expected_max_corner = Cartesian2dTrajectoryPoint.domain_classes['BasePoint']()

    point0=Cartesian2dTrajectoryPoint(0,0)
    point1=Cartesian2dTrajectoryPoint(1,1)
    point2=Cartesian2dTrajectoryPoint(2,2)

    c_expected_min_corner = Cartesian2dTrajectoryPoint(0,0)
    c_expected_max_corner = Cartesian2dTrajectoryPoint(2,2)
    expected = c_bbox_type(c_expected_min_corner, c_expected_max_corner)

    map_bbox = geomath.compute_bounding_box([point0,point1,point2])
    error_count += verify_result(expected, map_bbox, "Basic cartesian box")

    #Test cartesian box with buffer
    x_buffer = .5
    y_buffer = 1.
    c_expected_min_corner[0] = point0[0] - ((point2[0] - point0[0]) * x_buffer)
    c_expected_min_corner[1] = point0[1] - ((point2[1] - point0[1]) * y_buffer)
    c_expected_max_corner[0] = point2[0] + ((point2[0] - point0[0]) * x_buffer)
    c_expected_max_corner[1] = point2[1] + ((point2[1] - point0[1]) * y_buffer)
    expected = c_bbox_type(c_expected_min_corner, c_expected_max_corner)

    map_bbox = geomath.compute_bounding_box([point0,point1,point2],(x_buffer,y_buffer))
    error_count += verify_result(expected, map_bbox, "Buffered cartesian box")

    # Test error conditions
    try:
        map_bbox = geomath.compute_bounding_box([])
    except ValueError:
        pass  # this is what we expect
    except Exception as other_exception:
        sys.stderr.write(
            ('ERROR: Expected ValueError from compute_bounding_box '
             'on empty input but got {}.').format(other_exception))
        error_count += 1

    try:
        map_bbox = geomath.compute_bounding_box(
            long_traj.points(),
            (1.0,))
    except ValueError:
        pass  # this is what we want
    except Exception as other_exception:
        sys.stderr.write(
            ('ERROR: Expected ValueError from compute_bounding_box '
             'with buffer tuple length 1 but got {}.').format(other_exception))
        error_count += 1

    try:
        map_bbox = geomath.compute_bounding_box(long_traj.points(),(1.0,2.0,3.0))
    except ValueError:
        pass  # this is what we want
    except Exception as other_exception:
        sys.stderr.write(
            ('ERROR: Expected ValueError from compute_bounding_box '
             'with buffer tuple length 3 but got {}.').format(other_exception))
        error_count += 1

    return error_count

# ----------------------------------------------------------------------

def main():
    return test_compute_bounding_box()

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
