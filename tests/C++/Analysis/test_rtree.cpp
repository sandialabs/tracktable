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
 * 2. Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following
 * disclaimer in the documentation and/or other materials provided
 * with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */


#include <tracktable/Analysis/RTree.h>
#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Cartesian3D.h>
#include <tracktable/Domain/Terrestrial.h>

#include <algorithm>
#include <typeinfo>
#include <utility>
#include <vector>

#include <boost/tuple/tuple.hpp>
#include <boost/tuple/tuple_comparison.hpp>
#include <boost/tuple/tuple_io.hpp>

template<typename point_type>
std::string to_string(point_type const& pt)
{
  std::ostringstream outbuf;
  outbuf << pt;
  return outbuf.str();
}

template<typename point_type, typename T2>
std::string to_string(std::pair<point_type, T2> const& my_pair)
{
  std::ostringstream outbuf;
  outbuf << "pair("
         << my_pair.first
         << ", "
         << my_pair.second
         << ")";
  return outbuf.str();
}

template<
  typename point_type,
  typename T2,
  typename T3,
  typename T4,
  typename T5,
  typename T6,
  typename T7,
  typename T8,
  typename T9,
  typename T10
  >
std::string to_string(boost::tuple<point_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& my_tuple)
{
  std::ostringstream outbuf;
  outbuf << my_tuple;
  return outbuf.str();
}

// ----------------------------------------------------------------------

template<typename container1_type, typename container2_type>
int compare_container_contents(std::string const& error_message_prefix,
                               container1_type const& c1,
                               container2_type const& c2)
{
  typename container1_type::const_iterator iter1(c1.begin());
  typename container2_type::const_iterator iter2(c2.begin());

  unsigned int index = 0;
  int error_count = 0;

  for (; iter1 != c1.end() && iter2 != c2.end();
       ++iter1, ++iter2)
    {
    typename container1_type::value_type thing1(*iter1);
    typename container2_type::value_type thing2(*iter2);

    if (thing1 != thing2)
      {
      std::cout << error_message_prefix
                << ": Elements differ at index "
                << index << "\n";
      ++error_count;
      }
    }

  if (iter1 != c1.end() || iter2 != c2.end())
    {
    std::cout << error_message_prefix
              << ": Container sizes are not the same.  Container 1 has "
              << c1.size()
              << " elements and container 2 has "
              << c2.size() << ".\n";
    ++error_count;
    }

  return error_count;
}

// ----------------------------------------------------------------------

template<typename point_type, typename output_iterator>
void create_point_grid(int rows, int columns, output_iterator out_sink)
{
  double start_point[2];

  start_point[0] = -(columns-1)/2;
  start_point[1] = -(rows-1)/2;

  for (int i = 0; i < rows; ++i)
    {
    double y = start_point[1] + i;
    for (int j = 0; j < columns; ++j)
      {
      double x = start_point[0] + j;

      point_type next_point;
      for (std::size_t d = 0; d < next_point.size(); ++d)
        {
        next_point[d] = 0;
        }

      next_point[0] = x;
      next_point[1] = y;
      *out_sink = next_point;
      ++out_sink;
      }
    }
}

// ----------------------------------------------------------------------

