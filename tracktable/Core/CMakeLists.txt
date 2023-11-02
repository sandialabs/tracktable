# -*- Mode: cmake; -*-
#
# Copyright (c) 2014-2023 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
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


# This is trajectory/C++/Core/CMakeLists.txt

include(GenerateExportHeader)

include_directories(
  ${PROJECT_SOURCE_DIR}
  ${PROJECT_BINARY_DIR}
  ${Boost_INCLUDE_DIR}
  )

# Most of the files in Core are header-only implementations and don't
# show up here.
set( Core_SRCS
  Logging.cpp
  MemoryUse.cpp
  PointLonLat.cpp
  PropertyConverter.cpp
  PropertyMap.cpp
  PropertyValue.cpp
  Timestamp.cpp
  TimestampConverter.cpp
  UUID.cpp
  )

set( Core_HEADERS
  Box.h
  Conversions.h
  FloatingPointComparison.h
  GeometricMean.h
  GeometricMedian.h
  Geometry.h
  GuardedBoostGeometryHeaders.h
  Logging.h
  MemoryUse.h
  PlatformDetect.h
  PointArithmetic.h
  PointBase.h
  PointCartesian.h
  PointLonLat.h
  PointTraits.h
  PropertyConverter.h
  PropertyMap.h
  PropertyValue.h
  Timestamp.h
  TimestampConverter.h
  TracktableCommon.h
  Trajectory.h
  TrajectoryPoint.h
  UnfortunateWorkarounds.h
  UUID.h
  )

set( Core_Detail_Points_HEADERS
  detail/points/AlmostEqual.h
  detail/points/AssignCoordinates.h
  detail/points/CheckCoordinateEquality.h
  detail/points/InterpolateCoordinates.h
)

set( Core_Detail_AlgorithmSignatures_HEADERS
  detail/algorithm_signatures/Bearing.h
  detail/algorithm_signatures/ConvexHull.h
  detail/algorithm_signatures/Distance.h
  detail/algorithm_signatures/EndToEndDistance.h
  detail/algorithm_signatures/Interpolate.h
  detail/algorithm_signatures/Extrapolate.h
  detail/algorithm_signatures/Intersects.h
  detail/algorithm_signatures/Length.h
  detail/algorithm_signatures/LengthFractionAtPoint.h
  detail/algorithm_signatures/PointAtFraction.h
  detail/algorithm_signatures/PointAtTime.h
  detail/algorithm_signatures/RadiusOfGyration.h
  detail/algorithm_signatures/SpeedBetween.h
  detail/algorithm_signatures/SimplifyLinestring.h
  detail/algorithm_signatures/SphericalCoordinateAccess.h
  detail/algorithm_signatures/SubsetDuringInterval.h
  detail/algorithm_signatures/TimeAtFraction.h
  detail/algorithm_signatures/TimeFractionAtPoint.h
  detail/algorithm_signatures/TransferProperties.h
  detail/algorithm_signatures/TurnAngle.h
)

set( Core_Detail_Implementations_HEADERS
  detail/implementations/CentroidCartesian.h
  detail/implementations/ConvexHullAreaCartesian.h
  detail/implementations/ConvexHullAreaTerrestrial.h
  detail/implementations/ConvexHullCartesian.h
  detail/implementations/ConvexHullTerrestrial.h
  detail/implementations/ConvexHullAspectRatioCartesian.h
  detail/implementations/ConvexHullAspectRatioTerrestrial.h
  detail/implementations/ConvexHullCentroidCartesian.h
  detail/implementations/ConvexHullCentroidTerrestrial.h
  detail/implementations/ConvexHullPerimeterCartesian.h
  detail/implementations/ConvexHullPerimeterTerrestrial.h
  detail/implementations/GenericDistance.h
  detail/implementations/GreatCircleInterpolation.h
  detail/implementations/NorthPoleConvexHull.h
  detail/implementations/PointAtTime.h
  detail/implementations/PointAtFraction.h
  detail/implementations/ProjectedConvexHullTerrestrial.h
  detail/implementations/RadiusOfGyration.h
  detail/implementations/SphericalMath.h
  detail/implementations/SphericalPolygons.h
  detail/implementations/SubsetDuringInterval.h
  detail/implementations/TimeAtFraction.h
  detail/implementations/TrajectoryPointComparison.h
  detail/implementations/TurnAngle.h
)

