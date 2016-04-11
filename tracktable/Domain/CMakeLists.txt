# Copyright (c) 2014, Sandia Corporation.
# All rights reserved.
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

find_package( Boost REQUIRED )
include(GenerateExportHeader)

include_directories(
  ${Tracktable_SOURCE_DIR}
  ${Tracktable_BINARY_DIR}
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

generate_export_header( TracktableDomain
   BASE_NAME TRACKTABLE_DOMAIN
   EXPORT_MACRO_NAME TRACKTABLE_DOMAIN_EXPORT
   STATIC_DEFINE TRACKTABLE_DOMAIN_STATIC_LIBRARY
   EXPORT_FILE_NAME ${Tracktable_BINARY_DIR}/tracktable/Domain/TracktableDomainWindowsHeader.h
   )


install(
  TARGETS TracktableDomain
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

install(
  FILES ${Domain_HEADERS}
  DESTINATION include/tracktable/Domain
)

install(
  FILES ${CMAKE_BINARY_DIR}/tracktable/Domain/TracktableDomainWindowsHeader.h
  DESTINATION include/tracktable/Domain
  )
