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

#import tracktable.inout.trajectory as trajectory
#from tracktable.domain import all_domains as ALL_DOMAINS
#import tracktable.analysis.sub_trajectorize as st

#import importlib
#import argparse
#import copy

#from pymongo import MongoClient

#todo seems to import all but two trajectories from the given file.  Look into that!

import argparse
from pymongo import MongoClient
import tracktable.inout.trajectory as trajectory

def main():
    parser = argparse.ArgumentParser(description=
                                     'Example of Reading a Json file into mongo.')
    parser.add_argument('json_file', type=argparse.FileType('r'))
    args = parser.parse_args()

    client = MongoClient('localhost', 27017)
    db = client.ASDI
    trajs = db.FlightsSample

    for traj in trajectory.from_ijson_file_iter(args.json_file):
        result = trajs.insert_one(trajectory.to_dict(traj, addId=True))

if __name__ == '__main__':
    main()
