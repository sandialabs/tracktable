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

# Exercise str() and repr() for the base point class in all domains.

from __future__ import print_function, division

import sys

from tracktable.domain.terrestrial import BasePoint as TerrestrialBasePoint
from tracktable.domain.cartesian2d import BasePoint as Cartesian2DBasePoint
from tracktable.domain.cartesian3d import BasePoint as Cartesian3DBasePoint

import tracktable.domain.terrestrial
import tracktable.domain.cartesian2d
import tracktable.domain.cartesian3d


def matches_expected(expected_value, actual_value, test_name='unnamed test'):
    if expected_value != actual_value:
        print('Test "{}" failed: expected "{}", got "{}"'.format(
            test_name, expected_value, actual_value))
        return False
    else:
        return True


def test_str_output():
    error_count = 0

    point1 = TerrestrialBasePoint(1, 2)
    if not matches_expected('(1, 2)', str(point1),
                            test_name='str(TerrestrialBasePoint)'):
        error_count += 1

    point2 = Cartesian2DBasePoint(1, 2)
    if not matches_expected('(1, 2)', str(point2),
                            test_name='str(Cartesian2DBasePoint)'):
        error_count += 1

    point3 = Cartesian3DBasePoint(1, 2, 3)
    if not matches_expected('(1, 2, 3)', str(point3),
                            test_name='str(Cartesian3DBasePoint)'):
        error_count += 1

    return error_count


def test_repr_output():
    error_count = 0

    point1 = TerrestrialBasePoint(1, 2)
    if not matches_expected(
            'tracktable.domain.terrestrial.BasePoint(1, 2)',
            repr(point1),
            test_name='repr(TerrestrialBasePoint)'):
        error_count += 1

    point2 = Cartesian2DBasePoint(1, 2)
    if not matches_expected(
            'tracktable.domain.cartesian2d.BasePoint(1, 2)',
            repr(point2),
            test_name='repr(Cartesian2DBasePoint)'):
        error_count += 1

    point3 = Cartesian3DBasePoint(1, 2, 3)
    if not matches_expected(
            'tracktable.domain.cartesian3d.BasePoint(1, 2, 3)',
            repr(point3),
            test_name='repr(Cartesian3DBasePoint)'):
        error_count += 1

    return error_count


def test_repr_equality():
    error_count = 0

    point1 = TerrestrialBasePoint(1, 2)
    reconstituted_point1 = eval(repr(point1))
    if not matches_expected(point1, reconstituted_point1,
                            test_name='eval(repr(TerrestrialBasePoint))'):
        error_count += 1

    point2 = Cartesian2DBasePoint(1, 2)
    reconstituted_point2 = eval(repr(point2))
    if not matches_expected(point2, reconstituted_point2,
                            test_name='eval(repr(Cartesian2DBasePoint))'):
        error_count += 1

    point3 = Cartesian3DBasePoint(1, 2, 3)
    reconstituted_point3 = eval(repr(point3))
    if not matches_expected(point3, reconstituted_point3,
                            test_name='eval(repr(Cartesian3DBasePoint))'):
        error_count += 1

    return error_count


def main():
    total_error_count = test_str_output()
    total_error_count += test_repr_output()
    total_error_count += test_repr_equality()

    return total_error_count


if __name__ == '__main__':
    sys.exit(main())
