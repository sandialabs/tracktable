# -*- Mode: cmake; -*-
#
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

# Tracktable C++ Analysis Library

# So far this is a header-only implementation.  The lack of libraries
# being built is not an error.

include_directories(
  ${Tracktable_SOURCE_DIR}
  ${Boost_INCLUDE_DIR}
)

set( Analysis_HEADERS
  AssembleTrajectories.h
  ComputeDBSCANClustering.h
  DistanceGeometry.h
  RTree.h
  GuardedBoostGeometryRTreeHeader.h
)

set( Detail_HEADERS
  detail/dbscan_points.h
  detail/point_converter.h
  detail/AssembleTrajectoriesIterator.h
  detail/dbscan_implementation.h
  detail/dbscan_drivers.h
  detail/point_converter.h
  detail/extract_pair_member.h
  detail/transfer_point_coordinates.h
)

#this adds the project to Visual Studio on Windows so the files are
# visible without creating a build command
add_custom_target( TracktableAnalysis
  SOURCES
  ${Analysis_HEADERS}
  ${Detail_HEADERS}
)

#This puts the header files under a separate folder in Visual Studio
source_group ("Header Files\\Detail" FILES ${Detail_HEADERS})

if (BUILD_TESTING)
  add_subdirectory(Tests)
endif (BUILD_TESTING)

install(
  FILES ${Analysis_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Analysis
)

install(
  FILES ${Detail_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Analysis/detail
)
