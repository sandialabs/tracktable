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

#include <cmath>

#include <iostream>
#include <sstream>

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

typedef tracktable::PointCartesian<2> Point2D;
typedef tracktable::TrajectoryPoint<Point2D> TrajectoryPoint2D;
typedef tracktable::Trajectory<TrajectoryPoint2D> Trajectory2D;

int test_point_at_time_fraction()
{
  Trajectory2D test_trajectory;

  TrajectoryPoint2D points[3];
  points[0][0] = 0;
  points[0][1] = 0;
  points[0].set_object_id("test");
  points[0].set_timestamp(tracktable::time_from_string("2010-01-01 00:00:00"));

  points[1][0] = 4;
  points[1][1] = 1;
  points[1].set_object_id("test");
  points[1].set_timestamp(tracktable::time_from_string("2010-01-01 02:00:00"));

  points[2][0] = 8;
  points[2][1] = 0;
  points[2].set_object_id("test");
  points[2].set_timestamp(tracktable::time_from_string("2010-01-01 04:00:00"));

  test_trajectory.push_back(points[0]);
  test_trajectory.push_back(points[1]);
  test_trajectory.push_back(points[2]);

  int error_count = 0;
  TrajectoryPoint2D halfway = tracktable::point_at_time_fraction(test_trajectory, 0.5);
  if (halfway != points[1])
    {
    std::cout << "ERROR: Expected halfway point to return exactly the second point.\n";
    std::cout << "Expected point: " << points[1].to_string() << "\n";
    std::cout << "Got point:      " << halfway.to_string() << "\n";
    ++error_count;
    }

  Point2D one_quarter = tracktable::point_at_time_fraction(test_trajectory, 0.25);
  if (!(tracktable::almost_equal(one_quarter[0], 2.0) &&
        tracktable::almost_equal(one_quarter[1], 0.5)))
    {
    std::cout << "ERROR: Expected one-quarter point to be at (2, 0.5).  Instead it is at ("
              << one_quarter[0] << ", " << one_quarter[1]
              << ").\n";
    ++error_count;
    }

  return error_count;
}

int main(int, char **)
{
  return test_point_at_time_fraction();
}
