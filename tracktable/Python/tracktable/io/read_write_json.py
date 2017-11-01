# Copyright (c) 2017, National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).
# All rights reserved.
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

# Author: Ben Newton
# Date:   October, 24, 2017

"""
tracktable.io.read_write_json - Read/Write a trajectory from/to a JSON file
"""

import sys
import json
from tracktable.io.read_write_dictionary import trajectory_from_dictionary
from tracktable.io.read_write_dictionary import dictionary_from_trajectory

# below by Mirec Miskuf from: https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

# below by Mirec Miskuf from: https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json
def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def trajectory_from_json(json_string):
    """Returns a trajectory constructed from the given json string.
    Args:
       json: the json to convert into a trajectory
    """
    if sys.version_info[0] < 3:
        return trajectory_from_dictionary(json_loads_byteified(json_string))
    else:
        return trajectory_from_dictionary(json.loads(json_string))

def json_from_trajectory(trajectory):
    """Returns a json string constructed from the given trajectory
    Args:
       trajectory: the trajectory to convert into a dictonary representation
    """

    return json.dumps(dictionary_from_trajectory(trajectory), sort_keys=True)

def trajectory_from_json_file(json_filename):
    json_string = open(json_filename).read() #todo handle error
    return trajectory_from_json(json_string)

def json_file_from_trajectory(trajectory, json_filename):
    with open(json_filename, 'w') as outfile: #todo handle error
        outfile.write(json_from_trajectory(trajectory))

#todo can improve performance for large files by streaming
