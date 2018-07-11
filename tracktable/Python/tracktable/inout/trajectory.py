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
# Date:   October, 19, 2017

#may need to include Timezone, include_tz=True at some point?

"""
tracktable.inout.trajectory - Read/Write a trajectory from/to a python
dictionary and from/to a json string or file
"""

from tracktable.core import Timestamp
import sys
import importlib
import datetime
import json
import ijson
#import ijson.backends.yajl2_cffi as ijson #would be faster, but don't thik yajl-py is currently supported in python3 (todo could look into later)

def from_dict(dictionary):
    """Returns a trajectory constructed from the given dictionary.
    Args:
       dictionary: the dictionary to convert into a trajectory
    """

    #verify domain is valid and import appropriate domain
    try:
        domain = importlib.import_module("tracktable.domain."+
                                         dictionary['domain'].lower())
    except ImportError:
        raise ValueError("Error: invalid domain name: "+
                         dictionary['domain'].lower())

    dimension = domain.DIMENSION

    #verify each coordinate matches dimension
    points = []
    numPoints = len(dictionary['coordinates'])
    for point in dictionary['coordinates']:
        if len(point) != dimension:
            raise ValueError("Error: point " + str(point) + " has "
                             + str(len(point)) + " coordinate(s), expected "
                             + str(dimension)+".")

    #verify point properties values lists are of equal length
    for (name, attributes) in dictionary['point_properties'].items():
        if len(attributes['values']) != numPoints:
            raise ValueError("Error: "+name+" property has only "
                             + str(len(attributes['values']))
                             + " values, but there are " + str(numPoints)
                             + " points in the trajectory.")

    #verify there are the right number of timestamps
    if len(dictionary['timestamps']) != numPoints:
        raise ValueError("Error: Only " + str(len(dictionary['timestamps']))
                         + " timestamp values, but there are "
                         + str(numPoints) + " points in the trajectory.")

    #verify object_id is a string
    if not isinstance(dictionary['object_id'], str):
        raise ValueError("Error: object_id must be a string, but got a "
                         + "value of type "
                         +type(dictionary['object_id']).__name__)

    #generate points / position list
    for i in range(numPoints):
        #print(type(dictionary['coordinates'][i]), dictionary['coordinates'][i])
        point = domain.TrajectoryPoint([float(i) for i in dictionary['coordinates'][i]]) #had to change from Decimal('132.32') to float when using ijson
        point.object_id = dictionary['object_id']
        point.timestamp = Timestamp.from_string(dictionary['timestamps'][i],
                                                format_string=
                                                '%Y-%m-%dT%H:%M:%S')
        for (name, attributes) in dictionary['point_properties'].items():
            if attributes['values'][i] is not None:
                if attributes['type'] == "timestamp":
                    ts = Timestamp.from_string(attributes['values'][i],
                                               format_string=
                                               '%Y-%m-%dT%H:%M:%S')
                    point.set_property(name, ts)
                else:
                    point.set_property(name, attributes['values'][i])
        points.append(point)

    #make trajectory
    trajectory = domain.Trajectory.from_position_list(points)

    #add trajectory properties
    for (name, attributes) in dictionary['trajectory_properties'].items():
        if attributes['type'] == "timestamp":
            ts = Timestamp.from_string(attributes['value'],
                                       format_string='%Y-%m-%dT%H:%M:%S')
            trajectory.set_property(name, ts)
        else:
            trajectory.set_property(name, attributes['value'])

    #add segment properties (if they exist)  #just save as trajectory
    # properties.  Names must start with "seg_" may want to check for that.
    if 'segment_properties' in dictionary: #pnnl only
        for (name, attributes) in dictionary['segment_properties'].items():
            if attributes['type'] == "timestamp":
                ts = Timestamp.from_string(attributes['value'],
                                           format_string='%Y-%m-%dT%H:%M:%S')
                trajectory.set_property(name, ts)
            else:
                trajectory.set_property(name, attributes['value'])

    return trajectory