set( Core_Detail_TraitSignatures_HEADERS
  detail/trait_signatures/Dimension.h
  detail/trait_signatures/Domain.h
  detail/trait_signatures/HasObjectId.h
  detail/trait_signatures/HasProperties.h
  detail/trait_signatures/HasTimestamp.h
  detail/trait_signatures/ObjectId.h
  detail/trait_signatures/PointDomainName.h
  detail/trait_signatures/Tag.h
  detail/trait_signatures/Timestamp.h
  detail/trait_signatures/UndecoratedPoint.h
)

set( Core_WarningGuards_HEADERS
  WarningGuards/CommonBoostWarnings.h
  WarningGuards/DeprecatedDeclaration.h
  WarningGuards/PopWarningState.h
  WarningGuards/PragmaMessages.h
  WarningGuards/PushWarningState.h
  WarningGuards/ShadowedDeclaration.h
  WarningGuards/SizeTConversion.h
  WarningGuards/UnusedTypedef.h
)

add_library( TracktableCore
  ${Core_SRCS}
  ${Core_HEADERS}
  ${Core_Detail_Points_HEADERS}
  ${Core_Detail_AlgorithmSignatures_HEADERS}
  ${Core_Detail_Implementations_HEADERS}
  ${Core_Detail_TraitSignatures_HEADERS}
  ${Core_WarningGuards_HEADERS}
)

set_property(
  TARGET TracktableCore
  PROPERTY SOVERSION ${SO_VERSION}
  )

set_property(
  TARGET TracktableCore
  PROPERTY VERSION ${TRACKTABLE_VERSION}
  )


# The following source_group directives make Visual Studio show the
# header files in their own sub-folders under the project for
# TracktableCore.  If you add a new group of headers above, add a new
# source_group directive with an appropriate sub-folder name
# (generally agreeing with the name of the header group).

source_group("Header Files\\Points" FILES ${Core_Detail_Points_HEADERS})
source_group("Header Files\\AlgorithmSignatures" FILES ${Core_Detail_AlgorithmSignatures_HEADERS})
source_group("Header Files\\Implementations" FILES ${Core_Detail_Implementations_HEADERS})
source_group("Header Files\\TraitSignatures" FILES ${Core_Detail_TraitSignatures_HEADERS})
source_group("Header Files\\WarningGuards" FILES ${Core_WarningGuards_HEADERS})

# Windows shared libraries require declarations in the header file of
# whether a symbol is being exported (provided by a shared library) or
# imported (used by a program linked to that shared library).  The
# file TracktableCoreWindowsHeader.h, created below, contains a macro
# TRACKTABLE_CORE_EXPORT that makes those declarations in TracktableCore.
#
# Incidentally, this is also why CMAKE_CURRENT_BINARY_DIRECTORY is on
# the include path -- since this is a generated file it gets written
# into the build directory rather than the source tree.

generate_export_header( TracktableCore
   BASE_NAME TRACKTABLE_CORE
   EXPORT_MACRO_NAME TRACKTABLE_CORE_EXPORT
   STATIC_DEFINE TRACKTABLE_CORE_STATIC_LIBRARY
   EXPORT_FILE_NAME TracktableCoreWindowsHeader.h
   )

target_link_libraries(TracktableCore ${Boost_LIBRARIES} Threads::Threads)

if (BUILD_TESTING)
  add_subdirectory(Tests)
endif (BUILD_TESTING)

install(
  FILES ${Core_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core
)

install(
  FILES ${CMAKE_BINARY_DIR}/tracktable/Core/TracktableCoreWindowsHeader.h
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core
  )

install(
  FILES ${Core_Detail_AlgorithmSignatures_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core/detail/algorithm_signatures
)

install(
  FILES ${Core_Detail_Points_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core/detail/points
)

install(
  FILES ${Core_Detail_Implementations_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core/detail/implementations
)

install(
  FILES ${Core_Detail_TraitSignatures_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core/detail/trait_signatures
)

install(
  FILES ${Core_WarningGuards_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/Core/WarningGuards
)

if (APPLE)
    set(CMAKE_INSTALL_BINDIR bin)
    set(CMAKE_INSTALL_LIBDIR lib)
endif ()

install(
  TARGETS TracktableCore
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

if (TRACKTABLE_PYTHON)
  message(STATUS "Installing C++ shared libraries alongside Python extensions.")
  install(
    TARGETS TracktableCore
    RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}/Python/tracktable/lib"
    LIBRARY DESTINATION "${CMAKE_INSTALL_PREFIX}/Python/tracktable/lib"
    RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}/Python/tracktable/lib"
    ARCHIVE
  )
endif ()