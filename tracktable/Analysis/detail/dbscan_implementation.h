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


// This is a simple implementation of the DBSCAN clustering algorithm
// that uses axis-aligned bounding boxes to find nearby points instead
// of spheres.
//
// The file ComputeDBSCANClustering.h provides a set of convenient
// interfaces to this module.

#ifndef __tracktable_DBSCAN_implementation_h
#define __tracktable_DBSCAN_implementation_h

// This #define causes Boost timers to be instantiated around the
// expensive steps of clustering.  If this is problematic on your
// system or you just don't want to bother then change #define to
// #undef.
#undef TIME_CLUSTERING_STEPS

#include <tracktable/Core/TracktableCommon.h>

#include <list>
#include <utility>
#include <vector>
#include <fstream>
#include <iomanip>

#include <boost/bind/bind.hpp>
#include <boost/mpl/assert.hpp>
#include <boost/tuple/tuple.hpp>

#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/CommonBoostWarnings.h>

// We need this in order to pull in boost/geometry/strategies/strategies.hpp --
// consider investigating what we can trim down
#include <boost/geometry/geometry.hpp>

#include <boost/geometry/geometries/point_xy.hpp>
#include <boost/geometry/geometries/register/point.hpp>
#include <boost/geometry/geometries/adapted/boost_tuple.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

#include <tracktable/Analysis/GuardedBoostGeometryRTreeHeader.h>

#if defined(TIME_CLUSTERING_STEPS)
# include <boost/timer/timer.hpp>
#endif

#include <tracktable/Analysis/detail/dbscan_points.h>
#include <tracktable/Core/PointArithmetic.h>

namespace bgi = boost::geometry::index;
namespace bg = boost::geometry;

namespace tracktable { namespace analysis { namespace detail { namespace implementation {

/** Cluster points using the DBSCAN algorithm.
 *
 * DBSCAN is a non-parametric clustering algorithm that defines a
 * point in a cluster as "a point with more than N neighbors inside a
 * search radius R".  N and R are user-specified parameters.  The
 * consequence of this definition is that areas of points with a
 * certain minimum density form clusters regardless of their shape.
 *
 * In order to use DBSCAN you must supply the following parameters:
 *
 * - A list of points to cluster.  These can be in any coordinate
 *   system supported by `boost::geometry` and any container that
 *   provides begin() and end() iterators.
 *
 * - A search box: the distance that a point can be in any dimension
 *   in order to count as "nearby".  Note that we use a search box
 *   instead of the sphere that the original DBSCAN implementation
 *   requires.  This helps when you have a space where different
 *   dimensions have different meaning such as longitude/latitude
 *   (sensible values are on the order of 0-200 in each dimension) and
 *   altitude (sensible values are up to 15000 meters).
 *
 * - A minimum cluster size: Any point that has at least this many
 *   points within its search box is part of a cluster.
 *
 * If you would rather use a slightly more convenient interface
 * please refer to the functions in
 * `Analysis/ComputeDBSCANClustering.h`.
 *
 *
 * For more information about the DBSCAN algorithm please refer to the
 * original paper: Ester, Martin; Kriegel, Hans-Peter; Sander, Jörg;
 * Xu, Xiaowei (1996). "A density-based algorithm for discovering
 * clusters in large spatial databases with noise". In Simoudis,
 * Evangelos; Han, Jiawei; Fayyad, Usama M. "Proceedings of the Second
 * International Conference on Knowledge Discovery and Data Mining
 * (KDD-96)".
 */

template <class PointT>
class DBSCAN
{
public:
  /// This is the point type we will be clustering
  typedef PointT point_type;
  /// Container for points - convenience typedef only
  typedef std::vector<point_type> point_vector_type;
  /// Internal point type with cluster ID and point ID.
  typedef IndexedPoint<PointT> indexed_point_type;
  typedef std::vector<indexed_point_type> indexed_point_vector_type;

