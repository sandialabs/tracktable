#
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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This is tracktable/C++/PythonWrapping/CMakeLists.txt
#
# Unlike the other libraries in Tracktable we do not generate a
# Windows export header in here.  Each Python extension module exports
# a single symbol -- its entry point -- and Boost.Python already
# handles the dllexport/dllimport annotation for that.

message(STATUS "*** DEBUG: ${CMAKE_CURRENT_SOURCE_DIR}: Python3_EXECUTABLE is ‘${Python3_EXECUTABLE}’")

# ----------------------------------------------------------------------
#
# (Not) Linking against libpython
#
# Some Python interpreters link statically against libpython.  Some
# link dynamically.  If we link to a different libpython than the one
# in/alongside the interpreter, we get segfaults at runtime.
#
# The solution is to not link against libpython and instead tell the
# linker to leave unresolved symbols unresolved until load time.  GCC
# and Visual C++ do this by default.  Clang has an applicable link
# flag: "-undefined dynamic_lookup".

if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  # using regular Clang or AppleClang
  set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -undefined dynamic_lookup")
endif()

if (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  set(PYTHON_EXTENSION_LIBRARIES ${Boost_LIBRARIES} ${Python3_LIBRARIES})
else ()
  set(PYTHON_EXTENSION_LIBRARIES ${Boost_LIBRARIES})
endif()

#message(STATUS "Boost_LIBRARIES ${Boost_LIBRARIES}")
#message(STATUS "PYTHON_EXTENSION_LIBRARIES ${PYTHON_EXTENSION_LIBRARIES}")

include(PythonExtension)

set( FEATURE_VECTOR_MAX_DIMENSION 30 CACHE STRING "Maximum dimension of feature vectors for Python wrapping." )

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/PythonWrappingParameters.h.in
  ${CMAKE_CURRENT_BINARY_DIR}/PythonWrappingParameters.h
  )

include_directories(
  ${Python3_INCLUDE_DIRS}
  ${Python3_NumPy_INCLUDE_DIRS}
  ${Boost_INCLUDE_DIR}
  ${Tracktable_SOURCE_DIR}
  ${Tracktable_BINARY_DIR}
  )

link_directories(
  ${Boost_LIBRARY_DIRS}
  ${Tracktable_BINARY_DIR}/lib
)

set(Tracktable_PYTHON_DIR ${Tracktable_SOURCE_DIR}/tracktable/Python/tracktable)

# We use Python-like naming for these files for two reasons.  First,
# we're going to be importing these from Python, so it's consistent.
# Second, the library name has to match what we pass to
# BOOST_PYTHON_MODULE(), so doing it right here will make that look
# right as well.

# This is a trivial module whose purpose is to make sure we can
# build Python extensions at all.  It exports a single function
# called greet() that returns a hello world message.

add_library(_tracktable_hello MODULE
  HelloWorldPythonModule.cpp
)
# puts the target into a folder in Visual studio
set_property(TARGET _tracktable_hello           PROPERTY FOLDER "Python")

#message("PYTHON_EXTENSION_LIBRARIES ${PYTHON_EXTENSION_LIBRARIES}")
target_link_libraries(_tracktable_hello
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_tracktable_hello lib ${Tracktable_PYTHON_DIR})

add_library(_core_types MODULE
  CorePythonModule.cpp
  DateTimeWrapper.cpp
  PairToTupleWrapper.cpp
  PropertyMapWrapper.cpp
  CommonMapWrappers.cpp
  )
set_property(TARGET _core_types PROPERTY FOLDER "Python")

target_link_libraries(_core_types PUBLIC
  TracktableCore
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_core_types lib ${Tracktable_PYTHON_DIR})

add_library(_domain_algorithm_overloads MODULE
  DomainAlgorithmOverloadsPythonModule.cpp
  )
set_property(TARGET _domain_algorithm_overloads PROPERTY FOLDER "Python")

target_link_libraries(_domain_algorithm_overloads PUBLIC
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_domain_algorithm_overloads lib ${Tracktable_PYTHON_DIR})

add_library(_terrestrial MODULE
  TerrestrialDomainModule.cpp
)
set_property(TARGET _terrestrial PROPERTY FOLDER "Python")

target_link_libraries(_terrestrial PUBLIC
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_terrestrial lib ${Tracktable_PYTHON_DIR})

add_library(_cartesian2d MODULE
  Cartesian2DDomainModule.cpp
)
set_property(TARGET _cartesian2d PROPERTY FOLDER "Python")

target_link_libraries(_cartesian2d PUBLIC
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_cartesian2d lib ${Tracktable_PYTHON_DIR})

