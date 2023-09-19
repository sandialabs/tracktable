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

#ifndef __tracktable_RTree_h
#define __tracktable_RTree_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Box.h>

#include <algorithm>
#include <utility>
#include <vector>

#include <boost/tuple/tuple.hpp>
#include <boost/tuple/tuple_comparison.hpp>

#include <tracktable/Analysis/GuardedBoostGeometryRTreeHeader.h>

namespace bgi = boost::geometry::index;

namespace tracktable {

/**
 * This is a wrapper for the Boost rtree implementation in
 * boost::geometry::index. Its purpose is to insulate you, the user,
 * from having to care about all the complexity (and power) involved
 * in boost::geometry::index::rtree. You supply a value type (which
 * can be a point, a pair or a tuple) and we do the rest.
 *
 * The disadvantage is that you're restricted from using some of the
 * more powerful query capabilities, including user-defined predicates
 * and query combination.
 *
 * Quick Start:
 *
 * @code
 *
 * typedef tracktable::RTree<my_point_type> rtree_type;
 *
 * rtree_type my_tree;
 *
 * for (int i = 0; i < my_points.size(); ++i)
 *   my_tree.insert(my_points[i]);
 *
 * std::vector<my_point_type> results;
 *
 * my_tree.find_points_inside_box(min_corner, max_corner, std::back_inserter(results));
 *
 * @endcode
 *
 * (your results vector now contains all the points inside the box)
 *
 * You can populate this R-tree with any point type known to
 * Tracktable / boost::geometry. This includes base_point_type and
 * trajectory_point_type from all the domains as well as any other
 * point that you have registered with boost::geometry.
 *
 * You can also populate the R-tree with `std::pair<>`s and
 * `boost::tuple<>`s where the first element of the pair / tuple is one
 * of the point types listed above. Note that when you query the
 * r-tree, *only* the geometry will be used in the query: the
 * auxiliary information is preserved but never compared.
 *
 * When querying the r-tree, you must use the same geometric point
 * type that you used to populate it. Like the values stored in the
 * tree, you can specify the search point(s) as a point type, a
 * `std::pair<>` or a `boost::tuple<>` whose first element is the
 * geometry. This is just for convenience: the only part that will be
 * used for the search is the geometry.
 *
 * You may only modify the contents of the R-tree with `insert()`,
 * `remove()` and `clear()`. There is no way to get a reference to an
 * internal element and modify it directly as you can do with
 * std::vector, std::map and friends. Doing so would break the search
 * structure.
 */
template<
  typename value_type,
  typename rtree_algorithm_type = bgi::quadratic<16>
  >
class RTree
{
public:
  typedef bgi::rtree<value_type, rtree_algorithm_type> rtree_type;
  typedef typename rtree_type::const_query_iterator query_result_iterator_type;
  typedef std::pair<query_result_iterator_type, query_result_iterator_type> query_result_range_type;
  typedef typename rtree_type::size_type size_type;

  /** Instantiate an empty RTree
   */
  RTree() { };

  /// Destructor
  ~RTree() { };

  /** Copy contructor, create an RTree with a copy of another
   *
   * @param [in] other RTree to copy from
   */
  RTree(RTree const& other)
    : _RTree(other._RTree)
    { }

  /** Assign a RTree to the value of another.
   *
   * @param [in] other RTree to assign value of
   * @return RTree with the new assigned value
   */
  RTree& operator=(RTree const& other)
    {
      this->_RTree = rtree_type(other._RTree);
      return *this;
    }

  /** Check whether one RTree is equal to another.
   *
   * @param [in] other RTree for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(RTree const& other) const
    {
      return (this->_RTree == other._RTree);
    }

  /** Check whether two RTrees are unequal.
   *
   * @param [in] other RTree for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(RTree const& other) const
    {
      return !(*this == other);
    }

  /** Create and populate an RTree from a range of elements.
   *
   * If you have a container of points you can use this constructor to
   * create and populate the tree in one swell foop instead of adding
   * elements one at a time.
   *
   * @param [in] range_begin  Iterator pointing to beginning of input points
   * @param [in] range_end    Iterator pointing past end of input points
   */
  template<typename value_iterator_type>
  RTree(value_iterator_type range_begin,
        value_iterator_type range_end)
    {
      this->_RTree.insert(range_begin, range_end);
    }

