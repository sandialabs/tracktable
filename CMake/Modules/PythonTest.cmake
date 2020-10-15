# Copyright (c) 2014-2020 National Technology and Engineering
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

# Function to set up and run a Python test using 'python -m foo'

function(add_python_test test_name module_to_run)

add_test(
  NAME ${test_name}
  COMMAND ${Python3_EXECUTABLE} -m ${module_to_run} ${ARGN}
  )

if (MINGW OR MSVC)
  string( REPLACE ";" "\\;" ESCAPED_SYSTEM_PATH "$ENV{PATH}" )
  string( REPLACE ";" "\\;" ESCAPED_PYTHONPATH "$ENV{PYTHONPATH}" )

  set_tests_properties(
    ${test_name}
    PROPERTIES
    ENVIRONMENT
	  "PYTHONPATH=${Tracktable_SOURCE_DIR}/tracktable/Python\\;${ESCAPED_PYTHONPATH};PATH=${Tracktable_BINARY_DIR}\\bin\\;${ESCAPED_SYSTEM_PATH}"
	)
else (MINGW OR MSVC)
  # Trust the compiler to set RPATH so that the libraries in bin/ are
  # accessible.
  set_tests_properties(
    ${test_name}
    PROPERTIES
    ENVIRONMENT
	  "PYTHONPATH=${Tracktable_SOURCE_DIR}/tracktable/Python:${Tracktable_BINARY_DIR}/lib:$ENV{PYTHONPATH}"
	)
endif (MINGW OR MSVC)

endfunction(add_python_test)

