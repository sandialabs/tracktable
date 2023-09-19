/*
 * Copyright (c) 2014-2023 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 * ComputeDBSCANClustering - Convenient driver functions for DBSCAN
 * ================================================================
 *
 * Overview
 * --------
 *
 * We have two goals here. First, give you a one-function interface
 * to DBSCAN: pass in a list of points, a search box and a minimum
 * cluster size, get back a vector of (vertex ID, cluster ID) labels.
 * Second, make it easy to say "These points are actually on the
 * surface of a sphere but I want you to pretend that they're in
 * Cartesian space."
 *
 * Rationale
 * ---------
 *
 * Our implementation of DBSCAN is templated on point type and uses
 * boost::geometry for all of its distance math. This means that it
 * will automatically adapt to whatever coordinate system you're using
 * for your points as long as Boost knows what to do with it.
 *
 * This is usually great. However, there are times when it will slow
 * you down tremendously. For example, if you're clustering a bunch
 * of points that are very close together on the surface of a sphere,
 * you might do just fine by pretending that the space is Cartesian
 * (flat) instead of spherical. That will run dramatically more
 * quickly and with greater precision than the trigonometry necessary
 * for doing distance computations on a sphere.
 */

#ifndef __tracktable_COMPUTE_DBSCAN_CLUSTERING_h
#define __tracktable_COMPUTE_DBSCAN_CLUSTERING_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Analysis/detail/dbscan_drivers.h>
#include <tracktable/Analysis/detail/point_converter.h>

#include <boost/iterator/transform_iterator.hpp>

#include <vector>
#include <map>

namespace tracktable {

/** Generate cluster labels for a set of points.
 *
 * This function runs DBSCAN on a list of points and returns its
 * results as a vector of integers, one for each input point.
 *
 * When you call `cluster_with_dbscan` you must indicate the type of
 * point (and thus the coordinate space) that you want to use for the
 * clustering. This lets you choose (for example) to run in Cartesian
 * space rather than longitude/latitude space if you're sure your
 * points don't run into the poles or the longitude discontinuity at
 * +/= 180.
 *
 * Example:
 *
 * @code
 *
 * typedef tracktable::cartesian2d::BasePoint point2d;
 * std::vector<tracktable::cartesian2d::BasePoint> my_points;
 * std::vector<std::pair<int, int>> cluster_labels;
 * point2d search_box(0.5, 0.5);
 * int min_cluster_size = 10;
 *
 *
 * int num_clusters = cluster_with_dbscan<point2d>(
 *    my_points.begin(),
 *    my_points.end(),
 *    search_box,
 *    min_cluster_size,
 *    std::back_inserter(cluster_labels)
 * );
 *
 * @endcode
 *
 * The search box must be specified in the coordinate system in which
 * you want to do the clustering.
 *
 * @param [in] input_begin   Iterator for beginning of input points
 * @param [in] input_end     Iterator for end of input points
 * @param [in] search_box_half_span  Distance defining "nearby" in all dimensions
 * @param [in] minimum_cluster_size  Minimum number of neighbors for core points
 * @param [out] output_sink  (Vertex ID, Cluster ID) for each point
 * @return Number of clusters discovered
 *
 * You can also pass in points as a `std::pair<MyPoint, Foo>` where Foo
 * is your own arbitrary ID. In that case, the returned labels will
 * be (Foo, int).
 */

template<class SearchBoxT, class PointIteratorT, class OutputIteratorT>
int cluster_with_dbscan(
  PointIteratorT input_begin,
  PointIteratorT input_end,
  SearchBoxT search_box_half_span,
  int minimum_cluster_size,
  OutputIteratorT output_sink
  )
{
  typedef typename PointIteratorT::value_type input_point_type;

  // Dispatch on the input point type will happen here so that we can
  // handle bare points or std::pair<metadata, point> instances.
  analysis::detail::DBSCAN_Driver<input_point_type> dbscan;

  int num_clusters = dbscan(
    input_begin,
    input_end,
    search_box_half_span,
    minimum_cluster_size,
    output_sink
    );

  return num_clusters;
}

/** Convert cluster labels into cluster membership lists
 *
 * The label output from `cluster_with_dbscan` is a list of (vertex_id,
 * cluster_id) pairs. It is often useful to have cluster membership
 * represented instead as lists of the vertices that belong to each
 * cluster. This function converts a list of IDs to a list of
 * members. The output will be saved as a sequence of `std::vector`s
 * written in order of ascending cluster ID.
 *
 * Example:
 *
 * @code
 * typedef std::pair<my_point, my_id> labeled_point_type;
 * tyepdef std::pair<my_id, int> cluster_label_type;
 * std::vector<labeled_point_type> my_labeled_points;
 * std::vector<cluster_label_type> cluster_labels;
 *
 * int num_clusters = tracktable::cluster_with_dbscan(
 *    my_labeled_points.begin(),
 *    my_labeled_points.end(),
 *    search_box,
 *    minimum_cluster_size,
 *    std::back_inserter(cluster_labels)
 * );
 *
 * typedef std::vector<my_id> cluster_member_list_type;
 * std::vector<cluster_member_list_type> membership_lists;
 *
 * tracktable::build_cluster_membership_lists(
 *   cluster_labels.begin(),
 *   cluster_labels.end(),
 *   std::back_inserter(membership_lists)
 * );
 * @endcode
 *
 * @param [in] label_begin   Iterator for beginning of DBSCAN cluster labels
 * @param [in] label_end     Iterator for end of DBSCAN cluster labels
 * @param [out] output_membership_lists  (Vertex ID, Cluster ID) for each point
 * @return Number of clusters discovered
 *
 */

template<typename ClusterLabelIteratorT, typename OutputIteratorT>
int build_cluster_membership_lists(
  ClusterLabelIteratorT label_begin,
  ClusterLabelIteratorT label_end,
  OutputIteratorT output_membership_lists
)
{
  typedef typename ClusterLabelIteratorT::value_type::first_type vertex_id_type;
  typedef std::vector<vertex_id_type> vertex_id_vector_type;
  typedef std::map<int, vertex_id_vector_type> member_map_type;

  member_map_type membership_lists;

  while (label_begin != label_end)
    {
    int cluster_id = label_begin->second;
    vertex_id_type vertex_id = label_begin->first;

    if (membership_lists.find(cluster_id) == membership_lists.end())
      {
      membership_lists[cluster_id] = vertex_id_vector_type();
      }
    membership_lists[cluster_id].push_back(vertex_id);
    ++label_begin;
    }

  // Since std::map keeps its contents sorted by the key (in this case
  // the cluster ID) we get them back in order here.
  for (typename member_map_type::const_iterator iter = membership_lists.begin();
       iter != membership_lists.end();
       ++iter)
    {
    *output_membership_lists = iter->second;
    ++output_membership_lists;
    }

  return boost::numeric_cast<int>(membership_lists.size());
}


} // exit namespace tracktable

#endif
