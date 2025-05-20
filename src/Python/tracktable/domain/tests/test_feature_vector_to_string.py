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

from __future__ import print_function, division, absolute_import

from six.moves import range
import logging
import sys

from tracktable.domain.feature_vectors import convert_to_feature_vector


def test_feature_vector_str(dimension):
    """Make sure that feature vector str() works as expected

    We expect str(my_feature_vector) to return a representation
    like '(1, 2, 3)'.

    Arguments:
        dimension {int}: How many components to give the feature vector

    Returns:
        0 on success, 1 on error (also prints an error message)
    """

    components = [x + 0.5 for x in range(dimension)]
    my_feature_vector = convert_to_feature_vector(components)

    expected_representation = '({})'.format(
        ', '.join([str(x) for x in components]))

    if expected_representation != str(my_feature_vector):
        logger = logging.getLogger(__name__)
        logger.error(
            ('Expected str(my_feature_vector) to be "'
             '{}" but got "{}" instead').format(
                 expected_representation,
                 str(my_feature_vector)))
        return 1
    else:
        return 0


def test_feature_vector_repr(dimension):
    """Make sure that feature vector repr() works as expected

    We expect repr(my_feature_vector) to return a representation
    like 'tracktable.domain.feature_vectors.FeatureVector3(1, 2, 3)'.

    Arguments:
        dimension {int}: How many components to give the feature vector

    Returns:
        0 on success, 1 on error (also prints an error message)
    """

    components = [x + 0.5 for x in range(dimension)]
    my_feature_vector = convert_to_feature_vector(components)

    expected_representation = (
        'tracktable.domain.feature_vectors.FeatureVector{}({})').format(
            dimension,
            ', '.join([str(x) for x in components]))

    if expected_representation != repr(my_feature_vector):
        logger = logging.getLogger(__name__)
        logger.error(
            ('Expected repr(my_feature_vector) to be "'
             '{}" but got "{}" instead').format(
                 expected_representation,
                 repr(my_feature_vector)))
        return 1
    else:
        return 0


def main():
    error_count = 0
    for i in range(1, 30):
        error_count += test_feature_vector_str(i)
        error_count += test_feature_vector_repr(i)
    return error_count


if __name__ == '__main__':
    sys.exit(main())
