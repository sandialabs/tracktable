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

#ifndef __tracktable_AlmostEqual_h
#define __tracktable_AlmostEqual_h

#include <cstdlib>
#include <algorithm>

#include <cmath>

namespace tracktable { namespace detail {

template<class number_type>
inline bool almost_equal(number_type const& a,
                         number_type const& b,
                         number_type const& epsilon)
{
  if (a == 0 && b == 0) return true;

  number_type delta = fabs(a - b);
  number_type max_abs = std::max(fabs(a), fabs(b));

  // Guard against underflow.  In order to avoid underflow, one of our
  // numbers must be larger than 1.0.
  if (max_abs > number_type(1))
    {
    return delta <= (max_abs * epsilon);
    }
  else if (max_abs > number_type(0))
    {
    // Checking with multiply could cause underflow.  Use a divide.
    // Yuck.  Using division to check floating-point equality.
    return (delta / max_abs) <= epsilon;
    }
  else
    {
    // Both A and B are zero.
    return true;
    }
}

} }

#endif
