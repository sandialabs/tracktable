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
#include <tracktable/Core/PointBase.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>

#include <iostream>
#include <sstream>

typedef tracktable::PointCartesian<2> Point2D;
typedef tracktable::TrajectoryPoint<Point2D> TrajectoryPoint2D;
typedef tracktable::Trajectory<TrajectoryPoint2D> Trajectory2D;

// ----------------------------------------------------------------------

int test_trajectory_current_length()
{
  TrajectoryPoint2D point;
  Trajectory2D trajectory;

  point[0] = 0;
  point[1] = 0;
  trajectory.push_back(point);

  point[0] = 0;
  point[1] = 1;
  trajectory.push_back(point);

  point[0] = 0;
  point[1] = 3;
  trajectory.push_back(point);

  point[0] = 0;
  point[1] = 4;
  trajectory.push_back(point);

  double expected_values[4] = { 0, 1, 3, 4 };
  int num_errors = 0;

  std::cout << "Current length at each point in trajectory:\n";
  for (std::size_t i = 0; i < trajectory.size(); ++i)
    {
    std::cout << "Point " << i << ": " << trajectory[i].current_length() << "\n";
    if (!tracktable::almost_equal(trajectory[i].current_length(), expected_values[i]))
      {
      std::cout << "ERROR: Expected value " << expected_values[i] << "!\n";
      ++num_errors;
      }
    }
  return num_errors;
}

int main(int /*argc*/, char* /*argv*/[])
{
  return test_trajectory_current_length();
}

