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

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

typedef tracktable::PointCartesian<2> PointCartesian2D;
typedef tracktable::PointLonLat PointLonLat;
typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> TrajectoryPointLonLat;
typedef tracktable::Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

void print_test_point(TrajectoryPointLonLat const& point, std::ostream& out = std::cout)
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

template<typename point_type>
int verify_result_redux(point_type const& actual, point_type const& expected, const char* description)
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

    if ((actual.timestamp() - expected.timestamp()) > boost::posix_time::time_duration(0, 0, 0, 100000))
    {
        errbuf << "ERROR: Timestamps do not match.\n";
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
    longitude_middle = 14.6929;
    longitude_after = 20;

    latitude_before = 30;
    latitude_middle = 35.1023;
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

    int error_count = 0;

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

    std::cout << "\nTesting duration\n";
    tracktable::Duration duration = surface_trajectory.duration();
    if (duration != after - before)
    {
        error_count++;
        std::cout << "ERROR: Duration did not match. Expected duration is " <<
            to_simple_string(after - before) << ", Returned duration is " << to_simple_string(duration) << std::endl;
    }

    std::cout << "\nTesting duration, no points\n";
    TrajectoryLonLat noPoints;
    tracktable::Duration duration_no = noPoints.duration();
    if (duration_no != tracktable::Duration(0, 0, 0, 0))
    {
        error_count++;
        std::cout << "ERROR: Duration did not match. Expected duration is " <<
            to_simple_string(tracktable::Duration(0, 0, 0, 0)) << ", Returned duration is " <<
            to_simple_string(duration_no) << std::endl;
    }

    std::cout << "\nTesting duration, one point\n";
    TrajectoryLonLat onePoint;
    onePoint.push_back(st_point_middle);
    tracktable::Duration zero_duration = onePoint.duration();
    if (zero_duration != tracktable::Duration(0, 0, 0, 0))
    {
        error_count++;
        std::cout << "ERROR: Duration did not match. Expected duration is " <<
            to_simple_string(tracktable::Duration(0, 0, 0, 0)) << ", Returned duration is " <<
            to_simple_string(zero_duration) << std::endl;
    }

    std::cout << "\nTesting time at fraction 0.5\n";
    tracktable::Timestamp test_middle = time_at_fraction(surface_trajectory, 0.5);
    if (test_middle != middle)
    {
        error_count++;
        std::cout << "Error: Time at fraction, 0.5, did not match. Expected time is " <<
            middle << ", Returned time is " << test_middle << std::endl;
    }

    std::cout << "\nTesting time at fraction 0.25\n";
    tracktable::Timestamp test_first_quarter = time_at_fraction(surface_trajectory, 0.25);
    if (test_first_quarter != first_quarter)
    {
        error_count++;
        std::cout << "Error: Time at fraction, 0.25, did not match. Expected time is " <<
            first_quarter << ", Returned time is " << test_first_quarter << std::endl;
    }

    std::cout << "\nTesting time at fraction 0.75\n";
    tracktable::Timestamp test_last_quarter = time_at_fraction(surface_trajectory, 0.75);
    if (test_last_quarter != last_quarter)
    {
        error_count++;
        std::cout << "Error: Time at fraction, 0.75, did not match. Expected time is " <<
            last_quarter << ", Returned time is " << test_last_quarter << std::endl;
    }

    std::cout << "\nTesting time at fraction 0\n";
    tracktable::Timestamp test_before = time_at_fraction(surface_trajectory, 0);
    if (test_before != before)
    {
        error_count++;
        std::cout << "Error: Time at fraction, 0, did not match. Expected time is " <<
            before << ", Returned time is " << test_before << std::endl;
    }

    std::cout << "\nTesting time at fraction 1.0\n";
    tracktable::Timestamp test_after = time_at_fraction(surface_trajectory, 1.0);
    if (test_after != after)
    {
        error_count++;
        std::cout << "Error: Time at fraction, 1.0, did not match. Expected time is " <<
            after << ", Returned time is " << test_after << std::endl;
    }

    std::cout << "\nTesting time at fraction -0.5\n";
    tracktable::Timestamp test_way_before = time_at_fraction(surface_trajectory, -0.5);
    if (test_way_before != before)
    {
        error_count++;
        std::cout << "Error: Time at fraction, -0.5, did not match. Expected time is " <<
            before << ", Returned time is " << test_way_before << std::endl;
    }

    std::cout << "\nTesting time at fraction 1.5\n";
    tracktable::Timestamp time_way_after = time_at_fraction(surface_trajectory, 1.5);
    if (time_way_after != after)
    {
        error_count++;
        std::cout << "Error: Time at fraction, 1.5, did not match. Expected time is " <<
            after << ", Returned time is " << time_way_after << std::endl;
    }

    std::cout << "\nTesting time at fraction no points\n";
    tracktable::Timestamp time_no = time_at_fraction(noPoints, 0.5);
    if (time_no != tracktable::BeginningOfTime)
    {
        error_count++;
        std::cout << "Error: Time at fraction, no points, did not match. Expected time is " <<
            tracktable::Timestamp() << ", Returned time is " << time_no << std::endl;
    }

    std::cout << "\nTesting point at fraction 0.5\n";
    TrajectoryPointLonLat point_mid = point_at_time_fraction(surface_trajectory, 0.5);
    error_count += verify_result(point_mid, expected_result_middle, "midpoint of trajectory");

    std::cout << "\nTesting point at fraction 0.25\n";
    TrajectoryPointLonLat point_first_quarter = point_at_time_fraction(surface_trajectory, 0.25);
    error_count += verify_result(point_first_quarter, expected_result_first_quarter, "halfway between beginning and midpoint");

    std::cout << "\nTesting point at fraction 0.75\n";
    TrajectoryPointLonLat point_last_quarter = point_at_time_fraction(surface_trajectory, 0.75);
    error_count += verify_result(point_last_quarter, expected_result_last_quarter, "halfway between midpoint and end");

    std::cout << "\nTesting point at fraction 0.0\n";
    TrajectoryPointLonLat point_start = point_at_time_fraction(surface_trajectory, 0.0);
    error_count += verify_result(point_start, expected_result_before, "beginning of trajectory");

    std::cout << "\nTesting point at fraction 1.0\n";
    TrajectoryPointLonLat point_end = point_at_time_fraction(surface_trajectory, 1.0);
    error_count += verify_result(point_end, expected_result_after, "end of trajectory");

    std::cout << "\nTesting point at fraction -0.5\n";
    TrajectoryPointLonLat point_before = point_at_time_fraction(surface_trajectory, -0.5);
    error_count += verify_result(point_before, expected_result_before, "before beginning of trajectory");

    std::cout << "\nTesting point at fraction 1.5\n";
    TrajectoryPointLonLat point_after = point_at_time_fraction(surface_trajectory, 1.5);
    error_count += verify_result(point_after, expected_result_after, "after end of trajectory");

    std::cout << "\nTesting point at fraction, no points\n";
    TrajectoryPointLonLat point_no = point_at_time_fraction(noPoints, 0.75);
    if (point_no.timestamp() != tracktable::BeginningOfTime) //Coordinates are trash. Use timestamp instead.
    {
        error_count++;
        std::cout << "Error: Point at fraction, no points, did not match. Expected point timestamp is " <<
            tracktable::BeginningOfTime << ", Returned point timestamp is " << point_no.timestamp() << std::endl;
    }
    std::cout << "\nTesting point at length fraction 0.5\n";
    point_mid = point_at_length_fraction(surface_trajectory, 0.5);
    error_count += verify_result_redux(point_mid, expected_result_middle, "midpoint of trajectory");

    std::cout << "\nTesting point at length fraction 0.25\n";
    point_first_quarter = point_at_length_fraction(surface_trajectory, 0.25);
    error_count += verify_result_redux(point_first_quarter, expected_result_first_quarter, "halfway between beginning and midpoint");

    std::cout << "\nTesting point at length fraction 0.75\n";
    point_last_quarter = point_at_length_fraction(surface_trajectory, 0.75);
    error_count += verify_result_redux(point_last_quarter, expected_result_last_quarter, "halfway between midpoint and end");

    std::cout << "\nTesting point at length fraction 0.0\n";
    point_start = point_at_length_fraction(surface_trajectory, 0.0);
    error_count += verify_result_redux(point_start, expected_result_before, "beginning of trajectory");

    std::cout << "\nTesting point at length fraction 1.0\n";
    point_end = point_at_length_fraction(surface_trajectory, 1.0);
    error_count += verify_result_redux(point_end, expected_result_after, "end of trajectory");

    std::cout << "\nTesting point at length fraction -0.5\n";
    point_before = point_at_length_fraction(surface_trajectory, -0.5);
    error_count += verify_result_redux(point_before, expected_result_before, "before beginning of trajectory");

    std::cout << "\nTesting point at length fraction 1.5\n";
    point_after = point_at_length_fraction(surface_trajectory, 1.5);
    error_count += verify_result_redux(point_after, expected_result_after, "after end of trajectory");

    std::cout << "\nTesting point at length fraction, no points\n";
    point_no = point_at_length_fraction(noPoints, 0.75);
    if (point_no.timestamp() != tracktable::BeginningOfTime) //Coordinates are trash. Use timestamp instead.
    {
        error_count++;
        std::cout << "Error: Point at length fraction, no points, did not match. Expected point timestamp is " <<
            tracktable::BeginningOfTime << ", Returned point timestamp is " << point_no.timestamp() << std::endl;
    }

    PointCartesian2D point1;
    PointCartesian2D point2;
    PointCartesian2D expected;
    point1[0] = 0;
    point1[1] = 0;

    point2[0] = 10;
    point2[1] = 10;

    std::cout << "\nTesting point interpolation, Cartesian2D halfway\n";
    expected[0] = 5;
    expected[1] = 5;
    PointCartesian2D interp_point = tracktable::interpolate(point1, point2, .5);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Interpolate, Cartesian2D halfway. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point interpolation, Cartesian2D first third\n";
    expected[0] = 3;
    expected[1] = 3;
    interp_point = tracktable::interpolate(point1, point2, .3);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Interpolate, Cartesian2D first third. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point interpolation, Cartesian2D start\n";
    expected[0] = 0;
    expected[1] = 0;
    interp_point = tracktable::interpolate(point1, point2, 0);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Interpolate, Cartesian2D start. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point interpolation, Cartesian2D end\n";
    expected[0] = 10;
    expected[1] = 10;
    interp_point = tracktable::interpolate(point1, point2, 1);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Interpolate, Cartesian2D end. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point extrapolation, Cartesian2D 1.5x\n";
    expected[0] = 15;
    expected[1] = 15;
    interp_point = tracktable::extrapolate(point1, point2, 1.5);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Extrapolate, Cartesian2D 1.5x. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point extrapolation, Cartesian2D -1.5x\n";
    expected[0] = -15;
    expected[1] = -15;
    interp_point = tracktable::extrapolate(point1, point2, -1.5);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Extrapolate, Cartesian2D -1.5x. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point extrapolation, Cartesian2D start\n";
    expected[0] = 0;
    expected[1] = 0;
    interp_point = tracktable::extrapolate(point1, point2, 0);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Extrapolate, Cartesian2D start. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    std::cout << "\nTesting point extrapolation, Cartesian2D end\n";
    expected[0] = 10;
    expected[1] = 10;
    interp_point = tracktable::extrapolate(point1, point2, 1);
    if (interp_point != expected) {
        error_count++;
        std::cout << "\nError: Extrapolate, Cartesian2D end. Expected point is " << expected.to_string() <<
            ", returned point is " << interp_point.to_string() << std::endl;
    }

    PointLonLat point3;
    PointLonLat point4;
    PointLonLat expected2;
    point3[0] = 45.0;
    point3[1] = 45.0;

    point4[0] = 135.0;
    point4[1] = 45.0;

    std::cout << "\nTesting point interpolation, LonLat halfway\n";
    expected2[0] = 90.0;
    expected2[1] = 54.7356;
    PointLonLat interp_point2 = tracktable::interpolate(point3, point4, .5);
    if (interp_point2 != expected2) {
        error_count++;
        std::cout << "\nError: Interpolate, LonLat halfway. Expected point is " << expected2.to_string() <<
            ", returned point is " << interp_point2.to_string() << std::endl;
    }

    std::cout << "\nTesting point interpolation, LonLat first third\n";
    expected2[0] = 69.7884;
    expected2[1] = 53.0018;
    interp_point2 = tracktable::interpolate(point3, point4, .3);
    if (interp_point2 != expected2) {
        error_count++;
        std::cout << "\nError: Interpolate, LonLat first third. Expected point is " << expected2.to_string() <<
            ", returned point is " << interp_point2.to_string() << std::endl;
    }

    std::cout << "\nTesting point extrapolation, LonLat 2x\n";
    expected2[0] = 180;
    expected2[1] = 0;
    interp_point2 = tracktable::extrapolate(point3, point4, 2);
    if (interp_point2[0] != expected2[0]) { // Bug: Done because result longitude is close but not exactly zero.
        error_count++;
        std::cout << "\nError: Extrapolate, LonLat 2x. Expected point is " << expected2.to_string() <<
            ", returned point is " << interp_point2.to_string() << std::endl;
    }

    std::cout << "\nTesting point interpolation, double halfway\n";
    double a = 10;
    double b = 20;
    double expected3 = 15;
    double interp_point3 = tracktable::interpolate(a, b, .5);
    if (interp_point3 != expected3) {
        error_count++;
        std::cout << "\nError: Interpolate, double halfway. Expected point is " << expected3 <<
            ", returned point is " << interp_point3 << std::endl;
    }

    std::cout << "\nTesting point extrapolation, double 1.5x\n";
    expected3 = 25;
    interp_point3 = tracktable::extrapolate(a, b, 1.5);
    if (interp_point3 != expected3) {
        error_count++;
        std::cout << "\nError: Extrapolate, double 1.5x. Expected point is " << expected3 <<
            ", returned point is " << interp_point3 << std::endl;
    }

    std::cout << "\nTesting point interpolation, TrajectoryPointLonLat halfway\n";
    TrajectoryPointLonLat interp_point4 = tracktable::interpolate(st_point_before, st_point_after, .5);
    interp_point4.set_property("string_property", s_property_middle);
    error_count += verify_result(interp_point4, st_point_middle, "interpolate TrajectoryPointLonLat halfway ");

    std::cout << "\nTesting point extrapolation, TrajectoryPointLonLat 2x\n";
    interp_point4 = tracktable::extrapolate(st_point_before, st_point_middle, 2);
    interp_point4.set_property("string_property", s_property_after);
    error_count += verify_result(interp_point4, st_point_after, "interpolate TrajectoryPointLonLat 2x ");

    return error_count;
}

int main(int, char **)
{
    return run_test();
}
