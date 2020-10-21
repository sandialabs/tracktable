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

###
### BuildWheel.cmake: Build a Python wheel
###

# This module can be called with 'cmake -P'.  This makes it suitable
# for use in add_custom_command().  Its purpose is to construct a
# Python wheel (binary install package) fully tagged with the version,
# platform, and ABI of the interpreter used to create it.

# Python binary install packages are called 'wheels'.  These are
# allowed to include not only Python code but also compiled extensions
# and arbitrary other files (including shared libraries).  As such,
# they have file-naming conventions that specify what Python
# interpreter and OS they are suited for.

# This module encapsulates as much of that as I can manage.  Here's
# how I expect it to be used:

# 1.  Use CMake to build your package
# 2.  Write setup.py to use distutils to build your wheel
# 3.  Invoke this module to assemble the wheel, add libraries, and
#     rename the file to include ABI/OS/version tags
#

# It is probably smartest to call 'make install' before you run this
# module and set _base_directory to CMAKE_INSTALL_PREFIX.

# Get the various ABI and platform tags from the Python interpreter

# tags: Python, ABI, platform


# ----------------------------------------------------------------------

# This function will get the version-and-interpreter tag that
# identifies a Python interpreter: 'cp37' for C-Python version 3.7 and
# so forth.

function(_get_python_version_tag _python_interpreter _output_var)
  execute_process(
    COMMAND
      ${_python_interpreter}
      "-c"
      "from __future__ import print_function; from packaging import tags; import sys;  print('{interpreter}{version}'.format(interpreter=tags.interpreter_name(), version=tags.interpreter_version()))"
    RESULT_VARIABLE _interpreter_result
    OUTPUT_VARIABLE _python_tag
    )
  if (NOT ${_interpreter_result} EQUAL 0)
    message(ERROR "Error while invoking Python interpreter to retrieve version tag: ${_interpreter_result}")
  else ()
    string(STRIP ${_python_tag} _python_tag)
    message(STATUS "Python version tag: ${_python_tag}")
    set(${_output_var} ${_python_tag} PARENT_SCOPE)
  endif ()
endfunction(_get_python_version_tag)

# ----------------------------------------------------------------------

# This function retrieves the platform (OS and version) tag from a
# Python interpreter.  For example, my Anaconda Python installation
# gives back 'macosx_10_9_x86_64'.

function(_get_python_platform_tag _python_interpreter _output_var)
  execute_process(
    COMMAND
      ${_python_interpreter}
      "-c"
      "from __future__ import print_function; import distutils.util; print(distutils.util.get_platform())"
    RESULT_VARIABLE _interpreter_result
    OUTPUT_VARIABLE _platform_tag
    )
  if (NOT ${_interpreter_result} EQUAL 0)
    message(ERROR "Error while invoking Python interpreter to retrieve platform tag: ${_interpreter_result}")
  else ()
    string(STRIP ${_platform_tag} _platform_tag)
    string(REPLACE "." "_" _platform_tag ${_platform_tag})
    string(REPLACE "-" "_" _platform_tag ${_platform_tag})
    message(STATUS "Python platform tag: ${_platform_tag}")
    set(${_output_var} ${_platform_tag} PARENT_SCOPE)
  endif()
endfunction(_get_python_platform_tag)

# ----------------------------------------------------------------------

# This function retrieves the ABI tag from a Python interpreter.  This
# is usually 'm' for pymalloc.

function(_get_python_abi_tag _python_interpreter _output_var)
  execute_process(
    COMMAND
      ${_python_interpreter}
      "-c"
      "from __future__ import print_function; from wheel import pep425tags; print(pep425tags.get_abi_tag())"
    RESULT_VARIABLE _interpreter_result
    OUTPUT_VARIABLE _abi_tag
    )
  if (NOT ${_interpreter_result} EQUAL 0)
    message("WARNING: Error while invoking Python interpreter to retrieve ABI tag: ${_interpreter_result}")
    set(${_output_var} "none" PARENT_SCOPE)
  else ()
    string(STRIP ${_abi_tag} _abi_tag)
    message(STATUS "Python ABI tag: ${_abi_tag}")
    set(${_output_var} ${_abi_tag} PARENT_SCOPE)
  endif()
