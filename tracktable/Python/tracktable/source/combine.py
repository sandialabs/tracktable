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
#

import heapq

# ----------------------------------------------------------------------

def interleave_points_by_timestamp(*point_sources):
    """From a series of point sources, generate a new sequence sorted by timestamp.

    Given one or more point sources that are themselves sorted by
    timestamp, generate a new sequence containing all of the points
    from all sources, again sorted by increasing timestamp.

    Note that this function reads all the points into memory in order
    to build a priority queue.  If you're feeling ambitious, feel free
    to write a new version that keeps only a single point in memory
    from each source at any time.

    Args:
       *point_sources (iterables): One or more iterables of points

    Yields:
       TrajectoryPoint instances sorted by increasing timestamp

    """

    def item_with_timestamp(point_iter):
        for point in point_iter:
            yield (point.timestamp, point)

    sources_with_timestamps = [ item_with_timestamp(source) for source in point_sources ]

    def strip_timestamps(all_points):
        for time_plus_point in all_points:
            yield (time_plus_point[1])

    return strip_timestamps(heapq.merge(*sources_with_timestamps))
