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
  ${Boost_INCLUDE_DIR}
)

add_executable(test_domain_terrestrial
  test_domain_terrestrial.cpp
)
# puts the target into a folder in Visual studio
set_property(TARGET test_domain_terrestrial             PROPERTY FOLDER "Tests")

add_executable(test_base_point_terrestrial
  test_base_point_terrestrial.cpp
)
set_property(TARGET test_base_point_terrestrial         PROPERTY FOLDER "Tests")

add_executable(test_feature_vector_to_string
  test_feature_vector_to_string.cpp
)
set_property(TARGET test_feature_vector_to_string PROPERTY FOLDER "Tests")

add_executable(test_trajectory_point_terrestrial
  test_trajectory_point_terrestrial.cpp
)
set_property(TARGET test_trajectory_point_terrestrial   PROPERTY FOLDER "Tests")

add_executable(test_trajectory_terrestrial
  test_trajectory_terrestrial.cpp
)
set_property(TARGET test_trajectory_terrestrial         PROPERTY FOLDER "Tests")

add_executable(test_trajectory_point_terrestrial_ECEF
  test_trajectory_point_terrestrial_ECEF.cpp
)
set_property(TARGET test_trajectory_point_terrestrial_ECEF         PROPERTY FOLDER "Tests")


target_link_libraries(test_domain_terrestrial
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_base_point_terrestrial
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
)

target_link_libraries(test_feature_vector_to_string
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_trajectory_point_terrestrial
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_terrestrial
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_point_terrestrial_ECEF
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
)

add_test(
  NAME C_TerrestrialDomain
  COMMAND test_domain_terrestrial
)

add_test(
  NAME C_BasePointTerrestrial
  COMMAND test_base_point_terrestrial
)

add_test(
  NAME C_FeatureVectorToString
  COMMAND test_feature_vector_to_string
)

add_test(
  NAME C_TrajectoryPointTerrestrial
  COMMAND test_trajectory_point_terrestrial
)

add_test(
  NAME C_TrajectoryTerrestrial
  COMMAND test_trajectory_terrestrial
)

add_test(
  NAME C_TrajectoryPointTerrestrialECEF
  COMMAND test_trajectory_point_terrestrial_ECEF
)
