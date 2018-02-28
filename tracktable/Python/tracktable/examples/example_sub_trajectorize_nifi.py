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

# Author: Ben Newton  - February 28, 2018

import tracktable.io.trajectory as trajectory
from tracktable.domain import all_domains as ALL_DOMAINS
import tracktable.analysis.sub_trajectorize as st

import importlib
import argparse

from enum import Enum

import ijson

class Method(Enum):
    straight = 'straight'
    accel = 'accel'

    def __str__(self):
        return self.value

def parse_args():
    desc = "Subtrajectorize the trajectories in a given json file and output \
    to stdout in json format (for use in a nifi workflow)\
    Example Straight Segmentation Method:     python example_sub_trajectorize_nifi.py -m straight -l 7 -s 1.001 ../../../../TestData/trajectories.json \
    Example Acceleration Segmentation Method: python example_sub_trajectorize_nifi.py -m accel -a .025 -t ../../../../TestData/trajectories.json"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', dest='method', type=Method, choices=list(Method), default='straight')
    parser.add_argument('input', type=argparse.FileType('r'))
    
    parser.add_argument('-s', dest='straightness_threshold', type=float,
                        default=1.001)
    #below - 2 is minimum  #could likely decrease?
    parser.add_argument('-l', dest='length_threshold', type=int, default=7)
    
    #below params for Accel only
    parser.add_argument('-a', dest='accel_threshold', type=float, default=0.025)
    parser.add_argument('-t', '--tight', dest='tight', action="store_true")
    
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()

    if args.verbose:
        print("Segmentation method is "+str(args.method))

    if args.method == Method.accel:
        subtrajer = \
        st.SubTrajerAccel(accel_threshold=args.accel_threshold,
                          tight=args.tight)
    else:
        subtrajer = \
        st.SubTrajerStraight(straightness_threshold=args.straightness_threshold,
                          length_threshold_samples=args.length_threshold)

    first_time = True
    
    count = 0
    #for traj_json in traj_iter:
    for traj in trajectory.from_ijson_file_iter(args.input):
        count += 1
        if args.verbose:
            print(count, traj[0].object_id)

        parent_id = traj[0].object_id+'_'+traj[0].timestamp.strftime('%Y-%m-%dT%H:%M:%S')

        if first_time: #assumes entire file is same domain
            domain_to_import = 'tracktable.domain.{}'.format(traj.DOMAIN)
            domain_module = importlib.import_module(domain_to_import)
            first_time = False
        leaves = subtrajer.subtrajectorize(traj, returnGraph=False)
        segment_num = 0
        segments = []
        for leaf in leaves:
            pts = []
            for i in range(leaf[0], leaf[1]+1):
                pts.append(traj[i])
            traj_dict = trajectory.to_dict(domain_module.Trajectory.from_position_list(pts))
            traj_dict['_id'] = traj_dict['_id']+'_'+str(segment_num).zfill(3)  #add the segment number to ensure unique ids 
            # as there can be duplicate timestamps
            traj_dict['segment_properties'] = {"seg_num" : segment_num, "seg_parent_id" : parent_id}
            segments.append(traj_dict)
            segment_num+=1
        entry = {"_id" : parent_id, "segments" : segments}
        #new_result = segs.insert_one(entry)
        print(entry)
    #end for trajectory

    
if __name__ == '__main__':
    main()
