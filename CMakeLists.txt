# Copyright (c) 2014-2020 National Technology and Engineering
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
message(STATUS "Building with CMake version ${CMAKE_VERSION}")

if (POLICY CMP0042)
  cmake_policy(SET CMP0042 NEW)
  set(CMAKE_MACOSX_RPATH ${Tracktable_BINARY_DIR}/lib)
endif ()

# This policy is supposed to set Python3_FIND_STRATEGY=LOCATION.
# However, at least on CMake 3.16.5 on MacOS, setting it appears
# to have no effect: we observe the same behavior we had previously
# with Python3_FIND_STRATEGY=VERSION.
#
# We're going to manually set Python3_FIND_STRATEGY for now.
if (POLICY CMP0094)
  cmake_policy(SET CMP0094 NEW)
endif ()

# TODO: Once we can verify that CMake policy CMP0094 produces the
# behavior the documentation claims it should, we will remove this
# line and let the policy mechanism handle it.
set(Python3_FIND_STRATEGY LOCATION)

if (UNIX AND NOT APPLE)
  set(LINUX TRUE)
endif ()


set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# set(Boost_DEBUG ON)

##########################################################################
# Begin RELEASE VARIABLES
#-------------------------------------------------------------------------

set(TRACKTABLE_VERSION 1.4.0)
set(RPM_RELEASE 6)

project(Tracktable LANGUAGES CXX VERSION ${TRACKTABLE_VERSION})

include(GNUInstallDirs)

# UNIX library ABI versioning according to libtool:
#
# A libtool version number C.R.A has three components:
#
# C - current library interface ID (abbreviated CURRENT), an integer.
# Any release that makes user-visible changes to the interface must
# increment CURRENT.
#
# R - interface revision number (abbreviated REVISION).  Any release
# that changes things under the hood but does not add new features or
# break existing code should increment REVISION.  Reset REVISION
# to zero whenever CURRENT changes.
#
# A - "age" of this release (abbreviated AGE).  (CURRENT - AGE) is the
# oldest interface version supported by a release.  If a new release breaks
# existing code, AGE must be reset to 0.  If a new release adds new features
# and does not break existing code, AGE should be incremented by 1.
#
# NOTE: This version information is often referred to as the
# "compatibility version".  It is not the same as the version number
# that is often attached to the software release as a whole.
#
# Quick reference:
# CURRENT : REVISION : AGE
# +1 :  ? : +1 == new interface that does not break old one
# +1 :  ? :  0 == new interface that breaks old one
#  ? :  ? :  0 == no new interfaces, but breaks apps
#  ? : +1 :  ? == just some internal changes, nothing breaks but might work better
set(UNIX_SO_VERSION_CURRENT  4)
set(UNIX_SO_VERSION_REVISION 0)
set(UNIX_SO_VERSION_AGE      3)

#-------------------------------------------------------------------------
# End RELEASE VARIABLES
##########################################################################

if (UNIX)
  set(UNIX_SO_VERSION ${UNIX_SO_VERSION_CURRENT}.${UNIX_SO_VERSION_REVISION}.${UNIX_SO_VERSION_AGE})
  set(SO_VERSION ${UNIX_SO_VERSION})
else()
  set(SO_VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})
endif()

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

# ----------------------------------------------------------------------

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

# add the automatically determined parts of the RPATH which point to
# directories outside the build tree to the install RPATH
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# the RPATH to be used when installing, but only if it's not a system directory
LIST(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_LIBDIR}" isSystemDir)
IF("${isSystemDir}" STREQUAL "-1")
   # This RPATH is absolute.  This is what you want when you're installing
   # into something like your home directory.
   SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
ELSE("${isSystemDir}" STREQUAL "-1")
  # This RPATH is relative.  It does not contain any sort of prefix.  That makes
  # it suitable for use in system directories like /usr and /usr/local.
  SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_LIBDIR}")
ENDIF("${isSystemDir}" STREQUAL "-1")

set(MACOSX_RPATH ON)
set(CMAKE_MACOSX_RPATH ON)

# ----------------------------------------------------------------------

### Organize programs into folders in Visual Studio, Windows
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

#=========================================================================
# Begin options and cache variables
#-------------------------------------------------------------------------
include(CMakeDependentOption)
option(BUILD_SHARED_LIBS "Build shared libraries.  Required for Python wrapping." ON)
CMAKE_DEPENDENT_OPTION(
  TRACKTABLE_PYTHON "Build and install tracktable's python bindings." ON
  "BUILD_SHARED_LIBS" OFF)
