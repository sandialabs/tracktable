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

"""tracktable.feature.annotations:

Annotate points or trajectories (or the points in a trajectory) with useful derived quantities
"""

from __future__ import print_function, division, absolute_import
from tracktable.core import geomath
import numpy

from six.moves import range

ALL_ANNOTATIONS = {}

# ----------------------------------------------------------------------

def climb_rate(trajectory, max_climb=2000):
    """climb_rate: Annotate points in an AirTrajectory with climb rate

    usage: climb_rate(t: AirTrajectory) -> None

    This will add a property 'climb_rate' to each point in the input
    trajectory.  This is measured in units/sec and is computed as
    (points[n].altitude - points[n-1].altitude) /
    (points[n].timestamp - points[n-1].timestamp).
    """

    if len(trajectory) == 0:
        return
    elif len(trajectory) == 1:
        trajectory[0].properties['climb_rate'] = 0.0
    else:
        for i in range(len(trajectory) - 1):
            if ('altitude' not in trajectory[i].properties or
                'altitude' not in trajectory[i+1].properties):
                altitude_delta = 0.0
            else:
                altitude_delta = trajectory[i+1].properties['altitude'] - trajectory[i].properties['altitude']
            try:
                time_delta = (trajectory[i+1].timestamp - trajectory[i].timestamp).total_seconds()
            except IndexError:
                time_delta = 1

            if time_delta == 0:
                time_delta = 1
            climb_rate = float(altitude_delta) / (time_delta / 60.0)
            trajectory[i].set_property('climb_rate', climb_rate)

        trajectory[-1].set_property('climb_rate', trajectory[-2].properties['climb_rate'])

    return trajectory

# ----------------------------------------------------------------------

def get_climb_rate(trajectory, max_velocity=2000):
    scalars = numpy.zeros(len(trajectory))

    for i in range(len(trajectory)):
        climb_rate = float(trajectory[i].property('climb_rate')) / max_velocity
        if climb_rate < -1:
            climb_rate = -1
        if climb_rate > 1:
            climb_rate = 1

        value = 0.5 * ( climb_rate + 1 )
        scalars[i] = value
    return scalars

# ----------------------------------------------------------------------

def get_airspeed(trajectory, min_speed=0, max_speed=980):
    """Return a vector of scalars for point-to-point speeds

    This is a feature accessor that can be used to color a trajectory.
    It will map the 'speed' property into a range from 0 to 1.

    Args:
       trajectory (tracktable.core.Trajectory): Trajectory containing speeds

    Kwargs:
       min_speed (float): Minimum speed in kilometers per hour.  This will be mapped to the bottom of the scalar range and thus the bottom of the color map.  Defaults to 0.
       max_speed (float): Maximum speed in kilometers per hour.  This will be mapped to the top of the scalar range and thus the top of the color map.  Defaults to 980 (0.8 Mach, a common maximum permitted speed for civilian airliners).

    Returns:
       A vector of scalars that can be used as input to a colormap.
    """

    return _get_scaled_speed(trajectory, min_speed=min_speed, max_speed=max_speed)

# ----------------------------------------------------------------------

def get_speed_over_water(trajectory, min_speed=0, max_speed=60):
    """Return a vector of scalars for point-to-point speeds over water

    This is a feature accessor that can be used to color a trajectory.
    It will map the 'speed' property into a range from 0 to 1.

    Args:
       trajectory (tracktable.core.Trajectory): Trajectory containing speeds

    Kwargs:
       min_speed (float): Minimum speed in kilometers per hour.  This will be mapped to the bottom of the scalar range and thus the bottom of the color map.  Defaults to 0.
       max_speed (float): Maximum speed in kilometers per hour.  This will be mapped to the top of the scalar range and thus the top of the color map.  Defaults to 60 km/h (32 knots, very fast for big ships but slower than the maximum speed of high-speed civilian ferries).

    Returns:
       A vector of scalars that can be used as input to a colormap.
    """

    return _get_scaled_speed(trajectory, min_speed=min_speed, max_speed=max_speed)

def get_speed(trajectory):
    """Get the speed for a trajectory without any scaling.

    Args:
      trajectory (tracktable.core.Trajectory): Trajectory containing speeds

    Returns:
      Numpy array containing the speed value for each point
    """
    scalars = numpy.zeros(len(trajectory))
    for i in range(len(trajectory)):
        scalars[i] = trajectory[i].speed

    return scalars

# ----------------------------------------------------------------------

def _get_scaled_speed(trajectory, min_speed, max_speed):
    """Internal method used for get_airspeed and get_speed_over_water

    This is a feature accessor that can be used to color a trajectory.
    It will map the 'speed' property into a range from 0 to 1.

    Args:
       trajectory (tracktable.core.Trajectory): Trajectory containing speeds

    Kwargs:
       min_speed (float): Minimum speed in kilometers per hour.  No default.
       max_speed (float): Maximum speed in kilometers per hour.  No default.

    Returns:
       A vector of scalars that can be used as input to a colormap.
    """

    scalars = numpy.zeros(len(trajectory))
    for i in range(len(trajectory)):
        speed = trajectory[i].speed
        value = (speed - min_speed) / (max_speed - min_speed)
        scalars[i] = value

    return scalars

# ----------------------------------------------------------------------

def get_progress(trajectory):

    scalars = numpy.zeros(len(trajectory))

    for i in range(len(trajectory)):
        scalars[i] = trajectory[i].property("progress")

    return scalars

# ----------------------------------------------------------------------

def progress(trajectory):

    """progress: Annotate points in an AirTrajectory with flight progress

    usage: progress(t: AirTrajectory) -> None

    This will add a property "progress" to each point in the input
    trajectory.  This property will be 0 at the first point, 1 at the
    last point, and spaced evenly in between.
    """

    if len(trajectory) == 0:
        return trajectory
    else:
        trajectory[0].set_property('progress', 0.0)
        if len(trajectory) > 1:
            step = 1.0 / (len(trajectory) - 1)
            current_value = step
            for i in range(1, len(trajectory)):
                trajectory[i].set_property('progress', 1.0 * current_value)
                current_value += step

    return trajectory

# ----------------------------------------------------------------------

def compute_speed_from_positions(trajectory):
    for i in range(len(trajectory) - 1):
        speed_between_points = geomath.speed_between_points(trajectory[i], trajectory[i+1])
        trajectory[i].speed = speed_between_points

    if len(trajectory) > 1:
        trajectory[-1].speed = trajectory[-2].speed
    if len(trajectory) == 1:
        trajectory[-1].speed = 0

    return trajectory

# ----------------------------------------------------------------------

def register_annotation(feature_name, compute_feature, retrieve_feature):
    global ALL_ANNOTATIONS
    ALL_ANNOTATIONS[feature_name] = [ compute_feature, retrieve_feature ]

# ----------------------------------------------------------------------

def retrieve_feature_function(name):
    global ALL_ANNOTATIONS
    return ALL_ANNOTATIONS[name][0]

def retrieve_feature_accessor(name):
    global ALL_ANNOTATIONS
    return ALL_ANNOTATIONS[name][1]

def available_annotations():
    global ALL_ANNOTATIONS
    return ALL_ANNOTATIONS.keys()


register_annotation('progress', progress, get_progress)
register_annotation('climb_rate', climb_rate, get_climb_rate)
register_annotation('airspeed', compute_speed_from_positions, get_airspeed)
register_annotation('speed_over_water', compute_speed_from_positions, get_speed_over_water)
register_annotation('speed', compute_speed_from_positions, get_speed)
