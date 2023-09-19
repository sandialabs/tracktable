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

from __future__ import print_function, division

from six.moves import range
import datetime
import sys
import random

#from . import create_points_and_trajectories as tt_generators
from .create_points_and_trajectories import generate_random_trajectory

from tracktable.domain.cartesian3d import Trajectory, TrajectoryPoint, TrajectoryPointWriter, TrajectoryPointReader, TrajectoryWriter, TrajectoryReader

from tracktable.core import Timestamp
from tracktable.core.test_utilities import version_appropriate_string_buffer

import datetime



def print_trajectory(t):
    print("Trajectory has {} points".format(len(t)))
    for point in t:
        print("{}".format(str(point)))

# ----------------------------------------------------------------------

def carefully_compare_trajectories(t1, t2):
    if len(t1) != len(t2):
        print("ERROR: Trajectory 1 has {} points and trajectory 2 has {}.".format(len(t1), len(t2)))
        return

    if t1.properties != t2.properties:
        t1_props = dict(t1.properties.items())
        t2_props = dict(t2.properties.items())
        if set(t1_props.keys()) != set(t2_props.keys()):
            print("ERROR: Trajectories have different properties.  T1 has {}, T2 has {}".format(t1_props.keys(), t2_props.keys()))
        for key in t1_props.keys():
            if t1.properties[key] != t2.properties[key]:
                if key.startswith('numeric'):
                    print("Trajectory numeric property {} disagrees with residual {}".format(key,
                                                                                             t1.properties[key] - t2.properties[key]))
                elif key.startswith('time'):
                    print("Trajectory timestamp property {} disagrees with residual {}".format(key,
                                                                                               t1.properties[key] - t2.properties[key]))
                else:
                    print("Trajectory string property {} disagrees: '{}', '{}'".format(key,
                                                                                       t1.properties[key],
                                                                                       t2.properties[key]))
    for point_index in range(len(t1)):
        p1 = t1[point_index]
        p2 = t2[point_index]

        if p1 != p2:
            print("ERROR: Point {} disagrees between trajectories.".format(point_index))
            print("P1: {}".format(str(p1)))
            print("P2: {}".format(str(p2)))
            if (p1.object_id != p2.object_id):
                print("Object IDs disagree: '{}', '{}'".format(p1.object_id, p2.object_id))
            if (p1.timestamp != p2.timestamp):
                print("Timestamps disagree: '{}', '{}', difference = {}".format(p1.timestamp, p2.timestamp, p1.timestamp - p2.timestamp))

            p1_props = dict(p1.properties.items())
            p2_props = dict(p2.properties.items())
            for key in p1_props.keys():
                if p1_props[key] != p2_props[key]:
                    if key.startswith('numeric'):
                        print("Numeric property {} differs with residual {}".format(key, p1_props[key] - p2_props[key]))
                    elif key.startswith('string'):
                        print("String property {} differs: '{}', '{}'".format(key, p1_props[key], p2_props[key]))
                    elif key.startswith('time'):
                        print("Time property {} differs with residual {}".format(key, p1_props[key] - p2_props[key]))

# ----------------------------------------------------------------------

def write_trajectories_to_string(trajectories):
    output = version_appropriate_string_buffer()
    writer = TrajectoryWriter(output)
    writer.write(trajectories)

    result = output.getvalue()
    print("Length of result string: {}".format(len(result)))
    return result

# ----------------------------------------------------------------------

def read_trajectories_from_string(text):
    input = version_appropriate_string_buffer(text)
    reader = TrajectoryReader(input)
    points = list(reader)
    return points

# ----------------------------------------------------------------------

def main():
    random.seed(0)
    num_errors = 0
    num_trajectories = 10
    num_point_properties = 5
    num_trajectory_properties = 10

    # original_trajectories = [ tt_generators.generate_random_trajectory(Trajectory,
    #                                                                    num_point_properties,
    #                                                                    num_trajectory_properties) for i in range(num_trajectories) ]

    original_trajectories = [ generate_random_trajectory(Trajectory,
                                                         num_point_properties,
                                                         num_trajectory_properties) for i in range(num_trajectories) ]

    trajectories_as_string = write_trajectories_to_string(original_trajectories)
    reconstituted_trajectories = read_trajectories_from_string(trajectories_as_string)

    if len(original_trajectories) != len(reconstituted_trajectories):
        print("ERROR: Original trajectory array contains {} entries.  Reconstituted array contains {}.".format(len(original_trajectories), len(reconstituted_trajectories)))
        return 1

    num_errors = 0
    for i in range(num_trajectories):
        if original_trajectories[i] != reconstituted_trajectories[i]:
            print("\n\n\nERROR: Trajectory {} was not reconstituted successfully.".format(i))
            print("Original trajectory ({}):\n{}".format(repr(original_trajectories[i]), str(original_trajectories[i])))
            print_trajectory(original_trajectories[i])
            print("\nReconstituted trajectory ({}):\n{}".format(repr(reconstituted_trajectories[i]), str(reconstituted_trajectories[i])))
            print_trajectory(reconstituted_trajectories[i])

            print("\n\n")
            carefully_compare_trajectories(original_trajectories[i],
                                           reconstituted_trajectories[i])
            num_errors += 1

    return (num_errors != 0)

if __name__ == '__main__':
    sys.exit(main())
