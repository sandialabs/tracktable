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

# We need this because heavily templated classes like DBSCAN create
# object files too big for the Visual C++ linker to handle normally.

if (MSVC)
  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj" )
endif (MSVC)

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
  ${Tracktable_BINARY_DIR}
  ${Boost_INCLUDE_DIRS}
)

add_executable(test_dbscan_cartesian
  test_dbscan_cartesian.cpp
)
# puts the target into a folder in Visual studio
set_property(TARGET test_dbscan_cartesian               PROPERTY FOLDER "Tests")

#add_executable(test_dbscan_cs_change
#  test_dbscan_cs_change.cpp
#)
#set_property(TARGET test_dbscan_cs_change               PROPERTY FOLDER "Tests")

add_executable(test_rtree
  test_rtree.cpp
)
If(MSVC)
  set_property(SOURCE test_rtree.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj ")
Endif(MSVC)
set_property(TARGET test_rtree                          PROPERTY FOLDER "Tests")

add_executable(test_trajectory_assembly_with_domain
  test_trajectory_assembly_with_domain.cpp
)
set_property(TARGET test_trajectory_assembly_with_domain        PROPERTY FOLDER "Tests")

add_executable(test_dbscan_decorated_points
  test_dbscan_decorated_points.cpp
  )
set_property(
  TARGET test_dbscan_decorated_points
  PROPERTY FOLDER "Tests"
  )

add_executable(test_terrestrial_distance_geometry_by_distance
  test_terrestrial_distance_geometry_by_distance.cpp
  )
set_property(
  TARGET test_terrestrial_distance_geometry_by_distance
  PROPERTY FOLDER "Tests"
  )

add_executable(test_cartesian2d_distance_geometry_by_distance
  test_cartesian2d_distance_geometry_by_distance.cpp
  )
set_property(
  TARGET test_cartesian2d_distance_geometry_by_distance
  PROPERTY FOLDER "Tests"
  )

add_executable(test_terrestrial_distance_geometry_by_time
  test_terrestrial_distance_geometry_by_time.cpp
  )
set_property(
  TARGET test_terrestrial_distance_geometry_by_time
  PROPERTY FOLDER "Tests"
  )

add_executable(test_cartesian2d_distance_geometry_by_time
  test_cartesian2d_distance_geometry_by_time.cpp
  )
set_property(
  TARGET test_cartesian2d_distance_geometry_by_time
  PROPERTY FOLDER "Tests"
  )

target_link_libraries(test_dbscan_cartesian
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
)

#target_link_libraries(test_dbscan_cs_change
#  TracktableCore
#  TracktableDomain
#  ${Boost_LIBRARIES}
#)

target_link_libraries(test_rtree
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_trajectory_assembly_with_domain
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_dbscan_decorated_points
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_terrestrial_distance_geometry_by_distance
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_cartesian2d_distance_geometry_by_distance
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_terrestrial_distance_geometry_by_time
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_cartesian2d_distance_geometry_by_time
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

add_test(
  NAME C_DBSCAN_Cartesian
  COMMAND test_dbscan_cartesian
)

#add_test(
#  NAME C_DBSCAN_Coordinate_Change
#  COMMAND test_dbscan_cs_change
#)

add_test(
  NAME C_DBSCAN_Decorated_Points
  COMMAND test_dbscan_decorated_points
  )

add_test(
  NAME C_Rtree
  COMMAND test_rtree
  )

add_test(
  NAME C_Terrestrial_DistanceGeometry_Distance
  COMMAND test_terrestrial_distance_geometry_by_distance
  )

add_test(
  NAME C_Cartesian2D_DistanceGeometry_Distance
  COMMAND test_cartesian2d_distance_geometry_by_distance
  )

add_test(
  NAME C_Terrestrial_DistanceGeometry_Time
  COMMAND test_terrestrial_distance_geometry_by_time
  )

add_test(
  NAME C_Cartesian2D_DistanceGeometry_Time
  COMMAND test_cartesian2d_distance_geometry_by_time
  )

add_test(
  NAME C_TrajectoryAssemblyDomain
  COMMAND test_trajectory_assembly_with_domain ${Tracktable_SOURCE_DIR}/TestData/Points/SampleTrajectories.csv 91 109 86321
  )

