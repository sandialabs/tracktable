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

#todo make sure lists are same length
def trajectory_from_dictionary(dictionary):
    """Returns a trajectory constructed from the given dictionary.
    Args:
       dictionary: the dictionary to convert into a trajectory
    """
    #verify coords list lengths are equal
    points = []
    dimension = dictionary['dimension']
    numPoints = len(dictionary['coords0'])
    for coordIndex in range(dimension):
        if len(dictionary['coords'+str(coordIndex)]) != numPoints:
            raise ValueError("coords"+str(coordIndex)+" with length of "+ str(len(dictionary['coords'+str(coordIndex)])) +
                             " does not match numPoints="+str(numPoints))

    #verify properties list lengths are equal
    numProperties = len(dictionary['propertyNames'])
    for propertyIndex in range(numProperties):
        if len(dictionary['property'+str(propertyIndex)]) != numPoints:
            raise ValueError("property"+str(propertyIndex)+" with length of "+ str(len(dictionary['property'+str(propertyIndex)])) +
                             " does not match numPoints="+str(numPoints))

    domain = importlib.import_module("tracktable.domain."+
                                     dictionary['domain'].lower())

    for i in range(numPoints):
        point = domain.TrajectoryPoint()
        for j in range(dimension):
            point[j] = dictionary['coords'+str(j)][i]
        point.object_id = dictionary['object_id']
        point.timestamp = Timestamp.from_string(dictionary['timestamps'][i])
        for propertyIndex in range(numProperties):
            point.set_property(dictionary['propertyNames'][propertyIndex],
                               dictionary['property'+str(propertyIndex)][i])
        points.append(point)

    trajectory = domain.Trajectory.from_position_list(points)

    #add trajectory properties
    index=0
    for trajectoryPropName in dictionary['trajectoryPropNames']:
        trajectory.set_property(trajectoryPropName, dictionary["trajectoryProp"+str(index)])
        index+=1

    return trajectory

def dictionary_from_trajectory(trajectory):
    """Returns a dictionary constructed from the given trajectory
    Args:
       trajectory: the trajectory to convert into a dictonary representation
    """

    dictionary = {}
    dimension = len(trajectory[0])
    dictionary['dimension'] = dimension
    dictionary['domain'] = trajectory.DOMAIN

    dictionary['trajectoryPropNames'] = trajectory.properties.keys()
    for trajectoryPropIndex in range(len(trajectory.properties)):
        dictionary['trajectoryProp'+str(trajectoryPropIndex)] = trajectory.property(trajectory.properties.keys()[trajectoryPropIndex])

    numProperties = len(trajectory[0].properties)
    dictionary['propertyNames'] = trajectory[0].properties.keys()
    for nameIndex in range(numProperties):
        dictionary['property'+str(nameIndex)] = []

    dictionary['object_id'] = trajectory[0].object_id
    dictionary['timestamps'] = []

    dictionary['coords0'] = []
    if dimension > 1:
        dictionary['coords1'] = []
    if dimension > 2:
        dictionary['coords2'] = []

    for i in range(len(trajectory)):
        dictionary['timestamps'].append(Timestamp.to_string(trajectory[i].timestamp,
                                                            include_tz=False))
        for j in range(dimension):
            dictionary['coords'+str(j)].append(trajectory[i][j])
        for propertyIndex in range(numProperties):
            dictionary['property'+str(propertyIndex)].append(trajectory[i].property(dictionary['propertyNames'][propertyIndex]))
    return dictionary

#need to handle double, string and timestamp properties
#does every point need to have a given property?
