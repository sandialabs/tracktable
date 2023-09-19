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

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/Geometry.h>

#include <cmath>
#include <iostream>


template<typename path_type>
int test_convex_hull_aspect_ratio(path_type const& path, double expected_answer)
{
  double actual_ratio = tracktable::convex_hull_aspect_ratio(path);
  double residual = fabs(actual_ratio - expected_answer);

  if (tracktable::almost_zero(actual_ratio))
    {
    return tracktable::almost_zero(residual, 1e-5);
    }
  else
    {
    return tracktable::almost_zero((residual / expected_answer), 1e-5);
    }
}

int main(int /*argc*/, char* /*argv*/[])
{
  typedef tracktable::PointCartesian<2> Point2D;
  typedef tracktable::TrajectoryPoint<Point2D> TrajectoryPoint2D;
  typedef tracktable::Trajectory<TrajectoryPoint2D> Trajectory2D;

  double corners[4][2] = { { 0, 0 }, { 1, 0 }, { 1, 1 }, { 0, 1 } };
  Trajectory2D cartesian_trajectory;
  cartesian_trajectory.push_back(Point2D(corners[0]));
  cartesian_trajectory.push_back(Point2D(corners[1]));
  cartesian_trajectory.push_back(Point2D(corners[2]));
  cartesian_trajectory.push_back(Point2D(corners[3]));

  int error_count = 0;
  error_count += test_convex_hull_aspect_ratio(cartesian_trajectory, 0.707107);
}
