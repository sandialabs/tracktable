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

/*
 * This test case exercises code in the case of a degenerate (zero-area)
 * convex hull.
 *
 * Consider a trajectory comprising the following three points:
 * A 44,33
 * B 44.0769, 32.5862
 * C 44,33
 *
 * Since the start and end points are the same, the convex hull lies
 * entirely on top of the line segment from A to B.
 *
 * Strictly speaking, the aspect ratio is indeed undefined.  The aspect
 * ratio of a polygon, or indeed a general 2D point cloud, is the ratio
 * between its maximum and minimum eigenvalues.
 *
 * The convex hull area should be zero.  The convex hull perimeter should
 * be twice the distance between points A and B.
 */

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/Geometry.h>

#include <cmath>
#include <iostream>


bool close_enough(double actual, double expected)
{
  double residual = actual - expected;
  if (tracktable::almost_zero(expected))
  {
    return tracktable::almost_zero(residual);
  }
  else
  {
    std::cout << "close_enough: residual / expected is " << residual / expected << "\n";
    std::cout << "almost_zero result is "
              << tracktable::almost_zero(residual / expected, 1e-5)
              << "\n";
    return tracktable::almost_zero(residual/expected, 1e-5);
  }
}

int main(int /*argc*/, char* /*argv*/[])
{
  typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> trajectory_point_type;
  typedef tracktable::Trajectory<trajectory_point_type> trajectory_type;

  double corners[3][2] = {
      { 44, 33 },
      { 44.0769, 32.5862 },
      { 44, 33 }
    };

  trajectory_type linestring;
  linestring.push_back(trajectory_point_type(corners[0]));
  linestring.push_back(trajectory_point_type(corners[1]));
  linestring.push_back(trajectory_point_type(corners[2]));

  double aspect = tracktable::convex_hull_aspect_ratio(linestring);
  double area = tracktable::convex_hull_area(linestring);
  double perimeter = tracktable::convex_hull_perimeter(linestring);

  int error_count = 0;
  if (!close_enough(aspect, 0))
  {
    ++error_count;
    std::cout << "ERROR: Aspect ratio: Expected 0, got " << aspect << "\n";
  }
  if (!close_enough(area, 0)) {
    ++error_count;
    std::cout << "ERROR: Area: Expected 0, got " << area << "\n";
  }
  if (!close_enough(perimeter, 93.1411)) {
    ++error_count;
    std::cout << "ERROR: Perimeter: Expected 93.1411, got " << perimeter << "\n";
  }

  return error_count;
}

