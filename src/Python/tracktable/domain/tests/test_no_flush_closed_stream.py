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

# Test tracktable.domain.terrestrial.TrajectoryWriter to make sure
# that it never tries to flush an already-closed stream.
#
# There is a race condition that sometimes shows up in code like
# the following.  Suppose that all_trajectories is a list of
# terrestrial trajectories.
#
# with open('myfile.traj', 'wb') as outfile:
#    writer = TrajectoryWriter(outfile)
#    writer.write(all_trajectories)
#
# Once in a while, 'outfile' will already be closed when the writer
# tries to flush the stream's in-flight contents to disk.  This
# results in an error about trying to flush an already-closed stream.
# It often segfaults the interpreter.
#
# This test case tries to exercise that bug.  I've patched the adapter
# that makes Python file-like objects look like C++ streams.  That
# seems to have fixed the problem.  Since it's intermittent, we're
# going to try writing a batch of trajectories a bunch of times
# on the assumption that sooner or later it will trigger the problem.
#

import tracktable.core
import tracktable.domain.terrestrial
from tracktable.applications.assemble_trajectories import AssembleTrajectoryFromPoints

import datetime
import os.path
import sys
import tempfile


def load_trajectories(filename):
    with open(filename, 'rb') as infile:
        point_reader = tracktable.domain.terrestrial.TrajectoryPointReader(infile)
        assembler = AssembleTrajectoryFromPoints()
        assembler.input = point_reader
        assembler.separation_time = datetime.timedelta(minutes=30)
        assembler.minimum_length = 5
        return list(assembler)


def try_saving_trajectories(trajectories, output_dir):
    with open('temp.traj', 'wb') as outfile:
        writer = tracktable.domain.terrestrial.TrajectoryWriter(outfile)
        return writer.write(trajectories)


def main():
    if len(sys.argv) == 2:
        trajectory_filename = sys.argv[1]
    else:
        trajectory_filename = os.path.join(os.path.dirname(__file__), '../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/Points/SampleTrajectories.csv')

    all_trajectories = load_trajectories(trajectory_filename)
    print('Loaded {} trajectories from disk.'.format(len(all_trajectories)))

    # If something goes wrong with this test we will get an exception
    # from this loop.
    with tempfile.TemporaryDirectory() as tempdir:
        for trial in range(10):
            if trial % 10 == 0:
                print('Starting trial {}'.format(trial))
            try_saving_trajectories(all_trajectories, tempdir)

    return 0


if __name__ == '__main__':
    sys.exit(main())
