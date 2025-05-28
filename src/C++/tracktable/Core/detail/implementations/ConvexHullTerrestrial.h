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

#ifndef __tracktable_core_ConvexHullTerrestrial_h
#define __tracktable_core_ConvexHullTerrestrial_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Conversions.h>

#include <tracktable/Core/detail/algorithm_signatures/ConvexHull.h>
#include <tracktable/Core/detail/implementations/NorthPoleConvexHull.h>
#include <tracktable/Core/detail/implementations/SphericalMath.h>
#include <tracktable/Core/PointLonLat.h>

namespace tracktable { namespace algorithms {


namespace bg = boost::geometry;

namespace implementations {

template<typename iterator>
void
compute_convex_hull_terrestrial(iterator point_begin, iterator point_end,
                                bg::model::polygon<typename iterator::value_type>& hull)
{
  hull.clear();

  typedef typename iterator::value_type point_type;
  std::vector<point_type> input_points(point_begin, point_end);

  PointLonLat center = spherical_math::terrestrial_center_of_mass(input_points.begin(),
                                                                  input_points.end());

  convex_hull_utilities::RotatePointsToNorthPole(input_points.begin(),
                                                 input_points.end(),
                                                 center);

  convex_hull_utilities::ComputeNorthPoleHull(input_points.begin(),
                                              input_points.end(),
                                              hull);

  convex_hull_utilities::ReturnPointsFromNorthPole(hull.outer().begin(),
                                                   hull.outer().end(),
                                                   center);
}

} // close implementations


} } // close tracktable::algorithms

#endif
