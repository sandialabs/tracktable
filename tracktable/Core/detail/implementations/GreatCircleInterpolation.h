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


#ifndef __tracktable_detail_implementations_GreatCircleInterpolation_h
#define __tracktable_detail_implementations_GreatCircleInterpolation_h

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Conversions.h>
#include <tracktable/Core/detail/algorithm_signatures/SphericalCoordinateAccess.h>

#include <cassert>
#include <algorithm>

namespace {

typedef std::pair<double, double> double_pair_type;

//
// This struct represents the intersection between a great circle and
// the equator.  We use this to interpolate between two points on a
// sphere.
//
// NOTE: THESE COORDINATES AND ANGLES ARE IN RADIANS.
//
struct great_circle_node
{
  // Coordinates of the intersection - the latitude will (by
  // definition) be zero
  double_pair_type node_coordinates;
  // Central angle between node and start point
  double sigma_01;
  // Heading along great circle at node
  double alpha_0;
};

// ----------------------------------------------------------------------

template<typename point_type>
double compute_great_circle_central_angle(
  point_type const& start,
  point_type const& end
  )
{
  double lon1 = tracktable::longitude_as_radians(start);
  double lat1 = tracktable::latitude_as_radians(start);

  double lon2 = tracktable::longitude_as_radians(end);
  double lat2 = tracktable::latitude_as_radians(end);

  double d_lon = (lon2 - lon1)/2.0;
  double angle = acos( cos(lat1 - lat2) -
   2.0 * cos(lat1) * cos(lat2) * sin(d_lon) * sin(d_lon) );
  return angle;
}

// ----------------------------------------------------------------------

template<typename point_type>
double_pair_type compute_great_circle_bearings(
  point_type const& start,
  point_type const& end
  )
{
  double lon1 = tracktable::longitude_as_radians(start);
  double lat1 = tracktable::latitude_as_radians(start);

  double lon2 = tracktable::longitude_as_radians(end);
  double lat2 = tracktable::latitude_as_radians(end);

  double d_lon = lon2 - lon1;

  double initial_bearing = atan2(sin(d_lon),
                                  cos(lat1) * tan(lat2) - sin(lat1) * cos(d_lon));
  double final_bearing   = atan2(sin(d_lon),
                                 -cos(lat2) * tan(lat1) + sin(lat2) * cos(d_lon));

  return double_pair_type(initial_bearing, final_bearing);
}

// ----------------------------------------------------------------------

template<typename point_type>
void find_great_circle_node(
  point_type const& start,
  point_type const& end,
  great_circle_node& out_node
)
{
  double lon1 = tracktable::longitude_as_radians(start);
  double lat1 = tracktable::latitude_as_radians(start);

  double_pair_type bearings(
    compute_great_circle_bearings(start, end)
    );

  double sin_alpha_0 = sin(bearings.first) * cos(lat1);
  double sigma_01;

  if ((fabs(lat1) < 0.001) && fabs(bearings.first - 0.5 * tracktable::conversions::constants::PI) < 0.001)
    {
    sigma_01 = 0;
    }
  else
    {
    sigma_01 = atan2( tan(lat1), cos(bearings.first) );
    }

  double lon0 = lon1 - atan2( sin_alpha_0 * sin(sigma_01), cos(sigma_01) );
  out_node.node_coordinates.first = lon0;
  out_node.node_coordinates.second = 0;
  out_node.sigma_01 = sigma_01;
  out_node.alpha_0 = asin(sin_alpha_0);
}

} // exit anonymous namespace


namespace tracktable { namespace algorithms { namespace implementations {

/** Interpolate between two longitude/latitude points
 *
 * This performs interpolation along a great circle.  Any two distinct
 * points on the surface of a sphere that are not exact antipodes lie
 * along exactly one great circle and divide it into two segments, one
 * longer and one shorter.  We interpolate along the shorter segment.
 *
 * Points that are exact antipodes lie on an infinite number of great
 * circles.  We'll pick one and do our best.
 */

struct great_circle_interpolate
{
  template<typename point_type>
  static inline point_type apply(
    point_type const& start,
    point_type const& end,
    double interpolant
    )
    {
      double central_angle = ::compute_great_circle_central_angle(start, end);
      ::great_circle_node node;
      ::find_great_circle_node(start, end, node);

      double partial_angle =
        node.sigma_01 + interpolant * central_angle;
      double latitude =
        asin( cos(node.alpha_0) * sin(partial_angle) );
      double longitude =
        node.node_coordinates.first +
        atan2( sin(node.alpha_0) * sin(partial_angle),
               cos(partial_angle) );

      point_type new_point;
      tracktable::set_longitude_from_radians(new_point, longitude);
      tracktable::set_latitude_from_radians(new_point, latitude);
      return new_point;
    }
};

} } } // exit namespace tracktable::algorithms::implementations

#endif
