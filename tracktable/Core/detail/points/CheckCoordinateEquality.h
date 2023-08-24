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

#ifndef __tracktable_detail_CheckCoordinateEquality_h
#define __tracktable_detail_CheckCoordinateEquality_h

#include <cassert>
#include <boost/geometry/core/coordinate_dimension.hpp>
#include <boost/geometry/core/coordinate_type.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/geometries/register/point.hpp>
#include <boost/mpl/int.hpp>

#include <tracktable/Core/detail/points/AlmostEqual.h>

namespace tracktable { namespace detail {

/** Helper object for checking equality between points
 *
 * Compare two points for equality by comparing all of their
 * coordinates.  It is sufficient for the points to have the same
 * number of points and coordinates that compare equal: they need not
 * have the same data type.
 *
 * You will probably not need to instantiate this directly.  It is,
 * however, an illustration of how to iterate over an object's members
 * at compile time.  You need two classes.  First you need the version
 * below templated on i.  Then you need a specialization with i=0 to
 * serve as the base case.
 */

template<std::size_t i>
struct check_coordinate_equality
{
  template<class left_point_type, class right_point_type>
  static inline bool apply(left_point_type const& left, right_point_type const& right)
    {
      return (
        almost_equal(
          left.template get<i-1>(),
          right.template get<i-1>(),
          1e-6
          )
        &&
        check_coordinate_equality<i-1>::apply(left, right)
        );
    }
};

/** Helper object for checking equality between points
 *
 * Compare two points for equality by comparing all of their
 * coordinates.
 *
 * You will definitely not need to instantiate this object directly.
 * This is the base case for the iteration over the coordinates of a
 * point that causes the template instantiation to stop after looping
 * over all of the dimensions at compile time.
 */

template<>
struct check_coordinate_equality<0>
{
  template<class left_point_type, class right_point_type>
  static inline bool apply(left_point_type const& /*destination*/, right_point_type const& /*source*/)
    {
      return true;
    }
};

} } // end namespace tracktable::detail


#endif
