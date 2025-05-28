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

"""
tracktable.domain.rtree - Find points in boxes and nearest neighbors with an R-tree.
"""

from __future__ import absolute_import, division, print_function

from tracktable.domain.feature_vectors import convert_to_feature_vector
from tracktable.lib import _rtree


class RTree(object):

    def __init__(self, points=None):
        self._tree = None
        self._original_points = None
        self._feature_vector_length = None

        if points is not None:
            self.insert_points(points)

    @property
    def points(self):
        """Return the points currently held in the r-tree

        Note:
            This will return the points as originally supplied by
            the user, not the feature vectors that actually populate the
            tree.

        Returns: Sequence of points originally supplied
        """

        return self._original_points

    @points.setter
    def points(self, new_points):
        """Populate the r-tree with a new set of points

        You must supply points (points in space or feature vectors)
        with dimension between 1 and 30. A new R-tree will be
        initialized with copies of those points.

        Note:
            This version of the code does indeed copy the points. A
            future version might get around that.

        Args:
           new_points (list): List of points to use
        """

        if new_points != self._original_points:
            self._tree = None
            self._feature_vector_length = None
            self._original_points = None
            self._feature_vectors = None
            self.insert_points(new_points)

    # ----------------------------------------------------------------------

    def _setup_tree(self):
        rtree_class_name = 'rtree_{}'.format(self._feature_vector_length)
        tree_class = getattr(_rtree, rtree_class_name)
        self._tree = tree_class()

    # ----------------------------------------------------------------------

    def insert_point(self, point):
        """Add a single point to the R-tree.

        Arguments:
            point (array-like or FeatureVector): Point to add.  If this is
                not the first point added, it must have the same dimension
                as all previous points.

        Returns:
            No return value.

        Raises:
            ValueError: The point you have supplied has a different number
                of components than the points already in the tree.
        """

        if self._tree is None:
            self._feature_vector_length = len(point)
            self._original_points = []
            self._feature_vectors = []
            self._setup_tree()
        else:
            if len(point) != self._feature_vector_length:
                raise ValueError((
                    'New point with {} components cannot be added to an '
                    'R-tree whose points all have {} components.'
                    ).format(
                        len(point),
                        self._feature_vector_length
                    ))

        self._original_points.append(point)
        self._feature_vectors.append(convert_to_feature_vector(point))
        self._tree.insert_point(self._feature_vectors[-1])

    # --------------------------------------------------------------------

    def insert_points(self, points):
        """Add many points to the R-tree

        Arguments:
            points (sequence of points): Points to insert into the
                R-tree.
        """

        if self._tree is None:
            # Since the input sequence might be a generator or other
            # traverse-once-only sequence, we pick the first point and use
            # that to configure the tree, then insert the others as a batch.

            point_iter = iter(points)
            try:
                first_point = next(point_iter)
                self.insert_point(first_point)
            except StopIteration:
                # If we're here, the sequence was empty and there are
                # no points to insert.
                return

            # At this point the tree definitely exists and has one point
            # in it.  Insert the rest of the points as a batch.
            self.insert_points(point_iter)

        else:
            # The tree already exists and has at least one point in it.
            # Add the rest of the points as a batch.
            new_points = list(points)
            new_fv = [convert_to_feature_vector(p) for p in new_points]
            self._original_points.extend(new_points)
            self._feature_vectors.extend(new_fv)
            self._tree.insert_points(new_fv)

    # --------------------------------------------------------------------

    def find_nearest_neighbors(self, seed_point, num_neighbors):
        """Find points near a search point

        Finds the K nearest neighbors to a search point.

        Note:
            That if the search point is already present in the R-tree
            then it will be one of the results returned.

        Args:
           seed_point (Tracktable point): Point whose neighbors you want to find
           num_neighbors (int): How many neighbors to find

        Returns: Sequence of points originally supplied
        """
        return self._tree.find_nearest_neighbors(convert_to_feature_vector(seed_point),
                                                 num_neighbors)

    # ----------------------------------------------------------------------

    def find_points_in_box(self, min_corner, max_corner):
        """Find points inside a box

        Finds all of the points in a box between minimum
        and maximum corner points.

        Args:
           min_corner (Tracktable point): Minimum corner to bound the box
           max_corner (Tracktable point): Maximum corner to bound the box

        Returns: Sequence of points originally supplied
        """
        return self._tree.find_points_in_box(
            convert_to_feature_vector(min_corner),
            convert_to_feature_vector(max_corner)
            )

    # ----------------------------------------------------------------------

    def intersects(self, min_corner, max_corner):
        """Find points/objects that intersect a box

        Finds all of the points/objects that intersect a box between minimum
        and maximum corner points.

        Args:
           min_corner (Tracktable point): Minimum corner to bound the box
           max_corner (Tracktable point): Maximum corner to bound the box

        Returns: Sequence of points originally supplied
        """
        return self._tree.intersects(
            convert_to_feature_vector(min_corner),
            convert_to_feature_vector(max_corner)
            )

    def __len__(self):
        """Return the number of points in the tree

        No arguments.

        Returns:
            Number of points that have been added to the Rtree.
        """

        if self._tree is None:
            return 0
        else:
            return len(self._tree)

