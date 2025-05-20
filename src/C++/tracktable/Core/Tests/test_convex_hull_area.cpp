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

#include <tracktable/Core/Geometry.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

#include <algorithm>
#include <iostream>
#include <vector>
#include <typeinfo>

// Test the area of the convex hull of the box from (0, 0) to (1, 1)

template<typename container_type>
int test_convex_hull_area(double expected_result)
{
  typedef typename container_type::value_type point_type;

  container_type linestring;
  double point0[2] = { 0, 0 };
  double point1[2] = { 0, 1 };
  double point2[2] = { 1, 1 };
  double point3[2] = { 1, 0 };

  linestring.push_back(point_type(point0));
  linestring.push_back(point_type(point1));
  linestring.push_back(point_type(point2));
  linestring.push_back(point_type(point3));


  double area = tracktable::convex_hull_area(linestring);
  double error = std::abs(area - expected_result);

  std::cout << "DEBUG: Area of convex hull is "
            << area << "\n";

  if (error < 0.001)
    {
    return 0;
    }
  else
    {
    std::cout << "ERROR: Expected convex hull area for point type "
              << typeid(point_type).name()
              << " and container type "
              << typeid(container_type).name()
              << " to be "
              << expected_result
              << " but got "
              << area
              << " instead (difference = "
              << error
              << ")\n";
    return 1;
    }
}

int main(int /*argc*/, char* /*argv*/[])
{
  int error_count = 0;

  typedef tracktable::PointLonLat point_ll;
  typedef tracktable::PointCartesian<2> point_2d;

  error_count += test_convex_hull_area<std::vector<point_ll> >(12363.9978);
  error_count += test_convex_hull_area<
    tracktable::Trajectory<
      tracktable::TrajectoryPoint<point_ll>
      > >(12363.9978);
  error_count += test_convex_hull_area<
    std::vector<point_2d>
    >(1);
  error_count += test_convex_hull_area<
    tracktable::Trajectory<
      tracktable::TrajectoryPoint<point_2d>
      > >(1);

  return error_count;
}
