/*
 * Copyright (c) 2014, Sandia Corporation.  All rights
 * reserved.
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

// This tells Windows that we want all the #defines from cmath
#define _USE_MATH_DEFINES
#include <cmath>

#include <iostream>
#include <sstream>

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> TrajectoryPointLonLat;
typedef tracktable::Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

void print_test_point(TrajectoryPointLonLat const& point, std::ostream& out=std::cout)
{
  out << "Object ID:       " << point.object_id() << "\n";
  out << "Timestamp:       " << point.timestamp() << "\n";
  out << "Longitude:       " << point.longitude() << "\n";
  out << "Latitude:        " << point.latitude() << "\n";
  out << "double_property: " << point.property("double_property") << "\n";
  out << "time_property:   " << point.property("time_property") << "\n";
  out << "string_property: " << point.property("string_property") << "\n";
}

// ----------------------------------------------------------------------

template<typename point_type>
int verify_result(point_type const& actual, point_type const& expected, const char* description)
{
  int error_count = 0;
  std::ostringstream errbuf;

  if (tracktable::distance(actual, expected) > 0.1)
    {
    errbuf << "ERROR: Distance between actual and expected points is "
           << tracktable::distance(actual, expected) << " units.\n";
    ++error_count;
    }

  if (actual.object_id() != expected.object_id())
    {
    errbuf << "ERROR: Object IDs do not match.\n";
    ++error_count;
    }

  if (actual.timestamp() != expected.timestamp())
    {
    errbuf << "ERROR: Timestamps do not match.\n";
    ++error_count;
    }

  if (!(actual.property("double_property") == expected.property("double_property")))
    {
    errbuf << "ERROR: Numeric properties do not match.\n";
    ++error_count;
    }

  if (!(actual.property("string_property") == expected.property("string_property")))
    {
    errbuf << "ERROR: String properties do not match.\n";
    ++error_count;
    }

  if (!(actual.property("time_property") == expected.property("time_property")))
    {
    errbuf << "ERROR: Timestamp properties do not match.\n";
    ++error_count;
    }

  if (error_count)
    {
    std::ostringstream finalbuf;
    finalbuf << "ERROR testing " << description << ": ";
    errbuf << "\nExpected result:\n";
    print_test_point(expected, errbuf);
    errbuf << "\nActual result:\n";
    print_test_point(actual, errbuf);
    finalbuf << errbuf.str();
    std::cout << finalbuf.str();
    }
  return error_count;
}

// ----------------------------------------------------------------------

int run_test()
{
  TrajectoryPointLonLat st_point_before, st_point_middle, st_point_after;
  tracktable::Timestamp before, middle, after;
  double heading_before, heading_middle, heading_after;
  double speed_before, speed_middle, speed_after;
  double longitude_before, longitude_middle, longitude_after;
  double latitude_before, latitude_middle, latitude_after;
  double d_property_before, d_property_middle, d_property_after;
  std::string s_property_before, s_property_middle, s_property_after;
  tracktable::Timestamp t_property_before, t_property_middle, t_property_after;

  using tracktable::point_at_time;

  using boost::posix_time::time_from_string;
  before = time_from_string("2014-01-01 00:00:00");
  middle = time_from_string("2014-01-01 06:00:00");
  after = time_from_string("2014-01-01 12:00:00");

  heading_before = 0;
  heading_middle = 90;
  heading_after = 180;

  speed_before = 100;
  speed_middle = 150;
  speed_after = 200;

  longitude_before = 10;
  longitude_middle = 15;
  longitude_after = 20;

  latitude_before = 30;
  latitude_middle = 35;
  latitude_after = 40;

  t_property_before = time_from_string("2020-12-01 00:00:00");
  t_property_middle = time_from_string("2020-12-01 00:30:00");
  t_property_after = time_from_string("2020-12-01 01:00:00");

  d_property_before = 100;
  d_property_middle = 150;
  d_property_after = 200;

  s_property_before = "string before";
  s_property_middle = "string middle";
  s_property_after = "string after";

  st_point_before.set_object_id("FOO");
  st_point_before.set_timestamp(before);
  st_point_before.set_property("speed", speed_before);
  st_point_before.set_property("heading", heading_before);
  st_point_before.set_longitude(longitude_before);
  st_point_before.set_latitude(latitude_before);
  st_point_before.set_property("double_property", d_property_before);
  st_point_before.set_property("time_property", t_property_before);
  st_point_before.set_property("string_property", s_property_before);

  std::cout << "st_point_before: " << st_point_before << "\n";

  st_point_middle.set_object_id("FOO");
  st_point_middle.set_timestamp(middle);
  st_point_middle.set_property("speed", speed_middle);
  st_point_middle.set_property("heading", heading_middle);
  st_point_middle.set_longitude(longitude_middle);
  st_point_middle.set_latitude(latitude_middle);
  st_point_middle.set_property("double_property", d_property_middle);
  st_point_middle.set_property("time_property", t_property_middle);
  st_point_middle.set_property("string_property", s_property_middle);

  std::cout << "st_point_middle: " << st_point_middle << "\n";

  st_point_after.set_object_id("FOO");
  st_point_after.set_timestamp(after);
  st_point_after.set_property("speed", speed_after);
  st_point_after.set_property("heading", heading_after);
  st_point_after.set_longitude(longitude_after);
  st_point_after.set_latitude(latitude_after);
  st_point_after.set_property("double_property", d_property_after);
  st_point_after.set_property("time_property", t_property_after);
  st_point_after.set_property("string_property", s_property_after);

  std::cout << "st_point_after: " << st_point_after << "\n";

  TrajectoryLonLat surface_trajectory;
  surface_trajectory.push_back(st_point_before);
  surface_trajectory.push_back(st_point_middle);
  surface_trajectory.push_back(st_point_after);

  tracktable::Timestamp way_before, first_quarter, last_quarter, way_after;

  way_before = time_from_string("2013-01-01 00:00:00");
  way_after = time_from_string("2015-01-01 00:00:00");
  first_quarter = time_from_string("2014-01-01 03:00:00");
  last_quarter = time_from_string("2014-01-01 09:00:00");

  TrajectoryPointLonLat result_before, result_first_quarter, result_middle, result_last_quarter, result_after;

  TrajectoryPointLonLat expected_result_before(st_point_before);
  TrajectoryPointLonLat expected_result_first_quarter;
  TrajectoryPointLonLat expected_result_middle(st_point_middle);
  TrajectoryPointLonLat expected_result_last_quarter;
  TrajectoryPointLonLat expected_result_after(st_point_after);

  std::cout << "expected_result_before: " << expected_result_before << "\n";
  std::cout << "expected_result_middle: " << expected_result_middle << "\n";
  std::cout << "expected_result_after: " << expected_result_after << "\n";

  expected_result_first_quarter.set_object_id("FOO");
  expected_result_first_quarter.set_timestamp(first_quarter);
  expected_result_first_quarter.set_property("speed", static_cast<double>(125));
  expected_result_first_quarter.set_property("heading", static_cast<double>(45));
  expected_result_first_quarter.set_longitude(12.4304);
  expected_result_first_quarter.set_latitude(32.5247);
  expected_result_first_quarter.set_property("double_property", static_cast<double>(125));
  expected_result_first_quarter.set_property("time_property", time_from_string("2020-12-01 00:15:00"));
  expected_result_first_quarter.set_property("string_property", s_property_middle);

  expected_result_last_quarter.set_object_id("FOO");
  expected_result_last_quarter.set_timestamp(last_quarter);
  expected_result_last_quarter.set_property("speed", static_cast<double>(175));
  expected_result_last_quarter.set_property("heading", static_cast<double>(135));
  expected_result_last_quarter.set_longitude(17.4162);
  expected_result_last_quarter.set_latitude(37.5263);
  expected_result_last_quarter.set_property("double_property", static_cast<double>(175));
  expected_result_last_quarter.set_property("time_property", time_from_string("2020-12-01 00:45:00"));
  expected_result_last_quarter.set_property("string_property", s_property_after);

  std::cout << "expected_result_first_quarter: " << expected_result_first_quarter << "\n";
  std::cout << "expected_result_last_quarter: " << expected_result_last_quarter << "\n";

  int error_count=0;

  std::cout << "\nTesting interpolation at timestamp way before trajectory\n";
  result_before = point_at_time(surface_trajectory, way_before);
  error_count += verify_result(result_before, expected_result_before, "point before trajectory starts");

  std::cout << "\nTesting interpolation at first quarter\n";
  result_first_quarter = point_at_time(surface_trajectory, first_quarter);
  error_count += verify_result(result_first_quarter, expected_result_first_quarter, "halfway between beginning and midpoint");

  std::cout << "\nTesting interpolation at midpoint\n";
  result_middle = point_at_time(surface_trajectory, middle);
  error_count += verify_result(result_middle, expected_result_middle, "midpoint of trajectory");

  std::cout << "\nTesting interpolation at last quarter\n";
  result_last_quarter = point_at_time(surface_trajectory, last_quarter);
  error_count += verify_result(result_last_quarter, expected_result_last_quarter, "halfway between midpoint and end");

  std::cout << "\nTesting interpolation beyond trajectory\n";
  result_after = point_at_time(surface_trajectory, way_after);
  error_count += verify_result(result_after, expected_result_after, "point after trajectory ends");

  return error_count;
}

int main(int /*argc*/, char */*argv*/[])
{
  return run_test();
}
