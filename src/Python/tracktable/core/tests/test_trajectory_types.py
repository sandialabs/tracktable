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

from __future__ import print_function

import pickle
import sys
from six import StringIO
import datetime
import pytz

from tracktable.core import geomath
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint

def verify_time(expected, actual, test_name):
    if(actual != expected):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def verify_point(expected, actual, test_name):
    if (geomath.distance(actual, expected) > .1 or actual.timestamp != expected.timestamp):
        sys.stderr.write('ERROR: {} does not match. Expected {}, but returned {}.\n'.format(test_name,expected,actual))
        return 1
    return 0

def test_trajectory():
    print("Testing Trajectory class.")
    error_count = 0

    right_now = datetime.datetime.now(pytz.utc)

    boston = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    boston.timestamp = right_now
    boston.object_id = 'ContinentalExpress'
    boston.set_property('favorite_food', 'baked_beans')
    boston.set_property('name', 'Boston')

    miami = TerrestrialTrajectoryPoint(-80.2241, 25.7877)
    miami.timestamp = right_now + datetime.timedelta(hours = 4)
    miami.object_id = 'ContinentalExpress'
    miami.set_property('favorite_food', 'cuban_sandwich')
    miami.set_property('name', 'Miami')

    san_francisco = TerrestrialTrajectoryPoint(-122.4167, 37.7833)
    san_francisco.timestamp = right_now + datetime.timedelta(hours = 8)
    san_francisco.object_id = 'ContinentalExpress'
    san_francisco.set_property('favorite_food', 'Ghirardelli chocolate')
    san_francisco.set_property('name', 'San Francisco')

    seattle = TerrestrialTrajectoryPoint(-122.3331, 47.6097)
    seattle.timestamp = right_now + datetime.timedelta(hours = 12)
    seattle.object_id = 'ContinentalExpress'
    seattle.set_property('favorite_food', 'seafood')
    seattle.set_property('name', 'Seattle')

    boston_return = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    boston_return.timestamp = right_now + datetime.timedelta(hours = 16)
    boston_return.object_id = 'ContinentalExpress'
    boston_return.set_property('favorite_food', 'baked_beans')
    boston_return.set_property('name', 'Boston')

    round_trip = [ boston, miami, san_francisco, boston_return ]

    my_trajectory = TerrestrialTrajectory.from_position_list(round_trip)

    print("Testing insert")
    my_trajectory.insert(3, seattle)
    test_point = my_trajectory[3]
    if test_point != seattle:
        sys.stderr.write('ERROR: Expected fourth point in trajectory to be Seattle.  Instead it claims to be {}.  Dumps of original and restored points follow.\n'.format(test_point.property('name')))
        sys.stderr.write(str(seattle))
        sys.stderr.write('\n')
        sys.stderr.write(str(my_trajectory[0]))
        sys.stderr.write('\n')

        print("Testing clone")
    copied_trajectory = my_trajectory.clone()
    for i in range(0, len(my_trajectory)):
        error_count += verify_point(my_trajectory[i], copied_trajectory[i], "Cloning Test")
    copied_trajectory[0][0] = 0.0
    if my_trajectory[0][0] == 0.0:
        sys.stderr.write('ERROR: Cloned trajectory not a deep copy')
        error_count += 1

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

    if my_trajectory[-1] != boston_return:
        sys.stderr.write('ERROR: Expected last point in trajectory to be Boston.  Instead it claims to be {}.\n'.format(my_trajectory[-1].property('name')))
        error_count += 1

    print("Testing duration")
    duration = my_trajectory.duration
    if(duration != datetime.timedelta(hours = 16)):
        sys.stderr.write('ERROR: Expected duration to be 16 hours.  Instead it claims to be {}.\n'.format(duration))
        error_count += 1

    print("Testing time_at_fraction, 0.25")
    first_quarter_time = geomath.time_at_fraction(my_trajectory, 0.25)
    delta = my_trajectory[-1].timestamp - right_now
    expected_first_quarter_time = right_now + (delta // 4)
    error_count += verify_time(expected_first_quarter_time, first_quarter_time, "Time at fraction 0.25")

    print("Testing time_at_fraction, 0.75")
    last_quarter_time = geomath.time_at_fraction(my_trajectory, 0.75)
    delta = my_trajectory[-1].timestamp - right_now
    expected_last_quarter_time = right_now + ((3*delta) // 4)
    error_count += verify_time(expected_last_quarter_time, last_quarter_time, "Time at fraction 0.75")

    print("Testing time_at_fraction, 0.5")
    midpoint_time = geomath.time_at_fraction(my_trajectory, 0.5)
    expected_midpoint_time = (right_now + (my_trajectory[-1].timestamp - right_now)//2)
    error_count += verify_time(expected_midpoint_time, midpoint_time, "Time at fraction 0.5")

    print("Testing time_at_fraction, 0.0")
    start_time = geomath.time_at_fraction(my_trajectory, 0.0)
    expected_start_time = right_now
    error_count += verify_time(expected_start_time, start_time, "Time at fraction 0.0")

    print("Testing time_at_fraction, 1.0")
    end_time = geomath.time_at_fraction(my_trajectory, 1.0)
    expected_end_time = my_trajectory[-1].timestamp
    error_count += verify_time(expected_end_time, end_time, "Time at fraction 1.0")

    print("Testing time_at_fraction, -0.5")
    before_time = geomath.time_at_fraction(my_trajectory, -0.5)
    expected_before_time = right_now
    error_count += verify_time(expected_before_time, before_time, "Time at fraction -0.5")

    print("Testing time_at_fraction, 1.5")
    after_time = geomath.time_at_fraction(my_trajectory, 1.5)
    expected_after_time = my_trajectory[-1].timestamp
    error_count += verify_time(expected_after_time, after_time, "Time at fraction 1.5")

    print("Testing time_at_fraction, 0.33")
    first_third_time = geomath.time_at_fraction(my_trajectory, 1.0/3.0)
    expected_third_quarter_time = (right_now + (my_trajectory[-1].timestamp - right_now)//3)
    error_count += verify_time(expected_third_quarter_time, first_third_time, "Time at fraction 0.33")

    print("Testing time_at_fraction, No Points")
    empty_trajectory = TerrestrialTrajectory()
    empty_time = geomath.time_at_fraction(empty_trajectory, 0.5)
    error_count += verify_time(datetime.datetime(1900,1,1,0,0,0,0,pytz.utc), empty_time, "Time at fraction (no points)")

    print("Testing point_at_time_fraction, 0.25")
    first_quarter_point =  geomath.point_at_time_fraction(my_trajectory, 0.25)
    expected_first_quarter_point = TerrestrialTrajectoryPoint(-80.2241, 25.7877)
    expected_first_quarter_point.timestamp = right_now + datetime.timedelta(hours = 4)
    error_count += verify_point(expected_first_quarter_point,first_quarter_point, "Point at fraction 0.25")

    print("Testing point_at_time_fraction, 0.75")
    third_quarter_point =  geomath.point_at_time_fraction(my_trajectory, 0.75)
    expected_third_quarter_point = TerrestrialTrajectoryPoint(-122.3331, 47.6097)
    expected_third_quarter_point.timestamp = right_now + datetime.timedelta(hours = 12)
    error_count += verify_point(expected_third_quarter_point,third_quarter_point, "Point at fraction 0.75")

    print("Testing point_at_time_fraction, 0.5")
    mid_point =  geomath.point_at_time_fraction(my_trajectory, 0.5)
    expected_mid_point = TerrestrialTrajectoryPoint(-122.4167, 37.7833)
    expected_mid_point.timestamp = right_now + datetime.timedelta(hours = 8)
    error_count += verify_point(expected_mid_point,mid_point, "Point at fraction 0.5")

    print("Testing point_at_time_fraction, 0.0")
    start_point =  geomath.point_at_time_fraction(my_trajectory, 0.0)
    expected_start_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_start_point.timestamp = right_now
    error_count += verify_point(expected_start_point,start_point, "Point at fraction 0.0")

    print("Testing point_at_time_fraction, 1.0")
    end_point =  geomath.point_at_time_fraction(my_trajectory, 1.0)
    expected_end_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_end_point.timestamp = right_now + datetime.timedelta(hours = 16)
    error_count += verify_point(expected_end_point,end_point, "Point at fraction 1.0")

    print("Testing point_at_time_fraction, -0.5")
    before_point =  geomath.point_at_time_fraction(my_trajectory, -0.5)
    expected_before_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_before_point.timestamp = right_now
    error_count += verify_point(expected_before_point,before_point, "Point at fraction -0.5")

    print("Testing point_at_time_fraction, 1.5")
    after_point =  geomath.point_at_time_fraction(my_trajectory, 1.5)
    expected_after_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_after_point.timestamp = right_now + datetime.timedelta(hours = 16)
    error_count += verify_point(expected_after_point,after_point, "Point at fraction 1.5")

    print("Testing point_at_time_fraction, 0.33")
    first_third_point =  geomath.point_at_time_fraction(my_trajectory, 1.0/3.0)
    expected_first_third_point = TerrestrialTrajectoryPoint(-92.9849, 31.3181)
    expected_first_third_point.timestamp = (right_now + (my_trajectory[-1].timestamp - right_now)//3)
    error_count += verify_point(expected_first_third_point,first_third_point, "Point at fraction 0.33")

    print("Testing point_at_time_fraction, No Points")
    no_point = geomath.point_at_time_fraction(empty_trajectory, 0.5)
    empty_point = TerrestrialTrajectoryPoint.zero()
    error_count += verify_point(no_point,empty_point, "Point at fraction (no points)")

    print("Testing point_at_length_fraction, 0.25")
    first_quarter_point =  geomath.point_at_length_fraction(my_trajectory, 0.25)
    expected_first_quarter_point = TerrestrialTrajectoryPoint(-87.3824, 29.1092)
    expected_first_quarter_point.timestamp = first_quarter_point.timestamp
    error_count += verify_point(expected_first_quarter_point,first_quarter_point, "Point at length fraction 0.25")

    print("Testing point_at_length_fraction, 0.75")
    third_quarter_point =  geomath.point_at_length_fraction(my_trajectory, 0.75)
    expected_third_quarter_point = TerrestrialTrajectoryPoint(-106.489, 48.5709)
    expected_third_quarter_point.timestamp = third_quarter_point.timestamp
    error_count += verify_point(expected_third_quarter_point,third_quarter_point, "Point at length fraction 0.75")

    print("Testing point_at_length_fraction, 0.5")
    mid_point =  geomath.point_at_length_fraction(my_trajectory, 0.5)
    expected_mid_point = TerrestrialTrajectoryPoint(-116.267, 37.0967)
    expected_mid_point.timestamp = mid_point.timestamp
    error_count += verify_point(expected_mid_point,mid_point, "Point at length fraction 0.5")

    print("Testing point_at_length_fraction, 0.0")
    start_point =  geomath.point_at_length_fraction(my_trajectory, 0.0)
    expected_start_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_start_point.timestamp = right_now
    error_count += verify_point(expected_start_point,start_point, "Point at length fraction 0.0")

    print("Testing point_at_length_fraction, 1.0")
    end_point =  geomath.point_at_length_fraction(my_trajectory, 1.0)
    expected_end_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_end_point.timestamp = right_now + datetime.timedelta(hours = 16)
    error_count += verify_point(expected_end_point,end_point, "Point at length fraction 1.0")

    print("Testing point_at_length_fraction, -0.5")
    before_point =  geomath.point_at_length_fraction(my_trajectory, -0.5)
    expected_before_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_before_point.timestamp = right_now
    error_count += verify_point(expected_before_point,before_point, "Point at length fraction -0.5")

    print("Testing point_at_length_fraction, 1.5")
    after_point =  geomath.point_at_length_fraction(my_trajectory, 1.5)
    expected_after_point = TerrestrialTrajectoryPoint(-71.0636, 42.3581)
    expected_after_point.timestamp = right_now + datetime.timedelta(hours = 16)
    error_count += verify_point(expected_after_point,after_point, "Point at length fraction 1.5")

    print("Testing point_at_length_fraction, 0.33")
    first_third_point =  geomath.point_at_length_fraction(my_trajectory, 1.0/3.0)
    expected_first_third_point = TerrestrialTrajectoryPoint(-96.4035, 32.5023)
    expected_first_third_point.timestamp = first_third_point.timestamp
    error_count += verify_point(expected_first_third_point,first_third_point, "Point at length fraction 0.33")

    print("Testing point_at_length_fraction, No Points")
    no_point = geomath.point_at_length_fraction(empty_trajectory, 0.5)
    empty_point = TerrestrialTrajectoryPoint.zero()
    error_count += verify_point(no_point,empty_point, "Point at length fraction (no points)")

    print("Testing interpolation at timestamp before trajectory")
    before_time = right_now - datetime.timedelta(hours = 4)
    before_point = geomath.point_at_time(my_trajectory, before_time);
    error_count += verify_point(boston,before_point, "Point at time (-4 hours)")

    print("Testing interpolation at start timestamp of trajectory")
    start_time = right_now
    start_point = geomath.point_at_time(my_trajectory, start_time);
    error_count += verify_point(boston,start_point, "Point at time (0 hours)")

    print("Testing interpolation at first third timestamp of trajectory")
    first_third_time = right_now + datetime.timedelta(hours = 16.0/3.0)
    first_third_point = geomath.point_at_time(my_trajectory, first_third_time);
    expected_first_third_point = TerrestrialTrajectoryPoint(-92.9849, 31.3181)
    expected_first_third_point.timestamp = right_now + datetime.timedelta(hours = 16.0/3.0)
    error_count += verify_point(expected_first_third_point,first_third_point, "Point at time (+5.33 hours)")

    print("Testing interpolation at mid timestamp of trajectory")
    mid_time = right_now + datetime.timedelta(hours = 8)
    mid_point = geomath.point_at_time(my_trajectory, mid_time);
    error_count += verify_point(san_francisco,mid_point, "Point at time (+8 hours)")

    print("Testing interpolation at end timestamp of trajectory")
    end_time = right_now + datetime.timedelta(hours = 16)
    end_point = geomath.point_at_time(my_trajectory, end_time);
    error_count += verify_point(boston_return,end_point, "Point at time (+16 hours)")

    print("Testing interpolation at timestamp after trajectory")
    after_time = right_now + datetime.timedelta(hours = 20)
    after_point = geomath.point_at_time(my_trajectory, after_time);
    error_count += verify_point(boston_return,after_point, "Point at time (+20 hours)")

    print("Testing interpolation at timestamp with no points trajectory")
    no_point = geomath.point_at_time(empty_trajectory, right_now + datetime.timedelta(hours = 8))
    empty_point = TerrestrialTrajectoryPoint.zero()
    error_count += verify_point(empty_point,no_point, "Point at time (no points)")

#    print("Testing pickle support")
#    picklebuf = StringIO()
#    pickle.dump(my_trajectory, picklebuf)
#    restorebuf = StringIO(picklebuf.getvalue())
#    restored_trajectory = pickle.load(restorebuf)

#    if my_trajectory != restored_trajectory:
#        sys.stderr.write('ERROR: Original trajectory is not the same as the one being restored from pickle jar.\n')
#        sys.stderr.write('Original trajectory: {}'.format(my_trajectory))
#        sys.stderr.write('Restored trajectory: {}'.format(restored_trajectory))
#        error_count += 1

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