option(BUILD_EXAMPLES "Build tracktable example programs" ON)
option(BUILD_DOCUMENTATION "Build Python and C++ documentation for Tracktable." OFF)
option(BUILD_DOCUMENTATION_CXX_ONLY "Build only C++ documentation for Tracktable." OFF)
set(PYTHON_INSTALL_PREFIX "Python/tracktable" CACHE PATH "Install directory for python modules" )
set(Python3_EXECUTABLE "" CACHE FILEPATH "Python executable for running tests and compiling modules")
set(Python3_ROOT_DIR "" CACHE PATH "Location of python installation for running tests and compiling modules")
#-------------------------------------------------------------------------
# End options and cache variables
#=========================================================================

#=========================================================================
# Begin FindPython3
#-------------------------------------------------------------------------
# Look for python early if we're going to build the wrappers
# These symbols are also used to look for Sphinx
if (TRACKTABLE_PYTHON)
  message(STATUS "Building and installing python bindings")
  if (UNIX AND APPLE)
    find_package(Python3 COMPONENTS Interpreter Development)
  else (UNIX AND APPLE)
    find_package(Python3 COMPONENTS Interpreter Development NumPy)
  endif(UNIX AND APPLE)
else(TRACKTABLE_PYTHON)
  message(STATUS "Python bindings will NOT be built or installed")
endif (TRACKTABLE_PYTHON)
#-------------------------------------------------------------------------
# End FindPython3
#=========================================================================


if (BUILD_SHARED_LIBS)
  message(STATUS "Building SHARED libraries.")
  add_definitions(-DBUILDING_SHARED_LIBS)
  add_definitions(-DBOOST_ALL_DYN_LINK)
  #set(CMAKE_INSTALL_RPATH ${CMAKE_INSTALL_LIBDIR})
  set(Boost_USE_STATIC_LIBS OFF)
else (BUILD_SHARED_LIBS)
#  if (TRACKTABLE_PYTHON)
#    message(ERROR "You must turn on BUILD_SHARED_LIBS if you want to use Tracktable's Python interface.")
#  else (TRACKTABLE_PYTHON)
    message(STATUS "Building STATIC libraries.")
    set(Boost_USE_STATIC_LIBS ON)
#  endif (TRACKTABLE_PYTHON)
endif (BUILD_SHARED_LIBS)

#=========================================================================
# Begin DOCUMENTATION
#-------------------------------------------------------------------------

