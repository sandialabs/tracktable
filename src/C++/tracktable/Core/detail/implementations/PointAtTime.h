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


#ifndef __tracktable_detail_implementations_PointAtTime_h
#define __tracktable_detail_implementations_PointAtTime_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/Timestamp.h>

#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/detail/algorithm_signatures/PointAtTime.h>
#include <tracktable/Core/detail/implementations/TrajectoryPointComparison.h>

#include <iostream>
#include <cassert>
#include <ostream>
#include <vector>
#include <typeinfo>

namespace tracktable { namespace algorithms { namespace implementations {

/** Return the estimated point at the specified time.
 *
 * If the specified time is found exactly in the trajectory, return
 * the first point with that time.  Otherwise, interpolate between
 * the two points immediately before and after.
 *
 * If you ask for a point off the ends of the trajectory you will
 * get either the first or the last point depending on whether you
 * asked for a time before the beginning or after the end.
 *
 */

template<typename ContainerT>
struct generic_point_at_time
{
  template<typename TrajectoryType>
  static typename TrajectoryType::point_type apply(
    TrajectoryType const& path,
    Timestamp const& time
    )
    {
      typedef typename TrajectoryType::point_type point_type;
      typedef typename TrajectoryType::const_iterator const_iterator;
      typedef compare_point_timestamps<point_type> compare_point_type;

      if (path.empty()) return tracktable::arithmetic::zero<point_type>();

      if (time <= path.front().timestamp())
        {
        return path.front();
        }
      if (time >= path.back().timestamp())
        {
        return path.back();
        }

      point_type key;
      Timestamp key_time(time);
      key.set_timestamp(key_time);

      // This will point to the first element that does not compare
      // less than the key (i.e. is >=)
      const_iterator equal_or_after = std::lower_bound(
        path.begin(), path.end(),
        key,
        compare_point_type()
        );

      // This will point to the first element whose time is greater
      // than the key
      const_iterator after = std::upper_bound(
        path.begin(), path.end(),
        key,
        compare_point_type()
        );

      const_iterator before;

      if (after == equal_or_after)
        {
        // there is no element that is exactly at the key time; we'll
        // have to interpolate between before and after
        before = equal_or_after -= 1;
        }
      else
        {
        // Did we find it exactly?
        if ((*equal_or_after).timestamp() == time)
          {
          // yes!
          return (*equal_or_after);
          }
        else
          {
          TRACKTABLE_LOG(log::warning)
            << "WARNING: Trajectory::point_at_time: This shouldn't ever happen.  "
            << "before: " << *before << " "
            << "after: " << *after << " "
            << "equal_or_after: " << *equal_or_after;
          before = equal_or_after;
          }
        }

      // Neither 'before' nor 'after' can point to an invalid element
      // like begin-1 or end().  If the timestamp were outside the
      // range of the trajectory we would have caught it at the top of
      // the function.
      assert(after > path.begin() && after < path.end());
      assert(before >= path.begin() && before < path.end());

      if ((*after).timestamp() == time)
        {
        return (*after);
        }
      else
        {
        boost::posix_time::time_duration before_after_span = ((*after).timestamp() - (*before).timestamp());
        boost::posix_time::time_duration before_key_span = (time - (*before).timestamp());
        double interpolant = static_cast<double>(before_key_span.total_milliseconds()) / static_cast<double>(before_after_span.total_milliseconds());

        return interpolate<point_type>::apply(*before, *after, interpolant);
        }
    }
};

} } } // exit namespace tracktable::algorithms::implementations

#endif
