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
tracktable.algorithms.boxiness - Determine how close to a perfect square/box a trajectory is as well
as determining how much a trajectory zigzags.

calculate_boxiness(), sort_boxiness(), calculate_zigzaginess() and sort_by_zigzaginess()
are the main driver functions for determining boxiness or zigzaginess.

.. warning:: The calculate_zigzaginess() and sort_by_zigzaginess()
    functions may produce results that are not expected as this functions are
    not fully fleshed out.

The algorithm details for boxiness can be found in the Demo 2: Detecting "boxes" notebook.
"""

import logging
from math import floor

import matplotlib.pyplot as plt
from tracktable.core.geomath import bearing, distance, length, simplify

logger = logging.getLogger(__name__)

#TODO: Create a function to generate plots for the bearing histograms.

########################################################################
# BOXINESS
########################################################################

def calculate_boxiness(trajectories,
                  window=5,
                  simplify_trajectory=False,
                  error_tolerance=0.00001,
                  ignore_zero_degree_quartet=True):
    """
    Calculates a boxiness score for each trajectory and appends it as a
    property, to be accessed as trajectory.property['boxiness'].

    .. note:: In actuality, this score will be higher for trajectories that move
        primarily in four directions that are each nintey degrees apart, and
        this does not exclusively limit to boxes.

    Arguments:
        trajectories (list of Tracktable trajectories):
            We will score each of these trajectories for "boxiness" and store
            the score as a trajectory property.

    Keyword Arguments:
        window (Odd int): To account for imperfect boxes, we sum our quartet products over a
                window of this width (in degrees), centered at the peak quartet
                product. Note: Even integers will be rounded up to the nearest odd
                integer. (Default: 5)
        simplify_trajectory (bool): We can opt to smooth the trajectory using Tracktable's simplify
            function. This can help if we have particularly noisy data, but
            should be used with caution, as oversmoothing can lower the boxiness
            scores of true boxes. (Default: False)
        error_tolerance (float): The simplify function will not exceed this positional error tolerance,
            measured in the trajectory's native distance represented in km. (Default: 0.00001)
        ignore_zero_degree_quartet (bool): GPS rounding can cause trajectories that don't move to create a
            box-like pattern (since GPS point round to a grid). To ignore these,
            we can opt to ignore all boxes on the north-south-east-west grid.
            WARNING: This may delete non-GPS rounding boxes! (Default: True)

    """
    # allow input of single trajectories or lists
    if not isinstance(trajectories, list):
        trajectories = [trajectories]

    # For each trajectory, calculate boxiness and store it as a parameter.
    for trajectory in trajectories:
        boxiness = _calculate_boxiness_using_quartets(trajectory,
                                                window=window,
                                                simplify_trajectory=simplify_trajectory,
                                                error_tolerance=error_tolerance,
                                                ignore_zero_degree_quartet=ignore_zero_degree_quartet)
        trajectory.set_property('boxiness', boxiness)


def sort_by_boxiness(trajectories,
                     calculate_boxiness=True,
                     window=5,
                     simplify_trajectory=False,
                     error_tolerance=0.00001,
                     ignore_zero_degree_quartet=True):
    """
    Sorts a list of trajectories by boxiness.

    Before sorting, boxiness will be calculated for each trajectory and
    stored as a property (trajectory.properties['boxiness']). If boxiness
    has already been calculated and stored under properties, set
    calculate_boxiness to False to avoid unnecessary computation time.

    .. note:: This boxiness score will be higher for
        trajectories that move primarily in four directions that are each
        ninety degrees apart, and this does not exclusively limit to boxes.

    Arguments:
        trajectories (list of Tracktable trajectories): We will score each of
            these trajectories for "boxiness" and store the score as a trajectory property.

    Keyword Arguments:
        calculate_boxiness (bool):
            Calculates boxiness as stores it as a property for each trajectory
            (trajectory.properties['boxiness']). This property must be
            calculated and stored before the trajectories can be sorted.
            (Default: True)
        window (Odd int): To account for imperfect boxes, we sum our quartet products over a
            window of this width (in degrees), centered at the peak quartet
            product. Note: Even integers will be rounded up to the nearest odd
            integer. (Default: 5)
        simplify_trajectory (bool): We can opt to smooth the trajectory using Tracktable's simplify
            function. This can help if we have particularly noisy data, but
            should be used with caution, as oversmoothing can lower the boxiness
            scores of true boxes. (Default: False)
        error_tolerance (float): The simplify function will not exceed this
            positional error tolerance, measured in the trajectory's native distance
            represented in km. (Default: 0.00001)
        ignore_zero_degree_quartet (bool): GPS rounding can cause trajectories that don't move to create a
            box-like pattern (since GPS point round to a grid). To ignore these,
            we can opt to ignore all boxes on the north-south-east-west grid.
            WARNING: This may delete non-GPS rounding boxes! (Default: True)

    Returns:
        List of trajectories sorted based off of their boxiness score.

    """

    if calculate_boxiness:
        calculate_boxiness(trajectories,
                      window=window,
                      simplify_trajectory=simplify_trajectory,
                      error_tolerance=error_tolerance,
                      ignore_zero_degree_quartet=ignore_zero_degree_quartet)

    try:
        return sorted(trajectories,
                      key=lambda trajectory: trajectory.properties['boxiness'],
                      reverse=True)
    except:
        logger.error('Unable to sort trajectories by boxiness. If boxiness '
              'has not already been calculated for these '
              'trajectories, make sure to set '
              'calculate_boxiness=True.')

def calculate_bearings_histogram(trajectory,
                            scale_by_length=True,
                            normalize=True,
                            simplify_trajectory=False,
                            error_tolerance=0.00001):
    """
    Calculates a bearings histogram, which can use the usual binning method
    or bin by segment length, and can also be optionally normalized.

    Arguments:
        trajectory (Tracktable trajectory): The trajectory for which
            we will create a scaled relative bearings histogram.

    Keyword Arguments:
        scale_by_length (bool): If true, then instead of traditional bining (each bearing value counts
            as one), we add the length of the segment with the corresponding
            bearing to the bin. The histogram is normalized by dividing each bin
            by the length of the trajectory. (Default: True)
        normalize (bool): If true, will yield a relative histogram (bins sum to 1) instead of
            an absolute histogram. (Default: True)
        simplify_trajectory (bool): We can opt to smooth the trajectory using Tracktable's simplify
            function. This can help if we have particularly noisy data, but
            should be used with caution, as oversmoothing can lower the boxiness
            scores of true boxes. (Default: False)
        error_tolerance (float): The simplify function will not exceed this positional error tolerance,
            measured in the trajectory's native distance represeted in km. (Default: 0.00001)

    Returns:
        Relative histogram of bearings, where dict keys define bins and dict
        values are percentages in each bin. Keys are degrees 0 through 359
        (but will only exist for nonzero histogram values). Values are the
        sum of the length of every segment with this bearing (rounded to the
        nearest degree), divided by the length of the entire trajectory.
    """

    if normalize and scale_by_length:
        # Since we are adding the segment length to each histogram bin, we
        # normalize by the length of the entire trajectory.
        traj_length = length(trajectory)

        # For zero length trajectories, there are no bearings.
        if traj_length == 0:
            return {}

    elif normalize:
        normalization_term = 0

    if simplify_trajectory:
        trajectory = simplify(trajectory, error_tolerance)

    bearings_histogram = {}

    for i in range(len(trajectory)-1):
        this_point = trajectory[i]
        next_point = trajectory[i+1]
        # Calculate the bearing, rounded to the nearest degree.
        segment_bearing = round(bearing(this_point, next_point)) % 360
        if scale_by_length:
            # Add the length of the segment to the appropriate bin.
            value_to_bin = distance(this_point, next_point) / traj_length
        else:
            # Just add a count of one to the appropriate bin.
            value_to_bin = 1
            if normalize:
                normalization_term += 1
        bearings_histogram[segment_bearing] = (bearings_histogram.get(segment_bearing, 0)
                                               + value_to_bin)

    if normalize and not scale_by_length:
        bearings_histogram = {bearing: count / normalization_term
                              for (bearing, count) in bearings_histogram.items()}

    ##
    # Plotting Code
    ##
    # bearings_bins = list(bearings_histogram.keys())
    # bearings_counts = list(bearings_histogram.values())
    # fig = plt.figure(figsize=(20,10))
    # plt.bar(bearings_bins, bearings_counts, color='g')
    # plt.title('Histogram of Bearings Scaled by Length', fontsize=30)
    # plt.xlim(-5,364)
    # ax = fig.axes
    # ax[0].tick_params(labelsize=30)
    # plt.show()

    return bearings_histogram

def _calculate_boxiness_using_quartets(trajectory,
                                    window=5,
                                    simplify_trajectory=False,
                                    error_tolerance=0.00001,
                                    ignore_zero_degree_quartet=True):
    """ Utilizing quartest calculate the boxiness values for the given trajectory

    Arguments:
        trajectory (Tracktable trajectory): trajectory to score for "boxiness".

    Keyword Arguments:
        window (Odd int): To account for imperfect boxes, we sum our quartet products over a
            window of this width (in degrees), centered at the peak quartet
            product. Note: Even integers will be rounded up to the nearest odd
            integer. (Default: 5)
        simplify_trajectory (bool): We can opt to smooth the trajectory using Tracktable's simplify
            function. This can help if we have particularly noisy data, but
            should be used with caution, as oversmoothing can lower the boxiness
            scores of true boxes. (Default: False)
        error_tolerance (float): The simplify function will not exceed this positional error tolerance,
            measured in the trajectory's native distance represented in km. (Default: 0.00001)
        ignore_zero_degree_quartet (bool): GPS rounding can cause trajectories that don't move to create a
            box-like pattern (since GPS point round to a grid). To ignore these,
            we can opt to ignore all boxes on the north-south-east-west grid.
            WARNING: This may delete non-GPS rounding boxes! (Default: True)

    Returns:
        A "boxiness" score. In actuality, this score will be higher for
        trajectories that move primarily in four directions that are each
        nintey degrees apart. Note that this does not exclusively limit
        to boxes.
    """
    # Get {bins: percentages} for a relative histogram of the bearings, scaled
    # by segment length.
    bearings_histogram = calculate_bearings_histogram(trajectory,
                                                    scale_by_length=True,
                                                    normalize=True,
                                                    simplify_trajectory=simplify_trajectory,
                                                    error_tolerance=error_tolerance)

    # If there are no bearings, boxiness must be zero.
    if len(bearings_histogram) == 0:
        return 0

    # CALCULATE "QUARTETS" USING A MODIFIED CONVOLUTION TECHNIQUE

    quartet_products = {}

    # Quartets will range from 0-90-180-270 to 89-179-269-359.
    start_degrees_for_quartets = range(90)

    # In this loop we both calculate boxiness for each quartet and keep track
    # of the boxiest quartet.
    all_zero = True
    boxiest_quartet_degree = None
    for start_degree in start_degrees_for_quartets:
        if start_degree == 0 and ignore_zero_degree_quartet:
            # Ignoring 0-90-180-270 quartet to filter out GPS grid artifacts.
            quartet_products[0] = 0
            continue

        # For each quartet, multiple the four peaks to gauge how likely it is
        # that the trajectory makes a box at the quartet's orientation.
        quartet_prod = 1
        for i in range(0, 4):
            quartet_prod *= bearings_histogram.get(start_degree + 90*i, 0)

        # Only store nonzero quartet products.
        if quartet_prod > 0:
            all_zero = False
            # Keep track of the quartet with the largest product.
            if (boxiest_quartet_degree == None
                  or quartet_products[boxiest_quartet_degree] < quartet_prod):
                boxiest_quartet_degree = start_degree
            # Store all nonzero quartet products
            quartet_products[start_degree] = quartet_prod

    # CALCULATE "BOXINESS"

    # To improve computation speed, skip remaining calculation if there were
    # no positive quartets.
    if all_zero:
        return 0

    # How far left/right from the peak quartet should we sum?
    window_radius = floor(window/2)

    ##
    # Plotting Code
    ##
    # fig = plt.figure(figsize=(20,10))
    # # Plot every nonzero quartet product as a blue bar chart.
    # plt.bar(quartet_products.keys(),
    #         quartet_products.values(),
    #         color='b',
    #         label='all quartet products')
    # plt.title('Quartet Products', fontsize=30)
    # plt.xlabel('degree', fontsize=30)
    # # Make every quartet product used for the boxiness score red (window
    # # centered at the peak).
    # degrees_summed = [(boxiest_quartet_degree+i) % 90
    #                   for i in range(-window_radius, window_radius+1)]
    # degrees_summed = [degree for degree in degrees_summed
    #                   if degree in quartet_products.keys()]
    # plt.bar(degrees_summed,
    #         [quartet_products[degree] for degree in degrees_summed],
    #         color='r',
    #         label='quartet products that are summed for score')
    # # plot adjustments
    # plt.legend(fontsize=20)
    # plt.xlim(-5,95)
    # ax = fig.axes
    # ax[0].tick_params(labelsize=30)
    # plt.show()


    # Now that we know the peak boxiness quartet, calculate the boxiness
    # score using a window centered on that quartet degree.
    boxiness = 0
    for i in range(-window_radius, window_radius+1):
        boxiness += quartet_products.get((boxiest_quartet_degree+i) % 90, 0)

    # We normalize by dividing by boxiest possible score of (1/4)^4.
    return boxiness * 256

########################################################################
# ZIGZAGINESS
########################################################################

def calculate_zigzaginess(trajectories,
                        buffer=5):

    """
    Calculates a zigzaginess score for each trajectory and appends it as a
    property, to be accessed as trajectory.property['zigzaginess'].

    Arguments:
        trajectories (list of Tracktable trajectories):
            We will score each of these trajectories for "boxiness" and store
            the score as a trajectory property.

    Keyword Arguments:
        buffer (int): To account for imperfect zigzags, we need to buffer for a given number of degrees
            the calculation of the zigzaginess score. (Default: 5)

    """

    # allow input of single trajectories or lists
    if not isinstance(trajectories, list):
        trajectories = [trajectories]

    # For each trajectory, calculate zigzaginess and store it as a parameter.
    for trajectory in trajectories:
        zigzaginess = _calculate_zigzaginess_score(trajectory,
                                             buffer=buffer,
                                             penalize=True)
        trajectory.set_property('zigzaginess', zigzaginess)


def sort_by_zigzaginess(trajectories,
                        calculate_zigzaginess=True,
                        buffer=5):

    """
    Sorts a list of trajectories by zigzaginess.

    Before sorting, zigzaginess will be calculated for each trajectory and
    stored as a property (trajectory.properties['zigzaginess']). If zigzaginess
    has already been calculated and stored under properties, set
    calculate_zigzaginess to False to avoid unnecessary computation time.

    Arguments:
        trajectories (list of Tracktable trajectories): We will score each of
            these trajectories for "boxiness" and store the score as a trajectory property.

    Keyword Arguments:
        buffer (int): To account for imperfect zigzags, we need to buffer for a given number of degrees
            the calculation of the zigzaginess score. (Default: 5)
        calculate_zigzaginess (bool):
            Calculates zigzaginess as stores it as a property for each trajectory
            (trajectory.properties['zigzaginess']). This property must be
            calculated and stored before the trajectories can be sorted.
            (Default: True)

    Returns:
        List of trajectories sorted based off of their zigzaginess score

    """

    if calculate_zigzaginess:
        calculate_zigzaginess(trajectories,
                         buffer=buffer)

    try:
        return sorted(trajectories,
                      key=lambda trajectory: trajectory.properties['zigzaginess'],
                      reverse=True)
    except:
        logger.error('Unable to sort trajectories by zigzaginess. If zigzaginess '
              'has not already been calculated for these trajectories, make '
              'sure to set calculate_zigzaginess=True.')

def _calculate_zigzaginess_score(trajectory,
                           buffer=5,
                           penalize=True):

    """ Calculate the zigzaginess score of the given trajectory

    Arguments:
        trajectory (Tracktable trajectory): trajectory to score for "zigzaginess".

    Keyword Arguments:
        buffer (int): To account for imperfect zigzags, we need to buffer for a given number of degrees
            the calculation of the zigzaginess score. (Default: 5)
        penalize (bool): Flag to penalize all bearings outside of the two peaks to avoid
            biasing towards trajectories with more data points. (Default: True)

    Returns:
        A "zigzaginess" score.
    """

    window_radius = floor(buffer/2)

    # Get {bins: percentages} for a relative histogram of the bearings, scaled
    # by segment length.
    bearings_histogram = calculate_bearings_histogram(trajectory,
                                                 scale_by_length=False,
                                                 normalize=False)

    # account for GPS rounding anomalies (hacky fix)
    bearings_histogram[0] = 0
    bearings_histogram[90] = 0
    bearings_histogram[180] = 0
    bearings_histogram[270] = 0

    # If the trajectory doesn't move, or only moves in one direction,
    # it's not zigzagging.
    if len(bearings_histogram) <= 1:
        return 0

    sorted_histogram = sorted(bearings_histogram.items(),
                              key = lambda item: (item[1], item[0]),
                              reverse=True)

    logger.debug(sorted_histogram)

    # peaks = [[FIRST PEAK DEGREE, FIRST PEAK COUNT],
    #          [SECOND PEAK DEGREE, SECOND PEAK COUNT]]
    peaks = sorted_histogram[:2]

    #peak_degrees = [sorted_bins[0], sorted_bins[1]]

    # Find the next highest peak that is at least buffer degrees away, and
    # not too close to being just the opposite direction of the peak bearing.
    second_peak_found = False
    for possible_peak in sorted_histogram[2:]:
        distance_between_peaks = abs(peaks[0][0] - peaks[1][0])
        if buffer < distance_between_peaks and abs(distance_between_peaks - 180) > window_radius:
            second_peak_found = True
            break
        peaks[1] = possible_peak

    logger.debug(distance_between_peaks)

    # No second bearings peak means no zigzagging.
    if not second_peak_found:
        return 0

    # We'll add up the scores over a window of width <buffer> degrees centered
    # at each peak.
    peak_area = [0, 0]
    for i in range(-window_radius, window_radius+1):
        peak_area[0] += bearings_histogram.get(peaks[0][0] + i, 0)
        peak_area[1] += bearings_histogram.get(peaks[1][0] + i, 0)

    # Multiply the two peaks to score zigzaginess. A high score indicates
    # that the trajectory is moving in just these two directions, for the
    # most part.
    preliminary_score = peaks[0][1] * peaks[1][1]

    # We need to penalize for all bearings outside of the two peaks to avoid
    # biasing towards trajectories with more data points.
    penalty_score = 0
    if penalize:
        for degree, count in sorted_histogram[1:]:
            near_peak = False
            for i in range(-window_radius, window_radius+1):
                if ((peaks[0][0] + i) % 360 == degree or
                    (peaks[1][0] + i) % 360 == degree):
                    near_peak = True
                    break
            if not near_peak:
                penalty_score += count

    logger.debug(f'max peak: {peaks[0][0]}, {peaks[0][1]}')
    logger.debug(f'next peak: {peaks[1][0]}, {peaks[1][1]}')
    logger.debug(f'penalty score: {penalty_score}')

    return max(preliminary_score - penalty_score**2, 0)