template<typename point_type>
int test_rtree_with_pair_value()
{
  typedef std::pair<point_type, std::size_t> point_with_id;
  int error_count = 0;

  std::vector<point_type> base_points;
  create_point_grid<point_type>(1, 9, std::back_inserter(base_points));

  std::vector<point_with_id> points;
  for (std::size_t i = 0; i < base_points.size(); ++i)
    {
    points.push_back(point_with_id(base_points[i], i));
    }

  tracktable::RTree<point_with_id> tree;
  for (typename std::vector<point_with_id>::iterator iter = points.begin();
       iter != points.end();
       ++iter)
    {
    tree.insert(*iter);
    }

  point_type min_point, max_point;
  for (std::size_t i = 0; i < min_point.size(); ++i)
    {
    min_point[i] = 0;
    max_point[i] = 0;
    }

  min_point[0] = -5;
  min_point[1] = 0;
  max_point[0] = 5;
  max_point[1] = 0;

  std::vector<point_with_id> results;
  tree.find_points_in_box(min_point, max_point, std::back_inserter(results));

  if (results.size() != 9)
    {
    std::cout << "ERROR: Expected loose-overlap test in 1D to return 9 points.  Instead it returned "
              << results.size() << ".\n";
    ++error_count;
    }
  else
    {
    std::cout << "Results from pair-value range query:\n";
    typedef typename std::vector<point_with_id>::const_iterator result_iter_type;
    for (result_iter_type iter = results.begin();
         iter != results.end();
         ++iter)
      {
      std::cout << "ID " << (*iter).second << ": " << (*iter).first << "\n";
      }
    }
  return error_count;
}

