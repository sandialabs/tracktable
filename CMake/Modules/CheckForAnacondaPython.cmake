# Copyright (c) 2014-2019 National Technology and Engineering
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

# This module runs a Python script to check to see whether a specific
# Python interpreter appears to be built by Anaconda.  We do this
# because we need different C++ linker flags than for the standard C
# Python interpreter.
# 
# 
# Use this module as follows:
# 
# Suppose you have a variable PYTHON_INTERPRETER that is a FILEPATH to
# an interpreter you want to test.  You want to store the result (a
# boolean) in the variable RESULT_OF_CHECK.
# 
# include(CheckForAnacondaPython)
# check_for_anaconda_python(PYTHON_INTERPRETER RESULT_OF_CHECK)
# 
# The result variable will either be set to TRUE or FALSE.  If the
# file does not exist, an error will be raised.

function(check_for_anaconda_python _PYTHON_EXECUTABLE _RESULT_VARIABLE)

set(${_RESULT_VARIABLE} FALSE PARENT_SCOPE)

message("check_for_anaconda_python: Executable is ${PYTHON_EXECUTABLE}")

if (NOT EXISTS ${_PYTHON_EXECUTABLE})
  message(FATAL_ERROR "CheckForAnacondaPython: Python executable ${_PYTHON_EXECUTABLE} doesn't exist.")
endif ()

if (NOT EXISTS "${CMAKE_SOURCE_DIR}/CMake/Modules/check_banner_for_anaconda.py")
  message(FATAL_ERROR "CheckForAnacondaPython: Helper script check_banner_for_anaconda.py does not exist in directory ${CMAKE_SOURCE_DIR}/CMake/Modules.")
endif ()

# execute_process(
#   COMMAND "${PYTHON_EXECUTABLE}" "-c" "import os; print(os.getcwd())"
#   )

execute_process(
  COMMAND "${PYTHON_EXECUTABLE}" "check_banner_for_anaconda.py" "${PYTHON_EXECUTABLE}"
  RESULT_VARIABLE _anaconda_is_python
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/CMake/Modules"
  )

if (${_anaconda_is_python} MATCHES 0)
  message(STATUS "STATUS: Python interpreter looks like Anaconda.")
  set(${_RESULT_VARIABLE} TRUE PARENT_SCOPE)
elseif (${_anaconda_is_python} MATCHES 1)
  message(STATUS "STATUS: Python interpreter does not look like Anaconda")
  # the variable was already set at the top of the function
else ()
  message(FATAL_ERROR "Couldn't run Python interpreter to check for Anaconda.  Message: (${_anaconda_is_python}")
endif()

endfunction(check_for_anaconda_python)