  /// Abstraction of index into list of points
  //
  // The Boost r-tree implementation keeps points around as a
  // combination of point and index -- a glorified pointer by another
  // name. This class handles the 'dereference' operation (actually
  // operator()) to turn an Indexable back into a point.
  typedef DBSCAN_IndexByIterator<
    indexed_point_vector_type, point_type
    > indexable_getter_type;

  /// Balancing algorithm for rtree
  typedef bgi::quadratic<16> rtree_parameter_type;

  /// This is what will actually be stored in the nodes
  typedef typename indexed_point_vector_type::iterator rtree_value_type;

  /// ...And here's the rtree itself
  typedef bgi::rtree<
    rtree_value_type,
    rtree_parameter_type,
    indexable_getter_type
    > rtree_type;

  /// Bounding box for nodes
  typedef bg::model::box<point_type> box_type;

  /// Container type for clustering results
  typedef std::vector<int> int_vector_type;

  /// Container type for cluster membership lists
  typedef std::vector<int_vector_type> int_vector_vector_type;

public:

  /** Initialize an empty clusterer.
   *
   */
  DBSCAN()
    : InputPointCount(0)
    { }
  virtual ~DBSCAN() { }

  /** Learn cluster labels for a set of points.
   *
   * This is the method that you will call to run DBSCAN.
   *
   * You will need to call cluster_membership_lists() or
   * point_cluster_labels() to get the results back.
   *
   * @param [in] point_begin            Iterator for beginning of input points
   * @param [in] point_end              Iterator past end of input points
   * @param [in] epsilon_box_half_span  "Nearby" distance in each dimension
   * @param [in] min_cluster_size       Minimum number of points for a cluster
   * @return    Number of clusters detected (cluster 0 is noise)
   */

  template<class IteratorT>
  int learn_clusters(IteratorT point_begin, IteratorT point_end,
                     point_type const& epsilon_box_half_span,
                     unsigned int min_cluster_size,
                     bool L2=false)
    {
      // Convert the points into a format that we can use in the R-tree
      indexed_point_vector_type indexed_points;
      IteratorT here(point_begin);
      int i = 0;
      for ( ; here != point_end; ++here, ++i)
        {
        indexed_point_type i_point = indexed_point_type(*here, i);
        indexed_points.push_back(i_point);
        }

      this->InputPointCount = indexed_points.size();
      rtree_parameter_type params;
      rtree_type rtree(params, indexable_getter_type(indexed_points));
      if (1)
        {
#if defined(TIME_CLUSTERING_STEPS)
        boost::timer::auto_cpu_timer t;
#endif
        for (rtree_value_type iter = indexed_points.begin();
             iter != indexed_points.end();
             ++iter)
          {
          rtree.insert(iter);
          }
        }

      this->num_range_queries = 0;

      if (1)
        {
#if defined(TIME_CLUSTERING_STEPS)
        boost::timer::auto_cpu_timer t;
#endif
        this->compute_cluster_membership(indexed_points,
                                         min_cluster_size,
                                         epsilon_box_half_span,
                                         rtree,
                                         L2);
        }

      return boost::numeric_cast<int>(this->ClusterMembership.size());
    }

  /** Return the point IDs belonging to each cluster.
   *
   * This method is the first of two ways to get clustering results
   * back from DBSCAN.  Given a DBSCAN run that detected C clusters,
   * this method will return a std::vector of C std::vector<int>.
   * Each vector lists the points that belong to a single cluster.
   *
   * Clusters 1 through C-1 are the "real" clusters.  Cluster 0 is the
   * noise cluster comprising all points that (1) did not have enough
   * nearby neighbors to qualify as cluster points in their own right
   * and (2) were not neighbors of any points that did.
   *
   * @param [out] output  Cluster membership lists.
   */

  void cluster_membership_lists(int_vector_vector_type& output)
    {
      output = this->ClusterMembership;
    }

