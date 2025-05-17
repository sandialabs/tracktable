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

# This is tracktable/C++/RW/Tests/CMakeLists.txt

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
  ${Tracktable_BINARY_DIR}
  )


add_cpp_test(
  NAME C_GenericReader
  SOURCE test_generic_reader.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_IntegratedPointReader_TPLonLat
  SOURCE test_integrated_point_reader_traj_lonlat.cpp
  LIBRARIES TracktableCore
  COMMAND test_integrated_point_reader_traj_lonlat 14 ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv
)

add_cpp_test(
  NAME C_IntegratedPointReader_Cartesian5
  SOURCE test_integrated_point_reader_cart5.cpp
  LIBRARIES TracktableCore
  COMMAND test_integrated_point_reader_cart5 14 ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv
)

add_cpp_test(
  NAME C_LineReader
  SOURCE test_line_reader.cpp
  LIBRARIES TracktableCore
  COMMAND test_line_reader 1000 ${Tracktable_DATA_DIR}/internal_test_data/Points/Points1000.csv
)

add_cpp_test(
  NAME C_IntegratedPointReader_PointFields
  SOURCE test_point_fields.cpp
  LIBRARIES TracktableCore
  COMMAND test_point_fields 826 ${Tracktable_DATA_DIR}/internal_test_data/Points/SampleNFlights.csv
)

add_cpp_test(
  NAME C_PointFromTokensReader
  SOURCE test_point_from_tokens_reader.cpp
  LIBRARIES TracktableCore
  COMMAND test_point_from_tokens_reader 14 ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv
)

add_cpp_test(
  NAME C_PointReader_Autoconfig_BasePoint
  SOURCE test_point_reader_autoconfig_base_point.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_PointReader_Autoconfig_TrajectoryPoint
  SOURCE test_point_reader_autoconfig_trajectory_point.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_PointWriter_BasePoint
  SOURCE test_point_writer_base_point.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_PointWriter_TrajectoryPoint
  SOURCE test_point_writer_trajectory_point.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_ReaderTimestampFormats
  SOURCE test_reader_timestamp_formats.cpp
  LIBRARIES TracktableCore
  COMMAND test_reader_timestamp_formats ${Tracktable_DATA_DIR}/internal_test_data/Timestamps/
)

add_cpp_test(
  NAME C_SkipCommentsReader
  SOURCE test_comment_reader.cpp
  LIBRARIES TracktableCore
  COMMAND test_comment_reader 15 ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv
)

add_cpp_test(
  NAME C_SkipHeadersReader
  SOURCE test_reader_skip_headers.cpp
  LIBRARIES TracktableCore
  COMMAND test_reader_skip_headers 4 14 ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithSkippableHeaders.csv
)

add_cpp_test(
  NAME C_StringTokenizingReader
  SOURCE test_tokenizing_reader.cpp
  LIBRARIES TracktableCore
  COMMAND test_tokenizing_reader ${Tracktable_DATA_DIR}/internal_test_data/Points/SampleASDI.csv
)

add_cpp_test(
  NAME C_TrajectoryPointReader_DefaultConfiguration
  SOURCE test_trajectory_point_reader_default.cpp
  TARGET test_trajectory_point_reader_default
  LIBRARIES TracktableDomain TracktableCore
  COMMAND test_trajectory_point_reader_default 998 ${Tracktable_DATA_DIR}/internal_test_data/Points/Points1000.csv
)

add_cpp_test(
  NAME C_TrajectoryReader
  SOURCE test_trajectory_reader.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_TrajectoryWriter
  SOURCE test_trajectory_writer.cpp
  LIBRARIES TracktableCore
)

add_cpp_test(
  NAME C_KML
  SOURCE test_kml.cpp
  LIBRARIES TracktableCore TracktableRW
  CATCH2
)

