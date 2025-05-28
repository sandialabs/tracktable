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

#ifndef __tracktable_ProjectedConvexHullTerrestrial_h
#define __tracktable_ProjectedConvexHullTerrestrial_h

#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>

#include <boost/geometry/algorithms/convex_hull.hpp>
#include <boost/geometry/geometries/polygon.hpp>
#include <boost/geometry/geometries/linestring.hpp>

#include <tracktable/Core/detail/implementations/SphericalMath.h>

#include <cmath>
#include <vector>
#include <algorithm>
#include <iostream>

namespace tracktable { namespace algorithms { namespace implementations {

namespace convex_hull_utilities {

namespace bg = boost::geometry;


// ----------------------------------------------------------------------

// We require that the iterator be a ForwardIterator so that we can
// traverse the range twice.
template<typename iterator>
void RotatePointsToNorthPole(iterator point_begin, iterator point_end,
                             PointLonLat const& centroid)
{
  // Rotate so that the center is at longitude 0.0.  No trig required.
  TRACKTABLE_LOG(log::trace)
    << "RotatePointsToNorthPole: Removing latitude excess "
    << centroid[1];

  for (iterator here = point_begin; here != point_end; ++here)
    {
    double new_lon = fmod(here->template get<0>() - centroid.get<0>(),
                          360.0);
    here->template set<0>(new_lon);
    }

  // Now rotate points so that the center is at latitude 90 degrees
  // (the North Pole).

  using tracktable::conversions::radians;
  using tracktable::conversions::degrees;
  for (iterator here = point_begin; here != point_end; ++here)
    {
    double old_lon = radians(here->template get<0>());
    double old_lat = radians(here->template get<1>());
    double theta = radians(centroid.template get<1>());

    double new_lon = atan2(
      sin(old_lon) * cos(old_lat),
      cos(old_lon) * cos(old_lat) * sin(theta) - sin(old_lat) * cos(theta)
      );
    double new_lat = asin(
      sin(old_lat)*sin(theta) + cos(old_lon)*cos(old_lat)*cos(theta)
      );

    here->template set<0>(degrees(new_lon));
    here->template set<1>(degrees(new_lat));
    }
}

// ----------------------------------------------------------------------

template<typename lonlat_iterator, typename point_type>
void ComputeNorthPoleHull(lonlat_iterator point_begin,
                          lonlat_iterator point_end,
                          bg::model::polygon<point_type>& lonlat_hull)
{
  typedef PointCartesian<2> Point2D;
  typedef boost::geometry::model::polygon<Point2D> Polygon2D;
  Polygon2D projection, flat_hull;

  using tracktable::conversions::radians;
  using tracktable::conversions::degrees;

  lonlat_hull.clear();

  // Project points down to a plane through the equator
  for (lonlat_iterator here = point_begin;
       here != point_end;
       ++here)
    {
    double r = cos(radians(here->template get<1>()));
    Point2D flat_point;
    flat_point.set<0>(r * cos(radians(here->template get<0>())));
    flat_point.set<1>(r * sin(radians(here->template get<0>())));
    boost::geometry::append(projection, flat_point);
    }

  // Now we can finally calculate the convex hull.  Take it away,
  // Boost!
  boost::geometry::convex_hull(projection, flat_hull);

  // And project back up to the sphere.
  for (typename Polygon2D::ring_type::iterator hull_iter = flat_hull.outer().begin();
       hull_iter != flat_hull.outer().end();
       ++hull_iter)
    {
    double x = hull_iter->get<0>();
    double y = hull_iter->get<1>();
    point_type sphere_point;
    sphere_point.template set<0>(degrees(atan2(y, x)));
    sphere_point.template set<1>(degrees(acos(sqrt(x*x + y*y))));
    lonlat_hull.outer().push_back(sphere_point);
    }

  // Remember that the points are still centered on the north pole.
  // We'll undo that in ReturnPointsFromNorthPole.
}

// ----------------------------------------------------------------------

template<typename iterator, typename point_type>
void ReturnPointsFromNorthPole(iterator point_begin, iterator point_end,
                               point_type const& center)
{
  using tracktable::conversions::degrees;
  using tracktable::conversions::radians;

  // This inverts the rotation done in RotatePointsToNorthPole.
  double theta = radians(center.template get<1>());
  for (iterator here = point_begin; here != point_end; ++here)
    {
    double old_lon = radians(here->template get<0>());
    double old_lat = radians(here->template get<1>());

    double new_lon = atan2(
      sin(old_lon)*cos(old_lat),
      cos(old_lon)*cos(old_lat)*sin(theta) + sin(old_lat)*cos(theta)
      );
    double new_lat = asin(
      sin(old_lat)*sin(theta) - cos(old_lon)*cos(old_lat)*cos(theta)
      );

    here->template set<0>(degrees(new_lon));
    here->template set<1>(degrees(new_lat));
    }

  for (iterator here = point_begin; here != point_end; ++here)
    {
    double final_lon = fmod(here->template get<0>() + center.template get<0>(), 360.0);
    here->template set<0>(final_lon);
    }
}


} // namespace convex_hull_utilities

} } } // namespace tracktable::algorithms::implementation


#endif