# Add a target to generate combined documentation with Doxygen and Sphinx
if (BUILD_DOCUMENTATION OR BUILD_DOCUMENTATION_CXX_ONLY)
  # Whichever is being build, we need Doxygen
  find_package(Doxygen REQUIRED)

  set( DOC_SOURCE_DIR ${Tracktable_SOURCE_DIR}/Documentation )
  set( DOC_BINARY_DIR ${Tracktable_BINARY_DIR}/Documentation )

  if(DOXYGEN_FOUND)

    # Now, let's look for dot and see if it's installed
    # We can still build the docs even if we don't find dot, but they won't be as nice
    find_program(DOT_FOUND dot)
    if (DOT_FOUND)
      set(HAVE_DOT YES)
    else(DOT_FOUND)
      set(HAVE_DOT NO)
    endif(DOT_FOUND)

    configure_file(
      ${DOC_SOURCE_DIR}/Doxyfile.in
      ${DOC_BINARY_DIR}/Doxyfile
      @ONLY
      )

    add_custom_target( doc_cxx ALL
      ${DOXYGEN_EXECUTABLE} ${DOC_BINARY_DIR}/Doxyfile
      WORKING_DIRECTORY ${DOC_BINARY_DIR}
      COMMENT "Generating C++ Doxygen documentation" VERBATIM
      )

    install(
      DIRECTORY ${DOC_BINARY_DIR}/doxygen/html/
      DESTINATION ${CMAKE_INSTALL_DOCDIR}/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}/cpp_reference
    )

    include(FindPythonModule)

    # We have found Sphinx, but that isn't the end of it. We need to make sure the sphinx_rtd_theme is accessible
    if(NOT BUILD_DOCUMENTATION_CXX_ONLY)
      unset(Sphinx_FOUND)
      find_package(Sphinx)

      if (NOT Sphinx_FOUND)
        message(ERROR ": Please provide the path to the Sphinx executable.")
      endif (NOT Sphinx_FOUND)

      find_python_module(sphinx SPHINX_MODULE_STATUS SPHINX_MODULE_LOCATION)

      find_python_module(sphinx_rtd_theme SPHINX_MODULE_STATUS SPHINX_MODULE_LOCATION)

      find_python_module(breathe SPHINX_MODULE_STATUS SPHINX_MODULE_LOCATION)

      # Yes, I'm writing a file into the source tree.  Sphinx requires
      # that its configuration file (conf.py) exist in the source tree
      # even though it can put all of its generated files elsewhere.
      configure_file(
        ${DOC_SOURCE_DIR}/conf.py.in
        ${DOC_SOURCE_DIR}/conf.py
        @ONLY
        )

      set(Sphinx_BUILD_DIR "${DOC_BINARY_DIR}/_build")

      if (MINGW OR MSVC)
        string( REPLACE ";" "\\;" ESCAPED_SYSTEM_PATH "$ENV{PATH}" )
        string( REPLACE ";" "\\;" ESCAPED_PYTHONPATH "$ENV{PYTHONPATH}" )
        add_custom_target( doc_python ALL
            COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${Tracktable_SOURCE_DIR}/tracktable/Python\\;${ESCAPED_PYTHONPATH} PATH=${Tracktable_BINARY_DIR}\\bin\\;${ESCAPED_SYSTEM_PATH}
            ${Python3_EXECUTABLE} ${Sphinx_BUILD_EXECUTABLE}
            -b html
            -d "${Sphinx_BUILD_DIR}/doctrees"
            ${DOC_SOURCE_DIR}
            ${DOC_BINARY_DIR}/html
          COMMENT "Generating Python documentation"
          DEPENDS doc_cxx
          WORKING_DIRECTORY ${DOC_SOURCE_DIR}
          VERBATIM
          )
      else (MINGW OR MSVC)
        # Trust the compiler to set RPATH so that the libraries in bin/ are accessible
        add_custom_target( doc_python ALL
            COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${Tracktable_SOURCE_DIR}/tracktable/Python:${Tracktable_BINARY_DIR}/lib:$ENV{PYTHONPATH}
            ${Python3_EXECUTABLE} ${Sphinx_BUILD_EXECUTABLE}
            -b html
            -d "${Sphinx_BUILD_DIR}/doctrees"
            ${DOC_SOURCE_DIR}
            ${DOC_BINARY_DIR}/html
          COMMENT "Generating Python documentation"
          DEPENDS doc_cxx
          WORKING_DIRECTORY ${DOC_SOURCE_DIR}
          VERBATIM
          )
      endif (MINGW OR MSVC)

      install(
        DIRECTORY ${DOC_BINARY_DIR}/html
        DESTINATION ${CMAKE_INSTALL_DOCDIR}/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
      )

    endif(NOT BUILD_DOCUMENTATION_CXX_ONLY)

    if (BUILD_DOCUMENTATION_CXX_ONLY)
      set(DOC_DEPENDS doc_cxx)
    else (BUILD_DOCUMENTATION_CXX_ONLY)
      set(DOC_DEPENDS doc_python)
    endif (BUILD_DOCUMENTATION_CXX_ONLY)

    add_custom_target( doc ALL
      DEPENDS ${DOC_DEPENDS}
      )

  else(DOXYGEN_FOUND)
    message(ERROR "Please provide the path to the Doxygen executable in DOXYGEN_EXECUTABLE and set DOXYGEN_FOUND to 1.")
  endif(DOXYGEN_FOUND)
endif (BUILD_DOCUMENTATION OR BUILD_DOCUMENTATION_CXX_ONLY)

#-------------------------------------------------------------------------
# End DOCUMENTATION
#=========================================================================

# ----------------------------------------------------------------------

install(FILES LICENSE.txt DESTINATION ${CMAKE_INSTALL_DOCDIR}/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})
install(FILES README.md DESTINATION ${CMAKE_INSTALL_DOCDIR}/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})

if (TRACKTABLE_PYTHON)
  install(FILES LICENSE.txt DESTINATION ${PYTHON_INSTALL_PREFIX})
  install(FILES README.md DESTINATION ${PYTHON_INSTALL_PREFIX})
endif ()
# ----------------------------------------------------------------------

if (TRACKTABLE_PYTHON AND NOT BUILD_SHARED_LIBS)
  message("Python wrapping requires shared libraries.  Please turn on BUILD_SHARED_LIBS.")
endif ()


if (BUILD_TESTING)
  if (NOT EXISTS "${Tracktable_BINARY_DIR}/TestOutput")
     file(MAKE_DIRECTORY "${Tracktable_BINARY_DIR}/TestOutput")
  endif()
  option(TEST_MOVIES "Include tests of movie-making.  These take a few minutes each." OFF)
endif (BUILD_TESTING)

message(STATUS "Project source directory: ${PROJECT_SOURCE_DIR}")

#=========================================================================
# Begin FindBoost
#-------------------------------------------------------------------------
set(BOOST_MINIMUM_VERSION_REQUIRED 1.61)