  /** Return the cluster ID for each point.
   *
   * This method is the second of two ways to get clustering results
   * back from DBSCAN.  Given a DBSCAN run on P points that detected C
   * clusters, this method will return a std::vector<int> with P
   * elements.  Each element will have a value between 0 and C-1
   * inclusive.
   *
   * Clusters 1 through C-1 are the "real" clusters.  Cluster 0 is the
   * noise cluster comprising all the points that (1) did not have
   * enough nearby neighbors to qualify as cluster points in their own
   * right and (2) were not neighbors of any points that did.
   *
   * @param [out] cluster_labels   Labels for each point in the input.
   */

  void point_cluster_labels(int_vector_type& out_labels)
    {
      out_labels.resize(this->InputPointCount, 0);
      for (int_vector_vector_type::size_type cluster_id = 0;
           cluster_id < this->ClusterMembership.size();
           ++cluster_id)
        {
        for (int_vector_type::size_type i = 0;
             i < this->ClusterMembership[cluster_id].size();
             ++i)
          {
          int_vector_type::value_type point_id =
            this->ClusterMembership[cluster_id][i];
          out_labels[point_id] = boost::numeric_cast<int>(cluster_id);
          }
        }
    }


private:
  /** Internal method.
   *
   * We use this when processing the results of a range query.  This
   * is just an accessor.
   */

  int get_cluster_id(rtree_value_type const& iter)
    {
      return iter->cluster_id();
    }

  /** Internal method.
   *
   * We use this when setting cluster IDs for many points at once.
   */
  void set_cluster_id(rtree_value_type& iter, int new_id)
    {
      iter->set_cluster_id(new_id);
    }

protected:

  /** Learn cluster assignments for all points.
   *
   * This is the driver method that implements the skeleton of DBSCAN.
   *
   * @param [in] points                Points with indices attached
   * @param [in] min_cluster_size      Minimum number of points in neighborhood
   *                                  required to define a core point
   * @param [in] epsilon_box_half_span Search range in each direction
   * @param [in] rtree                 Boost RTree to accelerate neighborhood
   *                                  queries
   */

  void compute_cluster_membership(indexed_point_vector_type& points,
                                  unsigned int min_cluster_size,
                                  const point_type& epsilon_box_half_span,
                                  rtree_type& rtree,
                                  bool L2)
    {
      // This is it.  Assigns all points to a cluster, with cluster 0 = noise
      // At the end, next_cluster_id is the number of clusters, *counting* the
      // noise cluster.  So, the clusters are numbered 0 to next_cluster_id-1.

      unsigned int next_cluster_id = 1;
      // Walk through the list of points.  When we find a point we
      // haven't yet assigned to a cluster, search its neighborhood
      // to see if there are enough points to merit declaring a new
      // cluster.

      int num_points_processed_in_cluster = 0;
      for (rtree_value_type iter = points.begin();
           iter != points.end();
           ++iter)
        {
        ++num_points_processed_in_cluster;
        if ((*iter).cluster_id() == 0 && (*iter).visited() == false)
          {
          bool new_cluster_found = this->expand_cluster(
            iter,
            min_cluster_size,
            epsilon_box_half_span,
            next_cluster_id,
            rtree,
            L2
            );

          if (new_cluster_found)
            {
            ++next_cluster_id;
            }
          }
        }
      this->build_cluster_membership_lists(points, next_cluster_id);

#if defined(COMPUTE_CLUSTER_STATISTICS)
      TRACKTABLE_LOG(log::info) << "Constructing cluster statistics...";
      this->num_core_points.resize(next_cluster_id, 0);
      this->core_point_avg_num_neighbors.resize(next_cluster_id, 0);
      this->total_num_neighbors.resize(next_cluster_id, 0);

      for (size_t cluster_id = 0; cluster_id < next_cluster_id; ++cluster_id)
        {
        for (int_vector_type::iterator piter =
               this->ClusterMembership[cluster_id].begin();
             piter != this->ClusterMembership[cluster_id].end();
             ++piter)
          {
          point_type box_center((points[*piter]).point());
          box_type epsilon_box(detail::make_box(box_center,
                                                epsilon_box_half_span));

          // Find all points near the seed
          std::vector<rtree_value_type> points_in_neighborhood;
          rtree.query(boost::geometry::index::within(epsilon_box),
                      std::back_inserter(points_in_neighborhood));

          // If doing sphere/ellipsoid, remove points in box outside sphere
          if (L2)
            {
            this->ellipsoid_filter(points_in_neighborhood,
                                   box_center,
                                   epsilon_box_half_span);
            }

          if (points_in_neighborhood.size() >= min_cluster_size)
            {
            ++ this->num_core_points[cluster_id];
            this->core_point_avg_num_neighbors[cluster_id] +=
              points_in_neighborhood.size();
            }
          total_num_neighbors[cluster_id] += points_in_neighborhood.size();
          }
        if (this->num_core_points[cluster_id])
          {
          this->core_point_avg_num_neighbors[cluster_id] /=
            static_cast<double>(this->num_core_points[cluster_id]);
          }
        }
      TRACKTABLE_LOG(log::info) << "Cluster statistics:";
      for (size_t i = 0; i < this->num_core_points.size(); ++i)
        {
        TRACKTABLE_LOG(log::info)
                  << "C " << i << ": "
                  << this->ClusterMembership[i].size() << " points, "
                  << this->num_core_points[i] << " core points, "
                  << this->core_point_avg_num_neighbors[i]
                  << " avg neighbors per core point, "
                  << this->total_num_neighbors[i]
                  << " neighbors for all points in cluster\n";
        }
#endif
    }

// ----------------------------------------------------------------------

