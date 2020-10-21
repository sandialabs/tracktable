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

# This is tracktable/C++/IO/Tests/CMakeLists.txt

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
  )

add_executable(test_line_reader
  test_line_reader.cpp
)
# puts the target into a folder in Visual studio
set_property(TARGET test_line_reader                    PROPERTY FOLDER "Tests")

add_executable(test_comment_reader
  test_comment_reader.cpp
)
set_property(TARGET test_comment_reader                 PROPERTY FOLDER "Tests")

add_executable(test_generic_reader
  test_generic_reader.cpp
)
set_property(TARGET test_generic_reader                 PROPERTY FOLDER "Tests")

add_executable(test_point_from_tokens_reader
  test_point_from_tokens_reader.cpp
)
set_property(TARGET test_point_from_tokens_reader       PROPERTY FOLDER "Tests")

add_executable(test_reader_skip_headers
  test_reader_skip_headers.cpp
)
set_property(TARGET test_reader_skip_headers       PROPERTY FOLDER "Tests")

add_executable(test_reader_timestamp_formats
  test_reader_timestamp_formats.cpp
)
set_property(TARGET test_reader_timestamp_formats       PROPERTY FOLDER "Tests")

add_executable(test_integrated_point_reader_traj_lonlat
  test_integrated_point_reader_traj_lonlat.cpp
)
set_property(TARGET test_integrated_point_reader_traj_lonlat    PROPERTY FOLDER "Tests")

add_executable(test_integrated_point_reader_cart5
  test_integrated_point_reader_cart5.cpp
)
set_property(TARGET test_integrated_point_reader_cart5  PROPERTY FOLDER "Tests")

add_executable(test_tokenizing_reader
  test_tokenizing_reader.cpp
)
set_property(TARGET test_tokenizing_reader              PROPERTY FOLDER "Tests")

add_executable(test_point_fields
  test_point_fields.cpp
)
set_property(TARGET test_point_fields                   PROPERTY FOLDER "Tests")

add_executable(test_point_writer_base_point
  test_point_writer_base_point.cpp
)
set_property(TARGET test_point_writer_base_point        PROPERTY FOLDER "Tests")

add_executable(test_point_writer_trajectory_point
  test_point_writer_trajectory_point.cpp
)
set_property(TARGET test_point_writer_trajectory_point  PROPERTY FOLDER "Tests")

add_executable(test_point_reader_autoconfig_base_point
  test_point_reader_autoconfig_base_point.cpp
)
set_property(TARGET test_point_reader_autoconfig_base_point     PROPERTY FOLDER "Tests")

add_executable(test_point_reader_autoconfig_trajectory_point
  test_point_reader_autoconfig_trajectory_point.cpp
)
set_property(TARGET test_point_reader_autoconfig_trajectory_point       PROPERTY FOLDER "Tests")

add_executable(test_trajectory_point_reader_default
  test_trajectory_point_reader_default.cpp
)
set_property(TARGET test_trajectory_point_reader_default        PROPERTY FOLDER "Tests")

add_executable(test_trajectory_writer
  test_trajectory_writer.cpp
)
set_property(TARGET test_trajectory_writer              PROPERTY FOLDER "Tests")

add_executable(test_trajectory_reader
  test_trajectory_reader.cpp
)
set_property(TARGET test_trajectory_reader              PROPERTY FOLDER "Tests")

add_executable(test_kml
  test_kml.cpp
)
set_property(TARGET test_kml              PROPERTY FOLDER "Tests")
# ----------------------------------------------------------------------

target_link_libraries(test_comment_reader
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_generic_reader
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_integrated_point_reader_traj_lonlat
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_integrated_point_reader_cart5
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_line_reader
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_point_fields
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_from_tokens_reader
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_reader_skip_headers
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_reader_timestamp_formats
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_point_reader_autoconfig_base_point
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_reader_autoconfig_trajectory_point
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_writer_base_point
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_point_writer_trajectory_point
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_tokenizing_reader
  TracktableCore
  ${Boost_LIBRARIES}
)

target_link_libraries(test_trajectory_point_reader_default
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_trajectory_writer
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_trajectory_reader
  TracktableCore
  ${Boost_LIBRARIES}
  )

target_link_libraries(test_kml
  TracktableIO
  ${Boost_LIBRARIES}
  )
# ------------------------------

add_test(
  NAME C_GenericReader
  COMMAND test_generic_reader
  )

add_test(
  NAME C_IntegratedPointReader_Cartesian5
  COMMAND test_integrated_point_reader_cart5 14 ${Tracktable_SOURCE_DIR}/TestData/Points/PointsWithComments.csv
)

add_test(
  NAME C_IntegratedPointReader_PointFields
  COMMAND test_point_fields 826 ${Tracktable_SOURCE_DIR}/TestData/Points/SampleNFlights.csv
)

add_test(
  NAME C_IntegratedPointReader_TPLonLat
  COMMAND test_integrated_point_reader_traj_lonlat 14 ${Tracktable_SOURCE_DIR}/TestData/Points/PointsWithComments.csv
)

add_test(
  NAME C_LineReader
  COMMAND test_line_reader 1000 ${Tracktable_SOURCE_DIR}/TestData/Points/Points1000.csv
)

add_test(
  NAME C_PointFromTokensReader
  COMMAND test_point_from_tokens_reader 14 ${Tracktable_SOURCE_DIR}/TestData/Points/PointsWithComments.csv
)

add_test(
  NAME C_PointReader_Autoconfig_BasePoint
  COMMAND test_point_reader_autoconfig_base_point
  )

add_test(
  NAME C_PointReader_Autoconfig_TrajectoryPoint
  COMMAND test_point_reader_autoconfig_trajectory_point
  )

add_test(
  NAME C_PointWriter_BasePoint
  COMMAND test_point_writer_base_point
  )

add_test(
  NAME C_PointWriter_TrajectoryPoint
  COMMAND test_point_writer_trajectory_point
  )

add_test(
  NAME C_SkipCommentsReader
  COMMAND test_comment_reader 15 ${Tracktable_SOURCE_DIR}/TestData/Points/PointsWithComments.csv
)

add_test(
  NAME C_SkipHeadersReader
  COMMAND test_reader_skip_headers 4 14 ${Tracktable_SOURCE_DIR}/TestData/Points/PointsWithSkippableHeaders.csv
)

add_test(
  NAME C_TimestampFormatsReader
  COMMAND test_reader_timestamp_formats ${Tracktable_SOURCE_DIR}/TestData/Timestamps/
)

add_test(
  NAME C_StringTokenizingReader
  COMMAND test_tokenizing_reader ${Tracktable_SOURCE_DIR}/TestData/Points/SampleASDI.csv
)

add_test(
  NAME C_TrajectoryPointReader_DefaultConfiguration
  COMMAND test_trajectory_point_reader_default 998 ${Tracktable_SOURCE_DIR}/TestData/Points/Points1000.csv
)

add_test(
  NAME C_TrajectoryWriter
  COMMAND test_trajectory_writer
  )

add_test(
  NAME C_TrajectoryReader
  COMMAND test_trajectory_reader
  )

  add_test(
  NAME C_Kml
  COMMAND test_kml
  )
