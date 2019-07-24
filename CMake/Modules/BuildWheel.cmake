# Copyright (c) 2014-2019 National Technology and Engineering
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
      "from __future__ import print_function; from wheel import pep425tags; print('{}{}'.format(pep425tags.get_abbr_impl(), pep425tags.get_impl_ver()))"
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
      "from __future__ import print_function; from wheel import pep425tags; print(pep425tags.get_platform())"
    RESULT_VARIABLE _interpreter_result
    OUTPUT_VARIABLE _platform_tag
    )
  if (NOT ${_interpreter_result} EQUAL 0)
    message(ERROR "Error while invoking Python interpreter to retrieve platform tag: ${_interpreter_result}")
  else ()
    string(STRIP ${_platform_tag} _platform_tag)
    message(STATUS "Python platform tag: ${_platform_tag}")
    set(${_output_var} ${_platform_tag} PARENT_SCOPE)
  endif()
endfunction(_get_python_platform_tag)

# ----------------------------------------------------------------------

# This function retrieves the ABI tag from a Python interpreter.  This
# is usually 'm' for multithreaded.

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
    message(ERROR "Error while invoking Python interpreter to retrieve ABI tag: ${_interpreter_result}")
  else ()
    string(STRIP ${_abi_tag} _abi_tag)
    message(STATUS "Python ABI tag: ${_abi_tag}")
    set(${_output_var} ${_abi_tag} PARENT_SCOPE)
  endif()
endfunction(_get_python_abi_tag)

# ----------------------------------------------------------------------

function(build_wheel _base_directory _output_directory _setup_py _python_interpreter _fixwheel)
  set(_platform "PLATFORM_NOT_FOUND")
  set(_abi "ABI_NOT_FOUND")
  set(_implementation_version "IMPLEMENTATION_VERSION_TAG_NOT_FOUND")

  _get_python_platform_tag(${_python_interpreter} _platform)
  _get_python_abi_tag(${_python_interpreter} _abi)
  _get_python_version_tag(${_python_interpreter} _implementation_version)

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

  if (NOT ${_wheel_build_result} EQUAL 0)
    message(ERROR "Error while building wheel: ${_wheel_build_result}")
  else ()
    message(STATUS "Wheel build succeeded.  Now you might need to run delocate/auditwheel.")
  endif ()

  message(STATUS "Globbing pattern ${_output_directory}/tracktable-*-${_implementation_version}-none-${_platform}.whl")
  file(
    GLOB _wheel_files
    ${_output_directory}/tracktable-*-${_implementation_version}-none-${_platform}.whl
    LIST_DIRECTORIES false
    )

  # Auditwheel and fixwheel need slightly different arguments.
  string(FIND ${_fixwheel} "auditwheel" _fixwheel_is_auditwheel)
  if (NOT ${_fixwheel_is_auditwheel} EQUAL -1)
    set(_using_auditwheel 1)
  else ()
    set(_using_auditwheel 0)
  endif()

  # We don't know what the exact filename is going to be.  It depends
  # on information scattered in several different locations.  Let's
  # just fix them all.

  foreach(_wheel_to_fix ${_wheel_files})
    message(STATUS "Adding external libraries to ${_wheel_to_fix}.")
    if (_using_auditwheel)
      execute_process(
        COMMAND
        ${_fixwheel} repair ${_wheel_to_fix}
        RESULT_VARIABLE _fixwheel_result
        WORKING_DIRECTORY ${_output_directory}
        )
    else (_using_auditwheel)
      execute_process(
        COMMAND
        ${_fixwheel} repair ${_wheel_to_fix}
        RESULT_VARIABLE _fixwheel_result
        WORKING_DIRECTORY ${_output_directory}
        )
    endif (_using_auditwheel)

    if (NOT ${_fixwheel_result} EQUAL 0)
      message(SEND_ERROR "Error while adding external libraries to wheel: ${_fixwheel_result}")
      return()
    endif ()
  endforeach ()

  if (APPLE)
    message(STATUS "INFO: You probably just saw a lot of warnings about being unable to find libc++, libicudata, and libicui18n, among others.  It is safe to ignore those warnings.")
  endif (APPLE)

  #  syntax of foreach:
  #
  #  foreach(<loop_var> <items>)
  #    <commands>
  #  endforeach()

  # execute_process(
  #   COMMAND
  #   ${_fixwheel} ${_wheel_filename}
  #   RESULT_VARIABLE _fixwheel_result
  #   WORKING_DIRECTORY ${_base_directory}
  #   )

  # if (NOT ${_fixwheel_result} EQUAL 0)
  #   message(ERROR "Error while adding libraries to wheel: ${_fixwheel_result}")
  # endif ()
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

build_wheel(${INSTALL_TREE_ROOT} ${OUTPUT_DIRECTORY} ${SETUP_SCRIPT} ${PYTHON_INTERPRETER} ${FIX_WHEEL_EXECUTABLE})

######################################################################
######################################################################
######################################################################
