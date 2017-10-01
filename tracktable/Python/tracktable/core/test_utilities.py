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

"""test_utilities - Functions to verify test output

Our Python tests typically create text files or images.  This module
contains functions that will let us easily verify that they match our
ground truth files, including computing differences where appropriate.
"""

from __future__ import print_function, division

from tracktable.core import tracktable_logging as tt_logging
from matplotlib.testing import compare as mpl_compare
import os.path

# useful constants for the rest of the world - the choice of NO_ERROR
# == 0 is so that we can return it to the shell and have it treated as
# a result code
NO_ERROR = 0
ERROR = 1

def log_test_output(*args, **kwargs):
    print(*args, **kwargs)

# ----------------------------------------------------------------------

def compare_images(expected, actual, tolerance=1):
    """Compare two images pixel-by-pixel.

    Args:
      image1 (str): Filename for image 1

      image2 (str): Filename for image 2

      tolerance (float): Number from 0 to 255 describing how much per-pixel difference is acceptable

    Returns:
      None if images compare equal, string explaining problem if images are different

    Note:
      At present we delegate this to Matplotlib's image comparison
      routine since it does all kinds of nice conversions and
      measurements.  We will bring this in-house if we ever need to.
    """

    return mpl_compare.compare_images(expected, actual, tol=tolerance)

# ----------------------------------------------------------------------

def compare_image_to_ground_truth(filename,
                                  ground_truth_dir,
                                  test_dir,
                                  tolerance=1):
    test_image_filename = os.path.join(test_dir, filename)
    expected_image_filename = os.path.join(ground_truth_dir, filename)

    result = compare_images(expected_image_filename,
                            test_image_filename,
                            tolerance=tolerance)

    if result is not None:
        tt_logging.log('error', result)
        return ERROR
    else:
        return NO_ERROR

