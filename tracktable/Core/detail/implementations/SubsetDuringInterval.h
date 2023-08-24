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

#ifndef __tracktable_TrajectorySubset_h
#define __tracktable_TrajectorySubset_h

#include <tracktable/Core/detail/algorithm_signatures/PointAtTime.h>
#include <tracktable/Core/detail/algorithm_signatures/SubsetDuringInterval.h>

namespace tracktable { namespace algorithms { namespace implementations {

template< typename TrajectoryType >
struct generic_subset_during_interval
{
  /** Extract a subset of a trajectory
   *
   * Given start and end timestamps, extract whatever subset of a
   * trajectory falls within that window.  An empty trajectory will be
   * returned if no points are within the window.
   *
   * If start_time and/or end_time don't match up exactly with points
   * in the trajectory, new points will be interpolated that fall
   * exactly at those boundaries.
   *
   * @param [in] _start_time    Beginning of time window
   * @param [in] _end_time      End of time window
   */

  template<class TrajectoryT, class TimestampT>
  inline static TrajectoryT apply(
    TrajectoryT const& path,
    TimestampT const& _start_time,
    TimestampT const& _end_time
    )
    {
      typedef TimestampT timestamp_type;
      typedef TrajectoryT trajectory_type;
      typedef typename trajectory_type::point_type point_type;
      typedef typename trajectory_type::const_iterator const_iterator;

      typedef compare_truncated_point_timestamps<point_type> compare_point_type;


      timestamp_type start_time(_start_time), end_time(_end_time);

      if (start_time > end_time)
        {
        TRACKTABLE_LOG(log::warning)
          << "Trajectory::subset_in_window: start_time ("
          << start_time << ") is after end_time (" << end_time
          << ").  We'll pretend you meant it the other way around.";
        start_time = _end_time;
        end_time = _start_time;
        }

      if (path.empty()) return trajectory_type();

      if (path.front().timestamp() > end_time) return trajectory_type();
      if (path.back().timestamp() < start_time) return trajectory_type();


      timestamp_type truncated_start(truncate_fractional_seconds(start_time));
      timestamp_type truncated_end(truncate_fractional_seconds(end_time));

      if (truncated_start < truncate_fractional_seconds(path.front().timestamp())) start_time = path.front().timestamp();
      if (truncated_end > truncate_fractional_seconds(path.back().timestamp())) end_time = path.back().timestamp();

      if (truncated_start == truncated_end)
        {
        trajectory_type result;
        result.push_back(point_at_time<trajectory_type>::apply(path, start_time));
        return result;
        }

      trajectory_type result;
      // These will be the points that we can just copy instead of
      // interpolating
      const_iterator middle_range_start, middle_range_end;

      // Do we have to interpolate the front point?
      const_iterator front_equal_or_after, front_after;
      point_type key;
      key.set_timestamp(start_time);
      front_equal_or_after = std::lower_bound(
        path.begin(), path.end(),
        key,
        compare_point_type()
        );
      front_after = std::upper_bound(
        path.begin(), path.end(),
        key,
        compare_point_type()
        );


      if (front_equal_or_after == front_after)
        {
        point_type interpolated_front(point_at_time<trajectory_type>::apply(path, start_time));
        middle_range_start = front_after;
        result.push_back(interpolated_front);
        }
      else
        {
        middle_range_start = front_equal_or_after;
        }

      key.set_timestamp(end_time);
      const_iterator back_equal_or_after, back_after;
      back_equal_or_after = std::lower_bound(
        path.begin(), path.end(),
        key,
        compare_point_type()
        );
      back_after = std::upper_bound(
        path.begin(), path.end(),
        key,
        compare_point_type()
        );


      if (back_equal_or_after == back_after)
        {
        // We have to interpolate the end point.
        middle_range_end = back_equal_or_after;
        std::copy(middle_range_start, middle_range_end, std::back_inserter(result));
        result.push_back(point_at_time<trajectory_type>::apply(path, end_time));
        }
      else
        {
        // The first point that tests as timestamp <= end_time is not
        // the same as the first one that tests as timestamp <
        // end_time.  That means we've found it exactly.
        middle_range_end = back_after;
        std::copy(middle_range_start, middle_range_end, std::back_inserter(result));
        }

      return result;
    }
};

} } } // namespace tracktable::algorithms::implementations

#endif
