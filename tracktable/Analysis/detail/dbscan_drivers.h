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
 * DBSCAN_Drivers - Dispatch machinery to handle point formats
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

#ifndef __tracktable_dbscan_drivers_h
#define __tracktable_dbscan_drivers_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Analysis/detail/dbscan_implementation.h>
#include <tracktable/Analysis/detail/transfer_point_coordinates.h>
#include <tracktable/Analysis/detail/extract_pair_member.h>

#include <boost/iterator/transform_iterator.hpp>
#include <boost/mpl/assert.hpp>
#include <boost/type_traits/is_same.hpp>

#include <iterator>
#include <vector>


namespace tracktable { namespace analysis { namespace detail {



// This is the most specific version.  We will fall through to this
// sooner or later.  We expect an undecorated point as input and an
// InsertIterator for a container that takes std::pair<foo, bar> where
// 'foo' and 'bar' are both integral types.
//
// We don't care precisely what the type of the search box is as long
// as it's something that we can use with boost::assign.  Any point
// type registered with boost::geometry should be enough.

template<class DispatchPointT>
struct DBSCAN_Driver
{
  template<
    class PointInputIteratorT,
    class SearchBoxPointT,
    class LabelOutputIteratorT>
  int operator()(
    PointInputIteratorT input_begin,
    PointInputIteratorT input_end,
    SearchBoxPointT search_box_half_span,
    int minimum_cluster_size,
    LabelOutputIteratorT output_sink
  )
  {
    typedef typename PointInputIteratorT::value_type input_point_type;
    typedef DispatchPointT dispatch_point_type;

    BOOST_MPL_ASSERT_MSG(
      (boost::is_same<input_point_type, dispatch_point_type>::value),
      Tracktable_INPUT_POINT_TYPE_MUST_MATCH_TEMPLATE_ARGUMENT,
      (input_point_type, dispatch_point_type)
    );

    input_point_type actual_search_box;
    boost::geometry::assign(actual_search_box, search_box_half_span);

    implementation::DBSCAN<input_point_type> dbscan;
    int num_clusters = dbscan.learn_clusters(
      input_begin, input_end,
      actual_search_box,
      minimum_cluster_size
    );


    std::vector<int> vertex_cluster_ids;
    dbscan.point_cluster_labels(vertex_cluster_ids);

    for (std::size_t i = 0; i < vertex_cluster_ids.size(); ++i)
      {
      *output_sink = std::make_pair(boost::numeric_cast<int>(i), vertex_cluster_ids[i]);
      ++output_sink;
      }

  return num_clusters;
  }
};

// ----------------------------------------------------------------------

template<class MetadataT, class PointT>
struct DBSCAN_Driver<
  std::pair<PointT, MetadataT>
  >
{
  template<class PointInputIteratorT, class SearchBoxPointT, class OutputIteratorT>
  int operator()(
    PointInputIteratorT input_begin,
    PointInputIteratorT input_end,
    SearchBoxPointT search_box_half_span,
    int minimum_cluster_size,
    OutputIteratorT output_sink
  )
  {
    typedef std::pair<PointT, MetadataT> dispatch_point_type;
    typedef typename PointInputIteratorT::value_type input_point_pair_type;
    typedef typename input_point_pair_type::first_type input_point_type;
    typedef typename input_point_pair_type::second_type input_metadata_type;

    typedef ExtractFirst<input_point_pair_type> point_extractor_type;

    BOOST_MPL_ASSERT_MSG(
      (boost::is_same<dispatch_point_type, input_point_pair_type>::value),
      Tracktable_DBSCAN_PAIR_DISPATCH_TYPE_MUST_MATCH_INPUT_VALUE_TYPE,
      (dispatch_point_type, input_point_pair_type)
    );

    BOOST_MPL_ASSERT_MSG(
      (boost::is_same<input_metadata_type, MetadataT>::value),
      Tracktable_DBSCAN_PAIR_METADATA_TYPES_MUST_MATCH,
      (input_point_pair_type, input_metadata_type, MetadataT)
    );

    BOOST_MPL_ASSERT_MSG(
      (boost::is_same<input_point_type, PointT>::value),
      Tracktable_INPUT_POINT_TYPE_MUST_MATCH_TEMPLATE_ARGUMENT,
      (input_point_type, PointT)
    );

#if 0
    BOOST_MPL_ASSERT_MSG(
      (boost::is_same<input_metadata_type, output_metadata_type>::value),
      Tracktable_DBSCAN_PAIR_OUTPUT_FIRST_MEMBER_MUST_MATCH_INPUT_METADATA,
      (input_metadata_type, output_metadata_type)
    );
#endif

    typedef std::pair<int, int> raw_vertex_cluster_label_type;

    std::vector<raw_vertex_cluster_label_type> raw_labels;
    DBSCAN_Driver<input_point_type> driver;
    int num_clusters = driver(
      boost::make_transform_iterator(input_begin, point_extractor_type()),
      boost::make_transform_iterator(input_end, point_extractor_type()),
      search_box_half_span,
      minimum_cluster_size,
      std::back_inserter(raw_labels)
    );

    typedef std::vector<input_metadata_type> metadata_vector_t;
    metadata_vector_t saved_metadata;
    for (; input_begin != input_end; ++input_begin)
      {
      saved_metadata.push_back(input_begin->second);
      }

    for (std::vector<raw_vertex_cluster_label_type>::iterator iter = raw_labels.begin();
         iter != raw_labels.end();
         ++iter)
      {
      int vertex_id = iter->first;
      int cluster_id = iter->second;

      *output_sink = std::make_pair(
        saved_metadata[vertex_id], cluster_id
      );
      ++output_sink;
      }

    return num_clusters;
  }
};


} } } // namespace tracktable::analysis::detail

#endif