  /** Insert a single element into an RTree
   *
   * @param [in] value   Element to insert (will be copied)
   */
  void insert(value_type const& value)
    {
      this->_RTree.insert(value);
    }

  /** Insert multiple elements into an RTRee
   *
   * @param [in] range_begin   Iterator pointing to beginning of input points
   * @param [in] range_end     Iterator pointing past end of input points
   */
  template<typename value_iterator_type>
  void insert(value_iterator_type range_begin,
              value_iterator_type range_end)
    {
      this->_RTree.insert(range_begin, range_end);
    }
  /** Remove a single element from the RTree
   *
   * @param [in] value  Element to remove
   * @return 1 if the element was removed, 0 otherwise
   */
  size_type remove(value_type const& value)
    {
      return this->_RTree.remove(value);
    }

  /** Remove many elements from the RTree
   *
   * @param [in] range_begin  First element to remove
   * @param [in] range_end    Past last element to remove
   * @return                Number of removed values
   */
  template<typename value_iterator_type>
  size_type remove(value_iterator_type range_begin,
                   value_iterator_type range_end)
    {
      return this->_RTree.remove(range_begin, range_end);
    }

  /** Return number of elements in RTree
   *
   * @return Non-negative integer (number of elements)
   */
  std::size_t size() const
    {
      return this->_RTree.size();
    }

  /** Check whether an rtree is empty
   *
   * @return Boolean explaining whether or not size() == 0
   */
  bool empty() const
    {
      return this->_RTree.empty();
    }

  /** Empty out an rtree
   *
   * This function will completely reset an rtree to its un-populated
   * state.
   */
  void clear()
    {
      this->_RTree.clear();
    }

  /** Find points inside a search box (output sink version)
   *
   * @fn Rtree::void find_points_inside_box(corner_type const& min_corner, corner_type const& max_corner, insert_iter_type result_sink) const
   *
   * This function finds points inside a box specified as two corners.
   * You must provide an InsertIterator as the third argument. This
   * iterator will be used to save the results.
   *
   * Example:
   *
   * @code
   *
   *    my_point min_corner, max_corner;
   *    std::vector<my_point> results;
   *
   *    my_tree.find_points_inside_box(min_corner, max_corner, std::back_inserter(results));
   *
   * @endcode
   *
   * Note that this function will return points that are exactly on
   * the boundary of the search box as well as those in the interior.
   * If you want only the points in the interior, use
   * `find_points_strictly_inside_box`.
   *
   * As with all the other RTree functions, you can use a point type,
   * a `std::pair<point_type, X>` or a `boost::tuple<point, type, [other
   * stuff]>` for your searches. In the case of a `std::pair` or
   * `boost::tuple`, your geometry type must be the first element.
   *
   * @param [in] min_corner   Corner at minimum end of search box
   * @param [in] max_corner   Corner at maximum end of search box
   * @param [in] result_sink  InsertIterator where results will be stored
   */
  template<typename corner_type, typename insert_iter_type>
  void find_points_inside_box(corner_type const& min_corner,
                              corner_type const& max_corner,
                              insert_iter_type result_sink) const
    {
      Box<corner_type> search_box(min_corner, max_corner);
      this->_find_points_inside_box(search_box, result_sink);
    }

  /**
   * @overload Rtree::void find_points_inside_box(std::pair<corner_type, T2> const& min_corner, std::pair<corner_type, T2> const& max_corner, insert_iter_type result_sink) const
   */
  template<typename corner_type, typename T2, typename insert_iter_type>
  void find_points_inside_box(std::pair<corner_type, T2> const& min_corner,
                              std::pair<corner_type, T2> const& max_corner,
                              insert_iter_type result_sink) const
    {
      Box<corner_type> search_box(min_corner.first, max_corner.first);
      this->_find_points_inside_box(search_box, result_sink);
    }

  /**
   * @overload Rtree::void find_points_inside_box(boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& min_corner, boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& max_corner, insert_iter_type result_sink) const
  */
  template<
    typename corner_type,
    typename insert_iter_type,
    typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9
    >
  void find_points_inside_box(
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& min_corner,
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& max_corner,
    insert_iter_type result_sink
    ) const
    {
      Box<corner_type> search_box(min_corner.template get<0>(),
                                  max_corner.template get<0>());
      this->_find_points_inside_box(search_box, result_sink);
    }