  /** Discover a single cluster.
   *
   * This method contains the heart of DBSCAN: searching the
   * neighborhood of a single point to discover whether it is in the
   * interior of a cluster and, if so, discovering the rest of that
   * cluster.
   *
   * @param [in] seed_point        Point to examine for cluster-ness
   * @param [in] min_cluster_size  Minimum neighbor count for core points
   * @param [in] epsilon_box_half_span  Search range in each direction
   * @param [in] next_cluster_id   Numeric ID for new cluster
   * @param [in] rtree             Search structure for neighbor queries
   * @return  Boolean - whether or not a new cluster was discovered
   */

  bool expand_cluster(rtree_value_type& seed_point,
                      unsigned int min_cluster_size,
                      const point_type& epsilon_box_half_span,
                      unsigned int next_cluster_id,
                      rtree_type& rtree,
                      bool L2)
    {
      using namespace boost::placeholders;

      std::list<rtree_value_type> seed_point_queue;
      seed_point_queue.push_back(seed_point);
      bool core_point_found = false;

      for (typename std::list<rtree_value_type>::iterator query_point =
             seed_point_queue.begin();
           query_point != seed_point_queue.end();
           ++query_point)
        {
        if ((*query_point)->visited()) continue;

        (*query_point)->set_visited(true);

        // Make a box describing the epsilon-neighborhood of the point
        // being considered
        point_type box_center((*query_point)->point());
        box_type epsilon_box(
          make_box(box_center, epsilon_box_half_span)
          );

        // Find all points near the seed
        std::vector<rtree_value_type> points_in_neighborhood;
        rtree.query(boost::geometry::index::within(epsilon_box),
                    std::back_inserter(points_in_neighborhood));

        // If doing sphere/ellipsoid, remove points in box outside sphere
        if (L2)
          {
          this->ellipsoid_filter(points_in_neighborhood,
                                 box_center,
                                 epsilon_box_half_span);
          }

        ++ this->num_range_queries;

         // Have we found a new core point?  If so, assign the current
         // cluster ID to all points in the query box (which will
         // necessarily include the query point).
        if (points_in_neighborhood.size() >= min_cluster_size)
          {
          core_point_found = true;

          // Remove all the points that already belong to another cluster
          points_in_neighborhood.erase(
            std::remove_if(
              points_in_neighborhood.begin(), points_in_neighborhood.end(),
              boost::bind(&DBSCAN::get_cluster_id, this, _1) != 0
              ),
            points_in_neighborhood.end()
            );

          // Set the cluster ID of all neighboring points to the new
          // cluster ID
          std::for_each(
            points_in_neighborhood.begin(),
            points_in_neighborhood.end(),
            boost::bind(
              &DBSCAN::set_cluster_id,
              this,
              _1,
              next_cluster_id
              )
            );

          // Add the new seed points to the queue
          std::copy(
            points_in_neighborhood.begin(),
            points_in_neighborhood.end(),
            std::back_inserter(seed_point_queue)
            );

          // Done processing new core point
          }
        // Done looping over seed point queue
        }
      return core_point_found;
    }

