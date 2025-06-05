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

#ifndef __tracktable_dbscan_points_h
#define __tracktable_dbscan_points_h

#include <boost/tuple/tuple.hpp>

namespace tracktable { namespace analysis { namespace detail {

template< class ContainerT, class PointT >
class DBSCAN_IndexByIterator
{
public:
  typedef typename ContainerT::iterator        key_type;
  typedef typename ContainerT::const_reference const_reference_type;
  typedef PointT const&                        result_type;

  explicit DBSCAN_IndexByIterator(ContainerT const& c) : Container(c) { }
  result_type operator() (key_type iter) const { return (*iter).point(); }

private:
  ContainerT const& Container;
};

// ----------------------------------------------------------------------

/*! @brief Point plus index and cluster ID
 *
 * We keep our own list of points internally in DBSCAN along with an
 * index into the original list, a cluster ID (if set) and a flag to
 * use while building clusters.  This class encapsulates that
 * function.
 *
 * It would take less memory to use pointers into the original list of
 * points but at the cost of lots more places to trip ourselves up
 * with layers of indirection.  In the interest of working code, we'll
 * take the simpler-and-more-memory approach for now.
 *
 * Note that there is no particular intelligence in this class.  It's
 * just a container.
 */

template<class PointT>
class IndexedPoint
{
public:
  typedef PointT point_type;

  IndexedPoint() : PointId(-1), ClusterId(0) { }
  IndexedPoint(PointT const& point_to_index)
    : Point(point_to_index)
    , PointId(-1)
    , ClusterId(0)
    , Visited(false) { }

  IndexedPoint(PointT const& point_to_index, int index)
    : Point(point_to_index)
    , PointId(index)
    , ClusterId(0)
    , Visited(false) { }

  ~IndexedPoint() { }

  IndexedPoint(IndexedPoint const& other)
    : Point(other.Point),
      PointId(other.PointId),
      ClusterId(other.ClusterId),
      Visited(false)
    {
    }

  IndexedPoint& operator=(IndexedPoint const& other)
    {
      this->Point = other.Point;
      this->PointId = other.PointId;
      this->ClusterId = other.ClusterId;
      this->Visited = other.Visited;
      return *this;
    }

  bool operator==(IndexedPoint const& other) const
    {
      return (
        this->Point == other.Point &&
        this->PointId == other.PointId &&
        this->ClusterId == other.ClusterId &&
        this->Visited == other.Visited
        );
    }

  PointT const& point() const { return this->Point; }
  int point_id() const { return this->PointId; }
  int cluster_id() const { return this->ClusterId; }
  bool visited() const { return this->Visited; }

  void set_point(PointT const& pt) { this->Point = pt; }
  void set_point_id(int id) { this->PointId = id; }
  void set_cluster_id(int id) { this->ClusterId = id; }
  void set_visited(bool v) { this->Visited = v; }

protected:
  PointT Point;
  int PointId;
  int ClusterId;
  bool Visited;
};

// ----------------------------------------------------------------------

template<class point_type>
boost::geometry::model::box<point_type> make_box(const point_type& center, const point_type& half_span)
{
  typedef boost::geometry::model::box<point_type> box_type;

  point_type min_corner(center);
  point_type max_corner(center);

  boost::geometry::add_point(max_corner, half_span);
  boost::geometry::subtract_point(min_corner, half_span);

  return box_type(min_corner, max_corner);
}

} } } // close namespace tracktable::analysis::detail

#endif
