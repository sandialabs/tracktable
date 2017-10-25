# -*- Mode: cmake; -*-
#
# This is tracktable/Python/tracktable/CMakeLists.txt
#
# Copyright (c) 2014-2017 National Technology and Engineering
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

if (BUILD_TESTING)
  add_subdirectory(analysis/tests)
  add_subdirectory(core/tests)
  add_subdirectory(examples/tests)
  add_subdirectory(source/tests)
  add_subdirectory(render/tests)
  add_subdirectory(domain/tests)
endif (BUILD_TESTING)


set( PYTHON_INSTALL_PREFIX "Python/tracktable" )

install(
  FILES __init__.py
  DESTINATION ${PYTHON_INSTALL_PREFIX}
)

file(GLOB core_files "core/*.py")
install(
  FILES ${core_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/core
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

file(GLOB example_data_files "examples/data/*.*")
install(
  FILES ${example_data_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/examples/data
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

file(GLOB render_files "render/*.py")
install(
  FILES ${render_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/render
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

file(GLOB source_files "source/*.py")
install(
  FILES ${source_files}
  DESTINATION ${PYTHON_INSTALL_PREFIX}/source
)
