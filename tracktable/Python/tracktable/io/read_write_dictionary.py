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
import sys

def trajectory_from_dictionary(dictionary):
    """Returns a trajectory constructed from the given dictionary.
    Args:
       dictionary: the dictionary to convert into a trajectory
    """

    #verify domain is valid and import appropriate domain
    try:
        domain = importlib.import_module("tracktable.domain."+
                                         dictionary['domain'].lower())
    except ImportError:
        raise ValueError("Error: invalid domain name: "+dictionary['domain'].lower())

    dimension = domain.DIMENSION

    #verify each coordinate matches dimension
    points = []
    numPoints = len(dictionary['coordinates'])
    for point in dictionary['coordinates']:
        if len(point) != dimension:
            raise ValueError("Error: point {} has {} coordinate(s), expected {}.".format(
                point, len(point), dimension))

    #verify point properties values lists are of equal length
    for (name, attributes) in dictionary['point_properties'].items():
        if len(attributes['values']) != numPoints:
            raise ValueError(("Error: property {} has only {} values but "
                              "there are {} points in the trajectory.").format(
                                  name, len(attributes['values']), numPoints))

    #verify there are the right number of timestamps
    if len(dictionary['timestamps']) != numPoints:
        raise ValueError(("Error: Dictionary contains only {} timestamps but "
                          "there are {} points in the trajectory.").format(
                              len(dictionary['timestamps']), numPoints))

    #verify object_id is a string
    if not isinstance(dictionary['object_id'], str):
        raise ValueError("Error: object_id must be a string, but got a value of type "+type(dictionary['object_id']).__name__)

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
    dictionary['object_id'] = trajectory[0].object_id

    # set trajectory properties
    dictionary['trajectory_properties'] = {}
    for (name, value) in trajectory.properties.items():
        if isinstance(value, datetime.datetime):
            dictionary['trajectory_properties'].update({name: {'type': type(value).__name__, 'value': Timestamp.to_string(value, include_tz=False)}})
        else:
            # Python 2 has both 'int' and 'long' data types.  The
            # first is your system's ordinary integer; the second is
            # arbitrary-precision.  In Python 3, all integers are of
            # type 'int' and are of arbitrary precision.
            if sys.version_info[0] == 2 and type(value) is long:
                type_name = 'int'
            else:
                type_name = type(value).__name__
            dictionary['trajectory_properties'].update({name: {'type': type_name, 'value': value}})

    # initialize timestamps and coordinates
    dictionary['timestamps'] = []
    dictionary['coordinates'] = []

    # initialize point properties
    dictionary['point_properties'] = {}
    for (name, value) in trajectory[0].properties.items():
        # As above -- Python 2 has a 'long' data type that we will
        # call 'int'.
        if sys.version_info[0] == 2 and type(value) is long:
            type_name = 'int'
        else:
            type_name = type(value).__name__

        dictionary['point_properties'].update({name: {'type': type_name, 'values': []}})

    # set timestamps, coordinates and point_properties
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



