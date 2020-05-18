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

"""
tracktable.source.trajectory - Sources that turn a sequence of points into a sequence of trajectories
"""

import datetime
import logging

from tracktable.core.geomath import distance


class AssembleTrajectoryFromPoints(object):
    """Turn a sequence of points into a set of trajectories

    We begin with an input sequence of TrajectoryPoints sorted by
    increasing timestamp.  As we iterate over that sequence, we
    separate points by their object IDs and build up a new trajectory
    for each object ID.  When we see a gap of duration
    'separation_time' or distance 'separation_distance' between the
    previous and latest point for a given object ID, we package up the
    points so far, emit a new trajectory and use the latest point to
    start a new one.

    Attributes:
       input (iterable): Sequence of TrajectoryPoint objects sorted by timestamp
       separation_time (datetime.timedelta): Maximum permissible time
            difference between adjacent points in a trajectory
       separation_distance (float): Maximum permissible geographic
            distance (in KM) between adjacent points in a trajectory
       minimum_length (integer): Complete trajectories with fewer
            than this many points will be discarded

    Example:
       p_source = SomePointSource()
       (configure point source here)

       t_source = AssembleTrajectoryFromPoints()
       t_source.input = p_source.points()
       t_source.separation_time = datetime.timedelta(minutes=30)
       t_source.separation_distance = 100
       t_source.minimum_length = 10

       for trajectory in t_source.trajectories():
          (do whatever you want)

    """

    def __init__(self):
        """Initialize an assembler

        Separation time will be set to 30 minutes and separation
        distance will be set to infinity by default.  Trajectory
        minimum length will be set to 2.
        """

        self.input = None
        self.separation_time = datetime.timedelta(minutes=30)
        self.separation_distance = None
        self.minimum_length = 2
        self.points_processed_count = 0
        self.valid_trajectory_count = 0


    def trajectories(self):
        """Return trajectories assembled from input points.

        Once you have supplied a point source in the 'input' attribute
        (which can be any iterable but is commonly the output of a
        PointSource) you can call trajectories() to get an iterable of
        trajectories.  All the computation happens on demand so the
        execution time between getting one trajectory and getting the
        next one is unpredictable.

        There are only loose guarantees on the order in which
        trajectories become available.  Given trajectories A and B, if
        timestamp(A.end) < timestamp(B.end) then A will come up before
        B.

        The input sequence of trajectories will only be traversed
        once.

        Yields:
          Trajectories built from input points
        """

        logger = logging.getLogger(__name__ + "AssembleTrajectoryFromPoints")
        trajectory_class = None
        trajectories_in_progress = {}

        self.valid_trajectory_count = 0
        self.invalid_trajectory_count = 0
        self.points_processed_count = 0

        logger.info(("New trajectories will be declared after a separation "
                     "of {} distance units between two points or a time lapse "
                     "of at least {} (hours, minutes, seconds).").format(
                                  self.separation_distance,
                                  self.separation_time))
        logger.info(("Trajectories with fewer than {} points will "
                     "be discarded.").format(self.minimum_length))

        for point in self.input:
            self.points_processed_count += 1

            if trajectory_class is None:
                trajectory_class = point.domain_classes['Trajectory']

            object_id = point.object_id
            if object_id not in trajectories_in_progress:
                trajectories_in_progress[object_id] = [ point ]
            else:
                updates_so_far = trajectories_in_progress[object_id]
                time_since_last_update = point.timestamp - updates_so_far[-1].timestamp
                distance_since_last_update = distance(point, updates_so_far[-1])

                if ((self.separation_time and
                     time_since_last_update > self.separation_time)
                    or
                    (self.separation_distance and
                     distance_since_last_update > self.separation_distance)):

                    # We've passed our threshold for declaring a new
                    # trajectory
                    if len(updates_so_far) >= self.minimum_length:
                        new_trajectory = trajectory_class.from_position_list(updates_so_far)
                        self.valid_trajectory_count += 1
                        yield(new_trajectory)

                        if self.valid_trajectory_count > 0 and self.valid_trajectory_count % 100 == 0:
                            logger.debug(
                                ("(1) {} trajectories announced and {} "
                                 "discarded for having fewer than {} "
                                 "points").format(
                                     self.valid_trajectory_count,
                                     self.invalid_trajectory_count,
                                     self.minimum_length))
                    else:
                        self.invalid_trajectory_count += 1
                        if self.invalid_trajectory_count > 0 and self.invalid_trajectory_count % 100 == 0:
                            logger.debug(
                                ("(2) STATUS: {} trajectories announced and {} "
                                 "discarded for having fewer than {} "
                                 "points").format(
                                     self.valid_trajectory_count,
                                     self.invalid_trajectory_count,
                                     self.minimum_length))
                    trajectories_in_progress[object_id] = [ point ]

                else:
                    # This is a continuation of an existing trajectory
                    updates_so_far.append(point)

            # Every so often we need to go through and flush out
            # trajectories that are in progress.  We can only do this
            # if the user has supplied a split_threshold_time
            # parameter.
            #
            # TODO: Make this run based on the number of points
            # currently being stored rather than the number of
            # trajectories announced
            if self.valid_trajectory_count > 0 and self.valid_trajectory_count % 1000 == 0:
                if self.separation_time:
                    old_trajectories = trajectories_in_progress
                    trajectories_in_progress = dict()

                    now = point.timestamp
                    for (object_id, update_list) in old_trajectories.items():
                        if (now - update_list[-1].timestamp) > self.separation_time:
                            if len(update_list) >= self.minimum_length:
                                new_trajectory = trajectory_class.from_position_list(update_list)
                                self.valid_trajectory_count += 1
                                yield(new_trajectory)

                                if self.valid_trajectory_count > 0 and self.valid_trajectory_count % 100 == 0:
                                    logger.debug(
                                        ("(3) {} trajectories "
                                         "announced and {} discarded for "
                                         "having fewer than {} points").format(
                                            self.valid_trajectory_count,
                                            self.invalid_trajectory_count,
                                            self.minimum_length))
                            else:
                                self.invalid_trajectory_count += 1
                                if self.invalid_trajectory_count > 0 and self.invalid_trajectory_count % 100 == 0:
                                    logger.debug(
                                        ("(4) {} trajectories"
                                         "announced and {} discarded for "
                                         "having fewer than {} points").format(
                                             self.valid_trajectory_count,
                                             self.invalid_trajectory_count,
                                             self.minimum_length))

                        else:
                            trajectories_in_progress[object_id] = update_list

        # We've finished iterating over all the position updates in
        # the window.  Go through all the position updates we're still
        # hanging onto and make trajectories out of them.
        for (object_id, update_list) in trajectories_in_progress.items():
            if len(update_list) >= self.minimum_length:
                new_trajectory = trajectory_class.from_position_list(update_list)
                self.valid_trajectory_count += 1
                yield(new_trajectory)
                if self.valid_trajectory_count > 0 and self.valid_trajectory_count % 100 == 0:
                    logger.debug(
                        ("{} trajectories announced and {} discarded for "
                         "having fewer than {} points").format(
                            self.valid_trajectory_count,
                            self.invalid_trajectory_count,
                            self.minimum_length))
            else:
                self.invalid_trajectory_count += 1
                if self.invalid_trajectory_count > 0 and self.invalid_trajectory_count % 100 == 0:
                    logger.debug(
                        ("{} trajectories announced and {} discarded for "
                         "having fewer than {} points").format(
                             self.valid_trajectory_count,
                             self.invalid_trajectory_count,
                             self.minimum_length))


        logger.info(
            ("Done assembling trajectories.  {} trajectories produced and "
             "{} discarded for having fewer than {} points.").format(
                 self.valid_trajectory_count,
                 self.invalid_trajectory_count,
                 self.minimum_length))

        if self.valid_trajectory_count == 0:
            logger.warning(
                ("Perplexity: No trajectories produced.  Are you sure your "
                 "delimiters and your column assignments are correct?"))
        return


    def __iter__(self):
        return self.trajectories()