add_library(_cartesian3d MODULE
  Cartesian3DDomainModule.cpp
)
set_property(TARGET _cartesian3d                PROPERTY FOLDER "Python")

target_link_libraries(_cartesian3d PUBLIC
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
)

install_python_extension(_cartesian3d lib ${Tracktable_PYTHON_DIR})

add_library(_feature_vector_points MODULE
  FeatureVectorModule.cpp
  ExplicitInstantiation/FeatureVectorWrapper_1_5.cpp
  ExplicitInstantiation/FeatureVectorWrapper_6_10.cpp
  ExplicitInstantiation/FeatureVectorWrapper_11_15.cpp
  ExplicitInstantiation/FeatureVectorWrapper_16_20.cpp
  ExplicitInstantiation/FeatureVectorWrapper_21_25.cpp
  ExplicitInstantiation/FeatureVectorWrapper_26_30.cpp
  ExplicitInstantiation/FeatureVectorWrapper_Extra.cpp
  )

If(MSVC)
  set_property(SOURCE FeatureVectorModule.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj ")
Endif(MSVC)
set_property(TARGET _feature_vector_points PROPERTY FOLDER "Python")

target_link_libraries(_feature_vector_points
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_feature_vector_points lib ${Tracktable_PYTHON_DIR})

add_library(_dbscan_clustering MODULE
  DBSCANClusteringPythonModule.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_1_3.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_4_6.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_7_9.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_10_12.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_13_15.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_16_18.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_19_21.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_22_24.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_25_27.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_28_30.cpp
  ExplicitInstantiation/DBSCAN_Wrapper_Extra.cpp
  )
set_property(TARGET _dbscan_clustering PROPERTY FOLDER "Python")

target_link_libraries(_dbscan_clustering PUBLIC
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )


install_python_extension(_dbscan_clustering lib ${Tracktable_PYTHON_DIR})


add_library(_rtree MODULE
  RTreePythonModule.cpp
  ExplicitInstantiation/RTree_Wrapper_1_3.cpp
  ExplicitInstantiation/RTree_Wrapper_4_6.cpp
  ExplicitInstantiation/RTree_Wrapper_7_9.cpp
  ExplicitInstantiation/RTree_Wrapper_10_12.cpp
  ExplicitInstantiation/RTree_Wrapper_13_15.cpp
  ExplicitInstantiation/RTree_Wrapper_16_18.cpp
  ExplicitInstantiation/RTree_Wrapper_19_21.cpp
  ExplicitInstantiation/RTree_Wrapper_22_24.cpp
  ExplicitInstantiation/RTree_Wrapper_25_27.cpp
  ExplicitInstantiation/RTree_Wrapper_28_30.cpp
  ExplicitInstantiation/RTree_Wrapper_Extra.cpp
  )
set_property(TARGET _rtree PROPERTY FOLDER "Python")

target_link_libraries(_rtree PUBLIC
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_rtree lib ${Tracktable_PYTHON_DIR})

get_filename_component(
  Python3_EXECUTABLE_DIRECTORY
  ${Python3_EXECUTABLE}
  DIRECTORY
  )

message(STATUS "Adding wheel target.")
message(STATUS "INFO: Python executable is ${Python3_EXECUTABLE}")
message(STATUS "INFO: Install prefix is ${CMAKE_INSTALL_PREFIX}")
message(STATUS "INFO: Wheel should go in ${CMAKE_BINARY_DIR}/wheel")

if (APPLE)
  find_program(
    FIX_WHEEL_EXECUTABLE
    delocate-wheel
    HINTS
    ${Python3_EXECUTABLE_DIRECTORY}
    DOC
    "delocate-wheel executable: OS X utility to add libraries to Python wheels"
    )
endif (APPLE)

if (UNIX AND NOT APPLE)
  find_program(
    FIX_WHEEL_EXECUTABLE
    auditwheel
    DOC
    "auditwheel: add libraries to a wheel"
    )
endif (UNIX AND NOT APPLE)


add_custom_target( wheel
  COMMAND
  ${CMAKE_COMMAND} -P ${Tracktable_SOURCE_DIR}/CMake/Modules/BuildWheel.cmake
  ${Python3_EXECUTABLE}
  ${CMAKE_BINARY_DIR}
  ${CMAKE_INSTALL_PREFIX}
  ${CMAKE_BINARY_DIR}/wheel
  ${Tracktable_SOURCE_DIR}/packaging/setup-generic.py
  ${FIX_WHEEL_EXECUTABLE}
  WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}
#  DEPENDS install
  )
