#
# Copyright (c) 2014-2017 National Technology and Engineering
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

from __future__ import print_function
from datetime import datetime
import sys
import pickle
from six import StringIO

from tracktable.core import TrajectoryPoint, Timestamp

def point_to_string(point):
    properties = []
    for thing in point.properties:
        properties.append( ( thing.key(), point.properties[thing.key()] ) )

    template_string = '[ lon: {} lat: {} altitude: {} speed: {} heading: {} id: {} timestamp: {} properties: {} ]\n'
    return template_string.format( point.longitude,
                                   point.latitude,
                                   point.altitude,
                                   point.speed,
                                   point.heading,
                                   point.object_id,
                                   point.timestamp,
                                   properties )
def test_point_type():
    print("Testing point type")

    error_count = 0

    surface_point = TrajectoryPoint()

    test_timestamp = Timestamp.from_any(datetime(year=1969,
                                                 month=7,
                                                 day=20,
                                                 hour=20,
                                                 minute=18))
    test_number = 12345
    test_string = 'this is a test'

    january_1_2014 = Timestamp.from_any(datetime(year=2014,
                                                 month=1,
                                                 day=1,
                                                 hour=12,
                                                 minute=34,
                                                 second=56))

    surface_point.object_id = 'GreenChileExpress'
    surface_point.latitude = 35.1107
    surface_point.longitude = -106.6100
    surface_point.altitude = 10000
    surface_point.timestamp = january_1_2014
    surface_point.heading = 45
    surface_point.speed = 100
    surface_point.set_property('number', test_number)
    surface_point.set_property('string', test_string)
    surface_point.set_property('timestamp', test_timestamp)

    print("Dump of point contents: {}".format(point_to_string(surface_point)))

    surface_point_copy = surface_point
    if surface_point_copy != surface_point:
        sys.stderr.write('ERROR: Point is not equal to its immediate copy!\n')
        error_count += 1

    surface_point_copy.set_property('another_number', 23456)

    for (property_name, test_value) in [ ('number', test_number),
                                         ('string', test_string),
                                         ('timestamp', test_timestamp) ]:

        if not surface_point.has_property(property_name):
            sys.stderr.write('ERROR: Point does not have property {}\n'.format(property_name))
            error_count += 1
        if surface_point.property(property_name) != test_value:
            sys.stderr.write('ERROR: Point property {} does not have expected value {}\n'.format(property_name, test_value))
            error_count += 1

    picklebuf = StringIO()
    pickle.dump(surface_point, picklebuf)
#    sys.stderr.write('Pickle buffer contents after pickling surface point: {}\n'.format(picklebuf.getvalue()))
    restorebuf = StringIO(picklebuf.getvalue())
    restored_point = pickle.load(restorebuf)

    if restored_point != surface_point:
        sys.stderr.write('ERROR: Restored point is not the same as what we pickled!\n')
        sys.stderr.write('Original point: {}\n'.format(point_to_string(surface_point)))
        sys.stderr.write('Restored point: {}\n'.format(point_to_string(restored_point)))
        error_count += 1

    if (error_count == 0):
        print("Point type passes its Python tests.")

    return error_count


# ----------------------------------------------------------------------

def test_point_types():
    error_count = test_point_type()

    print("test_point_types: error count is {}".format(error_count))

    return error_count


if __name__ == '__main__':
    sys.exit(test_point_types())