endfunction(_get_python_abi_tag)

# ----------------------------------------------------------------------

function(build_wheel _build_directory _base_directory _output_directory _setup_py _python_interpreter _fixwheel _extra_search_paths)
  set(_platform "PLATFORM_NOT_FOUND")
  set(_abi "ABI_NOT_FOUND")
  set(_implementation_version "IMPLEMENTATION_VERSION_TAG_NOT_FOUND")

  _get_python_platform_tag(${_python_interpreter} _platform)
  _get_python_abi_tag(${_python_interpreter} _abi)
  _get_python_version_tag(${_python_interpreter} _implementation_version)

  # Python 2.7 does not have defined ABI tags.
  if (_implementation_version STREQUAL "cp27")
    execute_process(
      COMMAND
      ${_python_interpreter}
      ${_setup_py}
      "bdist_wheel"
      "--bdist-dir" ${_base_directory}/wheel_build_temp
      "--plat-name" ${_platform}
      "--dist-dir" ${_output_directory}
      "--python-tag" ${_implementation_version}
      RESULT_VARIABLE _wheel_build_result
      WORKING_DIRECTORY ${_base_directory}
      )
  else()
    execute_process(
      COMMAND
      ${_python_interpreter}
      ${_setup_py}
      "bdist_wheel"
      "--bdist-dir" ${_base_directory}/wheel_build_temp
      "--plat-name" ${_platform}
      "--dist-dir" ${_output_directory}
      "--python-tag" ${_implementation_version}
      "--py-limited-api" ${_implementation_version}${_abi}
      RESULT_VARIABLE _wheel_build_result
      WORKING_DIRECTORY ${_base_directory}
      )
  endif()

  if (NOT ${_wheel_build_result} EQUAL 0)
    message(ERROR "Error while building wheel: ${_wheel_build_result}")
  elseif (NOT WIN32)
    message(STATUS "Wheel build succeeded.  Next up: include binary dependencies.")
  else ()
    message(STATUS "Wheel build succeeded.")
  endif ()

  message(STATUS "Globbing pattern ${_output_directory}/tracktable-*-${_implementation_version}-none-${_platform}.whl")
  file(
    GLOB _wheel_files
    ${_output_directory}/tracktable-*-${_implementation_version}-none-${_platform}.whl
    LIST_DIRECTORIES false
    )



  # We don't know what the exact filename is going to be.  It depends
  # on information scattered in several different locations.  Let's
  # just fix them all.

  foreach(_wheel_to_fix ${_wheel_files})
    message(STATUS "Adding external libraries to ${_wheel_to_fix}.")
    if (${_fixwheel} MATCHES ".*auditwheel.*")
      execute_process(
        COMMAND
        ${_fixwheel} repair --plat manylinux2010_x86_64 ${_wheel_to_fix}
        RESULT_VARIABLE _fixwheel_result
        WORKING_DIRECTORY ${_output_directory}
        OUTPUT_VARIABLE _fixwheel_output
        ERROR_VARIABLE _fixwheel_error
        )
    elseif (${_fixwheel} MATCHES ".*delocate.*")
      execute_process(
        COMMAND
        ${_fixwheel} ${_wheel_to_fix}
        RESULT_VARIABLE _fixwheel_result
        WORKING_DIRECTORY ${_output_directory}
        OUTPUT_VARIABLE _fixwheel_output
        ERROR_VARIABLE _fixwheel_error
      )
    elseif (${_fixwheel} MATCHES ".*winlocate.*")
      # Since winlocate searches the user's PATH for dependencies, we need
      # to add the binary and library directories from our build tree as
      # well as any other paths (like the Boost search path) that the
      # user supplied.
      set(WINDOWS_PATH $ENV{PATH})
      set(_bin_directory "${_build_directory}/bin")
      set(_lib_directory "${_build_directory}/lib")
      string(REPLACE "/" "\\" _bin_directory_backslash ${_bin_directory})
      string(REPLACE "/" "\\" _lib_directory_backslash ${_lib_directory})
      string(REPLACE "/" "\\" _extra_search_paths_backslashes ${_extra_search_paths})
      set(WINDOWS_PATH "${WINDOWS_PATH};${_bin_directory_backslash};${_lib_directory_backslash};${_extra_search_paths_backslashes}")
      set(ENV{PATH} "${WINDOWS_PATH}")

      # And now, with the path set, we're ready to fix the wheel.
      execute_process(
        COMMAND
          ${_python_interpreter} ${_fixwheel} -d ${_output_directory} ${_wheel_to_fix}
        RESULT_VARIABLE _fixwheel_result
        WORKING_DIRECTORY ${_output_directory}
        OUTPUT_VARIABLE _fixwheel_output
        ERROR_VARIABLE _fixwheel_error
      )
    else()
      message(SEND_ERROR "ERROR: Unknown fixwheel executable '${_fixwheel}'.")
    endif()

    if (NOT ${_fixwheel_result} EQUAL 0)
      message(SEND_ERROR "Error while adding external libraries to wheel: ${_fixwheel_error}")
      return()
    endif ()
  endforeach ()


