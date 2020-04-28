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

#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Terrestrial.h>

#include <tracktable/Analysis/DistanceGeometry.h>

typedef tracktable::domain::cartesian2d::CartesianPoint2D Cartesian2dPoint;
typedef tracktable::domain::cartesian2d::CartesianTrajectoryPoint2D TrajectoryCartesian2dPoint;
typedef tracktable::Trajectory<TrajectoryCartesian2dPoint> TrajectoryCartesian2d;

typedef tracktable::domain::terrestrial::TerrestrialTrajectoryPoint TerrestrialTrajectoryPoint;
typedef tracktable::Trajectory<TerrestrialTrajectoryPoint> TerrestrialTrajectory;

//----------------------------------------------------

TerrestrialTrajectoryPoint create_terrestrial_trajectory_point(double lat, double lon, std::string const& id=std::string())
{
    TerrestrialTrajectoryPoint point;
    point.set_object_id(id);
    point.set_longitude(lon);
    point.set_latitude(lat);

    return point;
}

TrajectoryCartesian2dPoint create_cartesian2d_point(double x, double y, std::string const& id=std::string())
{
    TrajectoryCartesian2dPoint point;
    point[0] = x;
    point[1] = y;

    return point;
}

// ----------------------------------------------------------------------



int run_test()
{
    using namespace tracktable;

    int error_count = 0;
    
    std::cout << "Testing Terrestrial Distance" << std::endl;

    TerrestrialTrajectoryPoint pt0 = 
     create_terrestrial_trajectory_point(80.0,0.0);
    TerrestrialTrajectoryPoint pt1 = 
     create_terrestrial_trajectory_point(80.0,90.0);
    TerrestrialTrajectoryPoint pt2 = 
     create_terrestrial_trajectory_point(80.0,180.0);
    TerrestrialTrajectoryPoint pt3 = 
     create_terrestrial_trajectory_point(80.0,-90.0);
    TerrestrialTrajectoryPoint pt4 = 
     create_terrestrial_trajectory_point(80.0,0.0);

    std::vector<TerrestrialTrajectory> all_trajs;
    TerrestrialTrajectory sq_traj;
    sq_traj.push_back(pt0);
    sq_traj.push_back(pt1);
    sq_traj.push_back(pt2);
    sq_traj.push_back(pt3);
    sq_traj.push_back(pt4);
    all_trajs.push_back(sq_traj);
    std::vector<std::vector<double> > dgs;
    GetDistanceGeometries(all_trajs,dgs,4);

    double expected0 = 0.0;
    double expected1 = 0.708916;
    double expected3 = 0.793393;
    double expected4 = 0.710916;
    double expected6 = 1.0;
    double tolerance = 1e-4;

    if ((fabs(dgs[0][0] - expected0) > tolerance) ||
     (fabs(dgs[0][1] - expected1) > tolerance) ||
     (fabs(dgs[0][3] - expected3) > tolerance) ||
     (fabs(dgs[0][4] - expected4) > tolerance) ||
     (fabs(dgs[0][6] - expected6) > tolerance)) {
      std::cout << "Error in terrestrial distance geometries" << "\n"
	     << dgs[0][0] << " (Should be " << expected0 << ")" << "\n"
	     << dgs[0][1] << " (Should be " << expected1 << ")" << "\n"
	     << dgs[0][2] << " (Should be " << expected1 << ")" << "\n"
	     << dgs[0][3] << " (Should be " << expected3 << ")" << "\n"
	     << dgs[0][4] << " (Should be " << expected4 << ")" << "\n"
	     << dgs[0][5] << " (Should be " << expected3 << ")" << "\n"
	     << dgs[0][6] << " (Should be " << expected6 << ")" << "\n"
	     << dgs[0][7] << " (Should be " << expected6 << ")" << "\n"
	     << dgs[0][8] << " (Should be " << expected6 << ")" << "\n"
	     << dgs[0][9] << " (Should be " << expected6 << ")" << "\n";
       error_count++;
    }

    std::cout << "Testing Cartesian 2D Distance" << std::endl;
    
    //double expected, actual;
    TrajectoryCartesian2dPoint point00 = create_cartesian2d_point(0,0);
    TrajectoryCartesian2dPoint point01 = create_cartesian2d_point(0,1);
    TrajectoryCartesian2dPoint point11 = create_cartesian2d_point(1,1);
    TrajectoryCartesian2dPoint point22 = create_cartesian2d_point(1,0);
    
    dgs.clear();
    TrajectoryCartesian2d traj1;
    traj1.push_back(point00);
    traj1.push_back(point01);
    traj1.push_back(point11);
    traj1.push_back(point22);
    traj1.push_back(point00);
    std::vector<TrajectoryCartesian2d> all_ctrajs;
    all_ctrajs.push_back(traj1);
    GetDistanceGeometries(all_ctrajs,dgs,4);

    expected0 = 0.0;
    expected1 = 1.0/sqrt(2.0);
    expected3 = sqrt(10.0)/4.0;
    expected4 = 1.0/sqrt(2.0);
    expected6 = 1.0;
    tolerance = 1e-4;

    if ((fabs(dgs[0][0] - expected0) > tolerance) ||
     (fabs(dgs[0][1] - expected1) > tolerance) ||
     (fabs(dgs[0][3] - expected3) > tolerance) ||
     (fabs(dgs[0][4] - expected4) > tolerance) ||
     (fabs(dgs[0][6] - expected6) > tolerance)) {
      std::cout << "Error in terrestrial distance geometries" << "\n"
	     << dgs[0][0] << " (Should be " << expected0 << ")" << "\n"
	     << dgs[0][1] << " (Should be " << expected1 << ")" << "\n"
	     << dgs[0][2] << " (Should be " << expected1 << ")" << "\n"
	     << dgs[0][3] << " (Should be " << expected3 << ")" << "\n"
	     << dgs[0][4] << " (Should be " << expected4 << ")" << "\n"
	     << dgs[0][5] << " (Should be " << expected3 << ")" << "\n"
	     << dgs[0][6] << " (Should be " << expected6 << ")" << "\n"
	     << dgs[0][7] << " (Should be " << expected6 << ")" << "\n"
	     << dgs[0][8] << " (Should be " << expected6 << ")" << "\n"
	     << dgs[0][9] << " (Should be " << expected6 << ")" << "\n";
       error_count++;
    }

    return error_count;
}

int main(int, char *argv[])
{
    return run_test();
}

