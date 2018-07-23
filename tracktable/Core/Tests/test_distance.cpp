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

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/PointCartesian.h>

#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Cartesian3D.h>
#include <tracktable/Domain/Terrestrial.h>

typedef tracktable::PointLonLat LonLatPoint;
typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> TrajectoryPointLonLat;
typedef tracktable::Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

typedef tracktable::domain::cartesian2d::CartesianPoint2D Cartesian2dPoint;
typedef tracktable::domain::cartesian2d::CartesianTrajectoryPoint2D TrajectoryCartesian2dPoint;
typedef tracktable::Trajectory<TrajectoryCartesian2dPoint> TrajectoryCartesian2d;

typedef tracktable::domain::cartesian3d::CartesianPoint3D Cartesian3dPoint;
typedef tracktable::domain::cartesian3d::CartesianTrajectoryPoint3D TrajectoryCartesian3dPoint;
typedef tracktable::Trajectory<TrajectoryCartesian3dPoint> TrajectoryCartesian3d;

typedef tracktable::domain::terrestrial::TerrestrialPoint TerrestrialPoint;
typedef tracktable::domain::terrestrial::TerrestrialTrajectoryPoint TerrestrialTrajectoryPoint;
typedef tracktable::Trajectory<TerrestrialTrajectoryPoint> TerrestrialTrajectory;

//----------------------------------------------------

int verify_result(double actual, double expected, const char* description)
{
    std::ostringstream errbuf;

    if (abs(actual - expected) > 0.001)
    {
        std::cout << "ERROR: "<< description <<  " distance expected to be " << expected << " units but actual distance is "
            << actual << " units. The difference is " << abs(actual - expected) << std::endl;
        return 1;
    }

    return 0;
}

TerrestrialPoint create_terrestrial_point(double lat, double lon, std::string& id = std::string(""))
{
    TerrestrialPoint point;
    point.set_longitude(lon);
    point.set_latitude(lat);

    return point;
}

TerrestrialTrajectoryPoint create_terrestrial_trajectory_point(double lat, double lon, std::string& id = std::string(""))
{
    TerrestrialTrajectoryPoint point;
    point.set_object_id(id);
    point.set_longitude(lon);
    point.set_latitude(lat);

    return point;
}

TrajectoryPointLonLat create_trajectory_point(double lat, double lon, std::string& id=std::string(""))
{
    TrajectoryPointLonLat point;
    point.set_object_id(id);
    point.set_longitude(lon);
    point.set_latitude(lat);

    return point;
}

LonLatPoint create_point(double lat, double lon, std::string& id = std::string(""))
{
    LonLatPoint point;
    point.set_longitude(lon);
    point.set_latitude(lat);

    return point;
}

TrajectoryCartesian2dPoint create_cartesian2d_point(double x, double y, std::string& id = std::string(""))
{
    TrajectoryCartesian2dPoint point;
    point[0] = x;
    point[1] = y;

    return point;
}

TrajectoryCartesian3dPoint create_cartesian3d_point(double x, double y, double z, std::string& id = std::string(""))
{
    TrajectoryCartesian3dPoint point;
    point[0] = x;
    point[1] = y;
    point[2] = z;

    return point;
}

// ----------------------------------------------------------------------



