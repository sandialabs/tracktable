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


# Use a back end for matplotlib that does not require access to a
# windowing system
import matplotlib
matplotlib.use('Agg')

import os.path
import sys
from tracktable.source.random_point_source import NormalRandomPointSource
from tracktable.render.histogram2d import cartesian as cartesian_histogram
from tracktable.core import test_utilities

from matplotlib import (pyplot, colors)

def test_cartesian_histogram(output_dir, ground_truth_dir):
    point_source = NormalRandomPointSource()
    point_source.num_points = 100000

    pyplot.figure()
    pyplot.subplot(111, aspect='equal', facecolor='black')

    artists = cartesian_histogram(point_source.points(),
                                  bbox_lowerleft=[-5, -5],
                                  bbox_upperright=[5, 5],
                                  colorscale=colors.LogNorm())
    outfilename = os.path.join(output_dir, 'cartesian_histogram.png')
    pyplot.savefig(outfilename, figsize=(4, 4), dpi=150)

    ground_truth_filename = os.path.join(ground_truth_dir, 'cartesian_histogram.png')

    compare_result = test_utilities.compare_images(ground_truth_filename,
                                                   outfilename)

    if compare_result is not None:
        test_utilities.log_test_output("Testing Cartesian histogram: images differ!")
        test_utilities.log_test_output(compare_result)
        return 1
    else:
        test_utilities.log_test_output("Testing Cartesian histogram: Images are identical.  Test passed.")
        return 0

# ----------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("usage: {} test_output_dir ground_truth_dir".format(sys.argv[0]))
        return 1

    test_output_directory = sys.argv[1]
    ground_truth_directory = sys.argv[2]

    status = test_cartesian_histogram(test_output_directory, ground_truth_directory)
    return status


# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
