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

# This is src/tracktable/examples/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our Python example scripts are working.
#
# This does not yet test the Jupyter notebooks.

include(PythonTest)
include(FindPythonModule)

set(EXAMPLE_MODULE tracktable.examples)
set(TEST_DATA ${Tracktable_DATA_DIR}/internal_test_data)

find_python_module(cartopy CARTOPY_MODULE_STATUS CARTOPY_MODULE_LOCATION)

find_package_handle_standard_args(PY_cartopy_module DEFAULT_MSG PY_CARTOPY_MODULE)
# message("PY_CARTOPY_MODULE ${PY_CARTOPY_MODULE}")

if (PY_CARTOPY_MODULE)
  add_python_test(
    P_TerrestrialHeatmapExample
    ${EXAMPLE_MODULE}.python_scripts.heatmap_from_points
    --domain terrestrial
    --longitude-column 2
    --latitude-column 3
    --object-id-column 0
    --timestamp-column 1
    --scale-length-in-km 1000
    ${TEST_DATA}/Points/SampleHeatmapPoints.csv
    ${Tracktable_BINARY_DIR}/TestOutput/test_output_heatmap_terrestrial.png
  )

  add_python_test(
    P_CartesianHeatmapExample
    ${EXAMPLE_MODULE}.python_scripts.heatmap_from_points
      --domain cartesian2d
      --object-id-column 0
      --timestamp-column 1
      --x-column 2
      --y-column 3
      ${TEST_DATA}/Points/SamplePointsCartesian.csv
      ${Tracktable_BINARY_DIR}/TestOutput/test_output_heatmap_cartesian.png
  )

  add_python_test(
    P_TerrestrialTrajectoryMapExample
    ${EXAMPLE_MODULE}.python_scripts.trajectory_map_from_points
    --domain terrestrial
    --object-id-column 0
    --timestamp-column 1
    --longitude-column 2
    --latitude-column 3
    ${TEST_DATA}/Points/SampleTrajectories.csv
    ${Tracktable_BINARY_DIR}/TestOutput/test_output_trajectory_map_terrestrial.png
  )


  add_python_test(
    P_CartesianTrajectoryMapExample
    ${EXAMPLE_MODULE}.python_scripts.trajectory_map_from_points
    --domain cartesian2d
    --object-id-column 0
    --timestamp-column 1
    --x-column 2
    --y-column 3
    --map-bbox -100 -100 100 100
    ${TEST_DATA}/Points/SamplePointsCartesian.csv
    ${Tracktable_BINARY_DIR}/TestOutput/test_output_trajectory_map_cartesian.png
  )


  add_python_test(
    P_CartesianTrajectoryMapAutoBbox
    ${EXAMPLE_MODULE}.python_scripts.trajectory_map_from_points
    --domain cartesian2d
    --object-id-column 0
    --timestamp-column 1
    --x-column 2
    --y-column 3
    ${TEST_DATA}/Points/SamplePointsCartesian.csv
    ${Tracktable_BINARY_DIR}/TestOutput/test_output_trajectory_map_cartesian_auto_bbox.png
  )
else (PY_CARTOPY_MODULE)
  message(STATUS "Cartopy module not found. Rendering tests will not be executed and rendering module will not execute with current python implementation.")
  message(STATUS "Rendering modules will be installed, but you must add cartopy to your current environment or change to a python environment with cartopy for rendering to work.")
endif(PY_CARTOPY_MODULE)


if (TEST_MOVIES)
  #add_python_test(
  #  P_Cartesian2DTrajectoryMovieExample
  #  ${EXAMPLE_MODULE}.python_scripts.movie_from_points
  #  --domain cartesian2d
  #  --object-id-column 0
  #  --timestamp-column 1
  #  --x-column 2
  #  --y-column 3
  #  --map-bbox -100 -100 100 100
  #  --trajectory-linewidth taper
  #  --trajectory-initial-linewidth 4
  #  --trajectory-final-linewidth 1
  #  ${TEST_DATA}/Points/SamplePointsCartesian.csv
  #  ${Tracktable_BINARY_DIR}/TestOutput/test_cartesian_trajectory_movie.m4v
  #  )

  #add_python_test(
  # P_ParallelProcessingMovieExample
  #  ${EXAMPLE_MODULE}.python_scripts.parallel_movie_from_points
  #  --processors 8
  #  --domain cartesian2d
  #  --object-id-column 0
  #  --timestamp-column 1
  #  --x-column 2
  #  --y-column 3
  #  --map-bbox -100 -100 100 100
  #  --trajectory-linewidth taper
  #  --trajectory-initial-linewidth 4
  #  --trajectory-final-linewidth 1
  #  ${TEST_DATA}/Points/SamplePointsCartesian.csv
  #  ${Tracktable_BINARY_DIR}/TestOutput/test_parallel_cartesian_trajectory_movie.m4v
  #  )

  #add_python_test(
  #  P_TerrestrialTrajectoryMovieExample_Points
  #  ${EXAMPLE_MODULE}.python_scripts.movie_from_points
  #  --domain terrestrial
  #  --object-id-column 0
  #  --timestamp-column 1
  #  --longitude-column 2
  #  --latitude-column 3
  #  --map region:conus
  #  --trajectory-linewidth taper
  #  --trajectory-initial-linewidth 2
  #  --trajectory-final-linewidth 0.5
  #  --trail-duration 1800
  #  ${TEST_DATA}/Points/SampleTrajectories.csv
  #  ${Tracktable_BINARY_DIR}/TestOutput/test_terrestrial_trajectory_movie_points.m4v
  #  )

   #add_python_test(
   #  P_TerrestrialTrajectoryMovieExample_Trajectories
   #  ${EXAMPLE_MODULE}.python_scripts.movie_from_trajectories
   #  --domain terrestrial
   #  --map region:conus
   #  --trajectory-linewidth taper
   #  --trajectory-initial-linewidth 2
   #  --trajectory-final-linewidth 0.5
   #  --trail-duration 1800
   #  ${TEST_DATA}/Points/SampleTrajectories.traj
   #  ${Tracktable_BINARY_DIR}/TestOutput/test_terrestrial_trajectory_movie_trajectories.m4v
   #  )

   endif (TEST_MOVIES)
