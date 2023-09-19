#
# Copyright (c) 2014-2023 National Technology and Engineering
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

from __future__ import division, print_function, absolute_import
import datetime
import math
import random
from six.moves import range

from tracktable.core import geomath, Timestamp
from tracktable.domain import terrestrial

# ----------------------------------------------------------------------

def datetime_from_minute_of_year(minute_of_year, year=2013):
    days_in_month = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

    day_of_year = int(math.floor(minute_of_year / 1440))
    month = 0
    day_of_month = day_of_year
    while day_of_month >= days_in_month[month]:
        day_of_month -= days_in_month[month]
        month += 1

    # Adjust month and day to start with 1 instead of 0
    month += 1
    day_of_month += 1

    minute_of_day = minute_of_year % 1440
    hour_of_day = int(math.floor(minute_of_day / 60))
    minute_of_hour = minute_of_day % 60

    when = datetime.datetime(year=year,
                             month=month,
                             day=day_of_month,
                             hour=hour_of_day,
                             minute=minute_of_hour,
                             second=0)

    return when

# ----------------------------------------------------------------------

def add_real_property(target, property_index, value):
    property_name = 'real_{}'.format(property_index)
    target.properties[property_name] = float(value)

# ----------------------------------------------------------------------

# Integer properties are deprecated as of 2019-06-17.

def add_integer_property(target, property_index, value):
    property_name = 'integer_{}'.format(property_index)
    target.properties[property_name] = int(value)

# ----------------------------------------------------------------------

def add_string_property(target, property_index, nonce):
    property_name = 'string_{}'.format(property_index)
    target.properties[property_name] = 'string_value_{}'.format(nonce)

# ----------------------------------------------------------------------

def add_timestamp_property(target, property_index, minute_of_year):

    property_name = 'timestamp_{}'.format(property_index)
    target.properties[property_name] = Timestamp.from_any(datetime_from_minute_of_year(minute_of_year))

# ----------------------------------------------------------------------

def generate_trajectory_from_endpoints(
        start_point,
        end_point,
        num_points,
        num_trajectory_properties=6
        ):

    trajectory_class = start_point.domain_classes['Trajectory']
    trajectory = trajectory_class()

    step = 1.0 / (num_points - 1)

    trajectory.append(start_point)

    for i in range(1, num_points - 1):
        interpolant = step * i
        new_point = geomath.interpolate(start_point, end_point, interpolant)
        new_point.timestamp = truncate_fractional_seconds(new_point.timestamp)
        for (name, value) in new_point.properties.items():
            if name.startswith('real'):
                value = float(int(value))
                new_point.properties[name] = value
            elif name.startswith('time'):
                new_point.properties[name] = truncate_fractional_seconds(value)

        trajectory.append(new_point)

    trajectory.append(end_point)

    assign_random_properties(trajectory, num_trajectory_properties)
    return trajectory

# ----------------------------------------------------------------------


def assign_random_properties(target, howmany):
    for property_index in range(howmany):
        if (property_index % 3 == 0):
            add_real_property(target, property_index, random.randint(1, 1000))
        elif (property_index % 3 == 1):
            add_string_property(target, property_index, random.randint(1, 1000))
        # elif (property_index % 4 == 2):
        #     add_integer_property(target, property_index, random.randint(1, 1000))
        else:
            add_timestamp_property(target, property_index, random.randint(0, 365*1440))

# ----------------------------------------------------------------------

def generate_random_points(prototype,
                           num_points,
                           num_point_properties=6):
    points = []

    for i in range(num_points):
        next_point = prototype()
        for i in range(len(next_point)):
            coord = random.uniform(-1000, 1000)
            # truncate to 5 significant figures
            coord = 0.01 * int(100 * coord)
            next_point[i] = coord

        if hasattr(next_point, 'object_id'):
            next_point.object_id = 'test_object_{}'.format(num_points)

        if hasattr(next_point, 'timestamp'):
            next_point.timestamp = Timestamp.from_any(datetime_from_minute_of_year(random.randint(0, 365*1440)))

        if next_point.domain_classes['BasePoint'] == terrestrial.BasePoint:
            restrict_point_to_globe(next_point)

        assign_random_properties(next_point, num_point_properties)
        points.append(next_point)

    return points

# ----------------------------------------------------------------------

def restrict_point_to_globe(point):
    point[0] = (point[0] % 360) - 180
    point[1] = (point[1] % 180) - 90

# ----------------------------------------------------------------------

def generate_random_trajectory(prototype, num_point_properties, num_trajectory_properties):
    object_id = 'test_object_{}'.format(random.randint(0,1000))

    start_minute = random.randint(0, 1440 * 180)
    end_minute = start_minute + random.randint(0, 2880)

    start_time = datetime_from_minute_of_year(start_minute)
    end_time = datetime_from_minute_of_year(end_minute)

    endpoints = generate_random_points(prototype.domain_classes['TrajectoryPoint'], 2, num_point_properties)
    endpoints[0].object_id = object_id
    endpoints[1].object_id = object_id
    endpoints[0].timestamp = Timestamp.from_any(start_time)
    endpoints[1].timestamp = Timestamp.from_any(end_time)

    print("generate_random_trajectory: Start point is {}".format(endpoints[0]))

    return generate_trajectory_from_endpoints(
        endpoints[0],
        endpoints[1],
        10,
        #int((end_minute - start_minute) / 2),
        num_trajectory_properties
        )

# ----------------------------------------------------------------------

def truncate_fractional_seconds(timestamp):
    return Timestamp.from_any(datetime.datetime(year=timestamp.year,
                                                month=timestamp.month,
                                                day=timestamp.day,
                                                hour=timestamp.hour,
                                                minute=timestamp.minute,
                                                second=timestamp.second))
