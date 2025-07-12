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

from __future__  import print_function, division

import sys

from tracktable.domain.terrestrial import BasePoint as TerrestrialBasePoint
from tracktable.domain.cartesian2d import BasePoint as Cartesian2DBasePoint
from tracktable.domain.cartesian3d import BasePoint as Cartesian3DBasePoint

def test_constructors():

    print("Testing empty (default) constructors")
    point1 = TerrestrialBasePoint()
    point2 = Cartesian2DBasePoint()
    point3 = Cartesian3DBasePoint()

    print("Testing explicit coordinate constructors")
    point1 = TerrestrialBasePoint(1, 2)
    assert(point1[0] == 1)
    assert(point1[1] == 2)

    point2 = Cartesian2DBasePoint(1, 2)
    assert(point2[0] == 1)
    assert(point2[1] == 2)

    point3 = Cartesian3DBasePoint(1, 2, 3)
    assert(point3[0] == 1)
    assert(point3[1] == 2)
    assert(point3[2] == 3)

    print("Testing coordinates-from-list constructors")
    point1 = TerrestrialBasePoint([1, 2])
    assert(point1[0] == 1)
    assert(point1[1] == 2)

    point2 = Cartesian2DBasePoint([1, 2])
    assert(point2[0] == 1)
    assert(point2[1] == 2)

    point3 = Cartesian3DBasePoint([1, 2, 3])
    assert(point3[0] == 1)
    assert(point3[1] == 2)
    assert(point3[2] == 3)

