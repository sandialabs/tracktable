#
# Copyright (c) 2014-2020 National Technology and Engineering
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

# This is tracktable/Python/tracktable/core/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our core classes and functions are working.

include(PythonTest)

add_python_test(P_ConvexHullArea tracktable.core.tests.test_convex_hull_area)

add_python_test(P_ConvexHullAspectRatio tracktable.core.tests.test_convex_hull_aspect_ratio)

add_python_test(P_ConvexHullCentroid tracktable.core.tests.test_convex_hull_centroid)

add_python_test(P_ConvexHullPerimeter tracktable.core.tests.test_convex_hull_perimeter)

add_python_test(P_CopyExampleNotebooks tracktable.core.tests.test_copy_example_notebooks "${Tracktable_BINARY_DIR}/TestOutput/")

add_python_test(P_DataDirectory tracktable.core.tests.test_data_directory)

add_python_test(P_EchoArgs tracktable.core.tests.echo_args foo bar baz)

add_python_test(P_ParseTimestampNoTimeZone tracktable.core.tests.parse_timestamp_no_time_zone)

add_python_test(P_ParseTimestampWithTimeZone tracktable.core.tests.parse_timestamp_with_time_zone)

add_python_test(P_ReaderTimestampFormats tracktable.core.tests.test_reader_timestamps "${Tracktable_SOURCE_DIR}/TestData/Timestamps/")

add_python_test(P_SpeedBetween tracktable.core.tests.test_speed_between)

add_python_test(P_TrajectoryTypes tracktable.core.tests.test_trajectory_types)

add_python_test(P_PointTypes tracktable.core.tests.test_point_types)

add_python_test(P_RadiusGyration tracktable.core.tests.test_trajectory_radius_of_gyration)

add_python_test(P_ComputeBoundingBox tracktable.core.tests.test_compute_bounding_box)

add_python_test(P_ComputeBoundingBoxAfterPickle tracktable.core.tests.test_compute_bounding_box_after_pickle)

add_python_test(P_Distance tracktable.core.tests.test_distance)

add_python_test(P_KM2LonLat tracktable.core.tests.test_kms_to_lon_lat)

add_python_test(P_LogLevel tracktable.core.tests.test_log_level)

add_python_test(P_TerrestrialECEF tracktable.core.tests.test_terrestrial_ECEF)