  /** Find points inside a search box (iterator range version)
   *
   * @fn Rtree::query_result_range_type find_points_inside_box(corner_type const& min_corner, corner_type const& max_corner) const
   *
   * This function finds points inside a box specified as a
   * tracktable::Box (also known as a tracktable::RTree<point_type>::box_type).
   *
   * Example:
   *
   * @code
   *
   *    typedef typename tracktable::RTree<my_point>::query_result_range_type query_result_type;
   *    my_point min_corner, max_corner;
   *
   *    query_result_type result_range =
   *    my_tree.find_points_inside_box(min_corner, max_corner);
   *
   *    std::vector<my_point> results(result_range.first, result_range.second);
   *
   * @endcode
   *
   * Note that this function will return points that are exactly on
   * the boundary of the search box as well as those in the interior.
   * If you want only the points in the interior, use
   * `find_points_strictly_inside_box`.
   *
   * As with all the other RTree functions, you can use a point type,
   * a `std::pair<point_type, X>` or a `boost::tuple<point, type, [other
   * stuff]>` for your searches. In the case of a `std::pair` or
   * `boost::tuple`, your geometry type must be the first element.
   *
   * @warning
   *    This function is sensitive to numerical
   *    imprecision issues when points are (allegedly) right on the
   *    border of the search box. This is especially problematic in
   *    the terrestrial domain (longitude/latitude points) since we
   *    have to do trigonometry to compute point-in-polygon results.
   *
   * @param [in] min_corner   Corner at minimum end of search box
   * @param [in] max_corner   Corner at maximum end of search box
   * @return   Pair of iterators pointing to query result range
   */
  template<typename corner_type>
  query_result_range_type
  find_points_inside_box(corner_type const& min_corner,
                         corner_type const& max_corner) const
    {
      tracktable::Box<corner_type> search_box(min_corner, max_corner);
      return this->_find_points_inside_box(search_box);
    }

  /**
   * @overload Rtree::query_result_range_type find_points_inside_box(std::pair<corner_type, T2> const& min_corner, std::pair<corner_type, T2> const& max_corner) const
   */
  template<typename corner_type, typename T2>
  query_result_range_type
  find_points_inside_box(std::pair<corner_type, T2> const& min_corner,
                         std::pair<corner_type, T2> const& max_corner) const
    {
      tracktable::Box<corner_type> search_box(min_corner.first, max_corner.first);
      return this->_find_points_inside_box(search_box);
    }

  /**
   * @overload Rtree::query_result_range_type find_points_inside_box(boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner, boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner)
   */
  template<typename corner_type,
           typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9, typename T10>
  query_result_range_type
  find_points_inside_box(
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner,
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner
    )
    {
      tracktable::Box<corner_type> search_box(min_corner.template get<0>(),
                                              max_corner.template get<0>());
      return this->_find_points_inside_box(search_box);
    }

  /** Find points strictly inside a search box
   *
   * @fn Rtree::void find_points_strictly_inside_box(corner_type const& min_corner, corner_type const& max_corner, insert_iter_type result_sink) const
   *
   * This function finds points inside a box specified as two corners.
   * You must provide an InsertIterator as the third argument. This
   * iterator will be used to save the results.
   *
   * Example:
   *
   * @code
   *
   *    my_point min_corner, max_corner;
   *    std::vector<my_point> results;
   *
   *    my_tree.find_points_strictly_inside_box(min_corner, max_corner, std::back_inserter(results));
   *
   * @endcode
   *
   * Note that this function will return points that are strictly
   * within the box. Points on the border will not be returned. If
   * you want points on the border, use `find_points_inside_box`.
   *
   * As with all the other RTree functions, you can use a point type,
   * a `std::pair<point_type, X>` or a `boost::tuple<point, type, [other
   * stuff]>` for your searches. In the case of a `std::pair` or
   * `boost::tuple`, your geometry type must be the first element.
   *
   * @param [in] min_corner   Corner at minimum end of search box
   * @param [in] max_corner   Corner at maximum end of search box
   * @param [in] result_sink  InsertIterator where results will be stored
   */
  template<typename corner_type, typename insert_iter_type>
  void find_points_strictly_inside_box(corner_type const& min_corner,
                                       corner_type const& max_corner,
                                       insert_iter_type result_sink) const
    {
      Box<corner_type> search_box(min_corner, max_corner);
      this->_find_points_strictly_inside_box(search_box, result_sink);
    }

