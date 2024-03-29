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

include(CplusplusTest)

unset(Boost_FOUND)
get_filename_component(_TEST_NAME_TMP ${CMAKE_CURRENT_SOURCE_DIR} DIRECTORY)
get_filename_component(_TEST_NAME_2 ${CMAKE_CURRENT_SOURCE_DIR} NAME)
get_filename_component(_TEST_NAME_1 ${_TEST_NAME_TMP} NAME)
message(STATUS "Looking for Boost components needed for C++ tests in ${_TEST_NAME_1}/${_TEST_NAME_2}")
find_package(Boost ${BOOST_MINIMUM_VERSION_REQUIRED} REQUIRED
  COMPONENTS
    ${BOOST_CORE_COMPONENTS_NEEDED}
    ${BOOST_TEST_COMPONENTS}
  )

include_directories(
  ${Tracktable_SOURCE_DIR}
)

add_executable(test_point_arithmetic
test_point_arithmetic.cpp
)
set_property(TARGET test_point_arithmetic PROPERTY FOLDER "Tests")

add_executable(test_distance
  test_distance.cpp
  )
set_property(TARGET test_distance               PROPERTY FOLDER "Tests")

add_executable(test_convex_hull_area
  test_convex_hull_area.cpp
  )
set_property(TARGET test_convex_hull_area               PROPERTY FOLDER "Tests")

# The convex hull centroid code is not ready just yet.
#
# add_executable(test_convex_hull_centroid
#   test_convex_hull_centroid.cpp
#   )
# set_property(TARGET test_convex_hull_centroid           PROPERTY FOLDER "Tests")

add_executable(test_convex_hull_aspect_ratio
  test_convex_hull_aspect_ratio.cpp
  )
set_property(TARGET test_convex_hull_aspect_ratio       PROPERTY FOLDER "Tests")

add_executable(test_convex_hull_perimeter
  test_convex_hull_perimeter.cpp
  )
set_property(TARGET test_convex_hull_perimeter          PROPERTY FOLDER "Tests")

add_executable(test_degenerate_convex_hull
  test_degenerate_convex_hull.cpp
  )
set_property(TARGET test_degenerate_convex_hull         PROPERTY FOLDER "Tests")

add_executable(test_log_level
  test_log_level.cpp
  )
set_property(TARGET test_log_level PROPERTY FOLDER "Tests")

add_executable(test_point_at_fraction
  test_point_at_fraction.cpp
  )
set_property(TARGET test_point_at_fraction              PROPERTY FOLDER "Tests")

add_executable(test_point_cartesian
  test_point_cartesian.cpp
)
set_property(TARGET test_point_cartesian                PROPERTY FOLDER "Tests")

add_executable(test_point_geometric_median
  test_point_geometric_median.cpp
)
set_property(TARGET test_point_geometric_median         PROPERTY FOLDER "Tests")

add_executable(test_point_geometry_math
 test_point_geometry_math.cpp
)
set_property(TARGET test_point_geometry_math            PROPERTY FOLDER "Tests")

add_executable(test_point_interpolation
 test_point_interpolation.cpp
)
set_property(TARGET test_point_interpolation            PROPERTY FOLDER "Tests")

add_executable(test_point_lonlat
  test_point_lonlat.cpp
)
set_property(TARGET test_point_lonlat                   PROPERTY FOLDER "Tests")

add_executable(test_base_point_serialization
  test_base_point_serialization.cpp
  )
set_property(TARGET test_base_point_serialization            PROPERTY FOLDER "Tests")

add_executable(test_property_map
 test_property_map.cpp
)
set_property(TARGET test_property_map                   PROPERTY FOLDER "Tests")

add_executable(test_serialize_variant
  test_serialize_variant.cpp
  )
set_property(TARGET test_serialize_variant             PROPERTY FOLDER "Tests")

add_executable(test_simplify_linestring
 test_simplify_linestring.cpp
 )
set_property(TARGET test_simplify_linestring            PROPERTY FOLDER "Tests")

add_executable(test_trajectory_lonlat
 test_trajectory_lonlat.cpp
)
set_property(TARGET test_trajectory_lonlat              PROPERTY FOLDER "Tests")

add_executable(test_trajectory_id
  test_trajectory_id.cpp
)
set_property(TARGET test_trajectory_id PROPERTY FOLDER "Tests")

add_executable(test_trajectory_point_serialization
  test_trajectory_point_serialization.cpp
  )
set_property(TARGET test_trajectory_point_serialization            PROPERTY FOLDER "Tests")

add_executable(test_trajectory_point_lonlat
 test_trajectory_point_lonlat.cpp
)
set_property(TARGET test_trajectory_point_lonlat        PROPERTY FOLDER "Tests")

add_executable(test_trajectory_radius_of_gyration
 test_trajectory_radius_of_gyration.cpp
)
set_property(TARGET test_trajectory_radius_of_gyration  PROPERTY FOLDER "Tests")

add_executable(test_trajectory_serialization
  test_trajectory_serialization.cpp
  )
set_property(TARGET test_trajectory_serialization PROPERTY FOLDER "Tests")

add_executable(test_trajectory_subset
 test_trajectory_subset.cpp
)
set_property(TARGET test_trajectory_subset              PROPERTY FOLDER "Tests")

