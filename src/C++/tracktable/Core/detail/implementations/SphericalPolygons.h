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

#ifndef __tracktable_core_implementations_SphericalPolygons_h
#define __tracktable_core_implementations_SphericalPolygons_h

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/detail/implementations/ConvexHullTerrestrial.h>
#include <tracktable/Core/detail/implementations/ProjectedConvexHullTerrestrial.h>
namespace tracktable { namespace algorithms { namespace spherical_polygons {

namespace bg = boost::geometry;

using tracktable::algorithms::spherical_math::to_terrestrial;
using tracktable::algorithms::spherical_math::to_cartesian;

typedef tracktable::PointCartesian<3> Point3D;

namespace {
  static const double PI = 3.141592653589793238462643383;
}

// ----------------------------------------------------------------------

inline double angle_between(Point3D const& point1, Point3D const& point2)
{
  return acos(tracktable::arithmetic::dot(point1, point2));
}

// ----------------------------------------------------------------------

// Compute the central angles of a spherical triangle given its three
// vertices A, B and C.
//
// The central angles are the angles subtended by each side of the
// triangle.  If O is a point at the center of the sphere, they are
// angles BOC, COA and AOB.

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

  return (A + B + C - PI);
}


inline double compute_spherical_triangle_area(const double central_angles[3])
{
  return compute_spherical_triangle_area(
    central_angles[0],
    central_angles[1],
    central_angles[2]);
}

inline double compute_spherical_triangle_area(Point3D const& point1,
                                              Point3D const& point2,
                                              Point3D const& point3)
{
  double angles[3];
  compute_spherical_triangle_central_angles(point1, point2, point3, angles);
  return compute_spherical_triangle_area(angles);
}


// ----------------------------------------------------------------------

// Compute the center of mass of a spherical triangle given its three
// corners in Cartesian coordinates.

inline Point3D compute_spherical_triangle_center_of_mass(Point3D const& A,
                                                         Point3D const& B,
                                                         Point3D const& C)
{
  Point3D result(A);
  tracktable::arithmetic::add_in_place(result, B);
  tracktable::arithmetic::add_in_place(result, C);

  tracktable::arithmetic::divide_scalar_in_place(
    result,
    tracktable::arithmetic::norm(result)
    );

  return result;
}

// ----------------------------------------------------------------------

template<typename iterator>
inline double compute_polygon_area(iterator point_begin,
                                   iterator point_end)
{
  std::vector<Point3D> points_3d;

  for (iterator here = point_begin; here != point_end; ++here)
    {
    points_3d.push_back(to_cartesian(*here));
    }

  double total_area_sum = 0;

  typename std::vector<Point3D>::iterator sequence_end = points_3d.end();
  for (typename std::vector<Point3D>::iterator here = points_3d.begin();
       (sequence_end - here) >= 3;
       here += 2)
    {
    double area = compute_spherical_triangle_area(*here, *(here+1), *(here+2));
    total_area_sum += area;
    }
  return total_area_sum;
}

// ----------------------------------------------------------------------

template<typename polygon_type>
typename polygon_type::Point compute_centroid(polygon_type const& polygon)
{
  typedef typename polygon_type::Point point_type;

  // Start with the center of mass of the vertices of the polygon.  If
  // the polygon is convex, this is guaranteed to be inside the
  // polygon.

  PointLonLat center_of_mass_lonlat =
    spherical_math::terrestrial_center_of_mass(polygon.outer().begin(), polygon.outer().end());
  Point3D center_of_mass_cartesian = to_cartesian(center_of_mass_lonlat);

  // Convert the convex hull into 3D coordinates - easier to do
  // computations that way
  std::vector<Point3D> hull_cartesian;
  for (typename polygon_type::PointList::iterator iter = polygon.outer().begin();
       iter != polygon.outer().end();
       ++iter)
    {
    hull_cartesian.push_back(to_cartesian(*iter));
    }

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
      compute_spherical_triangle_central_angles(*previous_point, *this_point, center_of_mass_cartesian, angles);
      double area = compute_spherical_triangle_area(angles);
      total_area += area;
      Point3D center_of_mass(
        compute_spherical_triangle_center_of_mass(
          *previous_point, *this_point, center_of_mass_cartesian
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

  return to_terrestrial<point_type>(final_centroid_cartesian);
}

} } } // tracktable::algorithms::convex_hull_utilities


#endif
