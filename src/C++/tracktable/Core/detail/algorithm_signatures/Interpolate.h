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

/*
 * OtherDefaults: default implementations for algorithms that do not
 * pertain to points or trajectories
 *
 * The most prominent member of this class is the 'interpolate'
 * algorithm.
 */

#ifndef __tracktable_core_detail_algorithms_Interpolate_h
#define __tracktable_core_detail_algorithms_Interpolate_h

#include <boost/mpl/assert.hpp>

namespace tracktable { namespace algorithms {

template<typename T>
struct interpolate_nearest_neighbor
{
  static inline T apply(T const& start, T const& end, double interpolant)
    {
      if (interpolant < 0.5)
        {
        return start;
        }
      else
        {
        return end;
        }
    }
};

template<typename T>
struct interpolate_linear
{
  static inline T apply(T const& start, T const& end, double interpolant)
    {
      if (interpolant <= 0)
        {
        return start;
        }
      else if (interpolant >= 1)
        {
        return end;
        }
      else
        {
        T result(end * static_cast<T>(interpolant));
        result += start * static_cast<T>(1 - interpolant);
        return result;
        }
    }
};

// By default, we will try linear interpolation unless we've been told
// differently.  This is a sensible default for all numeric POD types.
template<typename T>
struct interpolate : interpolate_linear<T> { };

} } // exit namespace tracktable::algorithms


// As usual, here are the driver functions so that we can call
// interpolate() instead of intoning
// algorithms::interpolate<T>::apply().

namespace tracktable {

template<typename T>
T interpolate(T const& start, T const& finish, double interpolant)
{
  return algorithms::interpolate<T>::apply(start, finish, interpolant);
}

} // exit namespace tracktable

#endif