# Do not use Boost's CMake modules yet.
set(Boost_NO_BOOST_CMAKE ON)

# Core: date_time log serialization
# IO: regex
set(BOOST_CORE_COMPONENTS_NEEDED date_time log regex serialization)

# These are the components, in addition to core components that are needed to
# build examples.
set(BOOST_EXAMPLE_COMPONENTS program_options)

# These are the components, in addition to core components that are needed to
# build tests.
set(BOOST_TEST_COMPONENTS system timer chrono)

# This first check gets the core component libraries needed for the pkgconfig file
unset(Boost_FOUND)
find_package(Boost
  ${BOOST_MINIMUM_VERSION_REQUIRED}
  REQUIRED
  COMPONENTS
    ${BOOST_CORE_COMPONENTS_NEEDED}
  )
set(BOOST_CORE_LIBRARIES "")
foreach(_component ${BOOST_CORE_COMPONENTS_NEEDED})
  set(BOOST_CORE_LIBRARIES "${BOOST_CORE_LIBRARIES} -lboost_${_component}")
endforeach()
#-------------------------------------------------------------------------
# End FindBoost
#=========================================================================

#=========================================================================
# Begin FindThreads
#-------------------------------------------------------------------------
# Prefer pthreads on systems where it's installed.  If the compiler will
# accept the '-pthread' flag as a compile argument, use that too.
set(THREADS_PREFER_PTHREAD_FLAG 1)
# Find the system's threads library.  We need it for boost::log.
find_package(Threads)

add_subdirectory(tracktable)
#-------------------------------------------------------------------------
# End FindThreads
#=========================================================================

#=========================================================================
# Begin PKGCONFIG
#-------------------------------------------------------------------------

if (UNIX)

  set(PKGCONFIG_VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})
  set(PKGCONFIG_FILE tracktable-${PKGCONFIG_VERSION}.pc)

  configure_file(
    ${PROJECT_SOURCE_DIR}/tracktable.pc.in
    ${PROJECT_BINARY_DIR}/${PKGCONFIG_FILE}
    @ONLY IMMEDIATE
  )

  install(FILES ${PROJECT_BINARY_DIR}/${PKGCONFIG_FILE} DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)

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

  add_custom_target(source_tar_bz2
    COMMAND "${CMAKE_COMMAND}" --build . --target package_source
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Building package source .tar.bz2"
    VERBATIM
  )

endif ()

#-------------------------------------------------------------------------
# End PKGCONFIG
#=========================================================================

#=========================================================================
# Begin RPM
#-------------------------------------------------------------------------
if (LINUX)

  configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/packaging/rpm/rhel7/tracktable.spec.in"
    "${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.spec"
    @ONLY
    IMMEDIATE
    )

  add_custom_target(srpm_rhel7
      DEPENDS source_tar_bz2
      WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
      COMMAND mock -r epel-7-x86_64 --buildsrpm --spec ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.spec --sources Tracktable-${TRACKTABLE_VERSION}-Source.tar.bz2 --resultdir=packaging/rhel7/srpms/
      COMMENT "Building RHEL/CentOS 7 source rpms with mock"
      BYPRODUCTS
        ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/srpms/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}-${TRACKTABLE_VERSION}-${RPM_RELEASE}.el7.src.rpm
      VERBATIM
  )

  add_custom_target(srpm
      DEPENDS srpm_rhel7
  )

  add_custom_target(rpm_rhel7_x86_64
      DEPENDS srpm_rhel7
      WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
      COMMAND mock -r epel-7-x86_64 rebuild packaging/rhel7/srpms/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}-${TRACKTABLE_VERSION}-${RPM_RELEASE}.el7.src.rpm --resultdir=packaging/rhel7/rpms
      COMMENT "Building RHEL/CentOS 7 rpms with mock"
      BYPRODUCTS
        ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/rpms/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}-${TRACKTABLE_VERSION}-${RPM_RELEASE}.el7.x86_64.rpm
        ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/rpms/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}-debuginfo-${TRACKTABLE_VERSION}-${RPM_RELEASE}.el7.x86_64.rpm
        ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/rpms/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}-devel-${TRACKTABLE_VERSION}-${RPM_RELEASE}.el7.x86_64.rpm
        ${CMAKE_CURRENT_BINARY_DIR}/packaging/rhel7/rpms/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}-doc-${TRACKTABLE_VERSION}-${RPM_RELEASE}.el7.noarch.rpm
      VERBATIM
  )

  add_custom_target(rpm
      DEPENDS rpm_rhel7_x86_64
  )

endif ()

#-------------------------------------------------------------------------
# End RPM
#=========================================================================

