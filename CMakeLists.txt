# Copyright (c) 2014-2017 National Technology and Engineering
# Solutions of Sandia, LLC . Under the terms of Contract DE-NA0003525
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

set(CMAKE_LEGACY_CYGWIN_WIN32 0)

cmake_minimum_required(VERSION 3.12)
if (POLICY CMP0042)
  cmake_policy(SET CMP0042 NEW)
  set(CMAKE_MACOSX_RPATH ${Tracktable_BINARY_DIR}/lib)
endif ()

include(GNUInstallDirs)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# set(Boost_DEBUG ON)

##########################################################################
# Release variables
##########################################################################

set(TRACKTABLE_VERSION 1.2.2)
set(RPM_RELEASE 4)

# UNIX library ABI versioning
# CURRENT : REVISION : AGE
# +1 :  ? : +1 == new interface that does not break old one
# +1 :  ? :  0 == new interface that breaks old one
#  ? :  ? :  0 == no new interfaces, but breaks apps
#  ? : +1 :  ? == just some internal changes, nothing breaks but might work better
set(UNIX_SO_VERSION_CURRENT  0)
set(UNIX_SO_VERSION_REVISION 0)
set(UNIX_SO_VERSION_AGE      0)

##########################################################################
# End release variables
##########################################################################

if (UNIX)
  set(UNIX_SO_VERSION ${UNIX_SO_VERSION_CURRENT}.${UNIX_SO_VERSION_REVISION}.${UNIX_SO_VERSION_AGE})
  set(SO_VERSION ${UNIX_SO_VERSION})
else()
  set(SO_VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})
endif()

project(Tracktable VERSION ${TRACKTABLE_VERSION})

include(CTest)

set(TRACKTABLE_INCLUDEDIR tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}/tracktable)

# We include CMake modules to find NumPy and a good set of Python
# libraries.  Add them to the search path.
set(CMAKE_MODULE_PATH
  ${CMAKE_MODULE_PATH}
  "${CMAKE_CURRENT_SOURCE_DIR}/CMake/Modules")

# Generic output paths for build systems with one output directory
set( CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib )
set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib )
set( CMAKE_RUNTIME_OUTPUT_DIRECTORY ${Tracktable_BINARY_DIR}/bin )

# Build-type-specific output paths for things like MSVC, XCode
foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )
  string( TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG )
  set( CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${Tracktable_BINARY_DIR}/bin )
  set( CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${Tracktable_BINARY_DIR}/lib )
  set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${Tracktable_BINARY_DIR}/lib )
endforeach( OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES )

# ----------------------------------------------------------------------

# Set RPATH for all libraries and executables we build
SET(CMAKE_SKIP_BUILD_RPATH FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)

SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_LIBDIR}")

# add the automatically determined parts of the RPATH which point to
# directories outside the build tree to the install RPATH
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# the RPATH to be used when installing, but only if it's not a system directory
LIST(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_LIBDIR}" isSystemDir)
IF("${isSystemDir}" STREQUAL "-1")
   SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_LIBDIR}")
ENDIF("${isSystemDir}" STREQUAL "-1")

set(MACOSX_RPATH ON)
set(CMAKE_MACOSX_RPATH ON)

# ----------------------------------------------------------------------

### Organize programs into folders in Visual Studio, Windows
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

option(BUILD_SHARED_LIBS "Build shared libraries.  Required for Python wrapping." ON)
option(BUILD_PYTHON_WRAPPING "Wrap trajectory classes for use in Python." ON)
option(BUILD_EXAMPLES "Build tracktable example programs" ON)
option(BUILD_DOCUMENTATION "Build documentation for Tracktable." OFF)
option(USE_ANACONDA_LINK_FLAGS "Use Anaconda-specific link flags." OFF)

# ----------------------------------------------------------------------

if (BUILD_SHARED_LIBS)
  message(STATUS "Building shared libraries.")
  add_definitions(-DBUILDING_SHARED_LIBS)
  add_definitions(-DBOOST_ALL_DYN_LINK)
  #set(CMAKE_INSTALL_RPATH ${CMAKE_INSTALL_LIBDIR})
  set(Boost_USE_STATIC_LIBS OFF)
else (BUILD_SHARED_LIBS)
  if (BUILD_PYTHON_WRAPPING)
    message(ERROR "You must turn on BUILD_SHARED_LIBS if you want to use Tracktable's Python interface.")
  else (BUILD_PYTHON_WRAPPING)
    message(STATUS "Building static libraries.")
    set(Boost_USE_STATIC_LIBS ON)
  endif (BUILD_PYTHON_WRAPPING)
endif (BUILD_SHARED_LIBS)

# ----------------------------------------------------------------------

# Add a target to generate combined documentation with Doxygen and Sphinx
if (BUILD_DOCUMENTATION)
  find_package(Doxygen REQUIRED)

#  message("Before FindSphinx, Python exe is ${Sphinx_PYTHON_EXECUTABLE}")
  find_package(Sphinx REQUIRED)
