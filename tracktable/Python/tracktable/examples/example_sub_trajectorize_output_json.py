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

#todo, may want to adjust object id to be originalId-001 where 001 is
#      segement number

import tracktable.inout.trajectory as trajectory
from tracktable.domain import all_domains as ALL_DOMAINS
#from tracktable.domain.terrestrial import Trajectory, TrajectoryPoint
import tracktable.analysis.sub_trajectorize as st

import importlib
import argparse
import copy

def parse_args():
    desc = "Subtrajectorize the trajectories in a given json file and output \
    to a json file of trajectories(segments).\
    Example: python example_sub_trajectorize_output_json.py -l 7 -s 1.001 ../../../../TestData/801Trajectories.json testOut.json"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('input', type=argparse.FileType('r'))
    parser.add_argument('output', type=argparse.FileType('w'))
    parser.add_argument('-s', dest='straightness_threshold', type=float,
                        default=1.001)
    #below - 2 is minimum  #could likely decrease?
    parser.add_argument('-l', dest='length_threshold', type=int, default=7)
    return parser.parse_args()

def main():
    args = parse_args()

    subtrajer = \
    st.SubTrajectorizer(straightness_threshold=args.straightness_threshold,
                        length_threshold_samples=args.length_threshold)

    first_time = True
    sub_trajs = []
    for traj in trajectory.from_ijson_file_iter(args.input):
        if first_time: #assumes entire file is same domain
            domain_to_import = 'tracktable.domain.{}'.format(traj.DOMAIN)
            domain_module = importlib.import_module(domain_to_import)
            first_time = False
        leaves = subtrajer.subtrajectorize(traj, returnGraph=False)
        segment_num = 0
        for leaf in leaves:
            pts = []
            for i in range(leaf[0], leaf[1]+1):
                #point = copy.deepcopy(traj[i]) #todo why does copy not work? 
                #point.object_id = point.object_id+'-'+str(segment_num).zfill(3)
                pts.append(traj[i])
            sub_trajs.append(domain_module.Trajectory.from_position_list(pts))
            segment_num+=1
    #output
    trajectory.to_json_file_multi(sub_trajs, args.output)

if __name__ == '__main__':
    main()
