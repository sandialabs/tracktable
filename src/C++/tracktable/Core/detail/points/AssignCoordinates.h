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

#ifndef __tracktable_detail_points_AssignCoordinates_h
#define __tracktable_detail_points_AssignCoordinates_h

#include <cassert>
#include <cstddef>
#include <boost/geometry/core/coordinate_dimension.hpp>
#include <boost/geometry/core/coordinate_type.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/geometries/register/point.hpp>
#include <boost/mpl/int.hpp>

namespace tracktable { namespace detail {

/** Helper object that implements assignment
 *
 * This is for boost::geometry.  You will not need to use it directly.
 */

template<std::size_t i>
struct assign_coordinates
{
  /// Run the compile-time loop unrolling to perform assignment
  template<class dest_point_type, class source_point_type>
  static inline void apply(dest_point_type & dest, source_point_type const& source)
    {
      boost::geometry::assert_dimension_equal<dest_point_type, source_point_type>();
      dest.template set<i-1>(source.template get<i-1>());
      assign_coordinates<i-1>::apply(dest, source);
    }
};

/** Helper object that implements a = b
 *
 * This is for boost::geometry.  You will not need to use it directly.
 */

template<>
struct assign_coordinates<0>
{
  /// Terminate the compile-time unrolling for assignment
  template<class dest_point_type, class source_point_type>
  static inline void apply(dest_point_type const& /*dest*/, source_point_type const& /*source*/)
    {
      return;
    }
};

/** Helper object that implements assignment from an array
 *
 * You will rarely need to use this directly.
 */

template<std::size_t i>
struct assign_coordinates_from_array
{
  /// Run the compile-time loop unrolling to perform assignment
  template<class dest_point_type, typename input_coordinate_type>
  static inline void apply(dest_point_type & dest, const input_coordinate_type * source)
    {
      dest.template set<i-1>(source[i-1]);
      assign_coordinates<i-1>::apply(dest, source);
    }
};


/** Helper object that implements a = b
 *
 * This is for boost::geometry.  You will not need to use it directly.
 */

template<>
struct assign_coordinates_from_array<0>
{
  /// Terminate the compile-time unrolling for assignment
  template<class dest_point_type, typename input_coordinate_type>
  static inline void apply(dest_point_type const&, const input_coordinate_type *)
    {
      return;
    }
};

// ----------------------------------------------------------------------

} } // end namespace tracktable::detail


#endif
