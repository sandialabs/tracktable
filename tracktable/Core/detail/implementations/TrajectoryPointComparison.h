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

// PointComparison.h - Operators to use when sorting points

#ifndef __tracktable_detail_trajectory_point_comparison_h
#define __tracktable_detail_trajectory_point_comparison_h

#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Timestamp.h>

namespace tracktable {

// ----------------------------------------------------------------------

/** Compare points based on their timestamps
 *
 * This object can be used to sort points solely by their timestamps.
 */

template<class TrajectoryPointT>
struct compare_point_timestamps
{
public:
  typedef TrajectoryPointT point_type;
  bool operator()(point_type const& left, point_type const& right) const
    {
      return (left.timestamp() < right.timestamp());
    }
};

// ----------------------------------------------------------------------

/** Compare points based on their cumulative distances
 *
 * This object can be used to sort points solely by their timestamps.
 */

template<class TrajectoryPointT>
struct compare_point_distances
{
public:
  typedef TrajectoryPointT point_type;
  bool operator()(point_type const& left, point_type const& right) const
    {
      return (left.current_length() < right.current_length());
    }
};

// ----------------------------------------------------------------------

/** Compare points based on their truncated timestamps
 *
 * This object can be used to sort points solely by their timestamps
 * truncated to whole seconds.
 */

template<class TrajectoryPointT>
struct compare_truncated_point_timestamps
{
public:
  typedef TrajectoryPointT point_type;
  bool operator()(point_type const& left, point_type const& right) const
    {
      return (truncate_fractional_seconds(left.timestamp()) < truncate_fractional_seconds(right.timestamp()));
    }
};

// ----------------------------------------------------------------------

/** Compare points based on their IDs and timestamps
 *
 * This object will compare points first by their IDs and then by
 * their timestamps.  It can be used to sort a list so that you get
 * back points grouped by ID.
 */

template<class TrajectoryPointT>
struct compare_point_ids_and_timestamps
{
public:
  typedef TrajectoryPointT point_type;

  bool operator()(point_type const& left, point_type const& right) const
    {
      bool ids_equal = (left.object_id() == right.object_id());
      if (ids_equal)
        {
        return (left.timestamp() < right.timestamp());
        }
      else
        {
        return (left.object_id() < right.object_id());
        }
    }
};

} // close namespace tracktable

#endif
