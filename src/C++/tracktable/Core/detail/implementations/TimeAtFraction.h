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

// Ben Newton, July 15, 2015

#ifndef __tracktable_detail_implementations_TimeAtFraction_h
#define __tracktable_detail_implementations_TimeAtFraction_h

#include <tracktable/Core/Timestamp.h>

#include <tracktable/Core/detail/algorithm_signatures/TimeAtFraction.h>

namespace tracktable { namespace algorithms { namespace implementations {

/** Return the time at the specified trajectory fraction
   *
   * Returns the timestamp a specified fraction the time along this trajectory.
   * If <0 or >1, you get start_time or end_time respectively.
   * A fraction of .25 of a 4 hour trajectory would find the timestamp one hour
   * after the start of the trajectory.
   *
   * @param fraction the fraction of the trajectory at which to find the time.
   *
   * @return the timestamp of a given fraction of the way along the trajectory.
   */
template<typename ContainerT>
struct generic_time_at_fraction
{
  template<typename TrajectoryType>
  static Timestamp apply(TrajectoryType const& path, double fraction)
    {
      if (path.empty()) return Timestamp(BeginningOfTime);
      if (fraction <= 0.0)
        {
        return path.front().timestamp();
        }

      if (fraction >= 1.0)
        {
        return path.back().timestamp();
        }

      long delta_sec = static_cast<long>(fraction*
                                         path.duration().total_seconds());

      return path.front().timestamp() +
        boost::posix_time::time_duration(boost::posix_time::seconds(delta_sec));
    }
};

} } } // exit namespace tracktable::algorithms::implementations

#endif

