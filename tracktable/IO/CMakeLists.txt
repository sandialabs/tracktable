# Copyright (c) 2014-2017 National Technology and Engineering
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


# This is tracktable/C++/IO/CMakeLists.txt

include(GenerateExportHeader)

include_directories(
  ${PROJECT_SOURCE_DIR}
  ${PROJECT_BINARY_DIR}
  ${Boost_INCLUDE_DIR}
)

if (BUILD_TESTING)
  add_subdirectory(Tests)
endif (BUILD_TESTING)

set( IO_SOURCES
  KmlOut.cpp
)
set( IO_Headers
  GenericReader.h
  LineReader.h
  ParseExceptions.h
  PointFromTokensReader.h
  PointReader.h
  PointWriter.h
  SkipCommentsReader.h
  StringTokenizingReader.h
  TokenWriter.h
  TrajectoryReader.h
  TrajectoryWriter.h
  KmlOut.h
)

set ( IO_Detail_HEADERS
  detail/CountProperties.h
  detail/HeaderStrings.h
  detail/PointHeader.h
  detail/PointReaderDefaultConfiguration.h
  detail/PropertyMapReadWrite.h
  detail/SetProperties.h
  detail/TrajectoryHeader.h
  detail/WriteObjectId.h
  detail/WriteTimestamp.h
)


#this adds the project to Visual Studio on Windows so the files are
# visible without creating a build command
add_library( TracktableIO
  ${IO_SOURCES}
  ${IO_Headers}
  ${IO_Detail_HEADERS}
)

target_link_libraries( TracktableIO
   TracktableCore
   ${Boost_LIBRARIES}
)

set_property(
  TARGET TracktableIO
  PROPERTY SOVERSION ${SO_VERSION}
  )

set_property(
  TARGET TracktableIO
  PROPERTY VERSION ${TRACKTABLE_VERSION}
  )

source_group ("Header Files\\Detail" FILES ${IO_Detail_HEADERS})

generate_export_header( TracktableIO
   BASE_NAME TRACKTABLE_IO
   EXPORT_MACRO_NAME TRACKTABLE_IO_EXPORT
   STATIC_DEFINE TRACKTABLE_IO_STATIC_LIBRARY
   EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/tracktable/IO/TracktableIOWindowsHeader.h
   )

if (APPLE)
    set(CMAKE_INSTALL_BINDIR bin)
    set(CMAKE_INSTALL_LIBDIR lib)
endif ()

install(
  TARGETS TracktableIO
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
  FILES ${IO_Headers}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/IO
)

install(
  FILES ${IO_Detail_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/IO/detail
)