endfunction(build_wheel)


######################################################################
######################################################################
######################################################################

# This block contains the commands that actually execute.

set(PYTHON_INTERPRETER ${CMAKE_ARGV3})
set(BUILD_TREE_ROOT ${CMAKE_ARGV4})
set(INSTALL_TREE_ROOT ${CMAKE_ARGV5})
set(OUTPUT_DIRECTORY ${CMAKE_ARGV6})
set(SETUP_SCRIPT ${CMAKE_ARGV7})
set(FIX_WHEEL_EXECUTABLE ${CMAKE_ARGV8})

message(STATUS "BuildWheel running.")
message(STATUS "INFO: Python interpreter is ${PYTHON_INTERPRETER}")
message(STATUS "INFO: Build tree is at ${BUILD_TREE_ROOT}.")
message(STATUS "INFO: Install tree is at ${INSTALL_TREE_ROOT}")
message(STATUS "INFO: Output directory is ${OUTPUT_DIRECTORY}")
message(STATUS "INFO: Setup script is ${SETUP_SCRIPT}")
message(STATUS "INFO: Wheel fixer is ${FIX_WHEEL_EXECUTABLE}")

message(STATUS "DEBUG: CMake ARGC is ${CMAKE_ARGC} (we use up to ARGV8 by default; CMake itself gets an extra three directories)")

# YOU ARE HERE
#
# Pass the Boost library directory as one of the arguments to BuildWheel.cmake in PythonWrapping/CMakeLists.txt.
#
# Grab any arguments after CMAKE_ARGV8 as extra search paths.  Pass those to the build_wheel function.

set(EXTRA_SEARCH_PATHS "")

if (${CMAKE_ARGC} GREATER 8)
  math(EXPR _last_argument_index "${CMAKE_ARGC} - 1")
  foreach (_i RANGE 9 ${_last_argument_index})
    message(STATUS "BuildWheel.cmake received extra search path: ${CMAKE_ARGV${_i}}")
    list(APPEND EXTRA_SEARCH_PATHS ${CMAKE_ARGV${_i}})
  endforeach()
endif()

build_wheel(
  ${BUILD_TREE_ROOT}
  ${INSTALL_TREE_ROOT}
  ${OUTPUT_DIRECTORY}
  ${SETUP_SCRIPT}
  ${PYTHON_INTERPRETER}
  ${FIX_WHEEL_EXECUTABLE}
  ${EXTRA_SEARCH_PATHS}
  )

######################################################################
######################################################################
######################################################################
