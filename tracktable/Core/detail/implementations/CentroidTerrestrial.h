/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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

#ifndef __tracktable_spherical_polygon_centroid_h
#define __tracktable_spherical_polygon_centroid_h

#define _USE_MATH_DEFINES
#include <cmath>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/detail/implementations/ConvexHullTerrestrial.h>

namespace tracktable { namespace algorithms { namespace convex_hull_utilities {

typedef PointCartesian<3> Point3D;

template<typename terrestrial_point_type>
Point3D to_cartesian(terrestrial_point_type const& original_point)
{
  double longitude = original_point.template get<0>();
  double latitude = original_point.template get<1>();

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

inline double angle_between(Point3D const& point1, Point3D const& point2)
{
  return acos(tracktable::arithmetic::dot(point1, point2));
}

// ----------------------------------------------------------------------

// Compute the central angles of a spherical triangle given its three
// vertices A, B and C.

inline void compute_spherical_triangle_central_angles(Point3D const& A,
                                              Point3D const& B,
                                              Point3D const& C,
                                              double out_angles[3])
{
  out_angles[0] = angle_between(B, C);
  out_angles[1] = angle_between(C, A);
  out_angles[2] = angle_between(A, B);
}

// ----------------------------------------------------------------------

// Compute the area of a spherical triangle given the three central
// angles a, b and c.
inline double compute_spherical_triangle_area(double a, double b, double c)
{
  double cos_a = cos(a);
  double cos_b = cos(b);
  double cos_c = cos(c);
  double sin_a = sin(a);
  double sin_b = sin(b);
  double sin_c = sin(c);

  // Angles on the surface of the sphere -- i.e. the internal angles
  // of the triangle.  These are what we can use to compute the area.
  // These formulas are instantiations of the cosine rule for
  // spherical triangles.
  double A, B, C;
  A = acos((cos_a - cos_b * cos_c) / (sin_b * sin_c));
  B = acos((cos_b - cos_c * cos_a) / (sin_c * sin_a));
  C = acos((cos_c - cos_a * cos_b) / (sin_a * sin_b));

  return (A + B + C - M_PI);
}

// ----------------------------------------------------------------------

// Compute the cross product of two 3D vectors.

inline Point3D cross_product(Point3D const& a, Point3D const& b)
{
  Point3D result;
  result.set<0>(a[1]*b[2] - a[2]*b[1]);
  result.set<1>(a[2]*b[0] - a[0]*b[2]);
  result.set<2>(a[0]*b[1] - a[1]*b[0]);
  return result;
}

// ----------------------------------------------------------------------

// Compute the center of mass of a spherical triangle given its
// central angles and the three unit vectors toward the vertices.

inline Point3D compute_spherical_triangle_center_of_mass(double central_angles[3],
                                                         Point3D unit_vectors[3])
{
  Point3D result;

  result = tracktable::arithmetic::multiply_scalar(
    cross_product(unit_vectors[0], unit_vectors[1]),
    central_angles[2]);

  tracktable::arithmetic::add_in_place(
    result,
    tracktable::arithmetic::multiply_scalar(
      cross_product(unit_vectors[1], unit_vectors[2]),
      central_angles[0]
      ));

  tracktable::arithmetic::add_in_place(
    result,
    tracktable::arithmetic::multiply_scalar(
      cross_product(unit_vectors[2], unit_vectors[0]),
      central_angles[1]
      ));

  return tracktable::arithmetic::divide_scalar(
    result,
    2 * spherical_triangle_area(
      central_angles[0], central_angles[1], central_angles[2]
      ));
}

// ----------------------------------------------------------------------

template<typename iterator>
inline double compute_spherical_polygon_area(iterator point_begin,
                                             iterator point_end)
{
  std::vector<Point3D> points_3d;

  for (iterator here = point_begin; here != point_end; ++here)
    {
    points_3d.push_back(to_cartesian(*here));
    }

  double weighted_coordinate_sums[3] = { 0, 0, 0 };
  double total_area_sum = 0;

  for (typename std::vector<Point3D>::iterator here = points_3d.begin();
       (here + 2) != points_3d.end();
       ++here)
    {
    double area = spherical_triangle_area(here, here+1, here+2);
    total_area_sum += area;
    }
  return total_area_sum;
}

// ----------------------------------------------------------------------

template<typename polygon_type>
struct compute_convex_hull_centroid
{
  typedef typename polygon_type::Point point_type;
  point_iterator::value_type point_type;
  typedef PointCartesian<3> Point3D;

  static inline point_type apply(polygon_type const& hull)
    {
      // Start with the center of mass of the vertices of the convex
      // hull (will by definition be inside the hull)
      PointLonLat center_of_mass_lonlat = convex_hull_utilities::LonLatCentroid(hull.outer().begin(), hull.outer().end());
      Point3D center_of_mass_cartesian = to_cartesian(center_of_mass_lonlat);

      // Convert the convex hull into 3D coordinates - easier to do
      // computations that way
      std::vector<Point3D> hull_cartesian;
      for (typename polygon_type::PointList::iterator iter = hull.outer().begin();
           iter != hull.outer().end();
           ++iter)
        {
        hull_cartesian.push_back(to_cartesian(*iter));
        }

      // Now compute the centroid by walking around the convex hull,
      // computing centers of mass of the spherical triangles between
      // that center of mass and each edge, and finding their average.
      std:vector<Point3D>::iterator this_point, previous_point;
      this_point = hull_cartesian.begin();
      previous_point = this_point;
      std::vector<Point3D> weighted_centroids;
      double total_area = 0;

      for (; this_point != hull_cartesian.end(); ++this_point)
        {
        if (this_point != previous_point)
          {
          double angles[3];
          compute_spherical_triangle_central_angles(*previous_point, *this_point, center_of_mass_cartesian, angles);
          double area = spherical_triangle_area(angles[0], angles[1], angles[2]);
          total_area += area;
          Point3D center_of_mass(
            spherical_triangle_center_of_mass(
              angles, *previous_point, *this_point, center_of_mass_cartesian
              ));
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

      return to_terrestrial(final_centroid_cartesian);
    };
};

} } } // tracktable::algorithms::convex_hull_utilities

namespace tracktable { namespace algorithms {

template<>
struct convex_hull_aspect_ratio<
  boost::geometry::cs::spherical_equatorial<
    boost::geometry_degree
    >, 2
  >
{
  template<typename iterator>
  static inline double apply(iterator point_begin, iterator point_end)
    {
      typedef typename iterator::value_type point_type;
      typedef boost::geometry::model::polygon<point_type> polygon_type;
      polygon_type hull;

      convex_hull_terrestrial(point_begin, point_end, hull);
      point_type centroid(convex_hull_utilities::compute_convex_hull_centroid::apply(hull));

      double short_axis = tracktable::conversions::radians_to_km(boost::geometry::distance(centroid, hull));
      double long_axis = 0;
      for (typename polygon_type::PointList::iterator hull_iter = hull.outer().begin();
           hull_iter != hull.outer().end();
           ++hull_iter)
        {
        long_axis = std::max(boost::geometry::distance(centroid, *hull_iter));
        }
      long_axis = tracktable::conversions::radians_to_km(long_axis);
      if (long_axis == 0)
        {
        return 0;
        }
      else
        {
        return short_axis / long_axis;
        }
    }
};

} }

#endif
