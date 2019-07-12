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

function(build_wheel _base_directory _output_directory _setup_py _python_interpreter)

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
      
endfunction(build_wheel)


######################################################################
######################################################################
######################################################################

# This block contains the commands that actually execute.

set(PYTHON_INTERPRETER ${CMAKE_ARGV3})
set(INSTALL_TREE_ROOT ${CMAKE_ARGV4})
set(OUTPUT_DIRECTORY ${CMAKE_ARGV5})
set(SETUP_SCRIPT ${CMAKE_ARGV6})

message(STATUS "BuildWheel running.")
message(STATUS "INFO: Python interpreter is ${PYTHON_INTERPRETER}")
message(STATUS "INFO: Install tree is at ${INSTALL_TREE_ROOT}")
message(STATUS "INFO: Output directory is ${OUTPUT_DIRECTORY}")
message(STATUS "INFO: Setup script is ${SETUP_SCRIPT}")

build_wheel(${INSTALL_TREE_ROOT} ${OUTPUT_DIRECTORY} ${SETUP_SCRIPT} ${PYTHON_INTERPRETER})

######################################################################
######################################################################
######################################################################


