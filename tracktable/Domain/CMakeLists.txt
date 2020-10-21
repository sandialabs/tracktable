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


# This is tracktable/Domain/CMakeLists.txt

include(GenerateExportHeader)

include_directories(
  ${PROJECT_SOURCE_DIR}
  ${PROJECT_BINARY_DIR}
  ${Boost_INCLUDE_DIR}
)

if (BUILD_TESTING)
   add_subdirectory(Tests)
endif (BUILD_TESTING)


set( Domain_SRCS
  PrintFunctions.cpp
)

set( Domain_HEADERS
  Cartesian2D.h
  Cartesian3D.h
  DomainMacros.h
  FeatureVectors.h
  Terrestrial.h
)

add_library( TracktableDomain
  ${Domain_SRCS}
  ${Domain_HEADERS}
)

target_link_libraries( TracktableDomain
  TracktableCore
)

set_property(
  TARGET TracktableDomain
  PROPERTY SOVERSION ${SO_VERSION}
  )

set_property(
  TARGET TracktableDomain
  PROPERTY VERSION ${TRACKTABLE_VERSION}
  )

generate_export_header( TracktableDomain
   BASE_NAME TRACKTABLE_DOMAIN
   EXPORT_MACRO_NAME TRACKTABLE_DOMAIN_EXPORT
   STATIC_DEFINE TRACKTABLE_DOMAIN_STATIC_LIBRARY
   EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/tracktable/Domain/TracktableDomainWindowsHeader.h
   )

if (APPLE)
    set(CMAKE_INSTALL_BINDIR bin)
    set(CMAKE_INSTALL_LIBDIR lib)
endif ()

install(
  TARGETS TracktableDomain
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
  FILES ${Domain_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Domain
)

install(
  FILES ${PROJECT_BINARY_DIR}/tracktable/Domain/TracktableDomainWindowsHeader.h
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Domain
  )
