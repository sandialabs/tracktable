# Copyright (c) 2014-2020 National Technology and Engineering
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

"""Compute the distance geometry signature of a trajectory."""

from __future__ import division, absolute_import, print_function

from tracktable.lib import _distance_geometry


def distance_geometry_by_distance(trajectory, depth):
    """Compute distance geometry signature sampled by length

    This function computes the multilevel distance geometry
    for a given trajectory.  Each level *d* approximates the
    input trajectory with *d* equal-length line segments.
    The distance geometry values for that level are the lengths
    of all *d* line segments, normalized to lie between 0 and 1.
    A value of 1 indicates the length of the entire trajectory.

    The D-level distance geometry for a curve will result in
    (D * (D+1)) / 2  separate values.

    This implementation creates the endpoints of the line segments
    by sampling the trajectory at fractions of total distance
    traveled.  To sample by total duration, use
    distance_geometry_by_time().

    Arguments:
        trajectory {Tracktable trajectory}: Input curve to analyze
        depth {integer}: How many levels to compute.  Must
            be greater than zero.

    Returns:
        List of distance geometry values laid out consecutively by
            increasing depth.

    Raises:
        ValueError: 'depth' is not a positive integer
        BoostPythonArgumentException: 'trajectory' is not a Tracktable
            trajectory
    """

    if depth < 1:
        raise ValueError(
            ('distance_geometry_by_distance: depth must be greater '
             'than zero (you supplied "{}")').format(depth)
            )

    return _distance_geometry._distance_geometry_by_distance(trajectory, depth)


def distance_geometry_by_time(trajectory, depth):
    """Compute distance geometry signature sampled by time

    This function computes the multilevel distance geometry
    for a given trajectory.  Each level *d* approximates the
    input trajectory with *d* equal-length line segments.
    The distance geometry values for that level are the lengths
    of all *d* line segments, normalized to lie between 0 and 1.
    A value of 1 indicates the length of the entire trajectory.

    The D-level distance geometry for a curve will result in
    (D * (D+1)) / 2  separate values.

    This implementation creates the endpoints of the line segments
    by sampling the trajectory at fractions of total duration
    To sample by distance traveled, use
    distance_geometry_by_distance().

    Arguments:
        trajectory {Tracktable trajectory}: Input curve to analyze
        depth {integer}: How many levels to compute.  Must
            be greater than zero.

    Returns:
        List of distance geometry values laid out consecutively by
            increasing depth.

    Raises:
        ValueError: 'depth' is not a positive integer
        BoostPythonArgumentException: 'trajectory' is not a Tracktable
            trajectory
    """

    if depth < 1:
        raise ValueError(
            ('distance_geometry_by_time: depth must be greater '
             'than zero (you supplied "{}")').format(depth)
            )

    return _distance_geometry._distance_geometry_by_time(trajectory, depth)
