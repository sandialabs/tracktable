# Copyright (c) 2014-2023 National Technology and Engineering
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

function(add_cpp_test)
  # Include this option if the test uses Catch2
  set(options CATCH2 MY_OPTION)
  # SOURCE is 'my_test.cpp', NAME is 'C_MyTest'
  set(single_value_arguments SOURCE NAME WORKING_DIRECTORY TARGET)
  set(multiple_value_arguments LIBRARIES COMMAND SOURCES)
  cmake_parse_arguments(PARSE_ARGV 0 arg
    "${options}" "${single_value_arguments}" "${multiple_value_arguments}"
    )

  if (NOT (arg_SOURCE OR arg_SOURCES))
    message(ERROR "You must specify either SOURCE or SOURCES with add_cpp_test().")
  endif()

  if (arg_SOURCE AND arg_SOURCES)
    message(ERROR "You can use either SOURCE or SOURCES but not both with add_cpp_test().")
  endif ()

  if (arg_SOURCES AND (NOT arg_TARGET))
    message(ERROR "You must specify TARGET when you specify SOURCES.")
  endif()

  # Add the binary target for the test

  # Single-source-file version
  if (arg_SOURCE)
    if (NOT arg_TARGET)
      # Get the basename of the source file for use as the target name
      cmake_path(GET arg_SOURCE STEM target_name)
    else ()
      set(target_name ${arg_TARGET})
    endif()
    add_executable(${target_name} ${arg_SOURCE})
  endif (arg_SOURCE)

  # Multiple-source-file version
  if (arg_SOURCES)
    set(target_name ${arg_TARGET})
    add_executable(${target_name} ${arg_SOURCES})
  endif (arg_SOURCES)


  target_link_libraries(${target_name} ${arg_LIBRARIES})

  # Have Visual Studio put tests in a subfolder in the IDE
  set_property(TARGET ${target_name} PROPERTY FOLDER "Tests")

  # Tell CMake about the test
  if (arg_CATCH2)
    if (NOT arg_COMMAND)
      set(arg_COMMAND ${target_name} -r console)
    endif ()
    if (arg_WORKING_DIRECTORY)
      add_test(
        NAME ${arg_NAME}
        COMMAND ${arg_COMMAND}
        #COMMAND ${target_name} -r console
        WORKING_DIRECTORY ${arg_WORKING_DIRECTORY}
        COMMAND_EXPAND_LISTS
      )
    else (arg_WORKING_DIRECTORY)
      add_test(
        NAME ${arg_NAME}
        COMMAND ${arg_COMMAND}
        # COMMAND ${target_name} -r console
        COMMAND_EXPAND_LISTS
      )
    endif (arg_WORKING_DIRECTORY)
  else (arg_CATCH2)
    if (NOT arg_COMMAND)
      set(arg_COMMAND "${target_name}")
    endif ()
    add_test(
      NAME ${arg_NAME}
      COMMAND ${arg_COMMAND}
      COMMAND_EXPAND_LISTS
    )
  endif (arg_CATCH2)
endfunction (add_cpp_test)


# This is outdated and will go away once I'm certain the new function works.

function(add_catch2_test test_name module_to_run)

    if (${ARGC} GREATER 2)
        add_test(
          NAME ${test_name}
          COMMAND ${module_to_run} -r console -o ${Tracktable_BINARY_DIR}/TestOutput/${test_name}.txt
          WORKING_DIRECTORY ${ARGV2}
          )
    else (${ARGC} GREATER 2)
        add_test(
          NAME ${test_name}
          COMMAND ${module_to_run} -r console -o ${Tracktable_BINARY_DIR}/TestOutput/${test_name}.txt
          )
    endif (${ARGC} GREATER 2)

endfunction(add_catch2_test)

