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

"""PyTest fixtures for Tracktable tests"""

import datetime
import itertools
import os.path
import pathlib

import pytest

from tracktable.domain import terrestrial
from tracktable.examples.tutorials import tutorial_helper

@pytest.fixture
def current_file_directory() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def repository_root(current_file_directory: pathlib.Path) -> pathlib.Path:
    # Go up until we find LICENSE.txt
    here = current_file_directory
    while not (here / "LICENSE.txt").exists():
        here = here.parent
    return here

@pytest.fixture
def tracktable_data_path(repository_root: pathlib.Path) -> pathlib.Path:
    return repository_root / "tracktable-data" / "tracktable-data" / "tracktable_data"

@pytest.fixture
def some_other_path() -> pathlib.Path:
    return pathlib.Path("/tmp")

@pytest.fixture
def ground_truth_path(tracktable_data_path: pathlib.Path) -> pathlib.Path:
    return tracktable_data_path / "internal_test_data"

@pytest.fixture
def sample_string_value() -> str:
    return "jabberwocky"

@pytest.fixture
def sample_float_value() -> float:
    return 3.14159

@pytest.fixture
def sample_timestamp_value() -> datetime.datetime:
    return datetime.datetime(year=1969, month=7, day=20, hour=20, minute=17,
                             tzinfo=datetime.timezone.utc)


@pytest.fixture
def sample_trajectories(sample_string_value,
                        sample_timestamp_value,
                        sample_float_value) -> list[terrestrial.Trajectory]:

    trajectories: list[terrestrial.Trajectory] = tutorial_helper.get_trajectory_list("us-flights")

    # Now we need more properties in order to test the converter.
    for trajectory in trajectories:
        trajectory.properties["trajectory_string_property"] = sample_string_value
        trajectory.properties["trajectory_float_property"] = sample_float_value
        trajectory.properties["trajectory_timestamp_property"] = sample_timestamp_value
        trajectory.properties["trajectory_null_property"] = None

        for (i, point) in enumerate(trajectory):
            if i % 10 == 0:
                point.properties["point_string_property"] = None
                point.properties["point_float_property"] = None
                point.properties["point_timestamp_property"] = None
                point.properties["point_null_property"] = None
            else:
                point.properties["point_string_property"] = sample_string_value
                point.properties["point_float_property"] = sample_float_value
                point.properties["point_timestamp_property"] = sample_timestamp_value
                point.properties["point_null_property"] = None

    return trajectories


@pytest.fixture
def sample_terrestrial_trajectory_points(sample_trajectories) -> list[terrestrial.TrajectoryPoint]:
    """Points from sample trajectories"""

    return list(itertools.chain(*sample_trajectories))


# YOU ARE HERE:
# Create .csv, .traj, and .parquet versions of the trajectory data above
