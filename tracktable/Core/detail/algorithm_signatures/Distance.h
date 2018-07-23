/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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
 * BasePointDefaults - Top-level trait structs for things that can be
 * computed for any point type.
 */

#ifndef __tracktable_core_algorithms_detail_BasePointDefaults_h
#define __tracktable_core_algorithms_detail_BasePointDefaults_h

#include <boost/mpl/assert.hpp>
#include <cmath>

namespace tracktable { namespace algorithms {

// You must implement this for a point type in order to compute the
// distance between points.
template<typename T>
struct distance
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(T)==0,
    DISTANCE_NOT_DEFINED_FOR_THIS_POINT_TYPE,
    (types<T>)
    );
};

} } // namespace tracktable::algorithms

/*
 * Now we have functions that wrap the algorithms structs so that we can
 * call them easily instead of worrying about instantiation.
 */

namespace tracktable {

template<class T>
double distance(T const& from, T const& to)
{
  return algorithms::distance<T>::apply(from, to);
}

// generic for comparing any two different geometry types
template<class P, class T>
double distance(P const& from, T const& to)
{
    return boost::geometry::distance(from, to);
}

// Used when comparing things like a point to a trajectory.
template<class P, template<class> class T>
double distance(P const& from, T<P> const& to)
{
   return algorithms::point_to_trajectory_distance<P, T>::apply(from, to);
}

// And the inverse
template<template<class> class T, class P>
double distance(T<P> const& from, P const& to)
{
    return algorithms::point_to_trajectory_distance<P, T>::apply(to, from);
}

} // namespace tracktable

#endif
