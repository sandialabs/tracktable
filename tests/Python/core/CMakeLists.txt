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

# This is tests/Python/core/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our core classes and functions are working.

include(PythonTest)

add_python_test(P_ConvexHullArea test_convex_hull_area.py)

add_python_test(P_ConvexHullAspectRatio test_convex_hull_aspect_ratio.py)

add_python_test(P_ConvexHullCentroid test_convex_hull_centroid.py)

add_python_test(P_ConvexHullPerimeter test_convex_hull_perimeter.py)

add_python_test(P_CopyExampleNotebooks test_copy_example_notebooks.py "${Tracktable_BINARY_DIR}/TestOutput/")

add_python_test(P_EchoArgs echo_args.py foo bar baz)

add_python_test(P_ParseTimestampNoTimeZone parse_timestamp_no_time_zone.py)

add_python_test(P_ParseTimestampWithTimeZone parse_timestamp_with_time_zone.py)

add_python_test(P_ReaderTimestampFormats test_reader_timestamps.py "${Tracktable_DATA_DIR}/internal_test_data/Timestamps/")

add_python_test(P_SpeedBetween test_speed_between.py)

add_python_test(P_TrajectoryTypes test_trajectory_types.py)

add_python_test(P_PointTypes test_point_types.py)

add_python_test(P_RadiusGyration test_trajectory_radius_of_gyration.py)

add_python_test(P_ComputeBoundingBox test_compute_bounding_box.py)

add_python_test(P_ComputeBoundingBoxAfterPickle test_compute_bounding_box_after_pickle.py)

add_python_test(P_Distance test_distance.py)

add_python_test(P_KM2LonLat test_kms_to_lon_lat.py)

add_python_test(P_LogLevel test_log_level.py)

add_python_test(P_TerrestrialECEF test_terrestrial_ECEF.py)

add_python_test(P_TimestampTimeZoneConversion timestamp_conversion_python_cpp.py)
