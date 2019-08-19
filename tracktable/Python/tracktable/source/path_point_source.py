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

"""
tracktable.source.path_point_source - Generate points along a path
"""

from __future__ import division, print_function, absolute_import

import datetime
import random
from tracktable.core import geomath
from six.moves import range

class TrajectoryPointSource(object):
    """Generate points interpolated between start and finish.

    Attributes:
        start_point (TrajectoryPoint): Location for first point
        end_point (TrajectoryPoint): Location for last point
        num_points (integer): Number of points in the path (at least 2)
    """

    def __init__(self):
        """Initialize an empty point source."""
        self.start_point = None
        self.end_point = None
        self.num_points = None

    def points(self):
        """Return an iterable containing the generated points in the trajectory.

        Longitude, latitude, altitude (if present) and time will be
        interpolated evenly from start_point to end_point and
        start_time to end_time.  Each point will have the object ID
        specified in self.object_id.

        Returns:
           An iterable of TrajectoryPoint instances

        Raises:
           ValueError: impossible / illegal values specified for one or more parameters
        """

        # Sanity checks first
        if self.start_point is None or self.end_point is None:
            raise ValueError("TrajectoryPointSource: You must specify both start_point and end_point")

        if self.num_points is None or self.num_points < 2:
            raise ValueError("TrajectoryPointSource: You must specify num_points and its value must be at least 2")

        for i in range(self.num_points):
            interpolant = i * (1.0 / (self.num_points - 1))
            yield( geomath.interpolate(self.start_point, self.end_point, interpolant) )


