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
import sys
from tracktable.rw.load import load_trajectories

logger = logging.getLogger(__name__)

def test_loader_csv(file):
    logger.info("Testing CSV Loader")
    trajectory_points = load_trajectories(file, return_trajectory_points=True)
    assert len(trajectory_points) > 0
    trajectories = load_trajectories(file)
    assert len(trajectories) > 0

def test_loader_tsv(file):
    logger.info("Testing TSV Loader")
    trajectory_points = load_trajectories(file, return_trajectory_points=True)
    assert len(trajectory_points) > 0
    trajectories = load_trajectories(file)
    assert len(trajectories) > 0

def test_loader_traj(file):
    logger.info("Testing Traj Loader")
    trajectory_points = load_trajectories(file, return_trajectory_points=True)
    assert len(trajectory_points) > 0
    trajectories = load_trajectories(file)
    assert len(trajectories) > 0

def main():
    test_loader_csv(sys.argv[1])
    test_loader_tsv(sys.argv[2])
    test_loader_traj(sys.argv[3])

if __name__ == '__main__':
    sys.exit(main())
