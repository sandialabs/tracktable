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
tracktable.applications.trajectory_splitter - Split trajectories that are idle for a
given amount of time in a given location radius. This is typically to prevent
analyzing trajectories of boats that are docked for long periods of time.

split_when_idle() is the main driver function for splitting trajectories.
"""

import logging
from math import floor

from tracktable.core.geomath import distance

logger = logging.getLogger(__name__)

def elapsed_seconds(point1, point2):
    """
    Calculate the time (in seconds) between two trajectory points.  Assumes
    that point1 is the earlier point.

    Arguments:
        point1 (Tracktable point): The eariler occurring trajectory point.
        point2 (Tracktable point): The later occurring trajectory point.

    Returns:
        The time that has elapsed from the first point to the second point,
        in seconds.

    """
    return (point2.timestamp - point1.timestamp).total_seconds()

# TODO: Does split_when_idle need to be domain-specific?
# Could it be easily generalized to handle trajectories from different domains?
def split_when_idle(trajectory,
                    idle_time_threshold=3600,
                    collocation_radius_threshold=0.2525,
                    min_points=10):
    """
    If over any subset of points the trajectory stays within an area of

    .. math::

        PI * collocation_radius_threshold^2,

    for at least idle_time_threshold seconds, call this an idle area.  Attempt
    to create new trajectories before and after the idle area, effectively
    deleting the idle area.

    Arguments:
        trajectory (Tracktable trajectory): The trajectory to split.

    Keyword Arguments:
        idle_time_threshold (int): Consider a trajectory area idle if it spends at least
            idle_time_threshold seconds in the same place.  (Default: 3600 (one hour))
        collocation_radius_threshold (float)
            Consider a trajectory area idle if it stays within an area of
            PI * collocation_radius_threshold^2 in terms of km.
            (Default: 0.2525 (creating an area threshold of approx. 0.2 km^2))
        min_points (int):
            The minimum number of points for a non-idle subinterval of the
            trajectory to become a new trajectory.  (Default: 10)

    Returns:
        A list of trajectories that are each subintervals of the input
        trajectory, and do not contain any idle regions (as defined by the
        input thresholds).

    """


    def _create_interval_list():
        """
        Divide the trajectory into adjacent intervals, necessarily overlapping
        only at the interval endpoints.  We will efficiently try to make each
        interval as large as possible, subject to the constraint that the
        duration of each interval must be <= half of the idle time threshold.

        There is one exception: The shortest interval in terms of points is
        exactly two points, meaning we might have some two point intervals
        that exceed half of the idle time threshold, but this does not affect
        the success of our algorithm later on.

        Each interval will be labeled as idle or not, using only the spacial
        threshold for now.  An interval will be considered idle if all points
        are within the collocation_radius_threshold of the first point in the
        interval.

        Ex: A trajectory with 100 points with idle_time_threshold = 3600
            seconds (1 hour) might be subdivided as follows:

            [0, 11]    20 minutes
            [11, 30]   11 minutes
            [30, 31]   45 minutes
            [31, 80]   29 minutes
            [80, 98]    2 minutes
            [98, 100]   3 minutes

            Note that all intervals containing more than two points are <=
            half of the time interval threshold = 3600/2 seconds = 30 minutes.
            The interval [30, 31] contains only two points, so is allowed to
            exceed 30 minutes.

        Inherited parameters:
            split_when_idle
                - trajectory
                - idle_time_threshold
                - collocation_radius_threshold
                - trajectory_duration

        Returns:
            No return value

        """

        def _create_interval():
            """
            Creates and returns a dictionary representing a subinterval of the
            trajectory that has duration <= half of the idle time threshold.

            Inherited parameters:
                split_when_idle
                    - trajectory
                    - collocation_radius_threshold
                _create_interval_list
                    - interval_start
                    - interval_end

            Returns:
                A dictionary representing a subinterval of the trajectory that
                has duration <= half of the idle time threshold.  It has the
                following key/value pairs:
                    'start': The trajectory point index of the start of the
                             interval.
                    'end': The trajectory point index of the end of the
                           interval.
                    'idle': boolean indicating whether the trajectories points
                            are all within collocation_radius_threshold of the
                            center point.
                    'center': Trajectory point index of the "center" point for
                              the interval, which is always initialized to the
                              same as the 'start' point index.

            """

            interval = {}

            interval['start'] = interval_start
            interval['end'] = interval_end

            # Determine if the interval is idle in space (ignore time
            # threshold for now).
            for index in range(interval_start+1, interval_end+1):
                    if (distance(trajectory[interval_start], trajectory[index])
                          >= collocation_radius_threshold):
                        # We found one point that is not close enough to the
                        # center of the interval, so we can label the entire
                        # interval as non-idle.
                        interval['idle'] = False
                        return interval

            # All points were close enough in space to the center of the
            # interval, so let's call this interval idle.
            interval['center'] = interval_start
            interval['idle'] = True
            return interval

        # We do not want our intervals to exceed this value in time.
        interval_duration_max = idle_time_threshold / 2

        # Calculate the proportion of the total duration that we want one
        # interval to occupy.
        interval_fraction_of_duration = (interval_duration_max
                                         / trajectory_duration)

        # This is an estimate of how far to jump to get from the start of an
        # interval to the end (one less than the interval width).  Our guess
        # would be exactly correct if all points are sampled at exactly the
        # same difference apart in time.  In essence, we want to move
        # interval_fraction_of_duration along the trajectory in time, but
        # we're going to settle for moving that fraction in terms of total
        # points, cause that's all we can do without another loop.
        estimated_interval_jump = max(floor((len(trajectory) - 1)
                                            * interval_fraction_of_duration),
                                      1)

        interval_list = []

        # Make a guess at what the first acceptable interval might be.
        interval_start = 0
        interval_end = estimated_interval_jump
        while interval_start < len(trajectory) - 1:
            logger.debug(f'Trying interval from {interval_start} to {interval_end}.')

            interval_duration = elapsed_seconds(trajectory[interval_start],
                                             trajectory[interval_end])
            if interval_duration <= interval_duration_max:
                logger.debug('\tGood interval (shorter than max duration).')
                # We have a good interval, label it as idle or not.
                interval_list.append(_create_interval())
                # Move to the next possible interval.
                interval_start = interval_end
                interval_end = min(interval_start + estimated_interval_jump,
                                   len(trajectory) - 1)
            else:
                if interval_end == interval_start + 1:
                    logger.debug('\tGood interval (just two points).')
                    # If we have a two point interval, it's okay if it's over
                    # the maximum interval duration.
                    interval_list.append(_create_interval())
                    # Move to the next possible interval.
                    interval_start = interval_end
                    interval_end = min(interval_start + estimated_interval_jump,
                                       len(trajectory) - 1)
                else:
                    # Our interval was not short enough in time, so let's make
                    # another educated guess for how much smaller to make the
                    # end of the interval.
                    interval_end = interval_start + max(floor((interval_end - interval_start)
                                                              * interval_duration_max
                                                              / interval_duration),
                                                        1)

        return interval_list


    def _add_interval_following_mobile_region():
        """
        The last interval was a mobile interval, meaning there is no currently
        defined idle region.

        If the current interval is mobile:

            Because the intervals are HALF of the idle time threshold, we know
            there cannot be an idle subinterval long enough in time to matter
            among the two mobile intervals, so we can just add mobile
            intervals onto the mobile region.

            NOTE: In the special case where the interval is exactly two points
            whose duration is more than half of the idle time threshold, we
            know the two points are farther than collocation_radius_threshold
            apart, so it is still impossible for an idle subinterval to form.

        If the current interval is idle:

            We shift points from the end of our last mobile interval to this
            new idle region if that's where they actually belong.

        Inherited parameters:
            split_when_idle
                - idle_region
                - mobile_region
                - interval

        Returns:
            No return value.

        """
        if interval['idle']:
            # The current interval is idle, and there is no current idle
            # region, so make this interval the idle region
            idle_region['start'] = interval['start']
            idle_region['end'] = interval['end']
            idle_region['center'] = interval['center']
            # Go back into the mobile region and shift points from the end of
            # the mobile region into the start of the idle region as
            # appropriate.
            for index in range(mobile_region['end']-1,
                               mobile_region['start'], -1):
                if not _update_idle_region_with_point(index, 'start'):
                    mobile_region['end'] = index + 1
                    break
        else:
            # The current interval is mobile, so append it to the mobile
            # region.
            mobile_region['end'] = interval['end']


    def _add_interval_following_idle_region():
        """
        The last interval was an idle interval, so there is a currently
        defined idle region and possibly a mobile region.

        If the current interval is idle:

            Check to see if it fits entirely within the idle region.  This is
            a quick check that checks a sufficient but not necessary
            condition.

            If the check fails, try to add points one at a time from the
            current idle interval to the idle region.  When we find a point
            that is too far from the idle region, check the duration of the
            idle region and either delete it or move it to the mobile region.
            If we deleted the idle region, make the mobile region into a
            new trajectory and delete the mobile region.  Make the remaining
            points of the current idle interval the new idle region.

        If the current interval is mobile:

            Add points from the start of the current mobile interval to the
            idle region if they belong there.  Then check the duration of the
            idle region and either delete it or move it to the mobile region.
            If we deleted the idle region, make the old mobile region into a
            new trajectory.  Make the remaining points of the current mobile
            interval into the new mobile region.

        Inherited parameters:
            split_when_idle
                - idle_region
                - mobile_region
                - interval

        Returns:
            No return value.

        """
        # Either the interval is mobile, or it is idle but failed to be
        # quickly added to the idle region.

        # Add points from the start of the current interval to the end of
        # the idle region until they get too far from the center of the
        # idle region.
        for index in range(interval['start']+1, interval['end']+1):
            if not _update_idle_region_with_point(index, 'end'):
                break

        # Check if any part of the current interval wasn't added to the
        # idle region.
        if idle_region['end'] != interval['end']:
            # Check if the duration of the idle region is over the idle
            # time threshold and either delete the idle region or add it
            # to the mobile region.
            _check_idle_duration()
            if interval['idle']:
                # What is left of the current idle interval becomes the
                # new idle region.
                idle_region['start'] = index - 1
                idle_region['end'] = interval['end']
                idle_region['center'] = index - 1
            else:
                # What is left of the current mobile interval gets added
                # to the mobile region.
                if len(mobile_region) == 0:
                    mobile_region['start'] = index - 1
                    mobile_region['end'] = interval['end']
                else:
                    mobile_region['end'] = interval['end']


    def _update_idle_region_with_point(index, location):
        """
        Add a point to the idle region, but only if it is close enough to the
        center of the idle region.

        Inherited parameters:
            split_when_idle
                - trajectory
                - collocation_radius_threshold
                - idle_region

        Arguments:
            index : int
                The trajectory point index that we would like to attempt to add to
                the idle region.
            location : string
                Either 'start' or 'end' to indicate if we are adding this point to
                the start or end of the idle region, respectively.

        Returns:
            True - point was successfully added to the idle region
            False - point was not close enough to the center of the idle
                    region, and therefore was not added

        """
        # Check to see if the point is close enough to the center of the idle
        # region.
        if (distance(trajectory[idle_region['center']], trajectory[index])
              >= collocation_radius_threshold):
            return False

        # Update the idle region at either the beginning or end with the new
        # point.
        idle_region[location] = index
        return True


    def _cut_mobile_region():
        """
        Check to see if there is a mobile region and if it has enough points.
        If so, create a new trajectory from the mobile region and append it to
        our list of new trajectories.  Then clear the mobile region.

        Inherited parameters:
            split_when_idle
                - trajectory
                - min_points
                - mobile_region
                - new_trajectories

        Returns:
            No return value.

        """
        # Check that the mobile region exists and has enough points to be
        # considered its own trajectory.
        if (len(mobile_region) != 0 and
              mobile_region['end'] - mobile_region['start'] + 1 >= min_points):

            logger.debug(f"\tCreating new trajectory for [{mobile_region['start']}, {mobile_region['end']}]")

            # Create a trajectory from the mobile region.
            new_trajectories.append(trajectory[mobile_region['start']:
                                               mobile_region['end']+1])
        # Reset the mobile region.
        mobile_region.clear()


    def _check_idle_duration():
        """
        If the idle region duration is at or above the idle time threshold,
        convert the mobile region (if it exists) to a trajectory and clear the
        idle region.

        If the idle region duration is below the idle time threshold, move all
        points from the idle region to the mobile region and clear the idle
        region.

        Inherited parameters:
            split_when_idle
                - trajectory
                - idle_time_threshold
                - idle_region
                - mobile_region

        Returns:
            No return value.

        """
        if elapsed_seconds(trajectory[idle_region['start']],
                        trajectory[idle_region['end']]) >= idle_time_threshold:
            # The idle region is too long (in time).  Let all the mobile
            # region points from before the idle region form a new trajectory.
            _cut_mobile_region()
        else:
            # The idle region is not long enough (in time) to be considered
            # truly idle.  Move those points to the mobile region.
            if len(mobile_region) == 0:
                mobile_region['start'] = idle_region['start']
            mobile_region['end'] = idle_region['end']

        # Reset the idle region.
        idle_region.clear()

    logger.debug('Commencing trajectory splitting...')

    trajectory_duration = elapsed_seconds(trajectory[0], trajectory[-1])

    # If the entire trajectory is below the idle time threshold, there can be
    # no part of it that is idle for the duration of the idle time threshold,
    # so skip straight to keeping or deleting it depending on if it has
    # enough data points.
    if trajectory_duration < idle_time_threshold:
        if len(trajectory) >= min_points:
            return [trajectory]
        else:
            return []

    logger.debug('Creating Interval Lists...')

    # Create a list that will contain the trajectory broken up into intervals.
    # Each interval will be represented as a dictionary containing the
    # following keys: 'start' (trajectory point index of the start of the
    # interval), 'end' (trajectory point index of the end of the interval),
    # 'idle' (boolean flag), 'center' (this key only exists if 'idle' is true,
    # and contains the trajectory point index of the "center" of the interval,
    # where all idle radius are calculated from).
    interval_list = _create_interval_list()

    # We will store all non-idle trajectories that we create here (if any).
    new_trajectories = []

    # The idle region will be a dictionary similar to the interval
    # dictionaries, containing the 'start', 'end' and 'center' trajectory
    # point indices for the idle region.  The mobile region is similar but
    # need only contain 'start' and 'end' keys.
    idle_region    = {}
    mobile_region  = {}

    logger.debug('Initializing mobile/idle regions using first interval...')

    # Intialize mobile/idle regions using the first interval.
    if interval_list[0]['idle']:
        idle_region    = interval_list[0].copy()
    else:
        mobile_region  = interval_list[0].copy()

    for i, interval in enumerate(interval_list[1:]):

        logger.debug(f"\tmobile region: {mobile_region}")
        logger.debug(f"\tidle region: {idle_region}")
        logger.debug(f"\nInterval: [{interval['start']}, {interval['end']}]\t Idle: {interval['idle']}")

        if len(idle_region) == 0:
            _add_interval_following_mobile_region()
        else:
            _add_interval_following_idle_region()

    logger.debug(f"\tmobile region: {mobile_region}")
    logger.debug(f"\tidle region: {idle_region}")
    logger.debug(f"\nNo intervals left.  Checking idle region then cutting mobile region...")

    if len(idle_region) != 0:
        # There may be some idle points that should be moved to the mobile
        # region.
        _check_idle_duration()

    # We're done adding points, so any points left in the mobile region
    # should be checked to see if they qualify to be a trajectory.
    _cut_mobile_region()

    logger.debug(f"\tmobile region: {mobile_region}")
    logger.debug(f"\tidle region: {idle_region}")

    return new_trajectories
