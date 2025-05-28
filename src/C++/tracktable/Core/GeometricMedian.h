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

#ifndef __tracktable_GeometricMedian_h
#define __tracktable_GeometricMedian_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/GeometricMean.h>
#include <tracktable/Core/PointTraits.h>

#include <tracktable/Core/detail/algorithm_signatures/Distance.h>

#include <cassert>
#include <cmath>
#include <algorithm>
#include <vector>
#include <iostream>
#include <limits>

namespace tracktable { namespace arithmetic {

/** L1 multivariate median for all point types.
 *
 * The L1 multivariate median generalizes the concept of the familiar
 * 1-dimensional median. Given a set of points x_i, the median y =
 * M(x_i) is the point that minimizes the sum of the distances to the
 * points x_i.
 *
 * There is no closed-form expression for the L1 median so we compute
 * it with an iterative algorithm.
 *
 * @param [in] input_begin Start point for median calculation
 * @param [in] input_end End point for median calculation
 */

template<typename forward_iterator_type>
typename std::iterator_traits<forward_iterator_type>::value_type
geometric_median(
  forward_iterator_type input_begin,
  forward_iterator_type input_end
  )
{
  typedef typename std::iterator_traits<forward_iterator_type>::value_type point_type;
  typedef std::vector<double> double_vector;

  double max_coordinate_span = 0;
  for (forward_iterator_type point_iter = input_begin;
       point_iter != input_end;
       ++point_iter)
    {
    double coord_min = std::numeric_limits<double>::max();
    double coord_max = - std::numeric_limits<double>::max();

    for (std::size_t d = 0; d < tracktable::traits::dimension<point_type>::value; ++d)
      {
      coord_min = std::min(coord_min, (*point_iter)[d]);
      coord_max = std::max(coord_max, (*point_iter)[d]);
      }
    max_coordinate_span = std::max(max_coordinate_span, coord_max - coord_min);
    }

  double tolerance = 1e-9 * max_coordinate_span;
  point_type median, new_median, median_estimate;
  double distance_moved = std::numeric_limits<double>::max();
  std::size_t num_points = std::distance(input_begin, input_end);
  assert(num_points >= 0);

  if (input_begin == input_end)
    {
    return point_type(); // no points - degenerate solution
    }

  // The median starts out at the geometric mean of all the points.
  median = tracktable::arithmetic::geometric_mean(input_begin, input_end);

  std::vector<double> weights(num_points, 0);
  double inverse_distance_sum = 0;
  std::size_t num_zeros = 0;

  while (distance_moved > tolerance)
    {
    inverse_distance_sum = 0;
    num_zeros = 0;

    // Compute the inverse distance from the current estimate of the
    // median to all the sample points
    forward_iterator_type point_iter = input_begin;
    double_vector::iterator weight_iter = weights.begin();

    for (
      ;
      point_iter != input_end && weight_iter != weights.end();
      ++point_iter, ++weight_iter
      )
      {
      double distance = tracktable::distance(median, *point_iter);

      // We adopt the convention that 0/0 == 0
      if (distance > 0)
        {
        distance = 1.0 / distance;
        }
      else
        {
        ++num_zeros;
        }

      inverse_distance_sum += distance;
      *weight_iter = distance;
      }

    // Normalize the inverse distances to get a set of weights for the
    // points
    for (double_vector::iterator normalize_weight_iter = weights.begin();
         normalize_weight_iter != weights.end();
         ++normalize_weight_iter)
      {
      *normalize_weight_iter /= inverse_distance_sum;
      }

    median_estimate = tracktable::arithmetic::weighted_sum(input_begin, input_end,
                                                           weights.begin(), weights.end());

    // Are we done? (all points at same location)
    if (num_zeros == num_points)
      {
      return median;
      }


    // No. Compute a better estimate for the median.
    if (num_zeros == 0)
      {
      new_median = median_estimate;
      }
    else
      {
      // We're sitting on top of one or more of the points -- adjust
      // the new estimate of the median accordingly
      point_type normalized_motion;
      normalized_motion = tracktable::arithmetic::subtract(median_estimate, median);
      tracktable::arithmetic::multiply_scalar_in_place(normalized_motion, inverse_distance_sum);

      double residual = tracktable::arithmetic::norm(normalized_motion);
      double residual_inverse = 0;
      if (residual > 0)
        {
        residual_inverse = num_zeros / residual;
        }

      point_type a, b;
      a = tracktable::arithmetic::multiply_scalar(median_estimate,
                                                  std::max(0.0, 1.0 - residual_inverse));
      b = tracktable::arithmetic::multiply_scalar(median,
                                                  std::min(1.0, residual_inverse));
      new_median = tracktable::arithmetic::add(a, b);
      }

    distance_moved = tracktable::distance(median, new_median);
    median = new_median;
    }

  return median;
}

} }

#endif