int run_test()
{
    using namespace tracktable;

    int error_count = 0;
    double actual, expected;
    
    std::cout << "Testing Terrestrial Distance" << std::endl;

    TrajectoryPointLonLat albuquerque = create_trajectory_point(35.0844, -106.6504);
    TerrestrialTrajectoryPoint albuquerque2 = create_terrestrial_trajectory_point(35.0844, -106.6504);
    LonLatPoint albuquerque3 = create_point(35.0844, -106.6504);
    TerrestrialPoint albuquerque4 = create_terrestrial_point(35.0844, -106.6504);
        
    TrajectoryPointLonLat dallas = create_trajectory_point(32.8205, -96.8716);
    TerrestrialTrajectoryPoint dallas2 = create_terrestrial_trajectory_point(32.8205, -96.8716);
    LonLatPoint dallas3 = create_point(32.8205, -96.8716);
    TerrestrialPoint dallas4 = create_terrestrial_point(32.8205, -96.8716);
    
    TrajectoryPointLonLat el_paso = create_trajectory_point(31.7619, -106.4850);
    TerrestrialTrajectoryPoint el_paso2 = create_terrestrial_trajectory_point(31.7619, -106.4850);
    LonLatPoint el_paso3 = create_point(31.7619, -106.4850);
    TerrestrialPoint el_paso4 = create_terrestrial_point(31.7619, -106.4850);
        
    TrajectoryPointLonLat san_antonio = create_trajectory_point(29.4813, -98.6544);
    TerrestrialTrajectoryPoint san_antonio2 = create_terrestrial_trajectory_point(29.4813, -98.6544);
    LonLatPoint san_antonio3 = create_point(29.4813, -98.6544);
    TerrestrialPoint san_antonio4 = create_terrestrial_point(29.4813, -98.6544);
    
    TrajectoryPointLonLat houston = create_trajectory_point(29.8168, -74.0060);
    TerrestrialTrajectoryPoint houston2 = create_terrestrial_trajectory_point(29.8168, -74.0060);
    LonLatPoint houston3 = create_point(29.8168, -74.0060);
    TerrestrialPoint houston4 = create_terrestrial_point(29.8168, -74.0060);
    
    TrajectoryLonLat ep_to_dal;
    ep_to_dal.push_back(el_paso);
    ep_to_dal.push_back(dallas);

    TerrestrialTrajectory ep_to_dal2;
    ep_to_dal2.push_back(el_paso2);
    ep_to_dal2.push_back(dallas2);

    TrajectoryLonLat sa_to_hou;
    sa_to_hou.push_back(san_antonio);
    sa_to_hou.push_back(houston);

    TerrestrialTrajectory sa_to_hou2;
    sa_to_hou2.push_back(san_antonio2);
    sa_to_hou2.push_back(houston2);

    TrajectoryLonLat sa_to_abq;
    sa_to_abq.push_back(san_antonio);
    sa_to_abq.push_back(albuquerque);

    expected = 369.764;
    actual = conversions::radians_to_km(distance(albuquerque, el_paso));
    error_count += verify_result(actual, expected, "TrajectoryPointLonLat to TrajectoryPointLonLat");

    actual = distance(albuquerque2, el_paso2);
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint to TerrestrialTrajectoryPoint");

    actual = conversions::radians_to_km(distance(albuquerque3, el_paso3));
    error_count += verify_result(actual, expected, "LonLatPoint to LonLatPoint");

    actual = distance(albuquerque4, el_paso4);
    error_count += verify_result(actual, expected, "TerrestrialPoint to TerrestrialPoint");

    expected = 975.674;
    actual = conversions::radians_to_km(distance(albuquerque, sa_to_hou));
    error_count += verify_result(actual, expected, "TrajectoryPointLonLat to TrajectoryLonLat");

    actual = distance(albuquerque2, sa_to_hou2);
    error_count += verify_result(actual, expected, "TerrestrialTrajectoryPoint to TerrestrialTrajectory");

    actual = distance(sa_to_hou2, albuquerque2);
    error_count += verify_result(actual, expected, "TerrestrialTrajectory to TerrestrialTrajectoryPoint");

    actual = conversions::radians_to_km(distance(albuquerque4, sa_to_hou2));
    error_count += verify_result(actual, expected, "TerrestrialPoint to TerrestrialTrajectory");

    expected = 349.276;
    actual = conversions::radians_to_km(distance(ep_to_dal, sa_to_hou));
    error_count += verify_result(actual, expected, "TrajectoryLonLat to TrajectoryLonLat");

    actual = distance(ep_to_dal2, sa_to_hou2);
    error_count += verify_result(actual, expected, "TerrestrialTrajectory to TerrestrialTrajectory");

    expected = 0.0;
    actual = distance(ep_to_dal, sa_to_abq);
    error_count += verify_result(actual, expected, "TerrestrialTrajectory to TerrestrialTrajectory Intersecting");
        
    std::cout << "Testing Cartesian 2D Distance" << std::endl;
    
    TrajectoryCartesian2dPoint point00 = create_cartesian2d_point(0,0);
    TrajectoryCartesian2dPoint point01 = create_cartesian2d_point(0,1);
    TrajectoryCartesian2dPoint point11 = create_cartesian2d_point(1,1);
    TrajectoryCartesian2dPoint point22 = create_cartesian2d_point(2,2);
    
    TrajectoryCartesian2d traj1;
    traj1.push_back(point00);
    traj1.push_back(point01);

    TrajectoryCartesian2d traj2;
    traj2.push_back(point11);
    traj2.push_back(point22);

    expected = 1.0;
    actual = distance(point00, point01);
    error_count += verify_result(actual, expected, "TrajectoryCartesian2dPoint to TrajectoryCartesian2dPoint");

    actual = distance(traj1, traj2);
    error_count += verify_result(actual, expected, "TrajectoryCartesian2d to TrajectoryCartesian2d");

    expected = 1.414;
    actual = distance(point00, traj2);
    error_count += verify_result(actual, expected, "TrajectoryCartesian2dPoint to TrajectoryCartesian2d");

    std::cout << "Testing Cartesian 3D Distance" << std::endl;
    
    TrajectoryCartesian3dPoint point000 = create_cartesian3d_point(0,0,0);
    TrajectoryCartesian3dPoint point001 = create_cartesian3d_point(0,0,1);
    TrajectoryCartesian3dPoint point111 = create_cartesian3d_point(1,1,1);
    TrajectoryCartesian3dPoint point222 = create_cartesian3d_point(2,2,2);

    TrajectoryCartesian3d traj3;
    traj3.push_back(point000);
    traj3.push_back(point001);

    TrajectoryCartesian3d traj4;
    traj4.push_back(point111);
    traj4.push_back(point222);

    expected = 1.0;
    actual = distance(point000, point001);
    error_count += verify_result(actual, expected, "TrajectoryCartesian3dPoint to TrajectoryCartesian3dPoint");

    // This doesnt work because boost::geometry::disjoint is not implemented for dimenstions > 2
    //expected = 1.414;
    //actual = distance(traj3, traj4);
    //actual = boost::geometry::distance(traj3, traj4);
    //error_count += verify_result(actual, expected, "TrajectoryCartesian3d to TrajectoryCartesian3d");

    expected = 1.732;
    actual = distance(point000, traj4);
    error_count += verify_result(actual, expected, "TrajectoryCartesian3dPoint to TrajectoryCartesian3d");
    return error_count;
}

int main(int /*argc*/, char */*argv*/[])
{
    return run_test();
}

