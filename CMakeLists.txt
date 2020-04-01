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
message(STATUS "Building with CMake version ${CMAKE_VERSION}")

if (POLICY CMP0042)
  cmake_policy(SET CMP0042 NEW)
  set(CMAKE_MACOSX_RPATH ${Tracktable_BINARY_DIR}/lib)
endif ()

if (UNIX AND NOT APPLE)
  set(LINUX TRUE)
endif ()

include(GNUInstallDirs)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# set(Boost_DEBUG ON)

##########################################################################
# Begin RELEASE VARIABLES
#-------------------------------------------------------------------------

set(TRACKTABLE_VERSION 1.2.4)
set(RPM_RELEASE 6)

# UNIX library ABI versioning
# CURRENT : REVISION : AGE
# +1 :  ? : +1 == new interface that does not break old one
# +1 :  ? :  0 == new interface that breaks old one
#  ? :  ? :  0 == no new interfaces, but breaks apps
#  ? : +1 :  ? == just some internal changes, nothing breaks but might work better
set(UNIX_SO_VERSION_CURRENT  0)
set(UNIX_SO_VERSION_REVISION 0)
set(UNIX_SO_VERSION_AGE      0)

#-------------------------------------------------------------------------
# End RELEASE VARIABLES
##########################################################################

project(Tracktable LANGUAGES CXX VERSION ${TRACKTABLE_VERSION})

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

# ----------------------------------------------------------------------

# Look for python early if we're going to build the wrappers
# These symbols are also used to look for Sphinx
if (TRACKTABLE_PYTHON)
  message(STATUS "Building and installing python bindings")
  if (UNIX AND APPLE)
    find_package(Python3 COMPONENTS Interpreter Development)
  else (UNIX AND APPLE)
    find_package(Python3 COMPONENTS Interpreter Development NumPy)
  endif(UNIX AND APPLE)
  message(STATUS "*** DEBUG: ${CMAKE_CURRENT_SOURCE_DIR}: Python3_EXECUTABLE is ‘${Python3_EXECUTABLE}’")
else(TRACKTABLE_PYTHON)
  message(STATUS "Python bindings will NOT be built or installed")
endif (TRACKTABLE_PYTHON)

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

    # We have found Sphinx, but that isn't the end of it. We need to make sure the sphinx_rtd_theme is accessible
    if(NOT BUILD_DOCUMENTATION_CXX_ONLY)
      unset(Sphinx_FOUND)
      find_package(Sphinx)

      if (NOT Sphinx_FOUND)
        message(ERROR ": Please provide the path to the Sphinx executable.")
      endif (NOT Sphinx_FOUND)

      execute_process(COMMAND "${Sphinx_EXECUTABLE_TMP}" "-c"
        "import re; import sphinx; print(re.compile('/__init__.py.*').sub('',sphinx.__file__))"
        RESULT_VARIABLE SPHINX_MODULE_STATUS
        OUTPUT_VARIABLE SPHINX_MODULE_LOCATION
        ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE
        )
      #message("SPHINX_MODULE_STATUS ${SPHINX_MODULE_STATUS}")
      #message("SPHINX_MODULE_LOCATION ${SPHINX_MODULE_LOCATION}")
      # The status is empty if everything went ok, but if it has anything in it there was an error
      if(SPHINX_MODULE_STATUS)
        message(ERROR ": Python module 'sphinx' is required to build Python documentation. Install the sphinx module or enable BUILD_DOCUMENTATION_CXX_ONLY.")
      endif(SPHINX_MODULE_STATUS)

      execute_process(COMMAND "${Sphinx_EXECUTABLE_TMP}" "-c"
        "import re; import sphinx_rtd_theme; print(re.compile('/__init__.py.*').sub('',sphinx_rtd_theme.__file__))"
        RESULT_VARIABLE SPHINX_RTD_THEME_STATUS
        OUTPUT_VARIABLE SPHINX_RTD_THEME_LOCATION
        ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE
        )
      #message("SPHINX_RTD_THEME_STATUS ${SPHINX_RTD_THEME_STATUS}")
      #message("SPHINX_RTD_THEME_LOCATION ${SPHINX_RTD_THEME_LOCATION}")
      # The status is empty if everything went ok, but if it has anything in it there was an error
      if(SPHINX_RTD_THEME_STATUS)
        message(ERROR ": Python module 'sphinx_rtd_theme' is required to build Python documentation. Install the sphinx_rtd_theme module or enable BUILD_DOCUMENTATION_CXX_ONLY.")
      endif(SPHINX_RTD_THEME_STATUS)

      execute_process(COMMAND "${Sphinx_EXECUTABLE_TMP}" "-c"
        "import re; import breathe; print(re.compile('/__init__.py.*').sub('',breathe.__file__))"
        RESULT_VARIABLE BREATHE_STATUS
        OUTPUT_VARIABLE BREATHE_LOCATION
        ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE
        )
      # The status is empty if everything went ok, but if it has anything in it there was an error
      if(BREATHE_STATUS)
        message(ERROR ": Python module 'breathe' is required to build Python documentation. Install the breathe module or enable BUILD_DOCUMENTATION_CXX_ONLY.")
      endif(BREATHE_STATUS)

      # Yes, I'm writing a file into the source tree.  Sphinx requires
      # that its configuration file (conf.py) exist in the source tree
      # even though it can put all of its generated files elsewhere.
      configure_file(
        ${DOC_SOURCE_DIR}/conf.py.in
        ${DOC_SOURCE_DIR}/conf.py
        @ONLY
        )

      set(Sphinx_BUILD_DIR "${DOC_BINARY_DIR}/_build")


      # NOTE: This approach to setting PYTHONPATH will only work on
      # Unix-like systems.  In CMake 3.1 we will get the '-E env'
      # capability which is what we really need here.  Since requiring the
      # bleeding-edge version of CMake isn't a terribly friendly thing to
      # do, I will probably end up faking it with batch files.

      add_custom_target( doc_python ALL
          ${Python3_EXECUTABLE} ${Sphinx_BUILD_EXECUTABLE}
          -b html
          -d "${Sphinx_BUILD_DIR}/doctrees"
          ${DOC_SOURCE_DIR}
          ${DOC_BINARY_DIR}/html
        COMMENT "Generating Python documentation"
        DEPENDS doc_cxx
        WORKING_DIRECTORY ${DOC_SOURCE_DIR}
        )

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
# Begin FIND PACKAGE
#-------------------------------------------------------------------------

