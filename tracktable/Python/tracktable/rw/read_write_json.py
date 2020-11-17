# Copyright (c) 2017-2020, National Technology & Engineering Solutions of
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
tracktable.rw.read_write_json - Read/Write a trajectory from/to a JSON file
"""

import sys
import json
from tracktable.rw.read_write_dictionary import trajectory_from_dictionary
from tracktable.rw.read_write_dictionary import dictionary_from_trajectory

# below by Mirec Miskuf from: https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json
def json_loads_byteified(json_text):
    """Constructes a byteified json string from the given json text.

    Leveraged from: https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json

    Args:
       json_text (json): the json to convert into a json string

    Returns:
        Returns a byteified json string constructed from the given json text

    """
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
    """Constructes a trajectory from the given json string.

    Args:
       json_string (json): the json to convert into a trajectory

    Returns:
        Returns a trajectory constructed from the given json string

    """

    if sys.version_info[0] < 3:
        return trajectory_from_dictionary(json_loads_byteified(json_string))
    else:
        return trajectory_from_dictionary(json.loads(json_string))

def json_from_trajectory(trajectory):
    """Constructes a json string from the given trajectory

    Args:
       trajectory (Trajectory): the trajectory to convert into a json representation

    Returns:
        Returns a json string constructed from the given trajectory

    """

    return json.dumps(dictionary_from_trajectory(trajectory), sort_keys=True)

def trajectory_from_json_file(json_filename):
    """Constructes a trajectory from the given json file

    Args:
       json_filename (File): the json file to convert into a trajectory representation

    Returns:
        Returns a trajectory constructed from the given json file

    """

    json_string = open(json_filename).read() #todo handle error
    return trajectory_from_json(json_string)

def json_file_from_trajectory(trajectory, json_filename):
    """Constructes a json file from the given trajectory

    Args:
       json_filename (File): the json file to convert into a trajectory representation
       trajectory (Trajectory): the trajectory to convert into a json representation

    Returns:
        Returns a trajectory constructed from the given json file

    """
    with open(json_filename, 'w') as outfile: #todo handle error
        outfile.write(json_from_trajectory(trajectory))

#todo can improve performance for large files by streaming
