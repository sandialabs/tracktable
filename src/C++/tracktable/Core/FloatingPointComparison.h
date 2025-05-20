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


// We need a robust way to compare floating point numbers for almost-equality

// \defgroup Tracktable_CPP C++ components of Tracktable


#ifndef __tracktable_floating_point_comparison_h
#define __tracktable_floating_point_comparison_h

#include <cmath>
#include <limits>

namespace tracktable {

namespace settings {

const double EQUALITY_RELATIVE_TOLERANCE=1e-5;
const double ZERO_ABSOLUTE_TOLERANCE=1e-5;

}

// ----------------------------------------------------------------------

/** Compare values to determine if they are almost equal
 *
 *  @param [in] a First value to use in comparison
 *  @param [in] b Second value to use in comparison
 *  @param [in] tolerance Tolerance for determining comparision, options are
 *    `settings::EQUALITY_RELATIVE_TOLERANCE` (default value) or `settings::ZERO_ABSOLUTE_TOLERANCE`
 */

template<typename T>
bool almost_equal(
  T a, T b,
  T tolerance=settings::EQUALITY_RELATIVE_TOLERANCE
  )
{
  T abs_a = std::fabs(a);
  T abs_b = std::fabs(b);
  T diff = std::fabs(a-b);

#if defined (__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wfloat-equal"
#endif
  if (a == b) // shortcut, handles infinities
    {
    return true;
    }
  else if (a == 0 || b == 0 || diff < std::numeric_limits<T>::epsilon())
    {
    // Either they're both close to zero or one of them actually is
    // zero. Relative error is less meaningful here.
    return (diff < tolerance);
    }
  else
    {
    // use relative error
    return (diff / (abs_a + abs_b)) < tolerance;
    }
#if defined (__clang__)
#pragma clang diagnostic pop
#endif
}

// ----------------------------------------------------------------------

/** Determine if value is almost zero
 *
 *  @param [in] z Value to determine if almost zero
 *  @param [in] epsilon Limit for determining value, options are
 *    `settings::EQUALITY_RELATIVE_TOLERANCE` or `settings::ZERO_ABSOLUTE_TOLERANCE` (default value)
 */

template<typename T>
bool almost_zero(
  T z,
  T epsilon=settings::ZERO_ABSOLUTE_TOLERANCE
  )
{
  return almost_equal<T>(z, static_cast<T>(0), epsilon);
}

} // close namespace tracktable

#endif
