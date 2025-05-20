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

from __future__ import division, print_function, absolute_import
import sys

import tracktable.domain.cartesian2d
import tracktable.domain.cartesian3d
import tracktable.domain.terrestrial

from logging import getLogger

def retrieve_classes_for_domain(domain_name):
    """retrieve_classes_for_domain(domain_name: string) -> list of classes

    Retrieve the classes for a given point domain.  Rather than maintain
    5 imports for 3 domains, we'll use this function to look up a class
    by its name.

    Args:
        domain_name [string]: one of "terrestrial", "cartesian2d",
            "cartesian3d"

    Returns:
        List of classes for that domain: BasePoint, TrajectoryPoint,
            LineString, Trajectory, BoundingBox
    """


    classes = []
    domain = getattr(tracktable.domain, domain_name)
    for class_name in [
          "BasePoint", "TrajectoryPoint", "Trajectory", "BoundingBox"
          ]:
        classes.append(getattr(domain, class_name))

    return classes


def check_domain_name(_class, expected_name):
    """check_domain_name(_class, expected_name) -> int

    Test the domain property of a class to make sure it
    matches what we expect.  The domain property reflects
    the value of the C++ trait tracktable::domain::<domain>::
    <class>::point_domain_name.

    Args:
        _class [class object]: Class to instantiate
        expected_name [string]: Expected value for the 'domain' property

    Returns:
        0 if _class().domain matches the expected name, 1 otherwise.
    """

    instance = _class()
    if instance.domain != expected_name:
        getLogger(__name__).error(
            "Class {}: expected domain '{}', got '{}'".format(
                _class, expected_name, instance.domain
            ))
        return 1
    else:
        return 0


def main():
    num_errors = 0
    for domain_name in ["terrestrial", "cartesian2d", "cartesian3d"]:
        for domain_class in retrieve_classes_for_domain(domain_name):
            num_errors += check_domain_name(domain_class, domain_name)
    return num_errors


if __name__ == '__main__':
    sys.exit(main())
