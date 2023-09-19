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

// This tells Windows that we want all the #defines from cmath
#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>

#include <iostream>
#include <sstream>

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/Geometry.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> TrajectoryPointLonLat;
typedef tracktable::Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

typedef tracktable::TrajectoryPoint< tracktable::PointCartesian<2> > TrajectoryPoint2dCartesian;
typedef tracktable::Trajectory<TrajectoryPoint2dCartesian> Trajectory2dCartesian;

template<typename point_type>
point_type create_point(double coord0, double coord1, std::string const& id)
{
  point_type my_point;

  my_point[0] = coord0;
  my_point[1] = coord1;
  my_point.set_object_id(id);
  return my_point;
}

TrajectoryPoint2dCartesian create_cart2_point(double x, double y, std::string const& id)
{
    TrajectoryPoint2dCartesian point;
    point.set_object_id(id);
    point[0] = x;
    point[1] = y;

    return point;
}

TrajectoryPointLonLat create_lonlat_point(double lon, double lat, std::string const& id)
{
  return create_point<TrajectoryPointLonLat>(lon, lat, id);
}

int verify_result(double expected, double actual, std::string const& test)
{
  if (!tracktable::almost_equal(actual, expected))
    {
    std::cout << "ERROR: " << test << " failed. "
              << "Expected radius of gyration of about " << expected
              << " but actual value was " << actual
              << "(difference " << (actual - expected) << ")"
              << std::endl;
    return 1;
    }
  return 0;
}

int run_test()
{
  int error_count = 0;
  double short_flight_radius, long_flight_radius, combined_radius,
    no_point_radius, one_point_radius, cart2d_radius;

  TrajectoryPointLonLat albuquerque = create_lonlat_point(-106.6504, 35.0844, "short flight");
  TrajectoryPointLonLat denver = create_lonlat_point(-104.9903, 39.7392, "short flight");
  TrajectoryPointLonLat el_paso = create_lonlat_point(-106.4850, 31.7619, "short flight");
  TrajectoryPointLonLat san_francisco = create_lonlat_point(-122.4194, 37.7749, "long_flight");
  TrajectoryPointLonLat new_york = create_lonlat_point(-74.0060, 40.7128, "long_flight");
  TrajectoryPointLonLat london = create_lonlat_point(-0.1278, 51.5074, "long_flight");

  TrajectoryPoint2dCartesian point1 = create_cart2_point(0,0, std::string("2d cartesian trajectory"));
  TrajectoryPoint2dCartesian point2 = create_cart2_point(0,1, std::string("2d cartesian trajectory"));
  TrajectoryPoint2dCartesian point3 = create_cart2_point(1,0, std::string("2d cartesian trajectory"));
  TrajectoryPoint2dCartesian point4 = create_cart2_point(1,1, std::string("2d cartesian trajectory"));

  TrajectoryLonLat short_trajectory;
  short_trajectory.push_back(el_paso);
  short_trajectory.push_back(albuquerque);
  short_trajectory.push_back(denver);

  //Short trajectorty should have small radius
  double expected_short_radius = 0.05805;

  short_flight_radius = tracktable::radius_of_gyration(short_trajectory);
  error_count += verify_result(expected_short_radius, short_flight_radius, std::string("Short flight"));

  TrajectoryLonLat long_trajectory;
  long_trajectory.push_back(san_francisco);
  long_trajectory.push_back(new_york);
  long_trajectory.push_back(london);

  //Longer flight should have larger radius
  double expected_long_radius = 0.581498;

  long_flight_radius = tracktable::radius_of_gyration(long_trajectory);
  error_count += verify_result(expected_long_radius, long_flight_radius, std::string("Long flight"));

  TrajectoryLonLat combined_trajectory;
  combined_trajectory.push_back(el_paso);
  combined_trajectory.push_back(albuquerque);
  combined_trajectory.push_back(denver);
  combined_trajectory.push_back(san_francisco);
  combined_trajectory.push_back(new_york);
  combined_trajectory.push_back(london);

  //Combined flight should have smaller radius since there are more points relatively clustered together
  double expected_combined_radius = 0.523586;

  combined_radius = tracktable::radius_of_gyration(combined_trajectory);
  error_count += verify_result(expected_combined_radius, combined_radius, std::string("Combined flight"));

  //No points in a trajectory should return 0
  double expected_no_point_radius = 0.0;

  TrajectoryLonLat no_points;
  no_point_radius = tracktable::radius_of_gyration(no_points);
  error_count += verify_result(
    expected_no_point_radius,
    no_point_radius,
    std::string("Empty flight")
  );

  //One point in a trajectory should return 0
  double expected_one_point_radius = 0.0;

  TrajectoryLonLat one_point;
  one_point.push_back(el_paso);

  one_point_radius = tracktable::radius_of_gyration(one_point);
  error_count += verify_result(
    expected_one_point_radius,
    one_point_radius,
    std::string("One point flight")
  );


  //Test Cartesian for good measure
  double expected_cartesian2d_radius = 0.707107;

  Trajectory2dCartesian cart_trajectory;
  cart_trajectory.push_back(point1);
  cart_trajectory.push_back(point2);
  cart_trajectory.push_back(point3);
  cart_trajectory.push_back(point4);

  cart2d_radius = tracktable::radius_of_gyration(cart_trajectory);
  error_count += verify_result(
    expected_cartesian2d_radius,
    cart2d_radius,
    std::string("Four points cartesian")
  );

  return error_count;
}

int main(int, char **)
{
    return run_test();
}