// ----------------------------------------------------------------------
template<typename base_point_type>
int test_find_points_inside_box(base_point_type const& base_min_corner,
                                base_point_type const& base_max_corner,
                                std::vector<base_point_type> const& points_to_search,
                                unsigned int expected_num_results)
{
  int error_count = 0;

  tracktable::RTree<base_point_type> rtree(points_to_search.begin(),
                                           points_to_search.end());

  std::vector<base_point_type> query_results_bare, query_results_pair, query_results_tuple;
  rtree.find_points_inside_box(
    base_min_corner,
    base_max_corner,
    std::back_inserter(query_results_bare)
    );

  rtree.find_points_inside_box(
    std::make_pair(base_min_corner, 1000),
    std::make_pair(base_max_corner, 2000),
    std::back_inserter(query_results_pair)
    );

  rtree.find_points_inside_box(
    boost::make_tuple(base_min_corner, 10000),
    boost::make_tuple(base_max_corner, 20000),
    std::back_inserter(query_results_tuple)
    );

  if (query_results_bare.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_inside_box<"
              << typeid(base_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for base point search, got "
              << query_results_bare.size()
              << "\n";
    ++error_count;
    }

  if (query_results_pair.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_inside_box<"
              << typeid(base_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for std::pair search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  if (query_results_tuple.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_inside_box<"
              << typeid(base_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for boost::tuple search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  error_count += compare_container_contents("test_find_points_inside_box (bare/pair)",
                                            query_results_bare, query_results_pair);

  error_count += compare_container_contents("test_find_points_inside_box (bare/tuple)",
                                            query_results_bare, query_results_tuple);

  error_count += compare_container_contents("test_find_points_inside_box (pair/tuple)",
                                            query_results_pair, query_results_tuple);

  return error_count;
}

// ----------------------------------------------------------------------

template<typename annotated_point_type, typename base_point_type>
int test_find_annotated_points_inside_box(base_point_type const& base_min_corner,
                                          base_point_type const& base_max_corner,
                                          std::vector<base_point_type> const& base_points_to_search,
                                          unsigned int expected_num_results)
{
  int error_count = 0;

  typedef std::vector<annotated_point_type> annotated_point_vector;
  annotated_point_vector points_to_search;

  for (unsigned int i = 0; i < base_points_to_search.size(); ++i)
    {
    points_to_search.push_back(annotated_point_type(base_points_to_search[i], 1234*i));
    }

  tracktable::RTree<annotated_point_type> rtree(points_to_search.begin(),
                                                points_to_search.end());

  std::vector<annotated_point_type> query_results_bare, query_results_pair, query_results_tuple;
  rtree.find_points_inside_box(
    base_min_corner,
    base_max_corner,
    std::back_inserter(query_results_bare)
    );

  rtree.find_points_inside_box(
    std::make_pair(base_min_corner, 1000),
    std::make_pair(base_max_corner, 2000),
    std::back_inserter(query_results_pair)
    );

  rtree.find_points_inside_box(
    boost::make_tuple(base_min_corner, 10000),
    boost::make_tuple(base_max_corner, 20000),
    std::back_inserter(query_results_tuple)
    );

  if (query_results_bare.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_inside_box<"
              << typeid(annotated_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for base point search, got "
              << query_results_bare.size()
              << "\n";
    ++error_count;
    }

  if (query_results_pair.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_inside_box<"
              << typeid(annotated_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for std::pair search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  if (query_results_tuple.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_inside_box<"
              << typeid(annotated_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for boost::tuple search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  error_count += compare_container_contents("test_find_points_inside_box (bare/pair)",
                                            query_results_bare, query_results_pair);

  error_count += compare_container_contents("test_find_points_inside_box (bare/tuple)",
                                            query_results_bare, query_results_tuple);

  error_count += compare_container_contents("test_find_points_inside_box (pair/tuple)",
                                            query_results_pair, query_results_tuple);

  return error_count;
}


// ----------------------------------------------------------------------

template<typename base_point_type>
int test_find_points_inside_box_all_value_types(unsigned int expected_num_results)
{
  typedef boost::tuple<base_point_type, unsigned int> tuple_point_type;
  typedef std::pair<base_point_type, double> pair_point_type;

  std::vector<base_point_type> base_points;
  create_point_grid<base_point_type>(1, 9, std::back_inserter(base_points));

  base_point_type base_min_corner, base_max_corner;
  for (std::size_t i = 0; i < base_min_corner.size(); ++i)
    {
    base_min_corner[i] = -0.01;
    base_max_corner[i] = 0.01;
    }
  base_min_corner[0] = -4;
  base_max_corner[0] = 4;

  int error_count = 0;
  error_count += test_find_points_inside_box(base_min_corner, base_max_corner, base_points, expected_num_results);
  error_count += test_find_annotated_points_inside_box<pair_point_type>(base_min_corner, base_max_corner, base_points, expected_num_results);
  error_count += test_find_annotated_points_inside_box<tuple_point_type>(base_min_corner, base_max_corner, base_points, expected_num_results);

  return error_count;
}

// ----------------------------------------------------------------------

template<typename base_point_type>
int test_find_points_strictly_inside_box(base_point_type const& base_min_corner,
                                         base_point_type const& base_max_corner,
                                         std::vector<base_point_type> const& points_to_search,
                                         unsigned int expected_num_results)
{
  int error_count = 0;

  tracktable::RTree<base_point_type> rtree(points_to_search.begin(),
                                                points_to_search.end());

  std::vector<base_point_type> query_results_bare, query_results_pair, query_results_tuple;
  rtree.find_points_strictly_inside_box(
    base_min_corner,
    base_max_corner,
    std::back_inserter(query_results_bare)
    );

  rtree.find_points_strictly_inside_box(
    std::make_pair(base_min_corner, 1000),
    std::make_pair(base_max_corner, 2000),
    std::back_inserter(query_results_pair)
    );

  rtree.find_points_strictly_inside_box(
    boost::make_tuple(base_min_corner, 10000),
    boost::make_tuple(base_max_corner, 20000),
    std::back_inserter(query_results_tuple)
    );

  if (query_results_bare.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_strictly_inside_box<"
              << typeid(base_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for base point search, got "
              << query_results_bare.size()
              << "\n";
    ++error_count;
    }

  if (query_results_pair.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_strictly_inside_box<"
              << typeid(base_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for std::pair search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  if (query_results_tuple.size() != expected_num_results)
    {
    std::cout << "ERROR: find_points_strictly_inside_box<"
              << typeid(base_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for boost::tuple search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  error_count += compare_container_contents("test_find_points_strictly_inside_box (bare/pair)",
                                            query_results_bare, query_results_pair);

  error_count += compare_container_contents("test_find_points_strictly_inside_box (bare/tuple)",
                                            query_results_bare, query_results_tuple);

  error_count += compare_container_contents("test_find_points_strictly_inside_box (pair/tuple)",
                                            query_results_pair, query_results_tuple);

  return error_count;
}

// ----------------------------------------------------------------------

template<typename annotated_point_type, typename base_point_type>
int test_find_annotated_points_strictly_inside_box(base_point_type const& base_min_corner,
                                                   base_point_type const& base_max_corner,
                                                   std::vector<base_point_type> const& base_points_to_search,
                                                   unsigned int expected_num_results)
{
  int error_count = 0;

  typedef std::vector<annotated_point_type> annotated_point_vector;
  annotated_point_vector points_to_search;
  for (unsigned int i = 0; i < base_points_to_search.size(); ++i)
    {
    points_to_search.push_back(annotated_point_type(base_points_to_search[i], 1234*i));
    }

  tracktable::RTree<annotated_point_type> rtree(points_to_search.begin(),
                                                points_to_search.end());

  std::vector<annotated_point_type> query_results_bare, query_results_pair, query_results_tuple;
  rtree.find_points_strictly_inside_box(
    base_min_corner,
    base_max_corner,
    std::back_inserter(query_results_bare)
    );

  rtree.find_points_strictly_inside_box(
    std::make_pair(base_min_corner, 1000),
    std::make_pair(base_max_corner, 2000),
    std::back_inserter(query_results_pair)
    );

  rtree.find_points_strictly_inside_box(
    boost::make_tuple(base_min_corner, 10000),
    boost::make_tuple(base_max_corner, 20000),
    std::back_inserter(query_results_tuple)
    );

  if (query_results_bare.size() != expected_num_results)
    {
    std::cout << "ERROR: find_annotated_points_strictly_inside_box<"
              << typeid(annotated_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for base point search, got "
              << query_results_bare.size()
              << "\n";
    ++error_count;
    }

  if (query_results_pair.size() != expected_num_results)
    {
    std::cout << "ERROR: find_annotated_points_strictly_inside_box<"
              << typeid(annotated_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for std::pair search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  if (query_results_tuple.size() != expected_num_results)
    {
    std::cout << "ERROR: find_annotated_points_strictly_inside_box<"
              << typeid(annotated_point_type).name()
              << ">: "
              << "Expected "
              << expected_num_results
              << " points for boost::tuple search, got "
              << query_results_pair.size()
              << "\n";
    ++error_count;
    }

  error_count += compare_container_contents("test_find_annotated_points_strictly_inside_box (bare/pair)",
                                            query_results_bare, query_results_pair);

  error_count += compare_container_contents("test_find_annotated_points_strictly_inside_box (bare/tuple)",
                                            query_results_bare, query_results_tuple);

  error_count += compare_container_contents("test_find_annotated_points_strictly_inside_box (pair/tuple)",
                                            query_results_pair, query_results_tuple);

  return error_count;
}


// ----------------------------------------------------------------------

template<typename base_point_type>
int test_find_points_strictly_inside_box_all_value_types(unsigned int expected_num_results)
{
  typedef boost::tuple<base_point_type, unsigned int> tuple_point_type;
  typedef std::pair<base_point_type, double> pair_point_type;

  std::vector<base_point_type> base_points;
  create_point_grid<base_point_type>(1, 9, std::back_inserter(base_points));

  base_point_type base_min_corner, base_max_corner;
  for (std::size_t i = 0; i < base_min_corner.size(); ++i)
    {
    base_min_corner[i] = -0.01;
    base_max_corner[i] = 0.01;
    }
  base_min_corner[0] = -4;
  base_max_corner[0] = 4;

  int error_count = 0;
  error_count += test_find_points_strictly_inside_box(base_min_corner, base_max_corner, base_points, expected_num_results);
  error_count += test_find_annotated_points_strictly_inside_box<pair_point_type>(base_min_corner, base_max_corner, base_points, expected_num_results);
  error_count += test_find_annotated_points_strictly_inside_box<tuple_point_type>(base_min_corner, base_max_corner, base_points, expected_num_results);

  return error_count;
}

// ----------------------------------------------------------------------

template<typename base_point_type>
int test_find_nearest_neighbors(base_point_type const& search_point,
                                std::vector<base_point_type> const& points_to_search,
                                unsigned int expected_neighbor_index)
{
  int error_count = 0;

  tracktable::RTree<base_point_type> rtree(points_to_search.begin(),
                                           points_to_search.end());

  std::vector<base_point_type> query_results_bare, query_results_pair, query_results_tuple;
  rtree.find_nearest_neighbors(
    search_point,
    1,
    std::back_inserter(query_results_bare)
    );

  rtree.find_nearest_neighbors(
    std::make_pair(search_point, 1000),
    1,
    std::back_inserter(query_results_pair)
    );

  rtree.find_nearest_neighbors(
    boost::make_tuple(search_point, 10000),
    1,
    std::back_inserter(query_results_tuple)
    );

  if (points_to_search[expected_neighbor_index] != query_results_bare[0])
    {
    std::cout << "ERROR: find_nearest_neighbors<"
              << typeid(base_point_type).name()
              << ">, bare point search: "
              << "Expected neighbor point "
              << to_string(points_to_search[expected_neighbor_index])
              << " but got "
              << to_string(query_results_bare[0])
              << "\n";
    ++error_count;
    }

  if (points_to_search[expected_neighbor_index] != query_results_pair[0])
    {
    std::cout << "ERROR: find_nearest_neighbors<"
              << typeid(base_point_type).name()
              << ">, pair point search: "
              << "Expected neighbor point "
              << to_string(points_to_search[expected_neighbor_index])
              << " but got "
              << to_string(query_results_pair[0])
              << "\n";
    ++error_count;
    }

  if (points_to_search[expected_neighbor_index] != query_results_tuple[0])
    {
    std::cout << "ERROR: find_nearest_neighbors<"
              << typeid(base_point_type).name()
              << ">, tuple point search: "
              << "Expected neighbor point "
              << to_string(points_to_search[expected_neighbor_index])
              << " but got "
              << to_string(query_results_tuple[0])
              << "\n";
    ++error_count;
    }

  return error_count;
}

// ----------------------------------------------------------------------

template<typename annotated_point_type, typename base_point_type>
int test_find_nearest_neighbors_annotated_points(
  base_point_type const& search_point,
  std::vector<base_point_type> const& base_points_to_search,
  unsigned int expected_neighbor_index
  )
{
  int error_count = 0;

  std::vector<annotated_point_type> points_to_search;
  for (unsigned int i = 0; i < base_points_to_search.size(); ++i)
    {
    points_to_search.push_back(annotated_point_type(base_points_to_search[i], 5000*i));
    }

  tracktable::RTree<annotated_point_type> rtree(points_to_search.begin(),
                                           points_to_search.end());

  std::vector<annotated_point_type> query_results_bare, query_results_pair, query_results_tuple;
  rtree.find_nearest_neighbors(
    search_point,
    1,
    std::back_inserter(query_results_bare)
    );

  rtree.find_nearest_neighbors(
    std::make_pair(search_point, 1000),
    1,
    std::back_inserter(query_results_pair)
    );

  rtree.find_nearest_neighbors(
    boost::make_tuple(search_point, 10000),
    1,
    std::back_inserter(query_results_tuple)
    );

  if (points_to_search[expected_neighbor_index] != query_results_bare[0])
    {
    std::cout << "ERROR: find_nearest_neighbors_annotated_points<"
              << typeid(base_point_type).name()
              << ">, bare point search: "
              << "Expected neighbor point "
              << to_string(points_to_search[expected_neighbor_index])
              << " but got "
              << to_string(query_results_bare[0])
              << "\n";
    ++error_count;
    }

  if (points_to_search[expected_neighbor_index] != query_results_pair[0])
    {
    std::cout << "ERROR: find_nearest_neighbors_annotated_points<"
              << typeid(base_point_type).name()
              << ">, pair point search: "
              << "Expected neighbor point "
              << to_string(points_to_search[expected_neighbor_index])
              << " but got "
              << to_string(query_results_pair[0])
              << "\n";
    ++error_count;
    }

  if (points_to_search[expected_neighbor_index] != query_results_tuple[0])
    {
    std::cout << "ERROR: find_nearest_neighbors_annotated_points<"
              << typeid(base_point_type).name()
              << ">, tuple point search: "
              << "Expected neighbor point "
              << to_string(points_to_search[expected_neighbor_index])
              << " but got "
              << to_string(query_results_tuple[0])
              << "\n";
    ++error_count;
    }

  return error_count;
}

// ----------------------------------------------------------------------

template<typename base_point_type>
int test_find_nearest_neighbors_all_value_types()
{
  typedef boost::tuple<base_point_type, unsigned int> tuple_point_type;
  typedef std::pair<base_point_type, double> pair_point_type;

  std::vector<base_point_type> base_points;
  create_point_grid<base_point_type>(1, 9, std::back_inserter(base_points));

  base_point_type search_point;
  for (unsigned int i = 0; i < search_point.size(); ++i)
    {
    search_point[i] = 0;
    }

  search_point[0] = -20;

  int error_count = 0;
  error_count += test_find_nearest_neighbors(search_point, base_points, 0);
  error_count += test_find_nearest_neighbors_annotated_points<pair_point_type>(search_point, base_points, 0);
  error_count += test_find_nearest_neighbors_annotated_points<tuple_point_type>(search_point, base_points, 0);

  return error_count;
}

// ----------------------------------------------------------------------

int
main(int , char**)
{
  int error_count = 0;

  error_count += test_find_points_inside_box_all_value_types< tracktable::domain::terrestrial::base_point_type >(9);
  error_count += test_find_points_inside_box_all_value_types< tracktable::domain::cartesian2d::base_point_type >(9);
  error_count += test_find_points_inside_box_all_value_types< tracktable::domain::cartesian3d::base_point_type >(9);


  std::cout << "\n\n\n";

  error_count += test_find_points_strictly_inside_box_all_value_types< tracktable::domain::terrestrial::base_point_type >(7);
  error_count += test_find_points_strictly_inside_box_all_value_types< tracktable::domain::cartesian2d::base_point_type >(7);
  error_count += test_find_points_strictly_inside_box_all_value_types< tracktable::domain::cartesian3d::base_point_type >(7);


  std::cout << "\n\n\n";

  error_count += test_find_nearest_neighbors_all_value_types< tracktable::domain::terrestrial::base_point_type >();
  error_count += test_find_nearest_neighbors_all_value_types< tracktable::domain::cartesian2d::base_point_type >();
  error_count += test_find_nearest_neighbors_all_value_types< tracktable::domain::cartesian3d::base_point_type >();

  std::cout << "\n\n\n";

  error_count += test_find_points_inside_box_all_value_types< tracktable::domain::terrestrial::base_point_type >(9);
  error_count += test_find_points_inside_box_all_value_types< tracktable::domain::cartesian2d::base_point_type >(9);
  error_count += test_find_points_inside_box_all_value_types< tracktable::domain::cartesian3d::base_point_type >(9);


  std::cout << "\n\n\n";

  error_count += test_find_points_strictly_inside_box_all_value_types< tracktable::domain::terrestrial::trajectory_point_type >(7);
  error_count += test_find_points_strictly_inside_box_all_value_types< tracktable::domain::cartesian2d::trajectory_point_type >(7);
  error_count += test_find_points_strictly_inside_box_all_value_types< tracktable::domain::cartesian3d::trajectory_point_type >(7);


  std::cout << "\n\n\n";

  error_count += test_find_nearest_neighbors_all_value_types< tracktable::domain::terrestrial::trajectory_point_type >();
  error_count += test_find_nearest_neighbors_all_value_types< tracktable::domain::cartesian2d::trajectory_point_type >();
  error_count += test_find_nearest_neighbors_all_value_types< tracktable::domain::cartesian3d::trajectory_point_type >();

  return (error_count != 0);
}
