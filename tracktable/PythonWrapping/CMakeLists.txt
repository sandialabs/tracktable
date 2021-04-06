#
# Copyright (c) 2014-2021 National Technology and Engineering
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



# ---------------------------------------------------------------------
# Begin find_package(Boost)
# ---------------------------------------------------------------------
#
# We did most of the work of finding Boost up in the top-level CMakeLists.
# However, the Python wrapping needs one component that introduces a
# tricky dependency: the Boost.Python library.  This is because
# libboost_python uses symbols from libpython.  This introduces two
# problems:
#
# 1. The rest of Tracktable has no reason at all to link against
#    libpython.
#
# 2. Depending on exactly which Python distribution you use, linking
#    against libpython might cause your code to segfault.
#
# On top of that, the very filename of the Boost.Python shared library
# changes based on which Python version it was built for.
#
# The cleanest thing to do is to bite the bullet and repeat some of the
# process of finding Boost here in this subdirectory.
#
#
# So, what's the Boost.Python library called?
#
# Versions of Boost from 1.57 through 1.66 generate
# libboost_python3.so for Python 3.  From 1.67 onward we get
# libboost_pythonXY.so for Python X.Y.  In order to figure out the
# proper library name we need to know BOTH the Python version and the
# Boost version.

set(Boost_PYTHON_LIBRARY_SUFFIX "")

if (TRACKTABLE_PYTHON AND Boost_FOUND AND EXISTS ${Python3_EXECUTABLE})
  message(STATUS "Boost_VERSION ${Boost_VERSION}")
  if (Boost_VERSION VERSION_LESS 1.67.0)
    #message(STATUS "This version of Boost uses libpython3.so.")
    # This version of Boost generates libboost_python[3].so.
    set(Boost_PYTHON_LIBRARY_SUFFIX "3")
  else (Boost_VERSION VERSION_LESS 1.67.0)
    #message(STATUS "Python3_VERSION_MAJOR ${Python3_VERSION_MAJOR}")
    #message(STATUS "Python3_VERSION_MINOR ${Python3_VERSION_MINOR}")
    #message(STATUS "This version of Boost needs a versioned Python library.")
    # This version of Boost needs a versioned library.
    set(Boost_PYTHON_LIBRARY_SUFFIX "${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR}")
  endif (Boost_VERSION VERSION_LESS 1.67.0)

  #message(STATUS "Boost_PYTHON_LIBRARY_SUFFIX ${Boost_PYTHON_LIBRARY_SUFFIX}")
  set(BOOST_PYTHON_COMPONENTS python${Boost_PYTHON_LIBRARY_SUFFIX})
else (TRACKTABLE_PYTHON AND Boost_FOUND AND EXISTS ${Python3_EXECUTABLE})
  message(ERROR "Boost.Python library version cannot be determined until both Boost and Python have been found.")
endif (TRACKTABLE_PYTHON AND Boost_FOUND AND EXISTS ${Python3_EXECUTABLE})

# This second check undoes the previous find and looks for all necessary components
unset(Boost_FOUND)
set(ALL_BOOST_COMPONENTS ${ALL_BOOST_COMPONENTS} ${BOOST_PYTHON_COMPONENTS})
message(STATUS "(PythonWrapping) Looking for Boost minimum version ${BOOST_MINIMUM_VERSION_REQUIRED} components ${ALL_BOOST_COMPONENTS}")
find_package(Boost ${BOOST_MINIMUM_VERSION_REQUIRED} REQUIRED COMPONENTS ${ALL_BOOST_COMPONENTS} )

if (NOT Boost_FOUND)
  message(WARNING "(PythonWrapping) DEBUG: Boost not found!")
endif ()


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
  FloatVectorWrapper.cpp
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

add_library(_distance_geometry MODULE
  DistanceGeometryModule.cpp
  )

set_property(TARGET _distance_geometry PROPERTY FOLDER "Python")

target_link_libraries(_distance_geometry
  TracktableCore
  TracktableDomain
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_distance_geometry lib ${Tracktable_PYTHON_DIR})


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


add_library(_logging MODULE
  LoggingModule.cpp
  )
set_property(TARGET _logging PROPERTY FOLDER "Python")

target_link_libraries(_logging PUBLIC
  TracktableCore
  ${PYTHON_EXTENSION_LIBRARIES}
  )

install_python_extension(_logging lib ${Tracktable_PYTHON_DIR})
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

# These modules end up containing so much code due to template 
# instantiation that Microsoft Visual C++ needs to use a slightly
# different object format.

if(MSVC)
  set_property(SOURCE FeatureVectorModule.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj ")
  set_property(SOURCE TerrestrialDomainModule.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj")
  set_property(SOURCE Cartesian2DDomainModule.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj")
  set_property(SOURCE Cartesian3DDomainModule.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj")
  set_property(SOURCE DomainAlgorithmOverloads.cpp APPEND_STRING PROPERTY COMPILE_FLAGS " /bigobj")
endif(MSVC)
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

# Wheel fixup:
#
# On Linux and MacOS, we have programs (auditwheel and delocate)
# that will inspect the contents of the wheel and track down any
# missing binary dependencies such as Boost shared libraries (and
# incidentally Tracktable's shared libraries!), then copy them into
# the wheel.
#
# Windows doesn't have anything comparable.  We have a utility called
# 'winlocate' that tracks down the dependencies and adds them to the
# list of files to be packaged in the wheel.
if (UNIX)
  if (APPLE)
    find_program(
      FIX_WHEEL_EXECUTABLE
      delocate-wheel
      HINTS
      ${Python3_EXECUTABLE_DIRECTORY}
      DOC
      "delocate-wheel executable: OS X utility to add libraries to Python wheels"
    )
  else (APPLE)
    find_program(
      FIX_WHEEL_EXECUTABLE
      auditwheel
      HINTS
      ${Python3_EXECUTABLE_DIRECTORY}
      DOC
      "auditwheel: add libraries to a wheel"
      )
  endif (APPLE)
else (UNIX)
  # Windows doesn't have delocate/auditwheel yet.  We wrote a replacement.
  set(FIX_WHEEL_EXECUTABLE "${Tracktable_SOURCE_DIR}/packaging/winlocate.py")
endif (UNIX)


if (UNIX)
  add_custom_target( wheel
    COMMAND
    ${CMAKE_COMMAND} -P ${Tracktable_SOURCE_DIR}/CMake/Modules/BuildWheel.cmake
    ${Python3_EXECUTABLE}
    ${CMAKE_BINARY_DIR}
    ${CMAKE_INSTALL_PREFIX}
    ${CMAKE_BINARY_DIR}/wheel
    ${Tracktable_SOURCE_DIR}/packaging/setup-generic.py
    ${FIX_WHEEL_EXECUTABLE}
    NO_EXTRA_SEARCH_PATHS
    WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}
#  DEPENDS install
    )
else (UNIX)
  message(STATUS "DEBUG: Boost_LIBRARY_DIRS is ${Boost_LIBRARY_DIRS}")
  add_custom_target( wheel
    COMMAND
    ${CMAKE_COMMAND} -P ${Tracktable_SOURCE_DIR}/CMake/Modules/BuildWheel.cmake
    ${Python3_EXECUTABLE}
    ${CMAKE_BINARY_DIR}
    ${CMAKE_INSTALL_PREFIX}
    ${CMAKE_BINARY_DIR}/wheel
    ${Tracktable_SOURCE_DIR}/packaging/setup-generic.py
    ${FIX_WHEEL_EXECUTABLE}
    # These will be picked up as extra search paths
    ${Boost_LIBRARY_DIRS}
    WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}
    )
endif (UNIX)