  // ----------------------------------------------------------------------

  /** Assemble cluster membership lists from points.
   *
   * The clustering algorithm stores its results in the indexed point
   * list.  This function extracts those results and builds cluster
   * membership lists that are more useful to the user.
   *
   * @param [in] points          Points labeled with cluster IDs
   * @param[in[ max_cluster_id  ID of last cluster found
   */
  void build_cluster_membership_lists(const indexed_point_vector_type& points,
                                      unsigned int max_cluster_id)
    {
      this->ClusterMembership.resize(max_cluster_id);
      for (typename indexed_point_vector_type::const_iterator iter =
             points.begin();
           iter != points.end();
           ++iter)
        {
        unsigned int cluster_id = (*iter).cluster_id();
        int original_point_id = (*iter).point_id();
        this->ClusterMembership[cluster_id].push_back(original_point_id);
        }
    }

  // ----------------------------------------------------------------------

  /** Removes points from a box that are not in the ellipsoid
   *
   * This is essentially allow an extension to a more traditional DBSCAN
   * by taking points from an ellipsoid that essentially has axes that are
   * the length of the epsilon_box_half_span parameters.  If they are all
   * the same, you just a sphere, and a traditional DBSCAN
   *
   * @param [in] points                  Points labeled with cluster IDs
   * @param [in] epsilon_box_half_span   Scaling parameters for ellipsoid
   */
  void ellipsoid_filter(std::vector<rtree_value_type>& points,
                        const point_type& box_center,
                        const point_type& epsilon_box_half_span)
    {

  // Okay.  This code looks a little obfuscated, but I hate to remove things
  // from a vector without using the erase/remove_if idiom.  The code below
  // allows this to be done without changing other parts of the code.
  //
  // Essentiall, parsing from the inside out, do operator* on the
  // rtree_value_type to get an indexed_point_type.  Then, do the point
  // method to get out a point_type.  Take that point, and subtract off
  // the point that it is in the neigborhood of to get an offset vector.
  // Divide the elements of the offset vector by the values in the
  // epsilon_box_half_span, to get the relative contributions of the
  // directions to figure out if it is in the ellipsoid.  Then, take the norm,
  // and it should be less than 1.  Erase all offending elements.
      using namespace boost::placeholders;
      points.erase(
       std::remove_if(points.begin(),points.end(),
        boost::bind(&tracktable::arithmetic::norm_squared<point_type>,
         boost::bind(&tracktable::arithmetic::divide<point_type>,
          boost::bind(&tracktable::arithmetic::subtract<point_type>,
           boost::bind(&indexed_point_type::point,
            boost::bind(&rtree_value_type::operator*,_1)),
          box_center),
         epsilon_box_half_span)) > 1.0),
      points.end());

      return;
    }

protected:
  /// List of points belonging to each cluster
  int_vector_vector_type ClusterMembership;
  /// How many range queries we make (performance statistic)
  int num_range_queries;
  /// How many points we've processed so far (progress statistic)
  int num_points_processed;
  /// How many points are on the interiors of the clusters
  int_vector_type num_core_points;
  /// How many neighbors each core point has (performance statistic)
  int_vector_type core_point_avg_num_neighbors;
  int_vector_type total_num_neighbors;
  std::size_t InputPointCount;
};

} } } } // namespace tracktable::analysis::detail::implementation

#endif
