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

function(find_python_module modulename modulestatus modulelocation)

  execute_process(COMMAND "${Python3_EXECUTABLE}" "-c"
  "import re; import ${modulename}; print(re.compile('/__init__.py.*').sub('',${modulename}.__file__))"
  RESULT_VARIABLE modulestatus
  OUTPUT_VARIABLE modulelocation
  ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  # message("MODULE: ${modulename}")
  # message("MODULE STATUS: ${modulestatus}")
  # message("MODULE LOCATION ${modulelocation}")

  if(modulename STREQUAL "cartopy")
    if(NOT modulestatus)
      set(PY_CARTOPY_MODULE ${modulelocation} CACHE STRING
          "Location of Python module cartopy")
    endif(NOT modulestatus)
  else(modulename STREQUAL "cartopy")
    if(modulestatus)
      # The status is empty if everything went ok, but if it has anything in it there was an error
      message(ERROR ": Python module '${modulestatus}' is required to build Python documentation. Install the ${modulestatus} module or enable BUILD_DOCUMENTATION_CXX_ONLY.  If you are certain that ${modulestatus} is already installed, make sure Python3_EXECUTABLE is correct.")
    endif(modulestatus)
  endif(modulename STREQUAL "cartopy")

endfunction(find_python_module)

