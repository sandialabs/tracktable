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
 * SpeedBetween - signature for "speed between two points" algorithm.
 * This only makes sense for points with timestamps --
 * e.g. TrajectoryPoint and subclasses.
 */

#ifndef __tracktable_core_detail_algorithm_signatures_TrajectoryPointDefaults_h
#define __tracktable_core_detail_algorithm_signatures_TrajectoryPointDefaults_h

#include <boost/mpl/assert.hpp>

namespace tracktable { namespace algorithms {

template<typename T>
struct speed_between
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(T)==0,
    SPEED_NOT_DEFINED_FOR_THIS_POINT_TYPE,
    (types<T>)
    );
};

} } // namespace tracktable::algorithms

/*
 * Now we have functions that wrap the traits structs so that we can
 * call them easily instead of worrying about instantiation.
 */

namespace tracktable {

template<class T>
double speed_between(T const& start, T const& finish)
{
  return algorithms::speed_between<T>::apply(start, finish);
}

} // namespace tracktable

#endif