  /**
   * @overload Rtree::void find_points_strictly_inside_box(std::pair<corner_type, T2> const& min_corner, std::pair<corner_type, T2> const& max_corner, insert_iter_type result_sink) const
   */
  template<typename corner_type, typename T2, typename insert_iter_type>
  void find_points_strictly_inside_box(std::pair<corner_type, T2> const& min_corner,
                                       std::pair<corner_type, T2> const& max_corner,
                                       insert_iter_type result_sink) const
    {
      Box<corner_type> search_box(min_corner.first, max_corner.first);
      this->_find_points_strictly_inside_box(search_box, result_sink);
    }

  /**
   * @overload Rtree::void find_points_strictly_inside_box(boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner, boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner, insert_iter_type result_sink) const
   */
  template<
    typename corner_type,
    typename insert_iter_type,
    typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9, typename T10
    >
  void find_points_strictly_inside_box(
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner,
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner,
    insert_iter_type result_sink
    ) const
    {
      Box<corner_type> search_box(min_corner.template get<0>(),
                                  max_corner.template get<0>());
      this->_find_points_strictly_inside_box(search_box, result_sink);
    }

  /** Find points inside a search box (iterator range version)
   *
   * @fn Rtree::query_result_range_type find_points_strictly_inside_box(corner_type const& min_corner, corner_type const& max_corner) const
   *
   * This function finds points inside a box specified as a
   * tracktable::Box (also known as a tracktable::RTree<point_type>::box_type).
   *
   * Example:
   *
   * @code
   *
   *    typedef typename tracktable::RTree<my_point>::query_result_range_type query_result_type;
   *    my_point min_corner, max_corner;
   *
   *    query_result_type result_range =
   *    my_tree.find_points_strictly_inside_box(min_corner, max_corner);
   *
   *    std::vector<my_point> results(result_range.first, result_range.second);
   *
   * @endcode
   *
   * Note that this function will return points that are strictly
   * within the box. Points on the border will not be returned. If
   * you want points on the border, use `find_points_inside_box`.
   *
   * As with all the other RTree functions, you can use a point type,
   * a `std::pair<point_type, X>` or a `boost::tuple<point, type, [other
   * stuff]>` for your searches. In the case of a `std::pair` or
   * `boost::tuple`, your geometry type must be the first element.
   *
   * @param [in] min_corner   Corner at minimum end of search box
   * @param [in] max_corner   Corner at maximum end of search box
   * @return   Pair of iterators pointing to query result range
   */
  template<typename corner_type>
  query_result_range_type
  find_points_strictly_inside_box(corner_type const& min_corner,
                                  corner_type const& max_corner) const
    {
      Box<corner_type> search_box(min_corner, max_corner);
      return this->_find_points_strictly_inside_box(search_box);
    }


  /**
   * @overload Rtree::query_result_range_type find_points_strictly_inside_box(std::pair<corner_type, T2> const& min_corner, std::pair<corner_type, T2> const& max_corner) const
   */
  template<typename corner_type, typename T2>
  query_result_range_type
  find_points_strictly_inside_box(std::pair<corner_type, T2> const& min_corner,
                                  std::pair<corner_type, T2> const& max_corner) const
    {
      Box<corner_type> search_box(min_corner.first, max_corner.first);
      return this->_find_points_strictly_inside_box(search_box);
    }


  /**
   * @overload Rtree::query_result_range_type find_points_strictly_inside_box(boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner, boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner)
   */
  template<typename corner_type,
           typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9, typename T10>
  query_result_range_type
  find_points_strictly_inside_box(
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner,
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner
    )
    {
      tracktable::Box<corner_type> search_box(min_corner.template get<0>(),
                                              max_corner.template get<0>());
      return this->_find_points_strictly_inside_box(search_box);
    }

