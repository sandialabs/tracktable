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

# Author: Ben Newton  - February 26, 2018
# Author: Paul Schrum - June/July 2018 (added Curvature based analysis)

import tracktable.inout.trajectory as trajectory
from tracktable.domain import all_domains as ALL_DOMAINS
import tracktable.analysis.sub_trajectorize as st

import importlib
import argparse
import copy

# from pymongo import MongoClient
import json, ijson

from enum import Enum

class Method(Enum):
    straight = 'straight'
    accel = 'accel'
    semantic = 'semantic'
    curvature = 'curvature'

    def __str__(self):
        return self.value

def parse_args():
    desc = "Subtrajectorize the trajectories in a given json file and output \
    to a mongo db\
    Example: python example_sub_trajectorize_mongo.py -l 7 -s 1.001"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--input', dest='json_trajectory_file',
                        type=argparse.FileType('r'),
                        default="../../../..//TestData/mapping_flight.json")

    parser.add_argument('-m', dest='method', type=Method, choices=list(Method), default='straight')
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
    elif args.method == Method.semantic:
        subtrajer = \
        st.SubTrajerSemantic(straightness_threshold=args.straightness_threshold,
                             length_threshold_samples=args.length_threshold)
    elif args.method == Method.curvature:
        subtrajer = \
        st.SubTrajerCurvature()
    else:
        subtrajer = \
        st.SubTrajerStraight(straightness_threshold=args.straightness_threshold,
                          length_threshold_samples=args.length_threshold)

    first_time = True

    count = 0
    count_actually_processed = 0

    #output_json_path = r'/ascldap/users/pschrum/Documents/tracktableTesting/' \
    #        r'testResults/From_Joseph/from_Paul_s.json'
    output_json_path = 'testB.json'
    with open(output_json_path, 'w') as out_json:
        pre_str = '\n'
        out_json.write('[')
        for traj in trajectory.from_ijson_file_iter(args.json_trajectory_file):
            print("       "+traj[0].object_id) #remove
            # traj = trajectory.from_dict(traj_json)
            count += 1
            if args.verbose:
                print(count, traj[0].object_id)

            if first_time: #assumes entire file is same domain
                domain_to_import = 'tracktable.domain.{}'.format(traj.DOMAIN)
                domain_module = importlib.import_module(domain_to_import)
                first_time = False
            # if args.method == Method.curvature:
            #     leaves, G = subtrajer.splitAndClassify(traj, returnGraph=False)
            # else: #could remove this if above responded to returnGraph=False todo #
            try:
                leaves = subtrajer.splitAndClassify(traj, returnGraph=False)
            except (IndexError, AttributeError, ZeroDivisionError, TypeError) as ie:
                # These are all the exceptions I need to deal with eventually
                # print (count)
                # # e.args[0] = e.args[0] + f'  count = {count}'
                # raise IndexError(ie.args[0] + f'  count = {count}')
                continue
            if not leaves[0]:
                continue
            segment_num = 0
            segments = []
            for leaf in leaves:
                pts = []
                #print(leaf[0], leaf[1])
                for i in range(leaf[0], leaf[1]+1):
                    pts.append(traj[i])
                traj_dict = trajectory.to_dict(domain_module.Trajectory.from_position_list(pts), addId=True)
                traj_dict['_id'] = traj_dict['_id']+'_'+str(segment_num).zfill(3)  #add the segment number to ensure unique ids
                # as there can be duplicate timestamps
                traj_dict['segment_properties'] = {"seg_num" : segment_num, "seg_parent_id" : traj[0].object_id, "seg_type" : leaf[2]}
                segments.append(traj_dict)
                segment_num+=1
            entry = {"_id" : traj[0].object_id, "segments" : segments}
            json_str = json.dumps(entry, sort_keys=True)
            out_json.write(pre_str + json_str)
            pre_str = ',\n'
            count_actually_processed += 1
            dbg = True
        out_json.write('\n]\n')

        # new_result = segs.insert_one(entry)
    print(f"Processed {count_actually_processed} out of {count} trajectories.")
    #end for trajectory


if __name__ == '__main__':
    main()
