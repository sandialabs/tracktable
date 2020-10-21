#
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


# This is tracktable/Python/tracktable/render/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our rendering code is working.  These are basically "smoke tests" --
# we don't yet have the ability to verify the content of an image.

include(PythonTest)
include(FindPythonModule)

find_python_module(cartopy CARTOPY_MODULE_STATUS CARTOPY_MODULE_LOCATION)

find_package_handle_standard_args(PY_cartopy_module DEFAULT_MSG PY_CARTOPY_MODULE)
# message("PY_CARTOPY_MODULE ${PY_CARTOPY_MODULE}")

if (PY_CARTOPY_MODULE)
  #add_python_test(P_Mapmaker_Airport
  #  tracktable.render.tests.test_mapmaker_airport "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput/"
  #)

  add_python_test(P_Mapmaker_CONUS
    tracktable.render.tests.test_mapmaker_conus "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput/"
  )

  #add_python_test(P_Mapmaker_NorthAmerica
  #  tracktable.render.tests.test_mapmaker_north_america "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput/"
  #)

  add_python_test(P_Mapmaker_Custom_Bounding_Box_Object
    tracktable.render.tests.test_mapmaker_custom_bbox_object "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput"
  )

  add_python_test(P_Mapmaker_Custom_Bounding_Box_Floats
    tracktable.render.tests.test_mapmaker_custom_bbox_float "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput"
  )

  add_python_test(P_Mapmaker_Europe
    tracktable.render.tests.test_mapmaker_europe "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput/"
  )

  add_python_test(P_Render_Trajectories
    tracktable.render.tests.test_render_trajectories "${Tracktable_SOURCE_DIR}/TestData/GroundTruth" "${Tracktable_BINARY_DIR}/TestOutput/" "${Tracktable_SOURCE_DIR}/tracktable/Python/tracktable/examples/data/"
  )

else (PY_CARTOPY_MODULE)
  message(STATUS "Cartopy module not found. Rendering tests will not be executed and rendering module will not execute with current python implementation.")
  message(STATUS "Rendering modules will be installed, but you must add cartopy to your current environment or change to a python environment with cartopy for rendering to work.")
endif(PY_CARTOPY_MODULE)
