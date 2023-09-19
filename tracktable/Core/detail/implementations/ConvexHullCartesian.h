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

#ifndef __tracktable_core_implementations_ConvexHullCartesian_h
#define __tracktable_core_implementations_ConvexHullCartesian_h

#include <tracktable/Core/TracktableCommon.h>

// #include <tracktable/Core/detail/algorithm_signatures/ConvexHull.h>
// #include <tracktable/Core/PointCartesian.h>
// #include <tracktable/Core/TrajectoryPoint.h>
// #include <boost/geometry/core/cs.hpp>
#include <boost/geometry/geometries/polygon.hpp>
#include <boost/geometry/algorithms/convex_hull.hpp>

#include <vector>

namespace tracktable { namespace algorithms { namespace implementations {

namespace bg = boost::geometry;

template<typename iterator>
void compute_convex_hull_cartesian(iterator point_begin, iterator point_end,
                                   bg::model::polygon<typename iterator::value_type>& hull_output)
{
  typedef typename iterator::value_type point_type;
  typedef std::vector<point_type> point_vector_type;

  point_vector_type points(point_begin, point_end);
  boost::geometry::convex_hull(points, hull_output);
}

} } } // close tracktable::algorithms

#endif
