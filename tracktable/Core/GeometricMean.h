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

/* Geometric mean for all point types.
 *
 * This is the familiar mean in both weighted and un-weighted
 * varieties.
 */

#ifndef __tracktable_GeometricMean_h
#define __tracktable_GeometricMean_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointArithmetic.h>
#include <cmath>
#include <algorithm>

namespace tracktable { namespace arithmetic {

/** Calculate the mean for the un-weighted input points
 *
 * @note
 *    This function requires a ForwardIterator as its argument. A
 *    ForwardIterator is one that can be traversed and dereferenced more
 *    than once.
 *
 * @param [in] input_begin Start point for mean calculation
 * @param [in] input_end End point for mean calculation
 */

template<typename forward_iterator_type>
typename std::iterator_traits<forward_iterator_type>::value_type
geometric_mean(
  forward_iterator_type input_begin,
  forward_iterator_type input_end
  )
{
  typedef typename std::iterator_traits<forward_iterator_type>::value_type point_type;

  point_type mean = tracktable::arithmetic::zero<point_type>();
  std::size_t num_points = 0;

  if (input_begin == input_end)
    {
    return point_type(); // no points - degenerate solution
    }

  for (forward_iterator_type iter = input_begin;
       iter != input_end;
       ++iter)
    {
    tracktable::arithmetic::add_in_place(mean, *iter);
    ++num_points;
    }

  tracktable::arithmetic::multiply_scalar_in_place(mean, 1.0 / static_cast<double>(num_points));
  return mean;
}

// ----------------------------------------------------------------------

/** Weighted sum of points
 *
 * @note
 *    You are responsible for ensuring that
 *    `point_iterator_type::value_type` is a Tracktable point and that
 *    `weight_iterator_type::value_type` is a scalar. Also,
 *    `point_iterator_type` and `weight_iterator_type` must both be
 *    ForwardIterators.
 *
 * @param [in] point_begin Start point for sum calculation
 * @param [in] point_end End point for sum calculation
 * @param [in] weight_begin Start of the point weights
 * @param [in] weight_end End of the point weights
 */

template<typename point_iterator_type, typename weight_iterator_type>
typename std::iterator_traits<point_iterator_type>::value_type
weighted_sum(
  point_iterator_type point_begin,
  point_iterator_type point_end,
  weight_iterator_type weight_begin,
  weight_iterator_type weight_end
  )
{
  typedef typename std::iterator_traits<point_iterator_type>::value_type point_type;

  point_type mean = tracktable::arithmetic::zero<point_type>();
  std::size_t num_points = 0;

  if (point_begin == point_end)
    {
    return point_type(); // no points - degenerate solution
    }

  point_iterator_type point_iter = point_begin;
  weight_iterator_type weight_iter = weight_begin;

  for (
    ;
    point_iter != point_end && weight_iter != weight_end;
    ++point_iter, ++weight_iter
    )
    {
    point_type next_point(*point_iter);
    tracktable::arithmetic::multiply_scalar_in_place(next_point, *weight_iter);

    tracktable::arithmetic::add_in_place(mean, next_point);
    ++num_points;
    }

  return mean;
}

} } // close namespace tracktable::arithmetic

#endif
