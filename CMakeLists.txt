# Copyright (c) 2014-2023 National Technology and Engineering
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

file(READ "version.txt" ver)
string(REGEX MATCH "CMAKE VERSION ([0-9\\.]*)" _ ${ver})
cmake_minimum_required(VERSION ${CMAKE_MATCH_1})
message(STATUS "Building with CMake version ${CMAKE_VERSION}")

if (POLICY CMP0042)
  cmake_policy(SET CMP0042 NEW)
  set(CMAKE_MACOSX_RPATH ${Tracktable_BINARY_DIR}/lib)
endif ()

# This policy says that Boost_ROOT will be ignored if set and
# we'll take hints as to Boost's location from BOOST_ROOT.
if (POLICY CMP0144)
  cmake_policy(SET CMP0144 NEW)
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


set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# set(Boost_DEBUG ON)

##########################################################################
# Begin RELEASE VARIABLES
#-------------------------------------------------------------------------
string(REGEX MATCH "TRACKTABLE VERSION ([0-9\\.]*)" _ ${ver})
set(TRACKTABLE_VERSION ${CMAKE_MATCH_1})
set(RPM_RELEASE 6)

project(Tracktable LANGUAGES C CXX VERSION ${TRACKTABLE_VERSION})

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
string(REGEX MATCH "UNIX SO VERSION CURRENT ([0-9]*)" _ ${ver})
set(UNIX_SO_VERSION_CURRENT  ${CMAKE_MATCH_1})
string(REGEX MATCH "UNIX SO VERSION REVISION ([0-9]*)" _ ${ver})
set(UNIX_SO_VERSION_REVISION ${CMAKE_MATCH_1})
string(REGEX MATCH "UNIX SO VERSION AGE ([0-9]*)" _ ${ver})
set(UNIX_SO_VERSION_AGE      ${CMAKE_MATCH_1})

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

# Git submodule paths
set(Tracktable_DATA_DIR ${Tracktable_SOURCE_DIR}/tracktable-data/tracktable-data/tracktable_data)

# ----------------------------------------------------------------------

### Organize programs into folders in Visual Studio, Windows
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

#=========================================================================
# Begin options and cache variables
#-------------------------------------------------------------------------
include(CMakeDependentOption)
option(BUILD_SHARED_LIBS "Build shared libraries.  Required for Python wrapping." ON)
CMAKE_DEPENDENT_OPTION(
  TRACKTABLE_PYTHON "Build and install Tracktable's Python bindings." ON
  "BUILD_SHARED_LIBS" OFF)
option(BUILD_EXAMPLES "Build Tracktable example programs" ON)
option(BUILD_DOCUMENTATION "Build Python and C++ documentation for Tracktable." OFF)
option(BUILD_DOCUMENTATION_CXX_ONLY "Build only C++ documentation for Tracktable." OFF)

