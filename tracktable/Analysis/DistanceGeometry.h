/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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

#ifndef __tracktable_analysis_distance_geometry_h
#define __tracktable_analysis_distance_geometry_h

#include <iostream>
#include <vector>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/Logging.h>

namespace tracktable {


/**
 * Create distance geometry signature with samples by distance
 *
 * This function computes the multilevel distance geometry
 * for a given trajectory. Each level *d* approximates the
 * input trajectory with *d* equal-length line segments.
 * The distance geometry values for that level are the lengths
 * of all *d* line segments, normalized to lie between 0 and 1.
 *
 * The D-level distance geometry for a curve will result in
 * (D * (D+1)) / 2  separate values.
 *
 * This implementation creates the endpoints of the line segments
 * by sampling the trajectory at fractions of total distance
 * traveled. To sample by total duration, use
 * distance_geometry_by_time().
 *
 * @param [in] trajectory input curve to analyze
 * @param [in] depth How many levels to compute. Must
 *         be greater than zero.
 * @return std::vector<double> containing the distance geometry values
 *         laid out consecutively by increasing depth.
 */

template<typename trajectory_type>
std::vector<double>
distance_geometry_by_distance(
  trajectory_type const& trajectory,
  unsigned int depth
  )
{
  return _distance_geometry(trajectory, depth, true);
}


/**
 * Create distance geometry signature with samples by time
 *
 * This function computes the multilevel distance geometry
 * for a given trajectory. Each level *d* approximates the
 * input trajectory with *d* equal-length line segments.
 * The distance geometry values for that level are the lengths
 * of all *d* line segments, normalized to lie between 0 and 1.
 *
 * The D-level distance geometry for a curve will result in
 * (D * (D+1)) / 2  separate values.
 *
 * This implementation creates the endpoints of the line segments
 * by sampling the trajectory at fractions of total duration
 * traveled. To sample by total travel distance, use
 * distance_geometry_by_distance().
 *
 * @param [in] trajectory  input curve to analyze
 * @param [in] depth How many levels to compute. Must
 *         be greater than zero.
 * @return std::vector<double> containing the distance geometry values
 *         laid out consecutively by increasing depth.
 */

template<typename trajectory_type>
std::vector<double>
distance_geometry_by_time(
  trajectory_type const& trajectory,
  unsigned int depth
  )
{
  return _distance_geometry(trajectory, depth, false);
}


/** @internal Do the actual computation for distance geometry
 *
 * See distance_geometry_by_distance and distance_geometry_by_time
 * for documentation on what this is for.
 *
 * @param [in] trajectory Input curve to analyze
 * @param [in] depth How many levels to compute. Must
 *         be greater than zero.
 * @param [in] sample_by_distance Whether to place the
 *         control points that define the line segments according to
 *         fraction of distance traveled versus fraction of time
 *         elapsed. Defaults to 'true', meaning sample by distance.
 *
 * @return `std::vector<double>` containing the distance geometry values
 *         laid out consecutively by increasing depth.
 */

template<typename trajectory_type>
std::vector<double>
_distance_geometry(
  trajectory_type const& trajectory,
  unsigned int depth,
  bool sample_by_distance=true
  )
{
  if (depth < 1 || trajectory.size() == 0)
  {
    return std::vector<double>();
  }

  double travel_distance = tracktable::length(trajectory);
  const std::size_t result_size = (depth * (depth+1)) / 2;

  // If a trajectory has overall length zero, all of the distance geometry
  // distances will be zero. Given the choice between returning a vector
  // of all zeros or a vector of all ones, we opt to return all ones for
  // cleanliness -- you won't get division-by-zero errors that way.
  //
  // As for the decision of whether or not the length is zero: since it is
  // perfectly reasonable for Cartesian trajectories to have very small but
  // non-zero lengths, we compare against exactly zero instead of almost zero.
  //
  // If we're sampling by time, we also need to consider whether or not the
  // duration is zero.

  if (travel_distance == 0)
  {
    TRACKTABLE_LOG(log::warning)
      << "distance_geometry: Total distance for trajectory is zero. "
      << "Distance geometry results may not be what you expect.";
    return std::vector<double>(result_size, 1.0);
  }

  if (!sample_by_distance)
  {
    tracktable::Duration duration =
      trajectory.back().timestamp() - trajectory.front().timestamp();
    if (duration.total_seconds() == 0)
    {
      return std::vector<double>(result_size, 1.0);
    }
  }

  // Since we know in advance how many values we'll generate, we can avoid
  // memory reallocations later.
  std::vector<double> distance_geometry_distances;
  distance_geometry_distances.reserve(result_size);
  std::vector<typename trajectory_type::point_type> control_points(depth + 1);

  for (unsigned int d = 1; d <= depth; ++d)
  {
    control_points.clear();
    _create_control_points(d, trajectory, sample_by_distance, control_points);
    for (unsigned int i = 0; i < d; ++i)
    {
      double control_point_distance = tracktable::distance(
        control_points[i], control_points[i+1]
        );
      distance_geometry_distances.push_back(control_point_distance / (travel_distance / d));
    }
  }
  return distance_geometry_distances;
}


/** @internal
 *
 *  Sample the input trajectory at (depth+1) locations evenly spaced
 *  along the trajectory by distance traveled or by time elapsed.
 *
 *  Results are returned via the 'output' parameter.
 *
 * @param [in] depth How many levels to compute. Must
 *         be greater than zero.
 * @param [in] trajectory Input curve to analyze
 * @param [in] sample_by_distance Whether to place the
 *         control points that define the line segments according to
 *         fraction of distance traveled versus fraction of time
 *         elapsed. Defaults to 'true', meaning sample by distance.
 * @param [out] output The output of the creation of the control points
 */

template<typename trajectory_type, typename point_type>
void _create_control_points(unsigned int depth,
                           trajectory_type const& trajectory,
                           bool sample_by_distance,
                           std::vector<point_type>& output)
{
  double step_fraction = 1.0 / depth;
  for (std::size_t i = 0; i < depth+1; ++i)
  {
    double here = i * step_fraction;
    if (sample_by_distance)
    {
      output.push_back(tracktable::point_at_length_fraction(trajectory, here));
    }
    else
    {
      output.push_back(tracktable::point_at_time_fraction(trajectory, here));
    }
  }
}



} // close namespace tracktable

#endif // __tracktable_analysis_distance_geometry_h
