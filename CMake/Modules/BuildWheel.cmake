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

# Great.  First the wheel package drops the pep425tags module.  Then
# pip drops it too.  Now the packaging package has removed the functions
# in its tags() module that we used as a fallback.
#
# Let's see if this helps...
#
# The very long line here is the equivalent of
#
# from __future__ import print_function
# import sysconfig
# import packaging.tags
# long_name = sysconfig.get_config_var('SOABI') # returns something like 'cpython-38-darwin'
# short_name = packaging.tags.INTERPRETER_SHORT_NAMES[long_name] # returns 'cp' for 'cpython'
# print('{}{}'.format(short_name, sysconfig.get_config_var('py_version_nodot'))) # finally prints 'cp38'

function(_get_python_version_tag _python_interpreter _output_var)
  if (WIN32)
    # The above approach doesn't work on Windows -- sysconfig config vars
    # are much sparser.  I give up.  On Windows we're just going to
    # assume that this is CPython.
    execute_process(
      COMMAND
        ${_python_interpreter}
        "-c"
        "from __future__ import print_function; import sys; print('cp{}{}'.format(sys.version_info.major, sys.version_info.minor))"
      RESULT_VARIABLE _interpreter_result
      OUTPUT_VARIABLE _python_tag
    )
  else (WIN32)
    execute_process(
      COMMAND
        ${_python_interpreter}
        "-c"
        "from __future__ import print_function; import sysconfig; import packaging.tags; long_name = sysconfig.get_config_var('SOABI'); interpreter_only = long_name.split('-')[0]; short_name = packaging.tags.INTERPRETER_SHORT_NAMES[interpreter_only]; print('{}{}'.format(short_name, sysconfig.get_config_var('py_version_nodot')))"
      RESULT_VARIABLE _interpreter_result
      OUTPUT_VARIABLE _python_tag
      )
  endif (WIN32)
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

# We do not depend on any particular ABI tag.

function(_get_python_abi_tag _python_interpreter _output_var)
  set(${_output_var} "none" PARENT_SCOPE)
endfunction(_get_python_abi_tag)

# ----------------------------------------------------------------------