  /** Find points inside a search box (output sink version)
   *
   * @fn Rtree::void intersects(corner_type const& min_corner, corner_type const& max_corner, insert_iter_type result_sink) const
   *
   * This function finds points/objects that are not disjoint from the box
   * You must provide an InsertIterator as the third argument. This
   * iterator will be used to save the results.
   *
   * Example:
   *
   * @code
   *
   *    my_point min_corner, max_corner;
   *    std::vector<my_point> results;
   *
   *    my_tree.intersects(min_corner, max_corner, std::back_inserter(results));
   *
   * @endcode
   *
   * Note that this function will return points that are exactly on
   * the boundary of the search box as well as those in the interior.
   * If you want only the points in the interior, use
   * `find_points_strictly_inside_box`.
   *
   * As with all the other RTree functions, you can use a point type,
   * a `std::pair<point_type, X>` or a `boost::tuple<point, type, [other
   * stuff]>` for your searches. In the case of a `std::pair` or
   * `boost::tuple`, your geometry type must be the first element.
   *
   * @param [in] min_corner   Corner at minimum end of search box
   * @param [in] max_corner   Corner at maximum end of search box
   * @param [in] result_sink  InsertIterator where results will be stored
   */
  template<typename corner_type, typename insert_iter_type>
  void intersects(corner_type const& min_corner,
                              corner_type const& max_corner,
                              insert_iter_type result_sink) const
    {
      Box<corner_type> search_box(min_corner, max_corner);
      this->_intersects(search_box, result_sink);
    }

  /**
   * @overload Rtree::void intersects(std::pair<corner_type, T2> const& min_corner, std::pair<corner_type, T2> const& max_corner, insert_iter_type result_sink) const
   */
  template<typename corner_type, typename T2, typename insert_iter_type>
  void intersects(std::pair<corner_type, T2> const& min_corner,
                              std::pair<corner_type, T2> const& max_corner,
                              insert_iter_type result_sink) const
    {
      Box<corner_type> search_box(min_corner.first, max_corner.first);
      this->_intersects(search_box, result_sink);
    }

  /**
   * @overload Rtree::void intersects(boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& min_corner, boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& max_corner, insert_iter_type result_sink) const
  */
  template<
    typename corner_type,
    typename insert_iter_type,
    typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9
    >
  void intersects(
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& min_corner,
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9> const& max_corner,
    insert_iter_type result_sink
    ) const
    {
      Box<corner_type> search_box(min_corner.template get<0>(),
                                  max_corner.template get<0>());
      this->_intersects(search_box, result_sink);
    }

  /** Find points inside a search box (iterator range version)
   *
   * @fn Rtree::query_result_range_type intersects(corner_type const& min_corner, corner_type const& max_corner) const
   *
   * This function finds points inside a box specified as a
   * tracktable::Box (also known as a tracktable::RTree<point_type>::box_type).
   *
   * Example:
   *
   * @code
   *
   *    typedef typename tracktable::RTree<my_point>::query_result_range_type query_result_type;
   *    my_point min_corner, max_corner;
   *
   *    query_result_type result_range =
   *    my_tree.intersects(min_corner, max_corner);
   *
   *    std::vector<my_point> results(result_range.first, result_range.second);
   *
   * @endcode
   *
   * Note that this function will return points that are exactly on
   * the boundary of the search box as well as those in the interior.
   * If you want only the points in the interior, use
   * `find_points_strictly_inside_box`.
   *
   * As with all the other RTree functions, you can use a point type,
   * a `std::pair<point_type, X>` or a `boost::tuple<point, type, [other
   * stuff]>` for your searches. In the case of a `std::pair` or
   * `boost::tuple`, your geometry type must be the first element.
   *
   * @warning
   *    This function is sensitive to numerical
   *    imprecision issues when points are (allegedly) right on the
   *    border of the search box. This is especially problematic in
   *    the terrestrial domain (longitude/latitude points) since we
   *    have to do trigonometry to compute point-in-polygon results.
   *
   * @param [in] min_corner   Corner at minimum end of search box
   * @param [in] max_corner   Corner at maximum end of search box
   * @return   Pair of iterators pointing to query result range
   */
  template<typename corner_type>
  query_result_range_type
  intersects(corner_type const& min_corner,
                         corner_type const& max_corner) const
    {
      tracktable::Box<corner_type> search_box(min_corner, max_corner);
      return this->_intersects(search_box);
    }

