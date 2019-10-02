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

from __future__ import print_function, division, absolute_import
from six.moves import range
from tracktable.lib import _feature_vector_points

POINT_TYPES = [ None,
                _feature_vector_points.FeatureVector1,
                _feature_vector_points.FeatureVector2,
                _feature_vector_points.FeatureVector3,
                _feature_vector_points.FeatureVector4,
                _feature_vector_points.FeatureVector5,
                _feature_vector_points.FeatureVector6,
                _feature_vector_points.FeatureVector7,
                _feature_vector_points.FeatureVector8,
                _feature_vector_points.FeatureVector9,

                _feature_vector_points.FeatureVector10,
                _feature_vector_points.FeatureVector11,
                _feature_vector_points.FeatureVector12,
                _feature_vector_points.FeatureVector13,
                _feature_vector_points.FeatureVector14,
                _feature_vector_points.FeatureVector15,
                _feature_vector_points.FeatureVector16,
                _feature_vector_points.FeatureVector17,
                _feature_vector_points.FeatureVector18,
                _feature_vector_points.FeatureVector19,

                _feature_vector_points.FeatureVector20,
                _feature_vector_points.FeatureVector21,
                _feature_vector_points.FeatureVector22,
                _feature_vector_points.FeatureVector23,
                _feature_vector_points.FeatureVector24,
                _feature_vector_points.FeatureVector25,
                _feature_vector_points.FeatureVector26,
                _feature_vector_points.FeatureVector27,
                _feature_vector_points.FeatureVector28,
                _feature_vector_points.FeatureVector29,
                _feature_vector_points.FeatureVector30
]

def convert_to_feature_vector(coords):
    """Turn a list of coordinates into a feature vector

    Args:
       coords: List, tuple or Tracktable point

    Returns:
       Appropriately sized tracktable.domain.feature_vector point with the same coordinates
    """

    if len(coords) == 0 or len(coords) >= len(POINT_TYPES):
        raise TypeError("Point must have between 1 and {} coordinates.".format(len(POINT_TYPES)))
    else:
        point = POINT_TYPES[len(coords)]()
        for i in range(len(coords)):
            point[i] = coords[i]
        return point