def to_dict(trajectory, addId=False):
    """Returns a dictionary constructed from the given trajectory
    Args:
       trajectory: the trajectory to convert into a dictonary representation
    """

    dictionary = {}
    dictionary['domain'] = trajectory.DOMAIN
    dictionary['object_id'] = trajectory[0].object_id
    if addId:
        dictionary['_id'] = trajectory[0].object_id+'_'+\
        trajectory[0].timestamp.strftime('%Y-%m-%dT%H:%M:%S') #pnnl only

    # set trajectory properties
    dictionary['trajectory_properties'] = {}
    dictionary['segment_properties'] = {}
    for (name, value) in trajectory.properties.items():
        if isinstance(value, datetime.datetime):
            ts = Timestamp.to_string(value, include_tz=False, format_string='%Y-%m-%dT%H:%M:%S')
            entry = {name: {'type': "timestamp", 'value': ts}}
            if name.startswith('seg_'): # a segment_property
                dictionary['segment_properties'].update(entry) #pnnl only
            else:
                dictionary['trajectory_properties'].update(entry)
        else:
            entry = {name: {'type': type(value).__name__, 'value': value}}
            if name.startswith('seg_'): # a segment_property
                dictionary['segment_properties'].update(entry) #pnnl only
            else:
                dictionary['trajectory_properties'].update(entry)

    # initialize timestamps and coordinates
    dictionary['timestamps'] = []
    dictionary['coordinates'] = []

    # initialize point properties
    dictionary['point_properties'] = {}

    # set timestamps, coordinates and point_properties
    for i in range(len(trajectory)):
        ts = Timestamp.to_string(trajectory[i].timestamp, include_tz=False, format_string='%Y-%m-%dT%H:%M:%S')
        dictionary['timestamps'].append(ts)
        dictionary['coordinates'].append(tuple(trajectory[i]))
        for (name, value) in trajectory[i].properties.items():
            if isinstance(value, datetime.datetime):
                ts = Timestamp.to_string(value, include_tz=False, format_string='%Y-%m-%dT%H:%M:%S')
                if name not in dictionary['point_properties']:
                    entry = {name: {'type': "timestamp",
                                    'values': [None]*len(trajectory)}}
                    dictionary['point_properties'].update(entry)
                dictionary['point_properties'][name]['values'][i] = ts
            else:
                if name not in dictionary['point_properties']:
                    entry = {name: {'type': type(value).__name__,
                                    'values': [None]*len(trajectory)}}
                    dictionary['point_properties'].update(entry)
                dictionary['point_properties'][name]['values'][i] = value

    return dictionary

# below by Mirec Miskuf from: https://stackoverflow.com/questions/956867
#    /how-to-get-string-objects-instead-of-unicode-from-json
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

# below by Mirec Miskuf from: https://stackoverflow.com/questions/956867
#    /how-to-get-string-objects-instead-of-unicode-from-json
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
            _byteify(key, ignore_dicts=True): _byteify(value,
                                                       ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def from_json_multi(json_string): #todo may want to make a multi version
    """Returns a list of trajectories constructed from the given json string.
    Args:
       json_string: the json to convert into a list of trajectories
    """
    trajectories = []
    if sys.version_info[0] < 3:
        for traj_json_string in json_loads_byteified(json_string):
            trajectories.append(from_dict(traj_json_string))
    else:
        for traj_json_string in json.loads(json_string):
            trajectories.append(from_dict(traj_json_string))
    return trajectories

def from_json(json_string):
     """Returns a single trajectory constructed from the given json string.
    Args:
       json_string: the json string to convert into a single trajectory
    """
     if sys.version_info[0] < 3:
         return from_dict(json_loads_byteified(json_string))
     else:
         return from_dict(json.loads(json_string))

def to_json_multi(trajectories):
    """Returns a json string constructed from the given list of trajectories
    Args:
       trajectories: the trajectories to convert into a dictonary
                     representation
    """
    json_string = "[\n"
    for trajectory in trajectories:
        json_string+=json.dumps(to_dict(trajectory), sort_keys=True)+",\n"
    json_string=json_string[:-2]+"\n]\n" # replace ",\n" with "]"
    return json_string

def to_json(trajectory):
    """Returns a json string constructed from the given single trajectory
    Args:
       trajectory: the trajectory to convert into a dictonary representation
    """
    return json.dumps(to_dict(trajectory), sort_keys=True)

def from_json_file(json_file):
    #with open(json_filename) as file:
    json_string = json_file.read() #todo handle error
    return from_json(json_string)

def from_ijson_file_multi(json_file):
    trajectories = []
    for obj in ijson.items(json_file, 'item'):
        trajectories.append(from_dict(obj))
    return trajectories

#requires lots of memory for large files.
def from_json_file_multi(json_file):
    json_string = json_file.read()
    return from_json_multi(json_string)

class from_ijson_file_iter:
    def __init__(self, json_file):
        self.generator = ijson.items(json_file, 'item')

    def __iter__(self):
        return self

    def __next__(self):
        return from_dict(next(self.generator))

class from_json_file_iter:
    def __init__(self, json_file):
        self.file = json_file

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.readline()  #doing all this will likely slow it down!
        if not line: #end of file
            raise StopIteration()
        if line.replace(" ", "") == "[\n":
            line = self.file.readline() #skip [\n and read another line
        if line.strip()[0] == "[":
            line = line.strip()[1:]#skip [ at head of line #todo is this okay?
        if line[-2:] == ",\n" or line[-2:] == "]\n":
            line = line[:-2] #remove ,\n on all but 2nd to last line and ]\n
                             # on last line
        if not line: #line is now empty
            raise StopIteration()
        else:
            if sys.version_info[0] < 3:
                return from_dict(json.loads_byteified(line))
            else:
                return from_dict(json.loads(line))

def to_json_file(trajectory, json_filename):
    with open(json_filename, 'w') as outfile: #todo handle error
        outfile.write(to_json(trajectory))

def to_json_file_multi(trajectories, outfile):
    outfile.write(to_json_multi(trajectories))

def to_json_filename_multi(trajectories, json_filename):
    with open(json_filename, 'w') as outfile: #todo handle error
        outfile.write(to_json_multi(trajectories))

#todo can improve performance for large files by streaming
