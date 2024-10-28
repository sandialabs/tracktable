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

# We need this because heavily templated classes like DBSCAN create
# object files too big for the Visual C++ linker to handle normally.

include(CplusplusTest)

if (MSVC)
  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj" )
endif (MSVC)

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
  ${Tracktable_BINARY_DIR}
  ${Boost_INCLUDE_DIRS}
)

add_cpp_test(NAME C_Cartesian2D_DistanceGeometry_Distance
             SOURCE test_cartesian2d_distance_geometry_by_distance.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES})


add_cpp_test(NAME C_Cartesian2D_DistanceGeometry_Time
             SOURCE test_cartesian2d_distance_geometry_by_time.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_DBSCAN_Cartesian
             SOURCE test_dbscan_cartesian.cpp
             LIBRARIES TracktableCore TracktableDomain ${Boost_LIBRARIES})

add_cpp_test(NAME C_DBSCAN_Decorated_Points
             SOURCE test_dbscan_decorated_points.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_GreatCircleFit
             SOURCE test_great_circle_fit.cpp
             LIBRARIES TracktableDomain TracktableTestSupport TracktableAnalysis
             CATCH2)

add_cpp_test(NAME C_Rtree
             SOURCE test_rtree.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES})

if (MSVC)
  set_property(SOURCE test_rtree.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj ")
endif (MSVC)

add_cpp_test(NAME C_Terrestrial_DistanceGeometry_Distance
             SOURCE test_terrestrial_distance_geometry_by_distance.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_Terrestrial_DistanceGeometry_Time
             SOURCE test_terrestrial_distance_geometry_by_time.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES})

add_cpp_test(NAME C_TrajectoryAssemblyWithDomain
             SOURCE test_trajectory_assembly_with_domain.cpp
             LIBRARIES TracktableDomain TracktableCore ${Boost_LIBRARIES}
             COMMAND test_trajectory_assembly_with_domain ${Tracktable_DATA_DIR}/internal_test_data/Points/SampleTrajectories.csv 91 109 86321
             )

