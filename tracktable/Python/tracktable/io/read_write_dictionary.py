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

"""
tracktable.io.read_write_dictionary - Read/Write a trajectory from/to a python
dictionary
"""

from tracktable.core import Timestamp
import importlib
import datetime

#todo make sure lists are same length
def trajectory_from_dictionary(dictionary):
    """Returns a trajectory constructed from the given dictionary.
    Args:
       dictionary: the dictionary to convert into a trajectory
    """
    domain = importlib.import_module("tracktable.domain."+
                                     dictionary['domain'].lower())
    dimension = domain.DIMENSION

    #verify each coordinate matches dimension
    points = []
    numPoints = len(dictionary['coordinates'])
    for point in dictionary['coordinates']:
        if len(point) != dimension:
            raise ValueError("Error: point " + str(point) + " has "+ str(len(point)) + " coordinate(s), expected " + str(dimension)+".")

    #verify properties values lists are of equal length
    for (name, attributes) in dictionary['point_properties'].items():
        if len(attributes['values']) != numPoints:
             raise ValueError("Error: "+name+" property has only " + str(len(attributes['values'])) + " values, but there are " + numPoints + " points in the trajectory.")

    #generate points / position list
    for i in range(numPoints):
        point = domain.TrajectoryPoint(dictionary['coordinates'][i])
        point.object_id = dictionary['object_id']
        point.timestamp = Timestamp.from_string(dictionary['timestamps'][i])
        for (name, attributes) in dictionary['point_properties'].items():
            if attributes['type'] == "datetime" or attributes['type'] == "timestamp":  #okay to support both?  todo
                point.set_property(name, Timestamp.from_string(attributes['values'][i], format_string='%Y-%m-%d %H:%M:%S'))
            else:
                point.set_property(name, attributes['values'][i])
        points.append(point)

    #make trajectory
    trajectory = domain.Trajectory.from_position_list(points)

    #add trajectory properties
    for (name, attributes) in dictionary['trajectory_properties'].items():
        if attributes['type'] == "datetime" or attributes['type'] == "timestamp":  #okay to support both?  todo
            trajectory.set_property(name, Timestamp.from_string(attributes['value'], format_string='%Y-%m-%d %H:%M:%S'))
        else:
            trajectory.set_property(name, attributes['value'])

    return trajectory

def dictionary_from_trajectory(trajectory):
    """Returns a dictionary constructed from the given trajectory
    Args:
       trajectory: the trajectory to convert into a dictonary representation
    """

    dictionary = {}
    dictionary['domain'] = trajectory.DOMAIN

    dictionary['trajectory_properties'] = {}
    for (name, value) in trajectory.properties.items():
        if isinstance(value, datetime.datetime):
            dictionary['trajectory_properties'].update({name: {'type': type(value).__name__, 'value': Timestamp.to_string(value, include_tz=False)}})
        else:
            dictionary['trajectory_properties'].update({name: {'type': type(value).__name__, 'value': value}})

    dictionary['point_properties'] = {}
    for (name, value) in trajectory[0].properties.items():
        dictionary['point_properties'].update({name: {'type': type(value).__name__, 'values': []}})

    dictionary['object_id'] = trajectory[0].object_id
    dictionary['timestamps'] = []

    dictionary['coordinates'] = []

    for i in range(len(trajectory)):
        dictionary['timestamps'].append(Timestamp.to_string(trajectory[i].timestamp,
                                                            include_tz=False))
        dictionary['coordinates'].append(tuple(trajectory[i]))
        for (name, value) in trajectory[i].properties.items():
            if isinstance(value, datetime.datetime):
                dictionary['point_properties'][name]['values'].append(Timestamp.to_string(value, include_tz=False))
            else:
                dictionary['point_properties'][name]['values'].append(value)

    return dictionary

#does every point need to have a given property?
