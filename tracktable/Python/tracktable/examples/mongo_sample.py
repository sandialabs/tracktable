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

# Author: Ben Newton  - April 17, 2018

import argparse
from pymongo import MongoClient

def main():
    parser = argparse.ArgumentParser(description=
                                     'Read from mongo and write back a \
                                     fraction of the entries to a new \
                                     collection.\
                                     Example: mongo_sample.py \
                                     HoldingTrajectories VerifiedHoldingTrajectories')
    parser.add_argument('mongo_collection')
    parser.add_argument('output_mongo_collection')
    parser.add_argument('-r', '--regex', default="")
    args = parser.parse_args()

    client = MongoClient('localhost', 27017)
    db = client.ASDI
    trajs = db[args.mongo_collection]

    trajs_out = db[args.output_mongo_collection]

    sample_rate = 100 # one in 100

    count = 0
    for traj in trajs.find():#'{'+args.regex+'}'):
        if count % sample_rate == 0:
            trajs_out.insert_one(traj)
        count+=1

if __name__ == '__main__':
    main()
