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

import sys
import traceback

from tracktable.source.scatter import uniform
from tracktable.render import histogram2d
from tracktable.domain.terrestrial import BasePoint, BoundingBox
from tracktable.render.mapmaker import mapmaker
from tracktable.source.point import random_box_uniform

from matplotlib import pyplot
from matplotlib import colors

def test_geographic_histogram(outfilename):
    min_corner = BasePoint(-180, -23.4378)
    max_corner = BasePoint(180, 23.4378)
    bbox = BoundingBox(min_corner, max_corner)
    num_points = 100000

    points_in_tropics = random_box_uniform(min_corner, max_corner, num_points)


    pyplot.figure()
    pyplot.subplot(111, aspect='equal')

    mymap = mapmaker(domain='terrestrial', map_name='region:world')

    histogram2d.render_histogram(map_projection=mymap,
                                 point_source=points_in_tropics,
                                 bounding_box=bbox,
                                 bin_size=0.5,
                                 colormap='gist_heat',
                                 colorscale=matplotlib.colors.LogNorm())
    pyplot.savefig(outfilename, figsize=(4, 4), dpi=150)
    return True

# ----------------------------------------------------------------------

def main():
    status = test_geographic_histogram(sys.argv[1])
    if status:
        return 0
    else:
        return 1

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