#  message("After FindSphinx, Python exe is ${Sphinx_PYTHON_EXECUTABLE}")

  set( DOC_SOURCE_DIR ${Tracktable_SOURCE_DIR}/Documentation )
  set( DOC_BINARY_DIR ${Tracktable_BINARY_DIR}/Documentation )

  if(DOXYGEN_FOUND AND Sphinx_FOUND)
    configure_file(
      ${DOC_SOURCE_DIR}/Doxyfile.in
      ${DOC_BINARY_DIR}/Doxyfile
      @ONLY
      )

    # Yes, I'm writing a file into the source tree.  Sphinx requires
    # that its configuration file (conf.py) exist in the source tree
    # even though it can put all of its generated files elsewhere.
    configure_file(
      ${DOC_SOURCE_DIR}/conf.py.in
      ${DOC_SOURCE_DIR}/conf.py
      @ONLY
      )


  add_custom_target( DoxygenXML
    ${DOXYGEN_EXECUTABLE} ${DOC_BINARY_DIR}/Doxyfile
    WORKING_DIRECTORY ${DOC_BINARY_DIR}
    COMMENT "Generating XML documentation with Doxygen" VERBATIM
    )

  set(Sphinx_BUILD_DIR "${DOC_BINARY_DIR}/_build")


  # NOTE: This approach to setting PYTHONPATH will only work on
  # Unix-like systems.  In CMake 3.1 we will get the '-E env'
  # capability which is what we really need here.  Since requiring the
  # bleeding-edge version of CMake isn't a terribly friendly thing to
  # do, I will probably end up faking it with batch files.

  add_custom_target( doc
      ${PYTHON_EXECUTABLE} ${Sphinx_BUILD_EXECUTABLE}
      -b html
      -d "${Sphinx_BUILD_DIR}/doctrees"
      ${DOC_SOURCE_DIR}
      ${DOC_BINARY_DIR}/html

    DEPENDS DoxygenXML
    WORKING_DIRECTORY ${DOC_SOURCE_DIR}
    )

  else(DOXYGEN_FOUND AND Sphinx_FOUND)
    message("ERROR: Please provide paths to the Sphinx and Doxygen executables.")
  endif(DOXYGEN_FOUND AND Sphinx_FOUND)
endif (BUILD_DOCUMENTATION)


# ----------------------------------------------------------------------

install(FILES LICENSE.txt DESTINATION ${CMAKE_INSTALL_DOCDIR})
install(FILES README.md DESTINATION ${CMAKE_INSTALL_DOCDIR})

if (BUILD_PYTHON_WRAPPING)
  install(FILES LICENSE.txt DESTINATION ${CMAKE_INSTALL_DOCDIR}/Python/tracktable)
  install(FILES README.md DESTINATION ${CMAKE_INSTALL_DOCDIR}/Python/tracktable)
endif ()
# ----------------------------------------------------------------------

if (BUILD_PYTHON_WRAPPING)
  if (NOT BUILD_SHARED_LIBS)
    message("Python wrapping requires shared libraries.  Please turn on BUILD_SHARED_LIBS.")
  endif ()
  if (USE_ANACONDA_LINK_FLAGS)
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -undefined dynamic_lookup")
  endif (USE_ANACONDA_LINK_FLAGS)
endif ()


if (BUILD_TESTING)
  if (NOT EXISTS "${Tracktable_BINARY_DIR}/TestOutput")
     file(MAKE_DIRECTORY "${Tracktable_BINARY_DIR}/TestOutput")
  endif()
  option(TEST_MOVIES "Include tests of movie-making.  These take a few minutes each." OFF)
endif (BUILD_TESTING)

add_subdirectory(tracktable)

message(STATUS "Project source directory: ${PROJECT_SOURCE_DIR}")

##########################################################################
# pkgconfig variables
##########################################################################
if (UNIX)

  set(PKGCONFIG_VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})
  set(PKGCONFIG_FILE tracktable-${PKGCONFIG_VERSION}.pc)

  configure_file(
    ${PROJECT_SOURCE_DIR}/tracktable.pc.in
    ${PROJECT_BINARY_DIR}/${PKGCONFIG_FILE}
    @ONLY IMMEDIATE
  )

  install(FILES ${PKGCONFIG_FILE} DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)

  set(CPACK_GENERATOR TBZ2)
  set(CPACK_PACKAGE_FILE_NAME tracktable)
  set(CPACK_ARCHIVE_FILE_NAME ${CPACK_PACKAGE_FILE_NAME}-${TRACKTABLE_VERSION})
  set(CPACK_SOURCE_GENERATOR TBZ2)
  set(CPACK_SOURCE_IGNORE_FILES
    "/build/;"
    "/.git/;"
    "/.ipynb_checkpoints/"
  )
  include(CPack)

endif ()

# Effectively, if LINUX
if (UNIX AND NOT APPLE)
  configure_file("${CMAKE_CURRENT_SOURCE_DIR}/packaging/rpm/rhel7/tracktable.spec.in" "${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/tracktable.spec" @ONLY IMMEDIATE)

  add_custom_target(srpm_rhel7
      COMMAND "${CMAKE_COMMAND}" --build . --target package_source
      WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
      COMMAND mock --buildsrpm --spec ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/tracktable.spec --sources Tracktable-${TRACKTABLE_VERSION}-Source.tar.bz2 --resultdir=packaging/rhel7/srpms/
      COMMENT Building source rpms with mock
  )

  add_custom_target(srpm
      DEPENDS srpm_rhel7
  )

  add_custom_target(rpm_rhel7
      COMMAND mock --no-clean rebuild packaging/rhel7/srpms/tracktable-${TRACKTABLE_VERSION}-${RPM_RELEASE}*.src.rpm --resultdir=packaging/rhel7/rpms
      DEPENDS srpm
      COMMENT Building rpms with mock
  )
  
  add_custom_target(rpm
      DEPENDS rpm_rhel7
  )
  
endif ()

