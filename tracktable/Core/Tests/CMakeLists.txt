# Copyright (c) 2014-2024 National Technology and Engineering
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

include(CplusplusTest)

unset(Boost_FOUND)
get_filename_component(_TEST_NAME_TMP ${CMAKE_CURRENT_SOURCE_DIR} DIRECTORY)
get_filename_component(_TEST_NAME_2 ${CMAKE_CURRENT_SOURCE_DIR} NAME)
get_filename_component(_TEST_NAME_1 ${_TEST_NAME_TMP} NAME)
message(STATUS "Looking for Boost components needed for C++ tests in ${_TEST_NAME_1}/${_TEST_NAME_2}")
find_package(Boost CONFIG ${BOOST_MINIMUM_VERSION_REQUIRED} REQUIRED
  COMPONENTS
    ${BOOST_CORE_COMPONENTS_NEEDED}
    ${BOOST_TEST_COMPONENTS}
  )

include_directories(
  ${Tracktable_SOURCE_DIR}
)


add_cpp_test(NAME C_BasePointSerialization
             SOURCE test_base_point_serialization.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_ConvexHullArea
             SOURCE test_convex_hull_area.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_ConvexHullAspectRatio
             SOURCE test_convex_hull_aspect_ratio.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_ConvexHullPerimeter
             SOURCE test_convex_hull_perimeter.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_CurrentLength
             SOURCE test_current_length.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_CurrentLengthFraction
             SOURCE test_current_length_fraction.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_CurrentTimeFraction
             SOURCE test_current_time_fraction.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_DegenerateConvexHull
             SOURCE test_degenerate_convex_hull.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_Distance
             SOURCE test_distance.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES}
             CATCH2)

add_cpp_test(NAME C_LogLevel
             SOURCE test_log_level.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_MemoryUse
             SOURCE test_memory_use.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PointArithmetic
             SOURCE test_point_arithmetic.cpp
             LIBRARIES TracktableCore TracktableDomain
             CATCH2)

add_cpp_test(NAME C_PointAtFraction
             SOURCE test_point_at_fraction.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PointCartesian
             SOURCE test_point_cartesian.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PointGeometricMedian
             SOURCE test_point_geometric_median.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PointGeometryMath
             SOURCE test_point_geometry_math.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PointInterpolation
             SOURCE test_point_interpolation.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PointLonLat
             SOURCE test_point_lonlat.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_PropertyMap
             SOURCE test_property_map.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_SerializeVariant
             SOURCE test_serialize_variant.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_SimplifyLineString
             SOURCE test_simplify_linestring.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TimestampFormat
             SOURCE test_timestamp_format.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryLonLat
             SOURCE test_trajectory_lonlat.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryId
             SOURCE test_trajectory_id.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryPointSerialization
             SOURCE test_trajectory_point_serialization.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryPointLonLat
             SOURCE test_trajectory_point_lonlat.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryRadiusOfGyration
             SOURCE test_trajectory_radius_of_gyration.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectorySerialization
             SOURCE test_trajectory_serialization.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectorySlicing
             SOURCE test_trajectory_slicing.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectorySubset
             SOURCE test_trajectory_subset.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryUuid
             SOURCE test_trajectory_uuid.cpp
             LIBRARIES TracktableCore ${Boost_LIBRARIES})

