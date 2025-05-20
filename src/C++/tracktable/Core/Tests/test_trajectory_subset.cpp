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
 * Time window entirely before trajectory +
 *
 * End of time window is start of trajectory +
 *
 * Time window entirely after trajectory +
 *
 * Start of time window is end of trajectory +
 *
 * Start of time window is before trajectory, end of time window is within trajectory +
 *
 * Start of time window is within trajectory, end of time window is after trajectory +
 *
 * Start of time window is exactly on some point
 *
 * Start of time window is between points
 *
 * End of time window is exactly on some point
 *
 * End of time window is between points
 *
 * Start and end of time window are the same
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
  time_duration time_step(hours(1));
  std::string object_id("FOO");

  for (int i = 0; i < 11; ++i)
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

//  result.recompute_speed();
//  result.recompute_heading();
  return result;
}

// ----------------------------------------------------------------------

int test_create_trajectory()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  std::cout << "Sample trajectory has "
            << trajectory.size() << " points.  Its first point is:\n";
  print_trajectory_point(trajectory.front());
  std::cout << "\nIts last point is:\n";
  print_trajectory_point(trajectory.back());

  return 0;
}

// ----------------------------------------------------------------------

int test_before_trajectory()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  tracktable::Timestamp start = time_from_string("2013-01-01 00:00:00");
  tracktable::Timestamp end = time_from_string("2013-01-01 12:00:00");

  TrajectoryLonLat subset = subset_during_interval(trajectory, start, end);

  if (subset.size() != 0)
    {
    std::cout << "ERROR: test_before_trajectory: Expected empty trajectory but got a subset with "
              << subset.size() << " points.\n";
    return 1;
    }
  return 0;
}

// ----------------------------------------------------------------------

int test_after_trajectory()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  tracktable::Timestamp start = time_from_string("2015-01-01 00:00:00");
  tracktable::Timestamp end = time_from_string("2015-01-01 12:00:00");

  TrajectoryLonLat subset = subset_during_interval(trajectory, start, end);

  if (subset.size() != 0)
    {
    std::cout << "ERROR: test_after_trajectory: Expected empty trajectory but got a subset with "
              << subset.size() << " points.\n";
    return 1;
    }
  return 0;
}

// ----------------------------------------------------------------------

int test_start_single_point()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  tracktable::Timestamp start = time_from_string("2013-01-01 00:00:00");
  tracktable::Timestamp end = time_from_string("2014-01-01 00:00:00");

  TrajectoryLonLat subset = subset_during_interval(trajectory, start, end);

  if (subset.size() != 1)
    {
    std::cout << "ERROR: test_start_single_point: Expected a trajectory with 1 point but got one with "
              << subset.size() << ".\n";
    return 1;
    }
  if (subset[0] != trajectory[0])
    {
    std::cout << "ERROR: test_start_single_point: Subset has 1 point as expected but the point is...\n";
    print_trajectory_point(subset[0]);
    std::cout << "\n...and we expected:\n";
    print_trajectory_point(trajectory[0]);
    return 1;
    }
  return 0;
}

// ----------------------------------------------------------------------

int test_end_single_point()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();

  tracktable::Timestamp start = time_from_string("2014-01-01 10:00:00");
  tracktable::Timestamp end = time_from_string("2015-01-01 00:00:00");

  TrajectoryLonLat subset = subset_during_interval(trajectory, start, end);

  if (subset.size() != 1)
    {
    std::cout << "ERROR: test_start_single_point: Expected a trajectory with 1 point but got one with "
              << subset.size() << ".\n";
    return 1;
    }
  if (subset[0] != trajectory.back())
    {
    std::cout << "ERROR: test_start_single_point: Subset has 1 point as expected but the point is...\n";
    print_trajectory_point(subset[0]);
    std::cout << "\n...and we expected:\n";
    print_trajectory_point(trajectory.back());
    return 1;
    }
  return 0;
}

// ----------------------------------------------------------------------

int test_trajectory_prefix()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();
  tracktable::Timestamp start(time_from_string("2013-12-01 00:00:00"));
  tracktable::Timestamp end(time_from_string("2014-01-01 03:30:00"));

  TrajectoryLonLat subset = subset_during_interval(trajectory, start, end);

  if (subset.size() != 5)
    {
    std::cout << "ERROR: test_trajectory_prefix: Expected a trajectory with 5 points but got one with "
              << subset.size() << "\n";
    print_trajectory_timestamps(subset);
    return 1;
    }

  int error_count = 0;
  for (int i = 0; i < 4; ++i)
    {
    if (subset[i] != trajectory[i])
      {
      std::cout << "ERROR: test_trajectory_prefix: Expected trajectory point "
                << i << " to be equal in subset and original trajectory but they weren't.  Points are:\n";
      std::cout << "(original)\n";
      print_trajectory_point(trajectory[i]);
      std::cout << "(subset)\n";
      print_trajectory_point(subset[i]);
      ++error_count;
      }
    }

  if (subset.back().timestamp() != end)
    {
    std::cout << "ERROR: test_trajectory_prefix: Expected last point in subset to have timestamp "
              << end << " but instead it has "
              << subset.back().timestamp() << "\n";
    ++error_count;
    }

  return error_count;
}

// ----------------------------------------------------------------------

