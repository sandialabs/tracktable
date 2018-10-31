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

find_package(PythonLibs REQUIRED)
find_package(NumPy REQUIRED)

# Recent versions of Boost.Python generate libboost_python.so for
# Python 2 and libboost_python3.so for Python 3.  CMake has not yet
# caught up to this so we have to determine the version number by hand.

set(Boost_PYTHON_LIBRARY_NAME "python")

include(FindPythonInterp)
if (PYTHONINTERP_FOUND)
  if (PYTHON_VERSION_MAJOR EQUAL 3)
    set(Boost_PYTHON_LIBRARY_NAME "python3")
  endif (PYTHON_VERSION_MAJOR EQUAL 3)
else (PYTHONINTERP_FOUND)
  message(WARNING "Couldn't find a Python interpreter on your path.  Assuming Python 2.")
endif (PYTHONINTERP_FOUND)

find_package(Boost 1.57 COMPONENTS date_time regex ${Boost_PYTHON_LIBRARY_NAME} REQUIRED)

include(PythonExtension)

set( FEATURE_VECTOR_MAX_DIMENSION 30 CACHE STRING "Maximum dimension of feature vectors for Python wrapping." )

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/PythonWrappingParameters.h.in
  ${CMAKE_CURRENT_BINARY_DIR}/PythonWrappingParameters.h
  )

include_directories(
  ${Tracktable_SOURCE_DIR}
  ${Tracktable_BINARY_DIR}
  ${Boost_INCLUDE_DIR}
  ${PYTHON_INCLUDE_DIRS}
  ${NUMPY_INCLUDE_DIRS}
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

target_link_libraries(_tracktable_hello
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
  )

install_python_extension( _tracktable_hello core ${Tracktable_PYTHON_DIR} )

add_library(_core_types MODULE
  CorePythonModule.cpp
  DateTimeWrapper.cpp
  PairToTupleWrapper.cpp
  PropertyMapWrapper.cpp
  CommonMapWrappers.cpp
  )
set_property(TARGET _core_types                PROPERTY FOLDER "Python")

target_link_libraries(_core_types
  TracktableCore
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
)

install_python_extension(_core_types core ${Tracktable_PYTHON_DIR})

add_library(_domain_algorithm_overloads MODULE
  DomainAlgorithmOverloadsPythonModule.cpp
  )
set_property(TARGET _domain_algorithm_overloads PROPERTY FOLDER "Python")

target_link_libraries(_domain_algorithm_overloads
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
)

install_python_extension(_domain_algorithm_overloads core ${Tracktable_PYTHON_DIR})

add_library(_terrestrial MODULE
  TerrestrialDomainModule.cpp
)
set_property(TARGET _terrestrial                PROPERTY FOLDER "Python")

target_link_libraries(_terrestrial
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
)

install_python_extension(_terrestrial domain ${Tracktable_PYTHON_DIR})


add_library(_cartesian2d MODULE
  Cartesian2DDomainModule.cpp
)
set_property(TARGET _cartesian2d                PROPERTY FOLDER "Python")

target_link_libraries(_cartesian2d
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
)

install_python_extension(_cartesian2d domain ${Tracktable_PYTHON_DIR})

add_library(_cartesian3d MODULE
  Cartesian3DDomainModule.cpp
)
set_property(TARGET _cartesian3d                PROPERTY FOLDER "Python")

target_link_libraries(_cartesian3d
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
)

install_python_extension(_cartesian3d domain ${Tracktable_PYTHON_DIR})


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
set_property(TARGET _feature_vector_points      PROPERTY FOLDER "Python")

target_link_libraries(_feature_vector_points
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
  )

install_python_extension(_feature_vector_points domain ${Tracktable_PYTHON_DIR})

add_library(_dbscan_clustering
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
set_property(TARGET _dbscan_clustering          PROPERTY FOLDER "Python")

target_link_libraries(_dbscan_clustering
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
  )


install_python_extension(_dbscan_clustering analysis ${Tracktable_PYTHON_DIR})


add_library(_rtree
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
set_property(TARGET _rtree          PROPERTY FOLDER "Python")

target_link_libraries(_rtree
  TracktableCore
  TracktableDomain
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
  )


install_python_extension(_rtree analysis ${Tracktable_PYTHON_DIR})
