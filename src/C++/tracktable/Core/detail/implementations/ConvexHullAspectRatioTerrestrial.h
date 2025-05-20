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

#ifndef __tracktable_implementations_ConvexHullAspectRatio_terrestrial_h
#define __tracktable_implementations_ConvexHullAspectRatio_terrestrial_h

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/detail/implementations/ConvexHullTerrestrial.h>
#include <tracktable/Core/detail/implementations/ConvexHullCentroidTerrestrial.h>
#include <tracktable/Core/detail/implementations/SphericalPolygons.h>

namespace tracktable { namespace algorithms {

namespace bg = boost::geometry;

template<>
struct compute_convex_hull_aspect_ratio<
  bg::cs::spherical_equatorial<bg::degree>, 2
  >
{
  template<typename iterator>
  static inline double apply(iterator point_begin, iterator point_end)
    {
      typedef typename iterator::value_type point_type;
      typedef boost::geometry::model::polygon<point_type> polygon_type;
      polygon_type hull;

      implementations::compute_convex_hull_terrestrial(point_begin, point_end, hull);
      point_type centroid(
        compute_convex_hull_centroid<
        bg::cs::spherical_equatorial<bg::degree>, 2>
        ::compute_centroid_from_hull(hull)
        );

      double short_axis = -1;
      double long_axis = -1;
      typedef typename polygon_type::ring_type::iterator point_iterator_type;
      std::vector<point_type> segment(2);

      point_iterator_type current_point = hull.outer().begin();
      point_iterator_type previous_point = current_point;
      for (; current_point != hull.outer().end(); ++current_point)
        {
        double new_distance = tracktable::conversions::radians_to_km(boost::geometry::distance(centroid, *current_point));
        long_axis = std::max(long_axis, new_distance);

        if (current_point != previous_point)
          {
          segment[0] = *previous_point;
          segment[1] = *current_point;
          double short_distance = tracktable::conversions::radians_to_km(boost::geometry::distance(centroid, segment));
          if (short_axis < 0)
            {
            short_axis = short_distance;
            }
          else
            {
            short_axis = std::min(short_axis, short_distance);
            }
          }

        previous_point = current_point;
        }

    if (std::abs(short_axis) < 1e-5)
      {
        return 0;
      }
    else
      {
        double result = long_axis / short_axis;
        if (std::isnan(result))
        {
          return 0;
        } else {
          return result;
        }
      }
    }
};

} }

#endif
