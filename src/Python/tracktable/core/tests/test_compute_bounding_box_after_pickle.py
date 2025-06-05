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
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
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

# This test ensures that compute_bounding_box() still works after pickling
# and unpickling trajectories.
#

import datetime
import io
import logging
import math
import pickle
import sys

import tracktable.domain
from tracktable.core import geomath
from tracktable.feature.interpolated_points import TrajectoryPointSource
from tracktable.domain.terrestrial import Trajectory as TerrestrialTrajectory
from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint

def test_compute_bounding_box_after_pickle():
    error_count = 0

    albuquerque = TerrestrialTrajectoryPoint(-106.6504, 35.0844)
    albuquerque.timestamp = datetime.datetime(year=2020, month=1, day=1, hour=12)
    san_francisco = TerrestrialTrajectoryPoint( -122.4194, 37.7749)
    san_francisco.timestamp = albuquerque.timestamp + datetime.timedelta(hours=3)
    tokyo = TerrestrialTrajectoryPoint(-221.6917, 35.6895)
    tokyo.timestamp = albuquerque.timestamp + datetime.timedelta(hours=12)

    trajectory_generator = TrajectoryPointSource()
    trajectory_generator.start_point = albuquerque
    trajectory_generator.end_point = tokyo
    trajectory_generator.num_points = 20

    print("DEBUG: TerrestrialTrajectory: {}".format(TerrestrialTrajectory))
    albuquerque_to_tokyo = TerrestrialTrajectory.from_position_list(list(trajectory_generator.points()))

    expected_min_corner = tracktable.domain.domain_class_for_object(albuquerque, 'BasePoint')()
    expected_max_corner = tracktable.domain.domain_class_for_object(albuquerque, 'BasePoint')()

    expected_min_corner[0] = min(albuquerque[0], tokyo[0])
    expected_min_corner[1] = min(albuquerque[1], tokyo[1])
    expected_max_corner[0] = max(albuquerque[0], tokyo[0])
    expected_max_corner[1] = max(albuquerque[1], tokyo[1])

    bbox_before_pickling = geomath.compute_bounding_box(albuquerque_to_tokyo)

    store = io.BytesIO()
    pickle.dump(albuquerque_to_tokyo, store)
    store.seek(0)
    restored_trajectory = pickle.load(store)
    bbox_after_pickling = geomath.compute_bounding_box(restored_trajectory)

    print("Bounding box before pickling: ({} {}) - ({} {})".format(
        bbox_before_pickling.min_corner[0],
        bbox_before_pickling.min_corner[1],
        bbox_before_pickling.max_corner[0],
        bbox_before_pickling.max_corner[1]))
    print("Bounding box after pickling: ({} {}) - ({} {})".format(
        bbox_after_pickling.min_corner[0],
        bbox_after_pickling.min_corner[1],
        bbox_after_pickling.max_corner[0],
        bbox_after_pickling.max_corner[1]))

    bbox_min_delta = (bbox_after_pickling.min_corner[0] -
                      bbox_before_pickling.min_corner[0],
                      bbox_after_pickling.min_corner[1] -
                      bbox_before_pickling.min_corner[1])
    bbox_max_delta = (bbox_after_pickling.max_corner[0] -
                      bbox_before_pickling.max_corner[0],
                      bbox_after_pickling.max_corner[1] -
                      bbox_before_pickling.max_corner[1])

    if (math.fabs(bbox_min_delta[0]) > 0.01 or
            math.fabs(bbox_min_delta[1]) > 0.01 or
            math.fabs(bbox_max_delta[0]) > 0.01 or
            math.fabs(bbox_max_delta[1]) > 0.01):
        print(("ERROR: Expected delta between bounding box before and after "
               "pickling to be zero.  Delta for minimum corner is {}.  "
               "Delta for maximum corner is {}.").format(
               bbox_min_delta, bbox_max_delta))
        error_count += 1

    return error_count

# ----------------------------------------------------------------------


def main():
    return test_compute_bounding_box_after_pickle()

# ----------------------------------------------------------------------


if __name__ == '__main__':
    sys.exit(main())
