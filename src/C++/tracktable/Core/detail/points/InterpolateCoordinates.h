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

#ifndef __tracktable_detail_InterpolateCoordinates_h
#define __tracktable_detail_InterpolateCoordinates_h

#include <cassert>

namespace tracktable { namespace detail {

// Helper object for interpolating coordinates

template<std::size_t i>
struct interpolate_coordinates
{
  template<class point_type>
  static inline void apply(point_type const& left, point_type const& right,
                           double t,
                           point_type& result)
    {
      result.template set<i-1>(
        (1-t) * left.template get<i-1>() +
        (t) * right.template get<i-1>()
        );

      interpolate_coordinates<i-1>::apply(left, right, t, result);
    }
};

template<>
struct interpolate_coordinates<0>
{
  /// Terminate the compile-time unrolling for assignment
  template<class point_type>
  static inline void apply(point_type const& /*left*/, point_type const& /*right*/,
                           double /*t*/,
                           point_type& /*result*/)
    {
      return;
    }
};


} } // end namespace tracktable::detail


#endif
