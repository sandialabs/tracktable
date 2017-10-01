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
from tracktable.core.geomath import travel_from_point, radians, km_to_radians, radians_to_km, distance_between_points
from tracktable.core import geomath


def run_test():
    albuquerque = ( -106.61, 35.1107 )
    livermore = ( -121.7681, 37.6819 )

    # The great-circle distance between these two points is
    # 1385 km. 
    distance_to_travel = 1385
    bearing = 286.3469

    hopefully_livermore = travel_from_point(albuquerque, bearing, distance_to_travel)

    distance_to_destination = geomath.distance_between_points(livermore, hopefully_livermore)

    print("INFO: test_travel: Distance is {} and bearing is {}.".format(distance_to_travel, bearing))
    print("INFO: test_travel: Distance to destination after travel is {} km.".format(distance_to_destination))

    if distance_to_destination > 10:
        print("ERROR: test_travel: Computed destination is {} but should have been {}.  The distance between them is {} km.".format(hopefully_livermore, livermore, distance_to_destination))
        return 1
    else:
        return 0

if __name__ == '__main__':
    sys.exit(run_test())
