/*
* Copyright (c) 2014-2018 National Technology and Engineering
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
#define _USE_MATH_DEFINES
#include <cmath>

#include <iostream>
#include <sstream>

#include <tracktable/Core/Geometry.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> TrajectoryPointLonLat;
typedef tracktable::Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;


TrajectoryPointLonLat create_point(double lat, double lon, std::string& id)
{
    TrajectoryPointLonLat point;
    point.set_object_id(id);
    point.set_longitude(lon);
    point.set_latitude(lat);

    return point;
}

int verify_result(double expected, double actual, std::string& test)
{
    if (abs(actual - expected) > .1)
    {
        std::cout << "ERROR: " << test << " failed. Expected radius of gyration of about " << expected <<
            " but actual value was " << actual << std::endl;
        return 1;
    }
    return 0;
}

int run_test()
{
    int error_count = 0;
    double short_flight_radius, long_flight_radius, combined_radius;


    TrajectoryPointLonLat albuquerque = create_point(35.0844, 106.6504, std::string("short_flight"));
    TrajectoryPointLonLat denver = create_point(39.7392, 104.9903, std::string("short_flight"));
    TrajectoryPointLonLat el_paso = create_point(31.7619, 106.4850, std::string("short_flight"));
    TrajectoryPointLonLat san_francisco = create_point(37.7749, 122.4194, std::string("long_flight"));
    TrajectoryPointLonLat new_york = create_point(40.7128, 74.0060, std::string("long_flight"));
    TrajectoryPointLonLat london = create_point(51.5074, 0.1278, std::string("long_flight"));

    TrajectoryLonLat short_trajectory;
    short_trajectory.push_back(el_paso);
    short_trajectory.push_back(albuquerque);
    short_trajectory.push_back(denver);

    //Short trajectorty should have small radius
    double expected_short_radius = 0.071;

    short_flight_radius = tracktable::radius_of_gyration(short_trajectory);
    error_count += verify_result(expected_short_radius, short_flight_radius, std::string("Short flight"));

    TrajectoryLonLat long_trajectory;
    long_trajectory.push_back(san_francisco);
    long_trajectory.push_back(new_york);
    long_trajectory.push_back(london);

    //Longer flight should have larger radius
    double expected_long_radius = 0.712;

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
    double expected_combined_radius = 0.573;

    combined_radius = tracktable::radius_of_gyration(combined_trajectory);
    error_count += verify_result(expected_combined_radius, combined_radius, std::string("Combined flight"));

    return error_count;
}

int main(int /*argc*/, char */*argv*/[])
{
    return run_test();
}