function(build_wheel _build_directory _base_directory _output_directory _python_interpreter _fixwheel _desired_wheel_tag _extra_search_paths)
  set(_platform "PLATFORM_NOT_FOUND")
  set(_abi "ABI_NOT_FOUND")
  set(_implementation_version "IMPLEMENTATION_VERSION_TAG_NOT_FOUND")

  _get_python_platform_tag(${_python_interpreter} _platform)
  _get_python_abi_tag(${_python_interpreter} _abi)
  _get_python_version_tag(${_python_interpreter} _implementation_version)


  execute_process(
    COMMAND
    ${_python_interpreter} -m build --outdir ${_output_directory} .
    RESULT_VARIABLE _wheel_build_result
    WORKING_DIRECTORY ${_base_directory}
    )

  if (NOT ${_wheel_build_result} EQUAL 0)
    message(FATAL_ERROR "Error while building wheel: ${_wheel_build_result}")
  elseif (NOT WIN32)
    message(STATUS "Wheel build succeeded.  Next up: add external dependencies.")
  else ()
    message(STATUS "Wheel build succeeded.")
  endif ()

  file(
    GLOB _wheel_files
    ${_output_directory}/tracktable-*.whl
    LIST_DIRECTORIES false
    )

  message(STATUS "Glob result: ${_wheel_files}")

  # we should only have one wheel
  list(LENGTH _wheel_files _wheel_count)
  if (_wheel_count EQUAL 0)
    message(FATAL_ERROR "No wheel files found in output directory.")
  elseif (_wheel_count GREATER 1)
    message(FATAL_ERROR "Too many wheel files (${_wheel_count}) found in output directory ${_output_directory}.")
  endif ()

  list(GET _wheel_files 0 _original_wheel_filename)
  if ("${_original_wheel_file}" STREQUAL "NOTFOUND")
    message(FATAL_ERROR "Couldn't find wheel file in output directory ${_output_directory}.  Glob result: ${_wheel_files}")
  endif ()

  # Add platform tag and interpreter tag.  This creates 
  # tracktable-1.7.1-cp310-none-macos10_x86_64.whl from 
  # tracktable-1.7.1-py3-none-any.whl.
  
  message(STATUS "Fixing wheel tags on ${_original_wheel_filename}.")
  execute_process(
    COMMAND
    ${_python_interpreter} -m wheel tags --python-tag ${_implementation_version} --platform-tag ${_platform} 
    ${_original_wheel_filename}
    RESULT_VARIABLE _fix_tags_result
    WORKING_DIRECTORY ${_output_directory}
    OUTPUT_VARIABLE _fix_tags_output
    ERROR_VARIABLE _fix_tags_error  
  )
  
  if (NOT ${_fix_tags_result} EQUAL 0) 
    message(FATAL_ERROR "Error fixing wheel tags: ${_fix_tags_error}")
    return()
  endif()

  # Move the original wheel file to a subdirectory so that we can glob the
  # filename and get just the one we care about.
  if (NOT EXISTS ${_output_directory}/original_wheel)
    file(
      MAKE_DIRECTORY ${_output_directory}/original_wheel
    )
  endif()
  cmake_path(GET _original_wheel_filename FILENAME _original_wheel_name_without_path)
  
  file(
    RENAME ${_original_wheel_filename}
    ${_output_directory}/original_wheel/${_original_wheel_name_without_path}
  )

  # Glob the wheel file so we can get the filename to pass to fixwheel.
  file(
    GLOB _wheel_files
    ${_output_directory}/tracktable-*.whl
    LIST_DIRECTORIES false
    )

  # we should only have one wheel
  list(LENGTH _wheel_files _wheel_count)
  if (_wheel_count EQUAL 0)
    message(FATAL_ERROR "No wheel files found in output directory ${_output_directory} (second pass).")
  elseif (_wheel_count GREATER 1)
    message(FATAL_ERROR "Too many wheel files (${_wheel_count}) found in output directory ${_output_directory} (second pass).")
  endif ()

  list(GET _wheel_files 0 _tagged_wheel_filename)


  # Now we can invoke auditwheel/delocate/winlocate to copy in the external
  # library dependencies.
  message(STATUS "Adding external libraries to ${_tagged_wheel_filename}.")
  if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message(STATUS "    Requesting wheel tag ${_desired_wheel_tag}.")
  endif ()

  # Linux uses auditwheel.
  if (${_fixwheel} MATCHES ".*auditwheel.*")
    execute_process(
      COMMAND
      ${_fixwheel} repair --plat ${_desired_wheel_tag} ${_tagged_wheel_filename}
      RESULT_VARIABLE _fixwheel_result
      WORKING_DIRECTORY ${_output_directory}
      OUTPUT_VARIABLE _fixwheel_output
      ERROR_VARIABLE _fixwheel_error
      )
  # MacOS uses delocate.
  elseif (${_fixwheel} MATCHES ".*delocate.*")
    execute_process(
      COMMAND
      ${_fixwheel} -v ${_tagged_wheel_filename}
      RESULT_VARIABLE _fixwheel_result
      WORKING_DIRECTORY ${_output_directory}
      OUTPUT_VARIABLE _fixwheel_output
      ERROR_VARIABLE _fixwheel_error
    )
  # Windows uses winlocate.
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
    set(WINDOWS_PATH "${WINDOWS_PATH};${_bin_directory_backslash};${_lib_directory_backslash}")
    
    if (NOT _extra_search_paths STREQUAL "NO_EXTRA_SEARCH_PATHS")
      string(REPLACE "/" "\\" _extra_search_paths_backslashes ${_extra_search_paths}) 
      set(WINDOWS_PATH "${WINDOWS_PATH};${_extra_search_paths_backslashes}")
    endif ()
    set(ENV{PATH} "${WINDOWS_PATH}")

    # And now, with the path set, we're ready to fix the wheel.
    execute_process(
      COMMAND
        ${_python_interpreter} ${_fixwheel} -d ${_output_directory} ${_tagged_wheel_filename}
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

endfunction(build_wheel)


######################################################################
######################################################################
######################################################################

# This block contains the commands that actually execute.

set(PYTHON_INTERPRETER ${CMAKE_ARGV3})
set(BUILD_TREE_ROOT ${CMAKE_ARGV4})
set(INSTALL_TREE_ROOT ${CMAKE_ARGV5})
set(OUTPUT_DIRECTORY ${CMAKE_ARGV6})
set(FIX_WHEEL_EXECUTABLE ${CMAKE_ARGV7})
set(DESIRED_WHEEL_TAG ${CMAKE_ARGV8})

message(STATUS "BuildWheel running.")
message(STATUS "INFO: Python interpreter is ${PYTHON_INTERPRETER}")
message(STATUS "INFO: Build tree is at ${BUILD_TREE_ROOT}.")
message(STATUS "INFO: Install tree is at ${INSTALL_TREE_ROOT}")
message(STATUS "INFO: Output directory is ${OUTPUT_DIRECTORY}")
message(STATUS "INFO: Wheel fixer is ${FIX_WHEEL_EXECUTABLE}")
message(STATUS "INFO: System name is ${CMAKE_SYSTEM_NAME}")
if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message(STATUS "INFO: Building on Linux; desired wheel tag is ${DESIRED_WHEEL_TAG}")
endif()

# YOU ARE HERE
#
# Pass the Boost library directory as one of the arguments to BuildWheel.cmake in PythonWrapping/CMakeLists.txt.
#
# Grab any arguments after CMAKE_ARGV9 as extra search paths.  Pass those to the build_wheel function.

set(EXTRA_SEARCH_PATHS "")

if (${CMAKE_ARGC} GREATER 9)
  math(EXPR _last_argument_index "${CMAKE_ARGC} - 1")
  foreach (_i RANGE 10 ${_last_argument_index})
    message(STATUS "BuildWheel.cmake received extra search path: ${CMAKE_ARGV${_i}}")
    list(APPEND EXTRA_SEARCH_PATHS ${CMAKE_ARGV${_i}})
  endforeach()
else ()
  list(APPEND EXTRA_SEARCH_PATHS NO_EXTRA_SEARCH_PATHS)
endif ()


build_wheel(
  ${BUILD_TREE_ROOT}
  ${INSTALL_TREE_ROOT}
  ${OUTPUT_DIRECTORY}
  ${PYTHON_INTERPRETER}
  ${FIX_WHEEL_EXECUTABLE}
  ${DESIRED_WHEEL_TAG}
  ${EXTRA_SEARCH_PATHS}
  )

######################################################################
######################################################################
######################################################################
