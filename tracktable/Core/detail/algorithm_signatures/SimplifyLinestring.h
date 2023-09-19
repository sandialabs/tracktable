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

/**
 * SimplifyLinestring: Translate a call to tracktable::simplify into a
 * call to boost::geometry::simplify
 *
 * By default, we forward the user's arguments (geometry to simplify,
 * tolerance) directly to boost::geometry::simplify for
 * Douglas-Peucker simplification.  We can override this (e.g. for
 * unit conversion) by specializing
 * tracktable::algorithms::simplify_linestring for particular point
 * types.
 *
 */

#ifndef __tracktable_algorithm_signatures_SimplifyLinestring_h
#define __tracktable_algorithm_signatures_SimplifyLinestring_h

#include <set>
#include <boost/geometry/algorithms/simplify.hpp>
#include <tracktable/Core/detail/trait_signatures/HasProperties.h>
#include <tracktable/Core/detail/algorithm_signatures/TransferProperties.h>

namespace tracktable { namespace algorithms {

// This default implementation should work in most cases.  However,
// you will need to specialize it in order to do unit conversions.

template<typename point_type>
struct simplify_linestring
{
  template<typename linestring_type>
  static inline void apply(linestring_type const& input,
                           linestring_type& output,
                           double error_tolerance)
    {
      boost::geometry::simplify(input, output, error_tolerance);
    }
};

} } // namespace tracktable::algorithms

namespace tracktable {

/** Geometric simplification for trajectory
 *
 * This function reduces the number of points in a trajectory without
 * introducing positional error greater than the supplied tolerance.
 * Under the hood it uses Douglas-Peucker simplification.
 *
 * NOTE: The points in the output are copies of the points in the
 * input. Changing the input after a call to simplify() will have no
 * effect on previous results.
 *
 * NOTE: This function only cares about geometric error in the
 * trajectory. It does not account for error in the attributes
 * attached to each point.
 *
 * @param [in] input Trajectory to simplify
 * @param [in] tolerance Error tolerance measured in the trajectory's native distance
 *
 * @return Simplified version of trajectory
 */
template<typename linestring_type>
linestring_type simplify(linestring_type const& input, double tolerance)
{
  linestring_type result;
  algorithms::simplify_linestring<typename linestring_type::value_type>::apply(input, result, tolerance);
  algorithms::transfer_properties<
    tracktable::traits::has_properties<linestring_type>::value
    >::apply(input, result);
  return result;
}

} // namespace tracktable

#endif
