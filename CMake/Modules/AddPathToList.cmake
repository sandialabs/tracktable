# Copyright (c) 2014-2022 National Technology and Engineering
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

# Add a path to a list of paths in an environment variable.
# Tries to be portable about it.  On Windows (MSVC, MINGW)
# the path separator is a semicolon.  On Unix-like systems
#(Cygwin, OSX, Linux, others) the separator is a colon.
#
# Arguments:
#
# starting_list: Path list to which we will append
# new_path: Path to add to list
# OUTPUT: Name of output variable.  This variable will store the result.

function(add_path_to_list starting_list new_path OUTPUT)
	if (MINGW OR MSVC)
	  # Escape all the semicolons in the existing path so
	  # that CMake won't interpret them as new variables.
	  string(REPLACE ";" "\\;" ${starting_list} _escaped_path)
	  set( ${OUTPUT} "${_escaped_path}\\;${new_path}" PARENT_SCOPE)
	else ()
	  # If it's not Windows then we're going to hope it's
	  # Unix-like.
	  set( ${OUTPUT} "${starting_list}:${new_path}" PARENT_SCOPE)
	endif (MINGW OR MSVC)
endfunction()


