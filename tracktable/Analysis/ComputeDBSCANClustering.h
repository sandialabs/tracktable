/*
 * Copyright (c) 2014, Sandia Corporation.  All rights
 * reserved.
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
 * We have two goals here.  First, give you a one-function interface
 * to DBSCAN: pass in a list of points, a search box and a minimum
 * cluster size, get back a vector of cluster labels.  Second, make it
 * easy to say "These points are actually on the surface of a sphere
 * but I want you to pretend that they're in Cartesian space."
 *
 * Rationale
 * ---------
 *
 * Our implementation of DBSCAN is templated on point type and uses
 * boost::geometry for all of its distance math.  This means that it
 * will automatically adapt to whatever coordinate system you're using
 * for your points as long as Boost knows what to do with it.
 *
 * This is usually great.  However, there are times when it will slow
 * you down tremendously.  For example, if you're clustering a bunch
 * of points that are very close together on the surface of a sphere,
 * you might do just fine by pretending that the space is Cartesian
 * (flat) instead of spherical.  That will run dramatically more
 * quickly and with greater precision than the trigonometry necessary
 * for doing distance computations on a sphere.
 */

#ifndef __tracktable_COMPUTE_DBSCAN_CLUSTERING_h
#define __tracktable_COMPUTE_DBSCAN_CLUSTERING_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Analysis/DBSCAN.h>
#include <tracktable/Analysis/detail/point_converter.h>

#include <boost/iterator/transform_iterator.hpp>

#include <vector>


namespace tracktable {

/** Generate cluster labels for a set of points.
 *
 * This function runs DBSCAN on a list of points and returns its
 * results as a vector of integers, one for each input point.
 *
 * When you call cluster_with_dbscan you must indicate the type of
 * point (and thus the coordinate space) that you want to use for the
 * clustering.  This lets you choose (for example) to run in Cartesian
 * space rather than longitude/latitude space if you're sure your
 * points don't run into the poles or the longitude discontinuity at
 * +/= 180.
 *
 * Here's an example::
 *
 * typedef tracktable::cartesian2d::BasePoint point2d;
 * std::vector<tracktable::cartesian2d::BasePoint> my_points;
 * std::vector<int> cluster_labels;
 * point2d search_box(0.5, 0.5);
 * int min_cluster_size = 10;
 *
 *
 * int num_clusters = cluster_with_dbscan<point2d>(
 *    my_points.begin(),
 *    my_points.end(),
 *    search_box,
 *    min_cluster_size,
 *    cluster_labels
 * );
 *
 * The search box must be specified in the coordinate system in which
 * you want to do the clustering.
 *
 * @param[in] input_begin   Iterator for beginning of input points
 * @param[in] input_end     Iterator for end of input points
 * @param[in] search_box_half_span  Distance defining "nearby" in all dimensions
 * @param[in] minimum_cluster_size  Minimum number of neighbors for core points
 * @param[out] output_cluster_labels  Cluster ID for each point
 * @return Number of clusters discovered
 */

template<class ClusterSpacePointT, class PointIteratorT>
int cluster_with_dbscan(
  PointIteratorT       input_begin,
  PointIteratorT       input_end,
  ClusterSpacePointT   search_box_half_span,
  int                  minimum_cluster_size,
  std::vector<int>&    output_cluster_labels
  )
{
  typedef typename PointIteratorT::value_type input_point_type;
  typedef ClusterSpacePointT cluster_point_type;

  typedef detail::PointConverter<
    input_point_type, cluster_point_type
    > point_converter_type;

  cluster_point_type actual_search_box;
  boost::geometry::assign(actual_search_box, search_box_half_span);

  tracktable::DBSCAN<cluster_point_type> dbscan;

  int num_clusters = dbscan.learn_clusters(
    boost::make_transform_iterator(input_begin, point_converter_type()),
    boost::make_transform_iterator(input_end, point_converter_type()),
    actual_search_box,
    minimum_cluster_size
    );

  dbscan.point_cluster_labels(output_cluster_labels);
  return num_clusters;
}


/** Generate cluster labels for a set of points.
 *
 * This function runs DBSCAN on a list of points and returns its
 * results as a vector of vectors, each listing members for one cluster.
 *
 * When you call cluster_with_dbscan you must indicate the type of
 * point (and thus the coordinate space) that you want to use for the
 * clustering.  This lets you choose (for example) to run in Cartesian
 * space rather than longitude/latitude space if you're sure your
 * points don't run into the poles or the longitude discontinuity at
 * +/= 180.
 *
 * Here's an example::
 *
 * typedef tracktable::cartesian2d::BasePoint point2d;
 * std::vector<tracktable::cartesian2d::TrajectoryPoint> my_points;
 * std::vector<std::vector<int> > cluster_lists;
 * point2d search_box(0.5, 0.5);
 * int min_cluster_size = 10;
 *
 *
 * int num_clusters = cluster_with_dbscan<point2d>(
 *    my_points.begin(),
 *    my_points.end(),
 *    search_box,
 *    min_cluster_size,
 *    cluster_lists
 * );
 *
 * The search box must be specified in the coordinate system in which
 * you want to do the clustering.
 *
 * @param[in] input_begin   Iterator for beginning of input points
 * @param[in] input_end     Iterator for end of input points
 * @param[in] search_box_half_span  Distance defining "nearby" in all dimensions
 * @param[in] minimum_cluster_size  Minimum number of neighbors for core points
 * @param[out] output_cluster_membership  Points belonging to each cluster
 * @return Number of clusters discovered
 */

template<class ClusterSpacePointT, class PointIteratorT>
int cluster_with_dbscan(
  PointIteratorT       input_begin,
  PointIteratorT       input_end,
  ClusterSpacePointT   search_box_half_span,
  int                  minimum_cluster_size,
  std::vector<std::vector<int> >&    output_cluster_membership
  )
{
  typedef typename PointIteratorT::value_type input_point_type;
  typedef ClusterSpacePointT cluster_point_type;

  typedef detail::PointConverter<
    input_point_type, cluster_point_type
    > point_converter_type;

  cluster_point_type actual_search_box;
  boost::geometry::assign(actual_search_box, search_box_half_span);

  tracktable::DBSCAN<cluster_point_type> dbscan;

  int num_clusters = dbscan.template learn_clusters(
    boost::make_transform_iterator(input_begin, point_converter_type()),
    boost::make_transform_iterator(input_end, point_converter_type()),
    actual_search_box,
    minimum_cluster_size
    );

  dbscan.cluster_membership_lists(output_cluster_membership);
  return num_clusters;
}

} // exit namespace tracktable

#endif
