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

//
//   test
//
//

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>

#include <boost/geometry/arithmetic/arithmetic.hpp>
#include <boost/geometry/algorithms/distance.hpp>
#include <iostream>

template<class point_type>
void test_geometry_math()
{
  double sample_points[][2] = {
    { 100, 0 },
    { 105.0, 45 },
    { 110.0, 30 },
    { 115.0, 35 },
    { 120.0, 40 },
    { 125.0, 45 }
  };

  // Try declaring points
  point_type point1(sample_points[0]);
  point_type point2(sample_points[1]);

  // Compute distance between them
  double distance = boost::geometry::distance(point1, point2);

  std::cout << "Basic point/point distance: " << distance << "\n";
  // Now some point/track distance examples
  point_type point3(sample_points[2]);
  point_type point4(sample_points[3]);
  point_type point5(sample_points[4]);
  point_type point6(sample_points[5]);

  tracktable::Trajectory<point_type> track;
  track.push_back(point3);
  track.push_back(point4);
  track.push_back(point5);
  track.push_back(point6);

  distance = boost::geometry::distance(track, point3);
  std::cout << "Point/track distance: " << distance << "\n";

  boost::geometry::multiply_value(point3, 0.5);

}

int main()
{
  test_geometry_math< tracktable::TrajectoryPoint<tracktable::PointLonLat> >();
//  test_geometry_math<tracktable::PointBaseLonLat<double> >();
  return 0;
}
