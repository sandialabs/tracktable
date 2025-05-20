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

#ifndef __tracktable_implementations_SphericalMath_h
#define __tracktable_implementations_SphericalMath_h

#include <tracktable/Core/Conversions.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>

#include <cmath>

namespace tracktable { namespace algorithms { namespace spherical_math {

typedef PointCartesian<3> Point3D;

template<typename terrestrial_point_type>
Point3D to_cartesian(terrestrial_point_type const& original_point)
{
  double longitude = tracktable::conversions::radians(original_point.template get<0>());
  double latitude = tracktable::conversions::radians(original_point.template get<1>());

  double coordinates[3];
  coordinates[0] = cos(latitude) * cos(longitude);
  coordinates[1] = cos(latitude) * sin(longitude);
  coordinates[2] = sin(latitude);

  return Point3D(coordinates);
}

// ----------------------------------------------------------------------

template<typename output_point_type>
output_point_type to_terrestrial(Point3D const& cart_point)
{
  using tracktable::conversions::degrees;

  // Assume the point is on a sphere of radius 1
  double theta = sqrt(cart_point[0]*cart_point[0] + cart_point[1]*cart_point[1]);
  double r_latitude = atan2(cart_point[2], theta);
  double r_longitude = atan2(cart_point[1], cart_point[0]);

  output_point_type return_point;
  return_point.template set<0>(degrees(r_longitude));
  return_point.template set<1>(degrees(r_latitude));
  return return_point;
}

// ----------------------------------------------------------------------

template<typename iterator>
PointLonLat terrestrial_center_of_mass(iterator point_begin, iterator point_end)
{
  if (point_begin == point_end) return PointLonLat();

  double x=0.0, y=0.0, z=0.0;
  std::size_t num_points=0;

  // Find the 3-space centroid of all of the lon/lat points.
  for (; point_begin != point_end; ++point_begin)
    {
    double lon_degrees = point_begin->template get<0>();
    double lat_degrees = point_begin->template get<1>();
    while (lon_degrees > 360) lon_degrees -= 360;
    while (lon_degrees < 0) lon_degrees += 360;

    double lon_radians = tracktable::conversions::radians(lon_degrees);
    double lat_radians = tracktable::conversions::radians(lat_degrees);

    x += cos(lat_radians) * cos(lon_radians);
    y += cos(lat_radians) * sin(lon_radians);
    z += sin(lat_radians);
    ++num_points;
    }

  x /= num_points;
  y /= num_points;
  z /= num_points;

  // Guard against roundoff error taking us off the sphere
  x = std::min(std::max(-1.0, x), 1.0);
  y = std::min(std::max(-1.0, y), 1.0);
  z = std::min(std::max(-1.0, z), 1.0);

  // Project from 3-space back into lon/lat.
  double center_lon = tracktable::conversions::degrees(atan2(y, x));
  double center_lat = tracktable::conversions::degrees(
    atan2(z, sqrt(x*x + y*y))
    );
  return PointLonLat(center_lon, center_lat);
}

template<typename point_iter_type, typename insert_iter_type>
void convert_points_to_cartesian(point_iter_type point_begin,
                                 point_iter_type point_end,
                                 insert_iter_type output)
{
  while (point_begin != point_end)
    {
    *output++ = to_cartesian(*point_begin);
    ++point_begin;
    }
}

} } }

#endif
