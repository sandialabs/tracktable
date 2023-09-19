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

#ifndef __tracktable_convex_hull_centroid_terrestrial_h
#define __tracktable_convex_hull_centroid_terrestrial_h

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/detail/implementations/ConvexHullTerrestrial.h>

#include <boost/geometry/core/cs.hpp>

namespace tracktable { namespace algorithms {

namespace bg = boost::geometry;
typedef PointCartesian<3> Point3D;

template<>
struct compute_convex_hull_centroid<
  bg::cs::spherical_equatorial<bg::degree>, 2
  >
{
  template<typename iterator>
  static inline typename iterator::value_type apply(iterator point_begin, iterator point_end)
    {
      typedef typename iterator::value_type point_type;
      typedef bg::model::polygon<point_type> polygon_type;
      polygon_type hull;

      implementations::compute_convex_hull_terrestrial(point_begin, point_end, hull);
      return apply(hull);
    }

  template<typename point_type>
  static inline point_type apply(bg::model::polygon<point_type> const& hull)
    {
      return compute_centroid_from_hull(hull);
    }

  template<typename point_type>
  static inline point_type compute_centroid_from_hull(bg::model::polygon<point_type> const& hull)
    {
      // Start with the center of mass of the vertices of the convex
      // hull (will by definition be inside the hull)
      PointLonLat center_of_mass_lonlat = spherical_math::terrestrial_center_of_mass(hull.outer().begin(), hull.outer().end());
      TRACKTABLE_LOG(log::trace) << "center of mass lonlat: " << center_of_mass_lonlat.to_string();
      Point3D center_of_mass_cartesian = spherical_math::to_cartesian(center_of_mass_lonlat);

      // Our spherical math routines assume that we have points on the
      // surface of the sphere specified in Cartesian coordinates
      std::vector<Point3D> hull_cartesian;
      spherical_math::convert_points_to_cartesian(hull.outer().begin(),
                                                  hull.outer().end(),
                                                  std::back_inserter(hull_cartesian));

      // Now compute the centroid by walking around the convex hull,
      // computing centers of mass of the spherical triangles between
      // that center of mass and each edge, and finding their average.
      std::vector<Point3D>::iterator this_point, previous_point;
      this_point = hull_cartesian.begin();
      previous_point = this_point;
      std::vector<Point3D> weighted_centroids;
      double total_area = 0;

      for (; this_point != hull_cartesian.end(); ++this_point)
        {
        if (this_point != previous_point)
          {
          double angles[3];
          spherical_polygons::compute_spherical_triangle_central_angles(
            *previous_point, *this_point,
            center_of_mass_cartesian,
            angles
            );

          double area = spherical_polygons::compute_spherical_triangle_area(angles[0], angles[1], angles[2]);
          total_area += area;
          Point3D center_of_mass(
            spherical_polygons::compute_spherical_triangle_center_of_mass(
              *previous_point, *this_point, center_of_mass_cartesian
              ));

          TRACKTABLE_LOG(log::trace)
             << "centroid: latest area is " << area << ", center of mass is "
             << spherical_math::to_terrestrial<point_type>(center_of_mass).to_string();

          tracktable::arithmetic::multiply_scalar_in_place(center_of_mass, area);
          weighted_centroids.push_back(center_of_mass);
          }
        previous_point = this_point;
        }

      Point3D final_centroid_cartesian = tracktable::arithmetic::zero<Point3D>();
      for (this_point = weighted_centroids.begin();
           this_point != weighted_centroids.end();
           ++this_point)
        {
        tracktable::arithmetic::add_in_place(final_centroid_cartesian,
                                             *this_point);
        }
      tracktable::arithmetic::divide_scalar_in_place(final_centroid_cartesian, total_area);
      // Normalize to magnitude 1
      tracktable::arithmetic::divide_scalar_in_place(
        final_centroid_cartesian,
        tracktable::arithmetic::norm(final_centroid_cartesian)
        );

      return spherical_math::to_terrestrial<point_type>(final_centroid_cartesian);
    }
};


} }

#endif
