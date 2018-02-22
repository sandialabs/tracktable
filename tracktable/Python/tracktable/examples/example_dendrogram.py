# Copyright (c) 2014-2018 National Technology and Engineering
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

# Author: Ben Newton  - February 21, 2018

import tracktable.io.trajectory as trajectory
from tracktable.core import geomath

import argparse

def parse_args():
    desc = "Given a set of trajectory segments (possibly from multiple \
    original trajectories) create a hierarchical clustering of the \
    trajectory segments."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('input', type=argparse.FileType('r'))
    parser.add_argument('-n', "--numSamples", dest="num_samples", type=int,
                        default=4)
    return parser.parse_args()

def distance_geometry(traj, samples):
    points = []
    for i in range(samples):
        fraction = 0.5
        if samples != 1:
            fraction = float(i)/(samples-1)
        points.append(geomath.point_at_fraction(traj, fraction)) # of dist
    featureVec = []
    for segment_length in range(2,samples+1): #similar to code in sub_trajectorize.py
        #print(segment_length)
        num_segments_of_length = (samples-segment_length)+1
        for start_index in range(num_segments_of_length):
            end_index = start_index+segment_length-1
            #print(start_index, end_index)
            featureVec.append(geomath.distance(points[start_index],
                                               points[end_index]))
    return featureVec

def main():
    args = parse_args()
    samples = args.num_samples
    features = []
    normalize = True
    for traj in trajectory.from_ijson_file_iter(args.input):
        features.append(distance_geometry(traj, samples))
        print(features)

if __name__ == '__main__':
    main()
