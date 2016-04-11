# Copyright (c) 2014, Sandia Corporation.
# All rights reserved.
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
#
#
# FindSphinx.cmake
#
# Try to find the Sphinx documentation builder.
#
# Usage:
#
# FindSphinx([COMPONENTS apidoc autogen build quickstart]
#            [REQUIRED]
#            [QUIET])
#
# The COMPONENTS clause is optional.  If you specify it, include at
# least one of the four components (apidoc, autogen, build and
# quickstart).  All of those components will have to be found before
# Sphinx_FOUND will be set.  We will always require sphinx-build.
#
# You may set any of the following variables as input:
#
# Sphinx_DIR:
#   Path where we should look first.
#
# After execution, this module will define the following variables:
#
# Sphinx_FOUND:
#   System has Sphinx and all requested components
#
# Sphinx_AUTOGEN_EXECUTABLE:
#   Absolute path and filename for sphinx-autogen (if found)
#
# Sphinx_APIDOC_EXECUTABLE:
#   Absolute path and filename for sphinx-apidoc (if found)
#
# Sphinx_BUILD_EXECUTABLE:
#   Absolute path and filename for sphinx-build (if found)
#
# Sphinx_QUICKSTART_EXECUTABLE:
#   Absolute path and filename for sphinx-quickstart (if found)
#
# Sphinx_PYTHON_EXECUTABLE:
#   Our best guess at the Python executable to use to run Sphinx.

set( _sphinx_search_paths
  /usr/bin
  /usr/local/bin
  /opt/local/bin
)

# If the user specified a search directory, check that first.
if (Sphinx_DIR)
  list( INSERT _sphinx_search_paths 0 ${Sphinx_DIR} )
endif (Sphinx_DIR)

if (Sphinx_FIND_COMPONENTS)
  set( _sphinx_required_components Sphinx_FIND_COMPONENTS )
else (Sphinx_FIND_COMPONENTS)
  set( _sphinx_required_components build )
endif (Sphinx_FIND_COMPONENTS)

set( _sphinx_all_components
  apidoc autogen build quickstart
)

function(find_sphinx_components)
   foreach(_component ${_sphinx_all_components})

     set(_component_name "sphinx-${_component}")
#     message("Searching for Sphinx component ${_component} with full name ${_component_name}")
     string(TOUPPER ${_component} _uc_executable_name)
     set(_varname "Sphinx_${_uc_executable_name}_EXECUTABLE")

     find_program( ${_varname}
       ${_component_name}
       PATHS ${_sphinx_search_paths}
       DOC "Path to sphinx-${_component} executable"
       )

     if (${_varname})
       set(Sphinx_${_component}_FOUND TRUE)
#       message("Found Sphinx component ${_component} at location ${${_varname}}")
     endif (${_varname})

     unset( _component_name )

   endforeach()
endfunction(find_sphinx_components)

function(extract_interpreter)
   set( _one_value_args FILE DESTINATION )
   cmake_parse_arguments(extract_interpreter "" "${_one_value_args}" "" ${ARGN} )

   # The #! notation only works on Unix-like systems.  What will
   # sphinx-build.bat look like on Windows?
   file(STRINGS ${extract_interpreter_FILE} _file_strings
     REGEX "^#!"
     )

   if (_file_strings)
     list(LENGTH ${_file_strings} _string_list_length)
     if (${_string_list_length} GREATER 0)
       list(GET ${_file_strings} 0 _first_line_of_file)
     else()
       set(_first_line_of_file ${_file_strings})
     endif()

     string(SUBSTRING ${_first_line_of_file} 2 -1 _interpreter_name)
#     message("Possible interpreter name: ${_interpreter_name}")
     set(${extract_interpreter_DESTINATION} ${_interpreter_name} PARENT_SCOPE)
   else (_file_strings)
     set(${extract_interpreter_DESTINATION} NOTFOUND PARENT_SCOPE)
   endif (_file_strings)

#   message("After extraction, _file_strings is ${_file_strings}")

endfunction(extract_interpreter)

find_sphinx_components()
if (Sphinx_BUILD_EXECUTABLE)
#   message("Sphinx_BUILD_EXECUTABLE is ${Sphinx_BUILD_EXECUTABLE}")
   if (NOT ${Sphinx_PYTHON_EXECUTABLE})
     extract_interpreter(FILE ${Sphinx_BUILD_EXECUTABLE} DESTINATION Sphinx_EXECUTABLE_TMP)
   endif()

   if (NOT "${Sphinx_PYTHON_EXECUTABLE}")
     set( Sphinx_PYTHON_EXECUTABLE ${Sphinx_EXECUTABLE_TMP}
       CACHE FILEPATH "Python interpreter to use to run Sphinx"
       )
   endif()
endif(Sphinx_BUILD_EXECUTABLE)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(
  Sphinx
  FOUND_VAR Sphinx_FOUND
  REQUIRED_VARS Sphinx_BUILD_EXECUTABLE
  HANDLE_COMPONENTS
)

