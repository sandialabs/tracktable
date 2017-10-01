/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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

#ifndef __tracktable_PointBase_h
#define __tracktable_PointBase_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/detail/algorithm_signatures/Intersects.h>
#include <tracktable/Core/detail/points/AssignCoordinates.h>
#include <tracktable/Core/detail/points/CheckCoordinateEquality.h>
#include <tracktable/Core/detail/trait_signatures/Dimension.h>
#include <tracktable/Core/detail/trait_signatures/Tag.h>
#include <tracktable/Core/detail/trait_signatures/HasObjectId.h>
#include <tracktable/Core/detail/trait_signatures/HasProperties.h>
#include <tracktable/Core/detail/trait_signatures/HasTimestamp.h>
#include <tracktable/Core/detail/trait_signatures/UndecoratedPoint.h>

#include <cstddef>
#include <cassert>
#include <vector>

#include <boost/geometry/core/coordinate_dimension.hpp>
#include <boost/geometry/core/coordinate_type.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/geometries/register/linestring.hpp>
#include <boost/geometry/geometries/register/point.hpp>
#include <boost/mpl/int.hpp>


namespace tracktable {

/** Base class for all points in Tracktable
 * \ingroup Tracktable_CPP
 *
 * This class defines a point independent of the number of coordinates
 * or the data type.  You will not use this directly.  Instead, you'll
 * use one of the coordinate-specific versions like PointBaseCartesian
 * or PointBaseLonLat.
 *
 * PointBase and all of its subclasses will be registered with
 * boost::geometry so that you can use all of the generic geometry
 * algorithms.
 */

template<std::size_t Dimension>
class PointBase
{
public:
  typedef tracktable::settings::point_coordinate_type coordinate_type;
  typedef tracktable::settings::point_coordinate_type element_type;

  /// Initialize an empty point
  PointBase() { }

  /// Initialize a copy of another point
  PointBase(PointBase const& other)
    {
      detail::assign_coordinates<Dimension>::apply(*this, other);
    }

  /** Destructor for our descendants
   *
   * Although PointBase itself only needs a trivial destructor, we
   * know that subclasses are going to extend it one way or another.
   */
  virtual ~PointBase() { }

  /** Get the value of a particular coordinate
   *
   * Since this is Boost, you set and get coordinates by specifying
   * the coordinate at compile time:
   *
   * `double x = point.get<0>();`
   */

  template<std::size_t d>
  coordinate_type const& get() const
    {
      BOOST_STATIC_ASSERT(d >= 0);
      BOOST_STATIC_ASSERT(d < Dimension);
      return this->Coordinates[d];
    }

  /** Set the value of a particular coordinate
   *
   * Since this is Boost, you set and get coordinates by specifying
   * the coordinate at compile time:
   *
   * point.set<0>(new_value);
   */

  template<std::size_t d>
  void set(coordinate_type const& value)
    {
      BOOST_STATIC_ASSERT(d >= 0);
      BOOST_STATIC_ASSERT(d < Dimension);
      this->Coordinates[d] = value;
    }

  /** Get/set the value of a coordinate
   *
   * You can use operator[] whether or not you know the coordinate you
   * want ahead of time.
   *
   * double x = point[0];
   * point[0] = x;
   */

  coordinate_type const& operator[](std::size_t d) const
    {
      assert(d >= 0 && d < Dimension);
      return this->Coordinates[d];
    }

  /** Get/set the value of a coordinate
   *
   * You can use operator[] whether or not you know the coordinate you
   * want ahead of time.
   *
   * double x = point[0];
   * point[0] = x;
   */

  coordinate_type& operator[](std::size_t d)
    {
      assert(d >= 0 && d < Dimension);
      return this->Coordinates[d];
    }

  /** Check two points for equality
   *
   * This requires that the two points have the same dimension.
   */
  bool operator==(PointBase const& other) const
    {
      return detail::check_coordinate_equality<Dimension>::apply(*this, other);
    }

  /** Check two points for inequality
   */
  bool operator!=(PointBase const& other) const
    {
      return ((*this == other) == false);
    }

  /** Make this point a copy of a different one
   */
  PointBase& operator=(PointBase const& other)
    {
      detail::assign_coordinates<Dimension>::apply(*this, other);
      return *this;
    }

  /** Get the number of dimensions in this point
   */

  std::size_t size() const
    {
      return Dimension;
    }

protected:
  /// Storage for the coordinate values
  coordinate_type Coordinates[Dimension];
};

} // exit namespace tracktable

// We need to tell boost::geometry a few things about PointBase so
// that we can copy coordinates back and forth.  This does not
// actually make the class usable with boost::geometry.  Among other
// things, it's missing a coordinate system.

namespace boost { namespace geometry { namespace traits {

template<std::size_t Dimension>
struct tag< tracktable::PointBase<Dimension> >
{
  typedef point_tag type;
};

template<std::size_t Dimension>
struct coordinate_type< tracktable::PointBase<Dimension> >
{
  typedef typename tracktable::PointBase<Dimension>::coordinate_type type;
};

template<std::size_t Dimension>
struct dimension< tracktable::PointBase<Dimension> > : ::boost::mpl::int_<Dimension> {};

} } } // exit namespace boost::geometry::traits


namespace tracktable { namespace traits {

template<std::size_t Dimension>
struct dimension< tracktable::PointBase<Dimension> > : ::boost::mpl::size_t<Dimension> {};

template<std::size_t Dimension>
struct undecorated_point< PointBase<Dimension> >
{
  typedef PointBase<Dimension> type;
};

} }

// This will make a std::vector of points usable as a linestring all through Tracktable.
BOOST_GEOMETRY_REGISTER_LINESTRING_TEMPLATED(std::vector)

#endif
