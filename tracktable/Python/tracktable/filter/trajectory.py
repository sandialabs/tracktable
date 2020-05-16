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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""tracktable.filter.trajectory - Filters that take trajectories as input
"""

import logging

from tracktable.core import geomath
from tracktable.core.geomath import subset_during_interval

class ClipToTimeWindow(object):
    """Truncate trajectories to fit within a time window

    Given an iterable of Trajectory objects, return those portions of
    each trajectory that fit within the specified time window.
    Interpolate endpoints as necessary.

    Attributes:
       input (iterable): Source of Trajectory objects
       start_time (datetime): Beginning time for window of interest
       end_time (datetime): End time for window of interest
    """

    def __init__(self):
        """Initialize ClipToTimeWindow with no input and no begin/end time."""

        self.input = None
        self.start_time = None
        self.end_time = None

    def trajectories(self):
        """Return sub-trajectories within window.

        Note: Since this is a generator, you can only traverse the sequence
          once unless you collect it in a list yourself.

        Yields:
           Trajectories derived from input trajectories.  Each trajectory
             is guaranteed to fall entirely within the window specified by
             self.start_time and self.end_time.  If one of the input
             trajectories extends beyond that boundary, a new endpoint will
             be interpolated so that it begins or ends precisely at the
             boundary.  Trajectories entirely outside the boundary will be
             returned as empty trajectories with 0 points.
        """

        if (self.input is None):
            raise ValueError("ClipToTimeWindow: No input source!  Set 'input' to a valid trajectory source.")

        if self.start_time is None or self.end_time is None:
            raise ValueError("ClipToTimeWindow: Incomplete time window!  You must set both 'start_time' and 'end_time'.  The current time window is ({}, {}).".format(self.start_time, self.end_time))

        for trajectory in self.input:
            subset = geomath.subset_during_interval(trajectory,
                self.start_time,
                self.end_time)
            if len(subset) > 0:
                yield(subset)


# ----------------------------------------------------------------------

class FilterByBoundingBox(object):
    """FilterByBoundingBox: Eliminate trajectories that don't intersect a given box

    Given a source that produces Trajectories, return only those
    trajectories that intersect the specified bounding box.  No
    clipping or subsetting is performed: if at least one point is
    within the desired region you will get the entire trajectory back.

    Attributes:
      input (iterable): Sequence of Trajectory objects
      bbox_min (TrajectoryPoint):  Southwest corner of bounding box
      bbox_max (TrajectoryPoint): Northeast corner of bounding box
    """

    def __init__(self):
        """Initialize the filter with a bounding box that covers the whole world.
        """
        self.input = None
        self.box = None

    def trajectories(self):
        """Return just those trajectories that intersect the bounding box

        Yields:
          Trajectory objects with at least one point inside the bounding box
        """

        if self.box is None:
            logging.getLogger(__name__).warning(
                "FilterByBoundingBox: Box is not set.")

        for trajectory in self.input:
            if self.box is None:
                yield(trajectory)
            elif geomath.intersects(box, trajectory):
                yield(trajectory)


# ----------------------------------------------------------------------

class FilterByAltitude(object):
    """Filter out trajectories that don't intersect an interval of altitude

    Given a source that produces Trajectories, return only those
    trajectories that have at least one point between min_altitude and
    max_altitude.

    Like FilterByBoundingBox, no clipping will take place.  If a
    trajectory crosses the specified interval at all then you will get
    the whole thing back.

    Attributes:
       input (iterable): Iterable containing Trajectory objects
       min_altitude (float): Minimum altitude for acceptance
       max_altitude (float): Maximum altitude for acceptance

    """

    def __init__(self):
        """Initialize the filter with a bounding box that covers the whole
        world.
        """
        self.input = None
        self.min_altitude = None
        self.max_altitude = None

    def trajectories(self):
        """Return just the trajectories that intersect the bounding box

        Yields:
           Trajectory objects that fall within the altitude region
        """

        point_below = False
        point_above = False

        for trajectory in self.input:
            for point in trajectory:
                altitude = point.properties['altitude']

                if altitude >= self.min_altitude and altitude <= self.max_altitude:
                    yield(trajectory)
                else:
                    # If the trajectory has points below and above the
                    # interval then it must by definition intersect
                    # the interval.
                    if altitude < self.min_altitude:
                        point_below = True
                    if altitude > self.max_altitude:
                        point_above = True

                    if point_below and point_above:
                        yield(trajectory)
