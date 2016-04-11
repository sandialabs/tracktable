# Copyright (c) 2014, Sandia Corporation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
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

# This is tracktable/Python/tracktable/core/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our core classes and functions are working.

#add_test(
#  NAME P_TravelFromPoint
#  COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_travel_from_point.py
#)

#add_test(
#  NAME P_WrappedPointTypes
#  COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_point_types.py
#)

#add_test(
#  NAME P_WrappedTrajectoryTypes
#  COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_trajectory_types.py
#)

include(PythonTest)

add_python_test(P_EchoArgs tracktable.core.tests.echo_args foo bar baz)

# if (MINGW OR MSVC)
#   string( REPLACE ";" "\\;" ESCAPED_SYSTEM_PATH "$ENV{PATH}" )
#   string( REPLACE ";" "\\;" ESCAPED_PYTHONPATH "$ENV{PYTHONPATH}" )
#   string( REPLACE "/" "\\" ESCAPED_RUNTIME_OUTPUT_DIR "${Tracktable_BINARY_DIR}/bin" )
  
#   set_tests_properties(
#     P_TravelFromPoint
#     P_WrappedPointTypes
#     P_WrappedTrajectoryTypes
#     PROPERTIES
#     ENVIRONMENT
# 	  "PYTHONPATH=${Tracktable_SOURCE_DIR}\\tracktable\\Python\\;${ESCAPED_PYTHONPATH};PATH=${ESCAPED_RUNTIME_OUTPUT_DIR}\\;${ESCAPED_SYSTEM_PATH}"
# 	)
# else (MINGW OR MSVC)
#   # Trust the compiler to set RPATH so that the libraries in bin/ are
#   # accessible.
#   set_tests_properties(
#     P_TravelFromPoint
#     P_WrappedPointTypes
#     P_WrappedTrajectoryTypes
#     PROPERTIES
#     ENVIRONMENT
# 	  "PYTHONPATH=${Tracktable_SOURCE_DIR}/tracktable/Python:${CTEST_PYTHONPATH_ADDITIONS}:$ENV{PYTHONPATH}"
# 	)
# endif (MINGW OR MSVC)

