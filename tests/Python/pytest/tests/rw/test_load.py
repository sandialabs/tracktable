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

import logging
import os.path
import sys

import pytest

from tracktable.rw.load import load_trajectories

logger = logging.getLogger(__name__)

def test_load_trajectory_points_csv(ground_truth_path: str):
    filename = os.path.join(ground_truth_path, "Points", "SampleFlightsUS.csv")
    trajectory_points = load_trajectories(filename, return_trajectory_points=True)
    assert len(trajectory_points) > 0

def test_load_trajectories_points_csv(ground_truth_path: str):
    filename = os.path.join(ground_truth_path, "Points", "SampleFlightsUS.csv")
    trajectories = load_trajectories(filename)
    assert len(trajectories) > 0

def test_load_trajectory_points_tsv(ground_truth_path: str):
    filename = os.path.join(
        ground_truth_path,
        "Points", "tab_separated", "SampleFlightsUS.tsv"
        )
    trajectory_points = load_trajectories(filename, return_trajectory_points=True)
    assert len(trajectory_points) > 0

def test_load_trajectories_tsv(ground_truth_path: str):
    filename = os.path.join(
        ground_truth_path,
        "Points", "tab_separated", "SampleFlightsUS.tsv"
        )
    trajectories = load_trajectories(filename)
    assert len(trajectories) > 0

def test_load_trajectory_points_traj(ground_truth_path: str):
    filename = os.path.join(
        ground_truth_path,
        "Trajectories", "NYHarbor_2020_06_30_first_hour.traj"
        )
    trajectory_points = load_trajectories(filename, return_trajectory_points=True)
    assert len(trajectory_points) > 0

def test_load_trajectories_traj(ground_truth_path: str):
    filename = os.path.join(
        ground_truth_path,
        "Trajectories", "NYHarbor_2020_06_30_first_hour.traj"
        )
    trajectories = load_trajectories(filename)
    assert len(trajectories) > 0
