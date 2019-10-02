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

"""Find points in boxes and nearest neighbors with an R-tree."""

from __future__ import division, print_function, absolute_import

from tracktable.lib import _rtree

from tracktable.domain.feature_vectors import convert_to_feature_vector

class RTree(object):

    def __init__(self, points=None):
        self._tree = None
        self._original_points = None

        if points is not None:
            self._original_points = points
            self._feature_vectors = [ convert_to_feature_vector(p) for p in points ]
            self._setup_tree()

    # ----------------------------------------------------------------------

    @property
    def points(self):
        """Return the points currently held in the r-tree

        Note: this will return the points as originally supplied by
        the user, not the feature vectors that actually populate the
        tree.

        Returns: Sequence of points originally supplied
        """


        return self._original_points

    @points.setter
    def points(self, new_points):
        """Populate the r-tree with a new set of points

        You must supply points (points in space or feature vectors)
        with dimension between 1 and 30.  A new R-tree will be
        initialized with copies of those points.

        NOTE: This version of the code does indeed copy the points.  A
        future version might get around that.

        Args:
           new_points: List of points to use
        """

        if new_points != self._original_points:
            self._original_points = list(new_points)
            self._feature_vectors = [ convert_to_feature_vector(p) for p in self._original_points ]
            self._setup_tree()

    # ----------------------------------------------------------------------

    def _setup_tree(self):
        point_size = len(self._feature_vectors[0])
        rtree_class_name = 'rtree_{}'.format(point_size)
        tree_class = getattr(_rtree, rtree_class_name)
        self._tree = tree_class()
        self._tree.points = self._feature_vectors

    # ----------------------------------------------------------------------

    def find_nearest_neighbors(self, seed_point, num_neighbors):
        return self._tree.find_nearest_neighbors(convert_to_feature_vector(seed_point),
                                                 num_neighbors)

    # ----------------------------------------------------------------------

    def find_points_in_box(self, min_corner, max_corner):
        return self._tree.find_points_in_box(
            convert_to_feature_vector(min_corner),
            convert_to_feature_vector(max_corner)
            )