add_executable(test_trajectory_uuid
 test_trajectory_uuid.cpp
)
set_property(TARGET test_trajectory_uuid        PROPERTY FOLDER "Tests")

add_executable(test_timestamp_format
  test_timestamp_format.cpp
)
set_property(TARGET test_timestamp_format               PROPERTY FOLDER "Tests")

add_executable(test_current_length
  test_current_length.cpp
  )
set_property(TARGET test_current_length                 PROPERTY FOLDER "Tests")

add_executable(test_current_length_fraction
  test_current_length_fraction.cpp
  )
set_property(TARGET test_current_length_fraction        PROPERTY FOLDER "Tests")

add_executable(test_current_time_fraction
  test_current_time_fraction.cpp
  )
set_property(TARGET test_current_time_fraction        PROPERTY FOLDER "Tests")

add_executable(test_memory_use
  test_memory_use.cpp
  )
set_property(TARGET test_memory_use                     PROPERTY FOLDER "Tests")

add_executable(test_trajectory_slicing
  test_trajectory_slicing.cpp
  )
set_property(TARGET test_trajectory_slicing             PROPERTY FOLDER "Tests")

# ----------------------------------------------------------------------
target_link_libraries(test_point_arithmetic
  TracktableCore
  TracktableDomain
  )
target_link_libraries(test_distance
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_convex_hull_area
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_convex_hull_aspect_ratio
  TracktableCore
  ${Boost_LIBRARIES}
)

# target_link_libraries(test_convex_hull_centroid
#   TracktableCore
#   ${Boost_LIBRARIES}
# )

target_link_libraries(test_convex_hull_perimeter
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_current_length
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_current_length_fraction
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_current_time_fraction
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_degenerate_convex_hull
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_log_level
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_at_fraction
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_cartesian
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_point_geometric_median
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_geometry_math
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_point_interpolation
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_point_lonlat
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_base_point_serialization
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_property_map
 TracktableCore
 ${Boost_LIBRARIES}
)

target_link_libraries(test_serialize_variant
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_simplify_linestring
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_id
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_lonlat
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_point_lonlat
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_point_serialization
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_radius_of_gyration
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_serialization
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_trajectory_subset
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_uuid
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_timestamp_format
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_memory_use
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_trajectory_slicing
  TracktableCore
  ${Boost_LIBRARIES}
  )

# ----------------------------------------------------------------------

add_catch2_test(
  C_PointArithmetic
  test_point_arithmetic
)

add_catch2_test(
 C_Distance
 test_distance
)

add_test(
 NAME C_ConvexHullArea
 COMMAND test_convex_hull_area
)

add_test(
 NAME C_ConvexHullAspectRatio
 COMMAND test_convex_hull_aspect_ratio
)

# add_test(
#  NAME C_ConvexHullCentroid
#  COMMAND test_convex_hull_area
# )

add_test(
 NAME C_ConvexHullPerimeter
 COMMAND test_convex_hull_perimeter
)

add_test(
  NAME C_DegenerateConvexHull
  COMMAND test_degenerate_convex_hull
)

# This test is not yet enabled because it depends on capability
# (adding a separate back-end log sink) that we don't yet have.
#
#add_test(
#  NAME C_LogLevel
#  COMMAND test_log_level
#  )

add_test(
  NAME C_MemoryUse
  COMMAND test_memory_use
  )

add_test(
 NAME C_PointAtFraction
 COMMAND test_point_at_fraction
)

add_test(
 NAME C_PointCartesian
 COMMAND test_point_cartesian
)

add_test(
  NAME C_CurrentLength
  COMMAND test_current_length
)

add_test(
  NAME C_CurrentLengthFraction
  COMMAND test_current_length_fraction
)

add_test(
  NAME C_CurrentTimeFraction
  COMMAND test_current_time_fraction
)

add_test(
  NAME C_PointGeometryMath
  COMMAND test_point_geometry_math
)

add_test(
  NAME C_PointGeometricMedian
  COMMAND test_point_geometric_median
)

add_test(
 NAME C_PointLonLat
 COMMAND test_point_lonlat
)

add_test(
  NAME C_PropertyMap
  COMMAND test_property_map
)

add_test(
  NAME C_PointInterpolation
  COMMAND test_point_interpolation
)

add_test(
  NAME C_SerializeVariant
  COMMAND test_serialize_variant
  )

add_test(
  NAME C_SimplifyLinestring
  COMMAND test_simplify_linestring
)

add_test(
  NAME C_TrajectoryId
  COMMAND test_trajectory_id
)

add_test(
  NAME C_TrajectoryLonLat
  COMMAND test_trajectory_lonlat
)

add_test(
  NAME C_TrajectoryPointLonLat
  COMMAND test_trajectory_point_lonlat
)

add_test(
  NAME C_TrajectorySubset
  COMMAND test_trajectory_subset
)

add_test(
  NAME C_TrajectoryRadiusOfGyration
  COMMAND test_trajectory_radius_of_gyration
)

add_test(
  NAME C_TrajectorySerialization
  COMMAND test_trajectory_serialization
  )

add_test(
  NAME C_TimestampFormat
  COMMAND test_timestamp_format
  )

add_test(
  NAME C_TrajectorySlicing
  COMMAND test_trajectory_slicing
  )