option(COPY_NOTEBOOKS_TRACKTABLE_DATA "Copy and clean notebooks from tracktable-data." ON)

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
  message(STATUS "Building and installing Python bindings")
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

  if(DOXYGEN_FOUND)
    # We need dot (from Graphviz) in order to build documentation.
    find_program(DOT_FOUND dot)
    if (NOT DOT_FOUND)
      message(ERROR "Please install GraphViz in the environment before building documentation.")
    endif (NOT DOT_FOUND)

    # Provide environment variables to Doxygen and Sphinx

    set( DOC_SOURCE_DIR ${Tracktable_SOURCE_DIR}/tracktable-docs/Documentation )
    set( DOC_OUTPUT_DIR ${Tracktable_BINARY_DIR}/Documentation )
    set( DOXYGEN_XML_OUTPUT_PATH ${Tracktable_BINARY_DIR}/doxygen_xml )
    set( DOXYGEN_HTML_OUTPUT_PATH ${DOC_OUTPUT_DIR}/html )
    set( DOXYGEN_GENERATE_XML "YES" )

    if (BUILD_DOCUMENTATION_CXX_ONLY)
      set(DOXYGEN_GENERATE_HTML "YES")
    else (DOCUMENTATION_BUILD_CXX_ONLY)
      set(DOXYGEN_GENERATE_HTML "NO")
    endif (BUILD_DOCUMENTATION_CXX_ONLY)

    if (NOT EXISTS ${DOC_OUTPUT_DIR})
      message(STATUS "Creating ${DOC_OUTPUT_DIR} for generated documentation.")
      file(MAKE_DIRECTORY ${DOC_OUTPUT_DIR})
    endif (NOT EXISTS ${DOC_OUTPUT_DIR})

    add_custom_target(doc_cxx
      ALL
      BYPRODUCTS
        ${DOC_OUTPUT_DIR}
        ${Tracktable_BINARY_DIR}/doxygen_xml
      WORKING_DIRECTORY
        ${DOC_SOURCE_DIR}
      COMMAND
        ${CMAKE_COMMAND} -E env
          TRACKTABLE_VERSION=${TRACKTABLE_VERSION}
          DOXYGEN_GENERATE_XML=${DOXYGEN_GENERATE_XML}
          DOXYGEN_XML_OUTPUT_PATH=${DOXYGEN_XML_OUTPUT_PATH}
          DOXYGEN_GENERATE_HTML=${DOXYGEN_GENERATE_HTML}
          DOXYGEN_HTML_OUTPUT_PATH=${DOXYGEN_HTML_OUTPUT_PATH}
          --
          ${DOXYGEN_EXECUTABLE} ${DOC_SOURCE_DIR}/Doxyfile
    )

    install(
      DIRECTORY ${DOC_DOXYGEN_HTML_PATH}
      DESTINATION ${CMAKE_INSTALL_DOCDIR}/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}/cpp_reference
    )

    include(FindPythonModule)


    # We have found Sphinx, but that isn't the end of it. We need to make sure
    # the sphinx_rtd_theme is accessible
    if(NOT BUILD_DOCUMENTATION_CXX_ONLY)
      unset(Sphinx_FOUND)
      find_package(Sphinx)

      if (NOT Sphinx_FOUND)
        message(ERROR ": Please provide the path to the Sphinx executable.")
      endif (NOT Sphinx_FOUND)

      find_python_module(sphinx SPHINX_MODULE_STATUS SPHINX_MODULE_LOCATION)
      find_python_module(sphinx_rtd_theme SPHINX_RTD_THEME_MODULE_STATUS SPHINX_RTD_THEME_MODULE_LOCATION)
      find_python_module(nbsphinx NBSPHINX_MODULE_STATUS NBSPHINX_MODULE_LOCATION)
      find_python_module(nbsphinx_link NBSPHINX_LINK_MODULE_STATUS NBSPHINX_LINK_MODULE_LOCATION)
      find_python_module(breathe BREATHE_MODULE_STATUS BREATHE_MODULE_LOCATION)

      set(Sphinx_BUILD_DIR "${DOC_OUTPUT_DIR}/_build")

      message(STATUS "Adding Sphinx documentation target.")

      if (MINGW OR MSVC)
        string( REPLACE ";" "\\;" ESCAPED_SYSTEM_PATH "$ENV{PATH}" )
        string( REPLACE ";" "\\;" ESCAPED_PYTHONPATH "$ENV{PYTHONPATH}" )
        string( REPLACE "/" "\\;" ESCAPED_SOURCE_DIR "${Tracktable_SOURCE_DIR}" )
        string( REPLACE "/" "\\;" ESCAPED_BINARY_DIR "${Tracktable_BINARY_DIR}" )

        add_custom_target( doc_python ALL
            BYPRODUCTS
              ${DOC_OUTPUT_DIR}/html
              ${Sphinx_BUILD_DIR}
            COMMAND
              ${CMAKE_COMMAND} -E env
                TRACKTABLE_VERSION=${TRACKTABLE_VERSION}
                # PYTHONPATH=${ESCAPED_SOURCE_DIR}\\tracktable\\Python\\;${ESCAPED_PYTHONPATH}
                PATH=${ESCAPED_BINARY_DIR}\\bin\\;${ESCAPED_SYSTEM_PATH}
                #SOURCE_DIR=${ESCAPED_SOURCE_DIR}
                #BINARY_DIR=${ESCAPED_BINARY_DIR}
                DOXYGEN_XML_OUTPUT_PATH=${DOXYGEN_XML_OUTPUT_PATH}
                --
                ${Python3_EXECUTABLE} ${Sphinx_BUILD_EXECUTABLE}
                  -b html
                  -d "${Sphinx_BUILD_DIR}/doctrees"
                  ${DOC_SOURCE_DIR}
                  ${DOC_OUTPUT_DIR}
            COMMENT "Generating Python documentation"
            DEPENDS doc_cxx
            WORKING_DIRECTORY ${DOC_SOURCE_DIR}
            VERBATIM
          )
      else (MINGW OR MSVC)
        # Trust the compiler to set RPATH so that the libraries in bin/ are accessible
        add_custom_target( doc_python ALL
          BYPRODUCTS
            ${DOC_OUTPUT_DIR}/html
            ${Sphinx_BUILD_DIR}/doctrees
          COMMAND
            ${CMAKE_COMMAND} -E env
            DOXYGEN_XML_OUTPUT_PATH=${DOXYGEN_XML_OUTPUT_PATH}
            --
            ${Python3_EXECUTABLE} ${Sphinx_BUILD_EXECUTABLE}
              -b html
              -d "${Sphinx_BUILD_DIR}/doctrees"
              ${DOC_SOURCE_DIR}
              ${DOC_OUTPUT_DIR}
          COMMENT "Generating Python documentation"
          DEPENDS doc_cxx
          WORKING_DIRECTORY ${DOC_SOURCE_DIR}
          VERBATIM
          )
      endif (MINGW OR MSVC)

      # Python documentation needs to build after these targets so that we
      # can import Tracktable.  These targets are populated in
      # PythonWrapping/CMakeLists.txt.
      set(COMPILED_EXTENSION_TARGETS
            _core_types _domain_algorithm_overloads _distance_geometry
            _terrestrial _cartesian2d _cartesian3d _feature_vector_points
            _dbscan_clustering _rtree)
      # CMake documentation says that we add dependencies between targets
      # this way rather than with the DEPENDS keyword to add_custom_target.
      add_dependencies(doc_python ${COMPILED_EXTENSION_TARGETS})

      install(
        DIRECTORY ${DOC_BINARY_DIR}/html
        DESTINATION ${CMAKE_INSTALL_DOCDIR}/tracktable-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
      )

    endif(NOT BUILD_DOCUMENTATION_CXX_ONLY)

    if (BUILD_DOCUMENTATION_CXX_ONLY)
      set(DOC_DEPENDS doc_cxx)
    else (BUILD_DOCUMENTATION_CXX_ONLY)
      set(DOC_DEPENDS doc_python doc_cxx)
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
  install(FILES README.md DESTINATION ${CMAKE_INSTALL_PREFIX})
  install(FILES packaging/MANIFEST.in DESTINATION ${CMAKE_INSTALL_PREFIX})
  install(FILES packaging/pyproject.toml DESTINATION ${CMAKE_INSTALL_PREFIX})
  install(FILES packaging/setup.cfg DESTINATION ${CMAKE_INSTALL_PREFIX})
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
string(REGEX MATCH "BOOST VERSION ([0-9\\.]*)" _ ${ver})
set(BOOST_MINIMUM_VERSION_REQUIRED ${CMAKE_MATCH_1})

# Do not use Boost's CMake modules yet.
set(Boost_NO_BOOST_CMAKE ON)

# Core: date_time log serialization
# IO: regex
set(BOOST_CORE_COMPONENTS_NEEDED date_time log regex serialization timer)

# These are the components, in addition to core components that are needed to
# build examples.
set(BOOST_EXAMPLE_COMPONENTS program_options)

# These are the components, in addition to core components that are needed to
# build tests.
set(BOOST_TEST_COMPONENTS system timer chrono)

# This first check gets the core component libraries needed for the pkgconfig file
unset(Boost_FOUND)
find_package(Boost CONFIG
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

#-------------------------------------------------------------------------
# Begin C++ Code Coverage
#=========================================================================

include(CodeCoverage)
SETUP_CODE_COVERAGE()

#-------------------------------------------------------------------------
# End C++ Code Coverage
#=========================================================================

#-------------------------------------------------------------------------
# Build the actual library
#=========================================================================
add_subdirectory(src)