set(BOOST_MINIMUM_VERSION_REQUIRED 1.61)

# Core: date_time log serialization
# IO: regex
set(BOOST_CORE_COMPONENTS_NEEDED date_time log regex serialization)

# These are the components, in addition to core components that are needed to
# build examples.
if (BUILD_EXAMPLES)
  set(BOOST_EXAMPLE_COMPONENTS program_options)
endif (BUILD_EXAMPLES)

# These are the components, in addition to core components that are needed to
# build tests.
if (BUILD_TESTING)
  set(BOOST_TEST_COMPONENTS system timer chrono)
endif (BUILD_TESTING)

# This first check gets the core component libraries needed for the pkgconfig file
unset(Boost_FOUND)
find_package(Boost ${BOOST_MINIMUM_VERSION_REQUIRED} REQUIRED COMPONENTS ${BOOST_CORE_COMPONENTS_NEEDED} )
set(BOOST_CORE_LIBRARIES "")
foreach(_component ${BOOST_CORE_COMPONENTS_NEEDED})
  set(BOOST_CORE_LIBRARIES "${BOOST_CORE_LIBRARIES} -lboost_${_component}")
endforeach()

set(Boost_PYTHON_LIBRARY_SUFFIX "")

#message(STATUS "Python3_INCLUDE_DIRS ${Python3_INCLUDE_DIRS}")
#message(STATUS "Python3_LIBRARIES ${Python3_LIBRARIES}")
#message(STATUS "Python3_LIBRARY_DIRS ${Python3_LIBRARY_DIRS}")

#
# So, what's the Boost.Python library called?
#
# Versions of Boost from 1.57 through 1.66 generate
# libboost_python3.so for Python 3.  From 1.67 onward we get
# libboost_pythonXY.so for Python X.Y.  In order to figure out the
# proper library name we need to know BOTH the Python version and the
# Boost version.
if (TRACKTABLE_PYTHON AND Boost_FOUND AND EXISTS ${Python3_EXECUTABLE})
  #message(STATUS "Boost_VERSION ${Boost_VERSION}")
  if (Boost_VERSION VERSION_LESS 106700)
    # This version of Boost generates libboost_python[3].so.
    set(Boost_PYTHON_LIBRARY_SUFFIX "3")
  else (Boost_VERSION VERSION_LESS 106700)
    #message(STATUS "Python3_VERSION_MAJOR ${Python3_VERSION_MAJOR}")
    #message(STATUS "Python3_VERSION_MINOR ${Python3_VERSION_MINOR}")
    # This version of Boost needs a versioned library.
    set(Boost_PYTHON_LIBRARY_SUFFIX "${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR}")
  endif (Boost_VERSION VERSION_LESS 106700)

  #message(STATUS "Boost_PYTHON_LIBRARY_SUFFIX ${Boost_PYTHON_LIBRARY_SUFFIX}")
  set(BOOST_PYTHON_COMPONENTS python${Boost_PYTHON_LIBRARY_SUFFIX})
else (TRACKTABLE_PYTHON AND Boost_FOUND AND EXISTS ${Python3_EXECUTABLE})
  message(ERROR "Boost.Python library version cannot be determined until both Boost and Python have been found.")
endif (TRACKTABLE_PYTHON AND Boost_FOUND AND EXISTS ${Python3_EXECUTABLE})

# This second check undoes the previous find and looks for all necessary components
unset(Boost_FOUND)
set(ALL_BOOST_COMPONENTS ${BOOST_CORE_COMPONENTS_NEEDED} ${BOOST_PYTHON_COMPONENTS} ${BOOST_EXAMPLE_COMPONENTS} ${BOOST_TEST_COMPONENTS})
message(STATUS "Looking for Boost minimum version ${BOOST_MINIMUM_VERSION_REQUIRED} components ${ALL_BOOST_COMPONENTS}")
find_package(Boost ${BOOST_MINIMUM_VERSION_REQUIRED} REQUIRED COMPONENTS ${ALL_BOOST_COMPONENTS} )

# Prefer pthreads on systems where it's installed.  If the compiler will
# accept the '-pthread' flag as a compile argument, use that too.
set(THREADS_PREFER_PTHREAD_FLAG 1)
# Find the system's threads library.  We need it for boost::log.
find_package(Threads)

add_subdirectory(tracktable)

#-------------------------------------------------------------------------
# End FIND PACKAGE
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

