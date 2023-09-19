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
 * TurnAngle - signatures for the signed_turn_angle and
 * unsigned_turn_angle algorithms for points.
 */

#ifndef __tracktable_core_detail_algorithm_signatures_TurnAngle_h
#define __tracktable_core_detail_algorithm_signatures_TurnAngle_h

#include <boost/mpl/assert.hpp>
#include <cmath>

namespace tracktable { namespace algorithms {

// Implement this for a point type in order to determine the signed
// turn angle between two vectors (A, B) and (B, C).
template<typename T>
struct signed_turn_angle
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(T)==0,
    SIGNED_TURN_ANGLE_NOT_DEFINED_FOR_THIS_TYPE,
    (types<T>)
    );
};

// Implement this for a point type in order to determine the unsigned
// turn angle between two vectors.  The default implementation will
// often suffice but there are situations (such as high-dimensional
// Cartesian coordinate systems) where the signed turn angle is
// undefined without reference to some plane but the unsigned angle is
// easy to determine.
template<typename T>
struct unsigned_turn_angle
{
  static inline double apply(T const& a, T const& b, T const& c)
    {
      return fabs(signed_turn_angle<T>::apply(a, b, c));
    }
};

} } // namespace tracktable::algorithms

/*
 * Now we have functions that wrap the algorithms structs so that we can
 * call them easily instead of worrying about instantiation.
 */

namespace tracktable {

template<class T>
double signed_turn_angle(T const& a, T const& b, T const& c)
{
  return algorithms::signed_turn_angle<T>::apply(a, b, c);
}

template<class T>
double unsigned_turn_angle(T const& a, T const& b, T const& c)
{
  return algorithms::unsigned_turn_angle<T>::apply(a, b, c);
}

} // namespace tracktable

#endif
