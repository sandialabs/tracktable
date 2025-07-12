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

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>

#include <iostream>
#include <sstream>

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>

typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> TrajectoryPointLonLat;
typedef tracktable::Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

/*
 * We need to test the following cases:
 *
 * Slicing a trajectory results in the correct points
 *
 * Slicing a trajectory keeps the original trajectory's properties
 */

using boost::posix_time::time_from_string;
using boost::posix_time::time_duration;
using boost::posix_time::hours;
using boost::posix_time::minutes;


void print_trajectory_timestamps(TrajectoryLonLat const& traj)
{
  std::cout << "DEBUG: Trajectory timestamps: ";
  for (TrajectoryLonLat::size_type i = 0; i < traj.size(); ++i)
    {
    std::cout << "(" << i << ") " << traj[i].timestamp() << " ";
    }
  std::cout << "\n";
}

void print_trajectory_point(TrajectoryPointLonLat const& point)
{
  std::cout << "Object ID:       " << point.object_id() << "\n";
  std::cout << "Timestamp:       " << point.timestamp() << "\n";
  std::cout << "Longitude:       " << point.longitude() << "\n";
  std::cout << "Latitude:        " << point.latitude() << "\n";
}

// ----------------------------------------------------------------------

TrajectoryLonLat make_test_surface_trajectory()
{
  TrajectoryLonLat result;

  tracktable::Timestamp current_time = time_from_string("2014-01-01 00:00:00");
  double current_longitude = 100;
  double current_latitude = 100;

  double longitude_step = 10;
  double latitude_step = 10;
  time_duration time_step(minutes(30));
  std::string object_id("FOOD");

  for (int i = 0; i < 20; ++i)
    {
    TrajectoryPointLonLat next_point;
    next_point.set_object_id(object_id);
    next_point.set_timestamp(current_time);
    next_point.set_longitude(current_longitude);
    next_point.set_latitude(current_latitude);
    result.push_back(next_point);

    current_time += time_step;
    current_longitude += longitude_step;
    current_latitude += latitude_step;
    }

  result.set_property("number", 123);
  result.set_property("pilot", "Melissa");

//  result.recompute_speed();
//  result.recompute_heading();
  return result;
}

// ----------------------------------------------------------------------

int test_create_trajectory()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  std::cout << "Sample trajectory has "
	    << trajectory.size() << " points. Its first point is:\n";
  print_trajectory_point(trajectory.front());
  std::cout << "\nIts last point is:\n";
  print_trajectory_point(trajectory.back());

  return 0;
}

// ---------------------------------------------------------------------

int test_slicing()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  // This causes a compile error on Windows
  TrajectoryLonLat subset = TrajectoryLonLat(trajectory.begin()+4, trajectory.begin()+18, trajectory);

  if (subset.size() != 14){
     std::cout << "ERROR: test_slicing: Expected 14 points but got " << subset.size() << " points";
     return 1;
  }
  return 0;
}

// -----------------------------------------------------------------------

int test_property_number()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  TrajectoryLonLat subset = TrajectoryLonLat(trajectory.begin()+6, trajectory.begin()+14, trajectory);

  if (!subset.has_property("number"))
  {
     std::cout << "ERROR: test_property_number: Subset expected to have property number but does not";
     return 1;
  }

  if (subset.real_property("number")!= trajectory.real_property("number"))
  {
    std::cout << "ERROR: test_property_number: Subset expected to have number 123 but got " << subset.real_property("number") << " instead";
    return 1;
  }
  return 0;
}

// ------------------------------------------------------------------------

int test_property_pilot()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  TrajectoryLonLat subset = TrajectoryLonLat(trajectory.begin()+6, trajectory.begin()+14, trajectory);

  if (!subset.has_property("pilot"))
  {
    std::cout << "ERROR: test_property_pilot: Subset expected to have property pilot but does not";
    return 1;
  }

  if (subset.string_property("pilot") != trajectory.string_property("pilot"))
  {
    std::cout << "ERROR: test_property_pilot: Subset expected to have pilot Melissa but got " << subset.string_property("pilot") << " instead";
    return 1;
  }

  return 0;
}

// -------------------------------------------------------------------------------

int run_test()
{
  int total_error_count = 0;

  tracktable::imbue_stream_with_timestamp_output_format(std::cout, "%Y-%m-%d %H:%M:%S");

  std::cout << "TEST: Testing trajectory creation\n";
  total_error_count += test_create_trajectory();
  std::cout << "TEST: Testing trajectory slicing\n";
  total_error_count += test_slicing();
  std::cout << "TEST: Testing slicing maintains original trajectory properties\n";
  total_error_count += test_property_number();
  total_error_count += test_property_pilot();

  return total_error_count;
}

// -----------------------------------------------------------------------------

int main(int, char **)
{
  return run_test();
}