  /**
   * @overload Rtree::query_result_range_type intersects(std::pair<corner_type, T2> const& min_corner, std::pair<corner_type, T2> const& max_corner) const
   */
  template<typename corner_type, typename T2>
  query_result_range_type
  intersects(std::pair<corner_type, T2> const& min_corner,
                         std::pair<corner_type, T2> const& max_corner) const
    {
      tracktable::Box<corner_type> search_box(min_corner.first, max_corner.first);
      return this->_intersects(search_box);
    }

  /**
   * @overload Rtree::query_result_range_type intersects(boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner, boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner)
   */
  template<typename corner_type,
           typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9, typename T10>
  query_result_range_type
  intersects(
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& min_corner,
    boost::tuple<corner_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& max_corner
    )
    {
      tracktable::Box<corner_type> search_box(min_corner.template get<0>(),
                                              max_corner.template get<0>());
      return this->_intersects(search_box);
    }

  /** Find points near a search point (output iterator version)
   *
   * @fn Rtree::void find_nearest_neighbors(search_point_type const& search_point, unsigned int num_neighbors, insert_iter_type result_sink) const
   *
   * This function finds the K nearest neighbors to a search point.
   * Note that if the search point is already present in the R-tree
   * then it will be one of the results returned.
   *
   * You must provide an output iterator as a place to store the
   * results.
   *
   * Example:
   *
   * @code
   *
   *    tracktable::RTree<my_point> tree;
   *    my_point search_point;
   *    std::vector<my_point> neighbors;
   *
   *    tree.find_nearest_neighbors(search_point, 10, std::back_inserter(neighbors));
   *
   * @endcode
   *
   * @param [in]  search_point   Point whose neighbors you want to find
   * @param [in]  num_neighbors  How many neighbors to find
   * @param [in]  result_sink    Where to write the results
   */
  template<typename search_point_type, typename insert_iter_type>
  void find_nearest_neighbors(search_point_type const& search_point,
                              unsigned int num_neighbors,
                              insert_iter_type result_sink) const
    {
      this->_find_nearest_neighbors(search_point, num_neighbors, result_sink);
    }

  /**
   * @overload Rtree::void find_nearest_neighbors(std::pair<search_point_type, T2> const& search_point, unsigned int num_neighbors, insert_iter_type result_sink) const
   */
  template<typename search_point_type, typename T2, typename insert_iter_type>
  void find_nearest_neighbors(std::pair<search_point_type, T2> const& search_point,
                              unsigned int num_neighbors,
                              insert_iter_type result_sink) const
    {
      this->_find_nearest_neighbors(search_point.first, num_neighbors, result_sink);
    }

  /**
   * @overload Rtree::void find_nearest_neighbors(std::pair<search_point_type, T2> const& search_point, unsigned int num_neighbors, insert_iter_type result_sink) const
   */
  template<typename search_point_type,
           typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9, typename T10,
           typename insert_iter_type>
  void find_nearest_neighbors(
    boost::tuple<search_point_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& search_point,
    unsigned int num_neighbors,
    insert_iter_type result_sink
    ) const
    {
      this->_find_nearest_neighbors(search_point.template get<0>(), num_neighbors, result_sink);
    }

  /** Find points near a search point (iterator range version)
   *
   * @fn Rtree::query_result_range_type find_nearest_neighbors(search_point_type const& search_point, unsigned int num_neighbors) const
   *
   * This function finds the K nearest neighbors to a search point.
   * Note that if the search point is already present in the R-tree
   * then it will be one of the results returned.
   *
   * The result is returned as a pair of iterators.
   *
   * Example:
   *
   * @code
   *
   *    typedef typename tracktable::RTree<my_point>::query_result_range_type query_result_type;
   *    tracktable::RTree<my_point> tree;
   *    my_point search_point;
   *    std::vector<my_point> neighbors;
   *
   *    query_result_type result_range =
   *    my_tree.find_nearest_neighbors(search_point, 10);
   *
   *    neighbors.assign(result_range.first, result_range.second);
   *
   * @endcode
   *
   * @param [in]  search_point   Point whose neighbors you want to find
   * @param [in]  num_neighbors  How many neighbors to find
   * @return    Pair of iterators pointing to neighboring points
   */
  template<typename search_point_type>
  query_result_range_type
  find_nearest_neighbors(search_point_type const& search_point,
                         unsigned int num_neighbors) const
    {
      return this->_find_nearest_neighbors(search_point, num_neighbors);
    }

