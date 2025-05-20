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

#include <tracktable/Core/GeometricMedian.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>
#include <iostream>

template<class point_type>
void test_geometric_median_2d(std::string const& type_name)
{
  std::size_t NUM_TEST_POINTS = 6;

  double sample_points[][2] = {
    { 10, 3 },
    { 12, 44 },
    { 15, 50 },
    { 14, 41 },
    { 16, 42 },
    { 20, 46 }
  };

  std::vector<point_type> points;
  for (std::size_t i = 0; i < NUM_TEST_POINTS; ++i)
    {
    point_type next_point;
    next_point[0] = sample_points[i][0];
    next_point[1] = sample_points[i][1];
    points.push_back(next_point);
    }

  point_type median = tracktable::arithmetic::geometric_median(points.begin(), points.end());

  std::cout << "INFO: Geometric median for type '"
            << type_name << "': "
            << median << "\n";
}


int main()
{
  test_geometric_median_2d<tracktable::PointLonLat>("PointLonLat");
  test_geometric_median_2d<tracktable::PointCartesian<2> >("PointCartesian2D");

  return 0;
}
