# -*- Mode: cmake; -*-
#
# This is tracktable/Python/tracktable/CMakeLists.txt
#
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

if (UNIX AND APPLE)
  set(PYTHON_INSTALL_PREFIX "Python/tracktable" )
endif (UNIX AND APPLE)

if (BUILD_TESTING)
  add_subdirectory(algorithms/tests)
  add_subdirectory(applications/tests)
  add_subdirectory(core/tests)
  add_subdirectory(data_generators/tests)
  add_subdirectory(domain/tests)
  add_subdirectory(examples)
  add_subdirectory(rw/tests)
  add_subdirectory(info/tests)
  add_subdirectory(render/tests)
 endif (BUILD_TESTING)

if (COPY_NOTEBOOKS_TRACKTABLE_DATA)
 message(STATUS "Copying notebooks from tracktable-docs. Don't modify these copies!")
 execute_process(COMMAND ${Python3_EXECUTABLE} _copy_notebooks.py WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR})
endif (COPY_NOTEBOOKS_TRACKTABLE_DATA)

install(
  FILES __init__.py
  DESTINATION ${PYTHON_INSTALL_PREFIX}
)

file(GLOB algorithms_files "algorithms/*.py")
install(
  FILES ${algorithms_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/algorithms
)

# TODO (mjfadem) Remove this in release 1.8
file(GLOB analysis_files "analysis/*.py")
install(
  FILES ${analysis_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/analysis
)

file(GLOB applications_files "applications/*.py")
install(
  FILES ${applications_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/applications
)

file(GLOB core_files "core/*.py")
install(
  FILES ${core_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/core
)

file(GLOB data_generator_files "data_generators/*.py")
install(
  FILES ${data_generator_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/data_generators
)

file(GLOB domain_files "domain/*.py")
install(
  FILES ${domain_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/domain
)

file(GLOB example_files "examples/*.py")
install(
  FILES ${example_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples
)

file(GLOB response_files "examples/response_files/*.txt")
install(
  FILES ${response_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/response_files
)

file(GLOB example_python_scripts "examples/python_scripts/*.py")
install(
  FILES ${example_python_scripts}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/python_scripts
)

file(GLOB tutorial_notebooks "examples/tutorials/*.ipynb")
install(
  FILES ${tutorial_notebooks}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/tutorials
)

file(GLOB tutorial_helpers "examples/tutorials/*.py")
install(
  FILES ${tutorial_helpers}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/tutorials
)

file(GLOB analytic_demo_notebooks "examples/analytic_demos/*.ipynb")
install(
  FILES ${analytic_demo_notebooks}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/analytic_demos
)

file(GLOB analytic_demo_images "examples/analytic_demos/demo_images/*.*")
install(
  FILES ${analytic_demo_images}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/analytic_demos/demo_images
)

file(GLOB analytic_demo_helpers "examples/analytic_demos/*.py")
install(
  FILES ${analytic_demo_helpers}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/analytic_demos
)

file(GLOB feature_files "feature/*.py")
install(
  FILES ${feature_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/feature
)

file(GLOB filter_files "filter/*.py")
install(
  FILES ${filter_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/filter
)

file(GLOB info_files "info/*.py")
install(
  FILES ${info_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/info
)

file(GLOB info_data_files "info/data/*.*")
install(
  FILES ${info_data_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/info/data
)

file(GLOB lib_files "lib/*.py")
install(
  FILES ${lib_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/lib
)

file(GLOB rw_files "rw/*.py")
install(
  FILES ${rw_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/rw
)

file(GLOB render_files "render/*.py")
install(
  FILES ${render_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/render
)

file(GLOB render_backend_files "render/backends/*.py")
install(
  FILES ${render_backend_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/render/backends
)

file(GLOB render_map_decoration_files "render/map_decoration/*.py")
install(
  FILES ${render_map_decoration_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/render/map_decoration
)

file(GLOB render_map_processing_files "render/map_processing/*.py")
install(
  FILES ${render_map_processing_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/render/map_processing
)

file (GLOB script_helper_files "script_helpers/*.py")
install(
  FILES ${script_helper_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/script_helpers
)

file (GLOB script_helper_argument_groups_files "script_helpers/argument_groups/*.py")
install(
  FILES ${script_helper_argument_groups_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/script_helpers/argument_groups
)
