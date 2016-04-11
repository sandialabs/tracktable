# Copyright (c) 2014, Sandia Corporation.
# All rights reserved.
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


import sys
import os.path
import traceback
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot
from tracktable.render.mapmaker import mapmaker
from tracktable.core import test_utilities

def test_map_for_airport(ground_truth_dir,
                         test_output_dir,
                         image_filename='MapForAirport.png'):

    pyplot.figure()
    (mymap, artists) = mapmaker(map_name='airport:ORD',
                                domain='terrestrial',
                                region_size=(400, 400),
                                land_color='#505050',
                                draw_coastlines=True)

    pyplot.savefig(os.path.join(test_output_dir, image_filename),
                   figsize=(4, 4), dpi=150)
    pyplot.close()
    return test_utilities.compare_image_to_ground_truth(image_filename,
                                                        ground_truth_dir,
                                                        test_output_dir)

# ----------------------------------------------------------------------

def test_conus_map(ground_truth_dir,
                   test_output_dir,
                   image_filename='ConusMap.png'):

    pyplot.figure()
    (mymap, artists) = mapmaker(map_name='conus', domain='terrestrial')
    pyplot.savefig(os.path.join(test_output_dir, image_filename),
                   figsize=(8, 8), dpi=150)
    pyplot.close()
    return test_utilities.compare_image_to_ground_truth(image_filename,
                                                        ground_truth_dir,
                                                        test_output_dir)

# ----------------------------------------------------------------------

def test_north_america_map(ground_truth_dir,
                           test_output_dir,
                           image_filename='NorthAmericaMap.png'):

    pyplot.figure()
    (mymap, artists) = mapmaker(domain='terrestrial',
                                map_name='north_america',
                                state_color='#FF8080',
                                country_color='#80FF80',
                                lonlat_color='#0000FF',
                                lonlat_linewidth=0.5)
    pyplot.savefig(os.path.join(test_output_dir, image_filename),
                   figsize=(8, 8), dpi=150)
    pyplot.close()

    return test_utilities.compare_image_to_ground_truth(image_filename,
                                                        ground_truth_dir,
                                                        test_output_dir)

# ----------------------------------------------------------------------

def test_europe_map(ground_truth_dir,
                    test_output_dir,
                    image_filename='EuropeMap.png'):

    pyplot.figure()
    (mymap, artists) = mapmaker(domain='terrestrial',
                                map_name='europe',
                                lonlat_linewidth=0.25,
                                lonlat_color='#6060FF')
    pyplot.savefig(os.path.join(test_output_dir, image_filename),
                   figsize=(8, 8), dpi=150)
    pyplot.close()

    return test_utilities.compare_image_to_ground_truth(image_filename,
                                                        ground_truth_dir,
                                                        test_output_dir)

# ----------------------------------------------------------------------

def test_mapmaker(ground_truth_path, test_output_path):

    status1 = test_map_for_airport(ground_truth_path, test_output_path)
    status2 = test_conus_map(ground_truth_path, test_output_path)
    status3 = test_north_america_map(ground_truth_path, test_output_path)
    status4 = test_europe_map(ground_truth_path, test_output_path)

    return sum([status1, status2, status3, status4])

# ----------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("usage: {} ground_truth_dir test_output_dir".format(sys.argv[0]))

    return test_mapmaker(sys.argv[1], sys.argv[2])

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
