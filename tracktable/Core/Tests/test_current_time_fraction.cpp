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
#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Terrestrial.h>

#include <iostream>
#include <sstream>

typedef tracktable::domain::cartesian2d::trajectory_point_type TrajectoryPointCartesian2D;
typedef tracktable::domain::cartesian2d::trajectory_type TrajectoryCartesian2D;
typedef tracktable::domain::terrestrial::trajectory_point_type TrajectoryPointTerrestrial;
typedef tracktable::domain::terrestrial::trajectory_type TrajectoryTerrestrial;

// ----------------------------------------------------------------------

int test_trajectory_current_time_fraction_cartesian2D()
{
  TrajectoryPointCartesian2D point;
  TrajectoryCartesian2D trajectory;

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 5:00:00.00"));
  trajectory.push_back(point);

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 6:00:00.00"));
  trajectory.push_back(point);

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 8:00:00.00"));
  trajectory.push_back(point);

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 9:00:00.00"));
  trajectory.push_back(point);

  double expected_values[4] = { 0.0, .25, .75, 1.0 };
  int num_errors = 0;

  std::cout << "Current time fraction at each point in trajectory (Cartesian2d):\n";
  for (std::size_t i = 0; i < trajectory.size(); ++i)
    {
    std::cout << "Point " << i << ": " << trajectory[i].current_time_fraction() << "\n";
    if (!tracktable::almost_equal(trajectory[i].current_time_fraction(), expected_values[i]))
      {
      std::cout << "ERROR: Expected value " << expected_values[i] << "!\n";
      ++num_errors;
      }
    }
  return num_errors;
}

// ----------------------------------------------------------------------

int test_trajectory_current_time_fraction_terrestrial()
{
  TrajectoryPointTerrestrial point;
  TrajectoryTerrestrial trajectory;

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 5:00:00.00"));
  trajectory.push_back(point);

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 6:00:00.00"));
  trajectory.push_back(point);

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 8:00:00.00"));
  trajectory.push_back(point);

  point.set_timestamp(boost::posix_time::time_from_string("2020/9/3 9:00:00.00"));
  trajectory.push_back(point);

  double expected_values[4] = { 0.0, .25, .75, 1.0 };
  int num_errors = 0;

  std::cout << "Current time fraction at each point in trajectory (Terrestrial:\n";
  for (std::size_t i = 0; i < trajectory.size(); ++i)
    {
    std::cout << "Point " << i << ": " << trajectory[i].current_time_fraction() << "\n";
    if (!tracktable::almost_equal(trajectory[i].current_time_fraction(), expected_values[i]))
      {
      std::cout << "ERROR: Expected value " << expected_values[i] << "!\n";
      ++num_errors;
      }
    }
  return num_errors;
}

int main(int /*argc*/, char* /*argv*/[])
{
  int num_errors = 0;
  num_errors += test_trajectory_current_time_fraction_cartesian2D();
  num_errors += test_trajectory_current_time_fraction_terrestrial();
  return num_errors;
}

