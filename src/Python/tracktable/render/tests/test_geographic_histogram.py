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


# Use a back end for matplotlib that does not require access to a
# windowing system
import matplotlib
matplotlib.use('Agg')

import sys
import traceback
from tracktable.source.random_point_source import UniformRandomPointSource
from tracktable.render.histogram2d import geographic_with_existing_map as geographic_histogram
from mpl_toolkits.basemap import Basemap

from matplotlib import pyplot
from matplotlib import colors

def test_geographic_histogram():
    tropics = UniformRandomPointSource()
    tropics.num_points = 100000
    tropics.bbox_min = ( -180, -23.4378 )
    tropics.bbox_max = ( 180, 23.4378 )

    try:
        pyplot.figure()
        pyplot.subplot(111, aspect='equal')

        mymap = Basemap(projection='moll',
                        lon_0=0,
                        resolution='l')
        mymap.drawcoastlines(color='white', zorder=5)
        mymap.fillcontinents(color='black', lake_color='white')

        artists = geographic_histogram( mymap,
                                        tropics.points(),
                                        bbox_lowerleft=(-180, -90),
                                        bbox_upperright=(180, 90)
                                        )

        pyplot.savefig('tracktable_geographic_histogram_test.png', figsize=(4, 4), dpi=150)
        return True
    except Exception as e:
        traceback.print_exc()
        return False

# ----------------------------------------------------------------------

def main():
    status = test_geographic_histogram()
    if status:
        return 0
    else:
        return 1

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
