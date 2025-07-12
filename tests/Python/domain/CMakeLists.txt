#
# Copyright (c) 2014-2025 National Technology and Engineering
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

# This is src/Python/tracktable/domain/tests/CMakeLists.txt
#
# Here we list the Python tests that we need to run to make sure that
# our domain classes and functions (mostly the readers) are working.

include(PythonTest)

add_python_test(P_BasePointToString test_base_point_to_string.py)

add_python_test(P_DomainNames test_domain_names.py)

add_python_test(P_GeometricMedian test_geometric_median.py)

add_python_test(P_NoFlushClosedStream test_no_flush_closed_stream.py)

add_python_test(P_Terrestrial_BasePointReader
  test_terrestrial_base_point_reader.py ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv 14
  )

add_python_test(P_Terrestrial_TrajectoryPointReader
  test_terrestrial_trajectory_point_reader.py ${Tracktable_DATA_DIR}/internal_test_data/Points/PointsWithComments.csv  14
  )

add_python_test(
  P_Terrestrial_ManyBasePointReader
  test_terrestrial_many_base_point_reader.py ${Tracktable_DATA_DIR}/internal_test_data/Points/tab_separated/SampleHeatmapPoints.tsv 50000
  )

add_python_test(
  P_Pickle_Cartesian2D_BasePoint
  test_pickle_cartesian2d_base_point.py
  )

add_python_test(
  P_Pickle_Cartesian3D_BasePoint
  test_pickle_cartesian3d_base_point.py
  )

add_python_test(
  P_Pickle_Terrestrial_BasePoint
  test_pickle_terrestrial_base_point.py
  )

add_python_test(
  P_Pickle_Cartesian2D_TrajectoryPoint
  test_pickle_cartesian2d_trajectory_point.py
  )

add_python_test(
  P_Pickle_Cartesian3D_TrajectoryPoint
  test_pickle_cartesian3d_base_point.py
  )

add_python_test(
  P_Pickle_Terrestrial_TrajectoryPoint
  test_pickle_terrestrial_trajectory_point.py
  )

add_python_test(
  P_Pickle_Terrestrial_Trajectory
  test_pickle_terrestrial_trajectory.py
  )

add_python_test(
  P_Pickle_Cartesian2D_Trajectory
  test_pickle_cartesian2d_trajectory.py
  )

add_python_test(
  P_Pickle_Cartesian3D_Trajectory
  test_pickle_cartesian3d_trajectory.py
  )

add_python_test(
  P_RTree_Nearest_Neighbors
  test_rtree_nearest_neighbors.py
  )

add_python_test(
  P_RTree_Points_In_Box
  test_rtree_points_in_box.py
  )

add_python_test(
  P_Terrestrial_BasePointWriter
  test_terrestrial_base_point_writer.py
  )

add_python_test(
  P_Terrestrial_MakeBoundingBox
  test_terrestrial_make_bounding_box.py
  )

add_python_test(
  P_Cartesian2D_MakeBoundingBox
  test_cartesian2d_make_bounding_box.py
  )

add_python_test(
  P_Cartesian3D_MakeBoundingBox
  test_cartesian3d_make_bounding_box.py
  )

add_python_test(
  P_Terrestrial_TrajectoryPointWriter
  test_terrestrial_trajectory_point_writer.py
  )

add_python_test(
  P_Terrestrial_TrajectoryPointWriterFidelity
  test_terrestrial_trajectory_point_writer_fidelity.py
  )

add_python_test(
  P_Terrestrial_TrajectoryWriter
  test_terrestrial_trajectory_writer.py
  )

add_python_test(
  P_Terrestrial_TrajectoryWriterFidelity
  test_terrestrial_trajectory_writer_fidelity.py
  )

add_python_test(
  P_Cartesian2D_BasePointWriter
  test_cartesian2d_base_point_writer.py
  )

add_python_test(
  P_Cartesian2D_TrajectoryPointWriter
  test_cartesian2d_trajectory_point_writer.py
  )

add_python_test(
  P_Cartesian2D_TrajectoryPointWriterFidelity
  test_cartesian2d_trajectory_point_writer_fidelity.py
  )

add_python_test(
  P_Cartesian2D_TrajectoryWriter
  test_cartesian2d_trajectory_writer.py
  )

add_python_test(
  P_Cartesian2D_TrajectoryWriterFidelity
  test_cartesian2d_trajectory_writer_fidelity.py
  )

add_python_test(
  P_Cartesian3D_BasePointWriter
  test_cartesian3d_base_point_writer.py
  )

add_python_test(
  P_Cartesian3D_TrajectoryPointWriter
  test_cartesian3d_trajectory_point_writer.py
  )

add_python_test(
  P_Cartesian3D_TrajectoryPointWriterFidelity
  test_cartesian3d_trajectory_point_writer_fidelity.py
  )

add_python_test(
  P_Cartesian3D_TrajectoryWriter
  test_cartesian3d_trajectory_writer.py
  )

add_python_test(
  P_Cartesian3D_TrajectoryWriterFidelity
  test_cartesian3d_trajectory_writer_fidelity.py
  )

add_python_test(
  P_Terrestrial_ManyTrajectoryPointReader
  test_terrestrial_many_trajectory_point_reader.py ${Tracktable_DATA_DIR}/internal_test_data/Points/tab_separated/SampleHeatmapPoints.tsv 50000
)

add_python_test(
  P_FeatureVector_ToString
  test_feature_vector_to_string.py
)

add_python_test(
  P_ImportDomainClasses
  import_everything.py
  )

add_python_test(
  P_BasePointConstructors
  test_base_point_constructors.py
  )

add_python_test(
  P_SimplifyTrajectory
  test_simplify_trajectory.py
  )

add_python_test(
  P_CurrentLengthAvailable
  test_current_length.py
  )

add_python_test(
  P_CurrentLengthFraction
  test_current_length_fraction.py
  )

add_python_test(
  P_CurrentTimeFraction
  test_current_time_fraction.py
  )

add_python_test(
  P_TrajectoryId
  test_trajectory_id.py
  )

add_python_test(
  P_TrajectorySlicing
  test_trajectory_slicing.py
  )
