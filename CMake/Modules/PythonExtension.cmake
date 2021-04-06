# Copyright (c) 2014-2021 National Technology and Engineering
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

function(install_python_extension targetname dirname basedirname)
   if (MSVC OR MINGW)
     set( PYTHON_EXTENSION_SUFFIX ".pyd" )
   else (MSVC OR MINGW)
     if (CYGWIN)
	   set( PYTHON_EXTENSION_SUFFIX ".dll" )
     else (CYGWIN)
	   set( PYTHON_EXTENSION_SUFFIX ".so" )
     endif (CYGWIN)
   endif (MSVC OR MINGW)

   set_target_properties( ${targetname}
     PROPERTIES
	 OUTPUT_NAME "${targetname}"
	 PREFIX ""
	 SUFFIX "${PYTHON_EXTENSION_SUFFIX}"
   )

   install(
     TARGETS ${targetname}
	 DESTINATION ${CMAKE_INSTALL_PREFIX}/Python/tracktable/${dirname}
	 RENAME "${targetname}.${PYTHON_EXTENSION_SUFFIX}"
	)

   add_custom_command( TARGET ${targetname}
     POST_BUILD
     COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${targetname}> ${basedirname}/${dirname}/$<TARGET_FILE_NAME:${targetname}>
     )

endfunction(install_python_extension)
