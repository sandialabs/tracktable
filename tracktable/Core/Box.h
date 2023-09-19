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

#ifndef __tracktable_Box_h
#define __tracktable_Box_h

#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/CommonBoostWarnings.h>
#include <boost/geometry/geometries/box.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

#include <tracktable/Core/detail/algorithm_signatures/Intersects.h>

namespace tracktable {

/** Axis-aligned bounding box
 *
 * This class is a thin wrapper around `boost::geometry::model::box`
 * that holds two points representing opposite corners.
 *
 * @warning
 *    Don't instantiate this class directly. Instead, use
 *    \c "tracktable::domain::<name>::box_type" so that you get the correct
 *    distance functions.
 *
 */
template<typename point_type>
class Box : public boost::geometry::model::box<point_type>
{
public:
  typedef boost::geometry::model::box<point_type> Superclass;

  /** Construct the bounding box using `boost::geometry::model::box`
   *
   * @param [in] low_corner Minimum corner to use for creation of the box
   * @param [in] high_corner Maximum corner to use for creation of the box
   */
  Box(point_type const& low_corner, point_type const& high_corner)
    : Superclass(low_corner, high_corner)
    { }

  /// Destructor
  ~Box() { }
};

} // exit namespace tracktable

namespace boost { namespace geometry { namespace traits {

template<typename PointT>
struct point_type< tracktable::Box<PointT> > : point_type<boost::geometry::model::box<PointT> > {};

template<typename point_type>
struct tag< tracktable::Box<point_type> > : tag< boost::geometry::model::box<point_type> > {};

template <typename point_type, std::size_t index, std::size_t Dimension>
struct indexed_access< tracktable::Box<point_type>, index, Dimension> : indexed_access< boost::geometry::model::box<point_type>, index, Dimension> {};

} } } // close boost::geometry::traits


/** Write a box corners to a stream as a string
 *
 * @param [in] os Stream to write to
 * @param [in] box Box to write to string
 */
template<class PointType>
std::ostream& operator<< (std::ostream& os, tracktable::Box<PointType> const& box)
{
  std::ostringstream outbuf;
  outbuf << "<BoundingBox: " << box.min_corner() << " - " << box.max_corner() << ">";
  os << outbuf.str();
  return os;
}

/** Write a box corners to a stream as a string
 *
 * @param [in] os Stream to write to
 * @param [in] box Box to write to string
 */
template<class PointType>
std::ostream& operator<< (std::ostream& os, boost::geometry::model::box<PointType> const& box)
{
  std::ostringstream outbuf;
  outbuf << "<BoundingBox: ";
  outbuf << box.min_corner();
  outbuf << " - ";
  outbuf << box.max_corner();
  outbuf << ">";
  os << outbuf.str();
  return os;
}

#endif // guard