int test_trajectory_suffix()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();
  tracktable::Timestamp start(time_from_string("2014-01-01 06:30:00"));
  tracktable::Timestamp end(time_from_string("2015-01-01 00:00:00"));

  TrajectoryLonLat subset = subset_during_interval(trajectory, start, end);

  if (subset.size() != 5)
    {
    std::cout << "ERROR: test_trajectory_prefix: Expected a trajectory with 5 points but got one with "
              << subset.size() << "\n";
    print_trajectory_timestamps(subset);

    return 1;
    }

  int error_count = 0;
  for (int i = 0; i < 4; ++i)
    {
    if (subset[i+1] != trajectory[i + trajectory.size() - 4])
      {
      std::cout << "ERROR: test_trajectory_suffix: Expected subset point " << i+1
                << " to equal original point " << i + trajectory.size() - 4
                << " but it wasn't.  Points are:\n";
      std::cout << "(original)\n";
      print_trajectory_point(trajectory[i + trajectory.size() - 4]);
      std::cout << "(subset)\n";
      print_trajectory_point(subset[i + 1]);
      ++error_count;
      }
    }

  if (subset.front().timestamp() != start)
    {
    std::cout << "ERROR: test_trajectory_suffix: Expected first point in subset to have timestamp "
              << start << " but instead it has "
              << subset.front().timestamp() << "\n";
    ++error_count;
    }

  return error_count;
}

// ----------------------------------------------------------------------

int test_exact_endpoints()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();
  tracktable::Timestamp start(time_from_string("2014-01-01 02:00:00"));
  tracktable::Timestamp end(time_from_string("2014-01-01 04:00:00"));
  TrajectoryLonLat subset(subset_during_interval(trajectory, start, end));

  int error_count = 0;
  if (subset.size() != 3)
    {
    std::cout << "ERROR: test_exact_endpoints: Expected trajectory subset to have "
              << 3 << " points but it actually has "
              << subset.size() << "\n";
    return 1;
    }

  if (subset[0] != trajectory[2])
    {
    std::cout << "ERROR: test_exact_endpoints: Expected subset first point to be equal to trajectory third point.  It isn't.  Actual points:\n";
    std::cout << "(original)\n";
    print_trajectory_point(trajectory[2]);
    std::cout << "(subset)\n";
    print_trajectory_point(subset[0]);
    ++error_count;
    }

  if (subset[2] != trajectory[4])
    {
    std::cout << "ERROR: test_exact_endpoints: Expected subset last point to be equal to trajectory fifth point.  It isn't.  Actual points:\n";
    std::cout << "(original)\n";
    print_trajectory_point(trajectory[4]);
    std::cout << "(subset)\n";
    print_trajectory_point(subset[2]);
    ++error_count;
    }

  return error_count;
}


// ----------------------------------------------------------------------

int test_interpolated_endpoints()
{
  TrajectoryLonLat trajectory = make_test_surface_trajectory();
  tracktable::Timestamp start(time_from_string("2014-01-01 01:30:00"));
  tracktable::Timestamp end(time_from_string("2014-01-01 04:30:00"));
  TrajectoryLonLat subset(subset_during_interval(trajectory, start, end));

  int error_count = 0;
  if (subset.size() != 5)
    {
    std::cout << "ERROR: test_interpolated_endpoints: Expected trajectory subset to have "
              << 5 << " points but it actually has "
              << subset.size() << "\n";
    return 1;
    }

  if (subset.front().timestamp() != start)
    {
    std::cout << "ERROR: test_interpolated_endpoints: Expected subset start time to equal "
              << start << ".  Instead it is "
              << subset.front().timestamp() << ".\n";
    ++error_count;
    }

  if (subset.back().timestamp() != end)
    {
    std::cout << "ERROR: test_interpolated_endpoints: Expected subset end time to equal "
              << end << ".  Instead it is "
              << subset.back().timestamp() << ".\n";
    ++error_count;
    }

  if (subset[1] != trajectory[2])
    {
    std::cout << "ERROR: test_interpolated_endpoints: Expected subset second point to be equal to trajectory third point.  It isn't.  Actual points:\n";
    std::cout << "(original)\n";
    print_trajectory_point(trajectory[2]);
    std::cout << "(subset)\n";
    print_trajectory_point(subset[1]);
    ++error_count;
    }

  if (subset[3] != trajectory[4])
    {
    std::cout << "ERROR: test_interpolated_endpoints: Expected subset fourth point to be equal to trajectory fifth point.  It isn't.  Actual points:\n";
    std::cout << "(original)\n";
    print_trajectory_point(trajectory[2]);
    std::cout << "(subset)\n";
    print_trajectory_point(subset[3]);
    ++error_count;
    }

  return error_count;
}

// ----------------------------------------------------------------------

int run_test()
{
  int total_error_count = 0;

  tracktable::imbue_stream_with_timestamp_output_format(std::cout, "%Y-%m-%d %H:%M:%S");

  std::cout << "TEST: Testing trajectory creation\n";
  total_error_count += test_create_trajectory();
  std::cout << "TEST: Testing window before trajectory\n";
  total_error_count += test_before_trajectory();
  std::cout << "TEST: Testing window after trajectory\n";
  total_error_count += test_after_trajectory();
  std::cout << "TEST: Testing window that ends at trajectory start\n";
  total_error_count += test_start_single_point();
  std::cout << "TEST: Testing window that starts at trajectory end\n";
  total_error_count += test_end_single_point();
  std::cout << "TEST: Testing trajectory prefix\n";
  total_error_count += test_trajectory_prefix();
  std::cout << "TEST: Testing trajectory suffix\n";
  total_error_count += test_trajectory_suffix();
  std::cout << "TEST: Testing endpoints that fall exactly on trajectory points\n";
  total_error_count += test_exact_endpoints();
  std::cout << "TEST: Testing interpolated endpoints\n";
  total_error_count += test_interpolated_endpoints();

  return total_error_count;
}

// ----------------------------------------------------------------------

int main(int, char **)
{
  return run_test();
}
