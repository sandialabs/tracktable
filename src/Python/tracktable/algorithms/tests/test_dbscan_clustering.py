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

from __future__ import absolute_import, division, print_function

import operator
import random
import sys

from six.moves import range
from tracktable.algorithms.dbscan import (cluster_labels_to_dict,
                                          compute_cluster_labels)

# Test dbscan in 3 dimensions

def cluster_points_around(central_point, span, count):
    start_point = [ (c - 0.5 * d) for (c, d) in zip(central_point, span) ]

    delta = [ s / float(count-1) for s in span ]

    points = []

    for i in range(count):
        x = start_point[0] + i * delta[0]
        for j in range(count):
            y = start_point[1] + j * delta[1]
            for k in range(count):
                z = start_point[2] + k * delta[2]
                points.append((x, y, z))

    return points

# ----------------------------------------------------------------------

def place_corner_clusters():
    all_points = []

    corners = [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (0, 1, 1),
        (1, 1, 1)
        ]

    for corner in corners:
        all_points.extend(cluster_points_around(corner, (0.1, 0.1, 0.1), 8))

    return all_points

# ----------------------------------------------------------------------

def place_noise_points(center, span, count):
    all_points = []

    for point_id in range(count):
        x = random.uniform(center[0] - 0.5 * span[0], center[0] + 0.5 * span[0])
        y = random.uniform(center[1] - 0.5 * span[1], center[1] + 0.5 * span[1])
        z = random.uniform(center[2] - 0.5 * span[2], center[2] + 0.5 * span[2])
        all_points.append([x, y, z])

    return all_points

# ----------------------------------------------------------------------

def test_clusters():
    random.seed(0)

    print("Creating points")
    corner_points = place_corner_clusters()
    noise_points = place_noise_points([0.5, 0.5, 0.5], [10, 10, 10], 100)

    all_points = corner_points + noise_points

    vertex_ids_as_strings = [ str(i) for i in range(len(all_points)) ]
    decorated_points = list(zip(all_points, vertex_ids_as_strings))

    print("Learning cluster IDs for bare points.")
    int_cluster_ids = compute_cluster_labels(all_points,
                                             [0.05, 0.05, 0.05],
                                             4)

    print("Learning cluster IDs for decorated points.")
    string_cluster_ids = compute_cluster_labels(decorated_points,
                                                [0.05, 0.05, 0.05],
                                                4)

    recomputed_int_ids = [ (int(my_id), cluster_label) for (my_id, cluster_label) in string_cluster_ids ]

    sorted_int_ids = sorted(int_cluster_ids, key=operator.itemgetter(0))
    sorted_string_ids = sorted(recomputed_int_ids, key=operator.itemgetter(0))

    if (sorted_int_ids != sorted_string_ids):
        print("ERROR: Cluster IDs for bare points do not match cluster IDs for decorated points.")
        print("First 10 for bare points: {}".format(sorted_int_ids[0:10]))
        print("First 10 for decorated points (result): {}".format(sorted_string_ids[0:10]))
        return 1

    return 0
#    print("Cluster IDs: {}".format(cluster_ids))

# ----------------------------------------------------------------------

def test_cluster_dictionary():
    random.seed(0)

    print("Creating points")
    corner_points = place_corner_clusters()
    noise_points = place_noise_points([0.5, 0.5, 0.5], [10, 10, 10], 100)

    all_points = corner_points + noise_points

    vertex_ids_as_strings = [ str(i) for i in range(len(all_points)) ]
    decorated_points = list(zip(all_points, vertex_ids_as_strings))

    print("Learning cluster IDs for bare points.")
    int_cluster_ids = compute_cluster_labels(all_points,
                                             [0.05, 0.05, 0.05],
                                             4)

    bare_point_dict = cluster_labels_to_dict(int_cluster_ids, all_points)

    print("Learning cluster IDs for decorated points.")
    string_cluster_ids = compute_cluster_labels(decorated_points,
                                                [0.05, 0.05, 0.05],
                                                4)

    decorated_point_dict = cluster_labels_to_dict(string_cluster_ids, decorated_points)

    for (v_id, c_id) in int_cluster_ids:
        if str(c_id) not in bare_point_dict:
            print("ERROR: Cluster IDs for bare point not found in cluster dictionary as a key.")
            return 1
        vid_found = False
        for (fv, vec_id) in bare_point_dict[str(c_id)]:
            if v_id == vec_id:
                vid_found = True
                break
        if not vid_found:
            print("ERROR: Vector IDs for bare point not found in cluster dictionary as a value.")
            return 1

    for (v_id, c_id) in string_cluster_ids:
        if str(c_id) not in decorated_point_dict:
            print("ERROR: Cluster IDs for decorated point not found in cluster dictionary as a key.")
            return 1
        vid_found = False
        for (fv, vec_id) in decorated_point_dict[str(c_id)]:
            if v_id == vec_id:
                vid_found = True
                break
        if not vid_found:
            print("ERROR: Vector IDs for decorated point not found in cluster dictionary as a value.")
            return 1
    return 0

# ----------------------------------------------------------------------

def main():
    num_errors = test_clusters()
    num_errors += test_cluster_dictionary()
    return num_errors

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())