  /**
   * @overload Rtree::query_result_range_type find_nearest_neighbors(std::pair<search_point_type, T2> const& search_point, unsigned int num_neighbors) const
   */
  template<typename search_point_type, typename T2>
  query_result_range_type
  find_nearest_neighbors(std::pair<search_point_type, T2> const& search_point,
                         unsigned int num_neighbors) const
    {
      return this->_find_nearest_neighbors(search_point.first, num_neighbors);
    }

  /**
   * @overload Rtree::query_result_range_type find_nearest_neighbors( boost::tuple<search_point_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& search_point, unsigned int num_neighbors)
   */
  template<typename search_point_type,
           typename T2, typename T3, typename T4, typename T5, typename T6, typename T7, typename T8, typename T9, typename T10>
  query_result_range_type
  find_nearest_neighbors(
    boost::tuple<search_point_type, T2, T3, T4, T5, T6, T7, T8, T9, T10> const& search_point,
    unsigned int num_neighbors
    )
    {
      return this->_find_nearest_neighbors(search_point.template get<0>(), num_neighbors);
    }

private:
  rtree_type _RTree;

  /** @internal
   */
  template<typename box_type, typename insert_iter_type>
  void _find_points_inside_box(box_type const& search_box,
                               insert_iter_type result_sink) const
    {
      this->_copy_range_to_output(this->_find_points_inside_box(search_box), result_sink);
    }

  /** @internal
   */
  template<typename box_type>
  query_result_range_type _find_points_inside_box(box_type const& search_box) const
    {
      return query_result_range_type(
        this->_RTree.qbegin(bgi::covered_by(search_box)),
        this->_RTree.qend()
        );
    }

  /** @internal
   */
  template<typename box_type, typename insert_iter_type>
  void _intersects(box_type const& search_box,
                               insert_iter_type result_sink) const
    {
      this->_copy_range_to_output(this->_intersects(search_box), result_sink);
    }

  /** @internal
   */
  template<typename box_type>
  query_result_range_type _intersects(box_type const& search_box) const
    {
      return query_result_range_type(
        this->_RTree.qbegin(bgi::intersects(search_box)),
        this->_RTree.qend()
        );
    }

  /** @internal
   */
  template<typename box_type, typename insert_iter_type>
  void _find_points_strictly_inside_box(box_type const& search_box, insert_iter_type output_sink) const
    {
      this->_copy_range_to_output(this->_find_points_strictly_inside_box(search_box),
                                 output_sink);
    }

  /** @internal
   */
  template<typename box_type>
  query_result_range_type
  _find_points_strictly_inside_box(box_type const& search_box) const
    {
      return query_result_range_type(this->_RTree.qbegin(bgi::within(search_box)),
                                     this->_RTree.qend());
    }

  /** @internal
   */
  template<typename search_point_type, typename insert_iter_type>
  void _find_nearest_neighbors(search_point_type const& search_point,
                               unsigned int num_neighbors,
                               insert_iter_type output_sink) const
    {
      this->_copy_range_to_output(this->_find_nearest_neighbors(search_point, num_neighbors),
                                  output_sink);
    }

  /** @internal
   */
  template<typename search_point_type>
  query_result_range_type _find_nearest_neighbors(search_point_type const& search_point,
                                                  unsigned int num_neighbors) const
    {
      return query_result_range_type(this->_RTree.qbegin(bgi::nearest(search_point, num_neighbors)),
                                     this->_RTree.qend());
    }

  /** @internal
   */
  template<typename iterator_range_type,
           typename output_iterator_type>
  void _copy_range_to_output(iterator_range_type range,
                             output_iterator_type output_sink) const
    {
      while (range.first != range.second)
        {
        *output_sink = *(range.first);
        ++output_sink;
        ++(range.first);
        }
    }
};

} // close namespace tracktable

#endif
