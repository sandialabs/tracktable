#
# Copyright (c) 2014-2019 National Technology and Engineering
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

from __future__ import absolute_import, division, print_function

import datetime
import pickle
import sys

from tracktable.core.test_utilities import pickle_and_unpickle
from tracktable.domain.cartesian3d import TrajectoryPoint

def test_pickle():
    my_point = TrajectoryPoint()
    my_point[0] = 123.45
    my_point[1] = 456.78
    my_point[2] = 90.123

    my_point.object_id = "Cartesian3DTrajectoryPoint"
    my_point.timestamp = datetime.datetime.now()

    my_point.properties["my_int"] = 12345
    my_point.properties["my_float"] = 123.45
    my_point.properties["my_string"] = "Hello world!"
    my_point.properties["my_timestamp"] = datetime.datetime.now() + datetime.timedelta(hours=12)
    my_point.properties["my_none"] = None

    return pickle_and_unpickle(my_point)

def main():
    return test_pickle()

if __name__ == '__main__':
    sys.exit(main())
