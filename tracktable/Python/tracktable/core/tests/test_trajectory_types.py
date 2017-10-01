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

from __future__ import print_function

import pickle
import sys
from six import StringIO
import datetime

from tracktable.core import Trajectory, TrajectoryPoint

def test_trajectory():
    print("Testing Trajectory class.")
    error_count = 0

    right_now = datetime.datetime.now()

    boston = TrajectoryPoint()
    boston.latitude = 42.3581
    boston.longitude = -71.0636
    boston.heading = 180
    boston.speed = 200
    boston.object_id = 'ContinentalExpress'
    boston.timestamp = right_now
    boston.set_property('favorite_food', 'baked_beans')
    boston.set_property('name', 'Boston')

    miami = TrajectoryPoint()
    miami.timestamp = right_now
    miami.latitude = 25.7877
    miami.longitude = -80.2241
    miami.heading = 280
    miami.speed = 200
    miami.object_id = 'ContinentalExpress'
    miami.set_property('favorite_food', 'cuban_sandwich')
    miami.set_property('name', 'Miami')

    san_francisco = TrajectoryPoint()
    san_francisco.timestamp = right_now
    san_francisco.latitude = 37.7833
    san_francisco.longitude = -122.4167
    san_francisco.heading = 0
    san_francisco.speed = 200
    san_francisco.object_id = 'ContinentalExpress'
    san_francisco.set_property('favorite_food', 'Ghirardelli chocolate')
    san_francisco.set_property('name', 'San Francisco')

    seattle = TrajectoryPoint()
    seattle.timestamp = right_now
    seattle.latitude = 47.6097
    seattle.longitude = -122.3331
    seattle.heading = 90
    seattle.speed = 200
    seattle.object_id = 'ContinentalExpress'
    seattle.set_property('favorite_food', 'seafood')
    seattle.set_property('name', 'Seattle')

    round_trip = [ boston, miami, san_francisco, seattle, boston ]

    my_trajectory = Trajectory.from_position_list(round_trip)

    print("Testing from_position_list")
    if len(my_trajectory) != 5:
        sys.stderr.write('ERROR: Expected length of trajectory to be 5 points but it was {}\n'.format(len(my_trajectory)))
        error_count += 1


    print("Sanity-checking first and last points")
    restored_point = my_trajectory[0]
    if restored_point != boston:
        sys.stderr.write('ERROR: Expected first point in trajectory to be Boston.  Instead it claims to be {}.  Dumps of original and restored points follow.\n'.format(restored_point.property('name')))
        sys.stderr.write(str(boston))
        sys.stderr.write('\n')
        sys.stderr.write(str(my_trajectory[0]))
        sys.stderr.write('\n')

        error_count += 1

    if my_trajectory[-1] != boston:
        sys.stderr.write('ERROR: Expected last point in trajectory to be Boston.  Instead it claims to be {}.\n'.format(my_trajectory[-1].property('name')))
        error_count += 1

    print("Testing pickle support")
    picklebuf = StringIO()
    pickle.dump(my_trajectory, picklebuf)
    restorebuf = StringIO(picklebuf.getvalue())
    restored_trajectory = pickle.load(restorebuf)

    if my_trajectory != restored_trajectory:
        sys.stderr.write('ERROR: Original trajectory is not the same as the one being restored from pickle jar.\n')
#        sys.stderr.write('Original trajectory: {}'.format(my_trajectory))
#        sys.stderr.write('Restored trajectory: {}'.format(restored_trajectory))
        error_count += 1

    if error_count == 0:
        print("Surface trajectory passed all tests.")

    return error_count

# ----------------------------------------------------------------------

def test_trajectory_types():
    error_count = test_trajectory()
    print("\n")

    return error_count

if __name__ == '__main__':
    sys.exit(test_trajectory_types())
