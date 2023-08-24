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

# This is tracktable/Python/tracktable/domain/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our domain classes and functions (mostly the readers) are working.

include(PythonTest)
set(DOMAIN "tracktable.domain.tests")

add_python_test(P_BasePointToString ${DOMAIN}.test_base_point_to_string)

add_python_test(P_DomainNames ${DOMAIN}.test_domain_names)

add_python_test(P_GeometricMedian ${DOMAIN}.test_geometric_median)

add_python_test(P_NoFlushClosedStream ${DOMAIN}.test_no_flush_closed_stream)

add_python_test(P_Terrestrial_BasePointReader
  ${DOMAIN}.test_terrestrial_base_point_reader ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv 14
  )

add_python_test(P_Terrestrial_TrajectoryPointReader
  ${DOMAIN}.test_terrestrial_trajectory_point_reader ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv  14
  )

add_python_test(
  P_Terrestrial_ManyBasePointReader
  ${DOMAIN}.test_terrestrial_many_base_point_reader ${Tracktable_DATA_DIR}/internal_test_data/Points/tab_separated/SampleHeatmapPoints.tsv 50000
  )

add_python_test(
  P_Pickle_Cartesian2D_BasePoint
  ${DOMAIN}.test_pickle_cartesian2d_base_point
  )

add_python_test(
  P_Pickle_Cartesian3D_BasePoint
  ${DOMAIN}.test_pickle_cartesian3d_base_point
  )

add_python_test(
  P_Pickle_Terrestrial_BasePoint
  ${DOMAIN}.test_pickle_terrestrial_base_point
  )

add_python_test(
  P_Pickle_Cartesian2D_TrajectoryPoint
  ${DOMAIN}.test_pickle_cartesian2d_trajectory_point
  )

add_python_test(
  P_Pickle_Cartesian3D_TrajectoryPoint
  ${DOMAIN}.test_pickle_cartesian3d_base_point
  )

add_python_test(
  P_Pickle_Terrestrial_TrajectoryPoint
  ${DOMAIN}.test_pickle_terrestrial_trajectory_point
  )

add_python_test(
  P_Pickle_Terrestrial_Trajectory
  ${DOMAIN}.test_pickle_terrestrial_trajectory
  )

add_python_test(
  P_Pickle_Cartesian2D_Trajectory
  ${DOMAIN}.test_pickle_cartesian2d_trajectory
  )

add_python_test(
  P_Pickle_Cartesian3D_Trajectory
  ${DOMAIN}.test_pickle_cartesian3d_trajectory
  )

add_python_test(
  P_RTree_Nearest_Neighbors
  ${DOMAIN}.test_rtree_nearest_neighbors
  )

add_python_test(
  P_RTree_Points_In_Box
  ${DOMAIN}.test_rtree_points_in_box
  )

add_python_test(
  P_Terrestrial_BasePointWriter
  ${DOMAIN}.test_terrestrial_base_point_writer
  )

add_python_test(
  P_Terrestrial_MakeBoundingBox
  ${DOMAIN}.test_terrestrial_make_bounding_box
  )

add_python_test(
  P_Cartesian2D_MakeBoundingBox
  ${DOMAIN}.test_cartesian2d_make_bounding_box
  )

add_python_test(
  P_Cartesian3D_MakeBoundingBox
  ${DOMAIN}.test_cartesian3d_make_bounding_box
  )

add_python_test(
  P_Terrestrial_TrajectoryPointWriter
  ${DOMAIN}.test_terrestrial_trajectory_point_writer
  )

add_python_test(
  P_Terrestrial_TrajectoryPointWriterFidelity
  ${DOMAIN}.test_terrestrial_trajectory_point_writer_fidelity
  )

add_python_test(
  P_Terrestrial_TrajectoryWriter
  ${DOMAIN}.test_terrestrial_trajectory_writer
  )

add_python_test(
  P_Terrestrial_TrajectoryWriterFidelity
  ${DOMAIN}.test_terrestrial_trajectory_writer_fidelity
  )

add_python_test(
  P_Cartesian2D_BasePointWriter
  ${DOMAIN}.test_cartesian2d_base_point_writer
  )

add_python_test(
  P_Cartesian2D_TrajectoryPointWriter
  ${DOMAIN}.test_cartesian2d_trajectory_point_writer
  )

add_python_test(
  P_Cartesian2D_TrajectoryPointWriterFidelity
  ${DOMAIN}.test_cartesian2d_trajectory_point_writer_fidelity
  )

add_python_test(
  P_Cartesian2D_TrajectoryWriter
  ${DOMAIN}.test_cartesian2d_trajectory_writer
  )

add_python_test(
  P_Cartesian2D_TrajectoryWriterFidelity
  ${DOMAIN}.test_cartesian2d_trajectory_writer_fidelity
  )

add_python_test(
  P_Cartesian3D_BasePointWriter
  ${DOMAIN}.test_cartesian3d_base_point_writer
  )

add_python_test(
  P_Cartesian3D_TrajectoryPointWriter
  ${DOMAIN}.test_cartesian3d_trajectory_point_writer
  )

add_python_test(
  P_Cartesian3D_TrajectoryPointWriterFidelity
  ${DOMAIN}.test_cartesian3d_trajectory_point_writer_fidelity
  )

add_python_test(
  P_Cartesian3D_TrajectoryWriter
  ${DOMAIN}.test_cartesian3d_trajectory_writer
  )

add_python_test(
  P_Cartesian3D_TrajectoryWriterFidelity
  ${DOMAIN}.test_cartesian3d_trajectory_writer_fidelity
  )

add_python_test(
  P_Terrestrial_ManyTrajectoryPointReader
  ${DOMAIN}.test_terrestrial_many_trajectory_point_reader ${Tracktable_DATA_DIR}/internal_test_data/Points/tab_separated/SampleHeatmapPoints.tsv 50000
)

add_python_test(
  P_FeatureVector_ToString
  ${DOMAIN}.test_feature_vector_to_string
)

add_python_test(
  P_ImportDomainClasses
  ${DOMAIN}.import_everything
  )

add_python_test(
  P_BasePointConstructors
  ${DOMAIN}.test_base_point_constructors
  )

add_python_test(
  P_SimplifyTrajectory
  ${DOMAIN}.test_simplify_trajectory
  )

add_python_test(
  P_CurrentLengthAvailable
  ${DOMAIN}.test_current_length
  )

add_python_test(
  P_CurrentLengthFraction
  ${DOMAIN}.test_current_length_fraction
  )

add_python_test(
  P_CurrentTimeFraction
  ${DOMAIN}.test_current_time_fraction
  )

add_python_test(
  P_TrajectoryId
  ${DOMAIN}.test_trajectory_id
  )

add_python_test(
  P_TrajectorySlicing
  ${DOMAIN}.test_trajectory_slicing
  )
