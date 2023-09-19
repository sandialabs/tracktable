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

#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Cartesian3D.h>
#include <tracktable/Domain/Terrestrial.h>

#include <tracktable/ThirdParty/TracktableCatch2.h>

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

using namespace tracktable;
//----------------------------------------------------

template< typename T >
struct CityPointsAndTrajectories {

    CityPointsAndTrajectories() {
        albuquerque = T(abq_coords);
        el_paso = T(ep_coords);
        houston = T(hou_coords);
        san_antonio = T(sa_coords);

        sa_to_hou.push_back(san_antonio);
        sa_to_hou.push_back(houston);
    };

    double abq_coords[2] = { -106.6504, 35.0844 };
    double ep_coords[2] = { -106.4850, 31.7619 };
    double hou_coords[2] = { -74.0060, 29.8168 };
    double sa_coords[2] = { -98.6544, 29.4813 };

    T albuquerque;
    T el_paso;
    T houston;
    T san_antonio;

    TrajectoryLonLat sa_to_hou;

};

TEMPLATE_TEST_CASE_METHOD(CityPointsAndTrajectories, "Testing LatLon Based Point Distance", "[latlon point]", LonLatPoint, TrajectoryPointLonLat) {

    SECTION("albuquerque to el_paso ") {
        CHECK(conversions::radians_to_km(distance(CityPointsAndTrajectories<TestType>::albuquerque,
                                                    CityPointsAndTrajectories<TestType>::el_paso)) == Approx(369.764));
    }

    SECTION("albuquerque to houston ") {
        CHECK(conversions::radians_to_km(distance(CityPointsAndTrajectories<TestType>::albuquerque,
                                                    CityPointsAndTrajectories<TestType>::houston)) == Approx(3104.256));
    }
}

TEMPLATE_TEST_CASE_METHOD(CityPointsAndTrajectories, "Testing Terrestrial Based Point Distance", "[terrestrial point]", TerrestrialPoint, TerrestrialTrajectoryPoint) {

    SECTION("albuquerque to el_paso ") {
        CHECK(distance(CityPointsAndTrajectories<TestType>::albuquerque, CityPointsAndTrajectories<TestType>::el_paso) == Approx(369.764));
    }

    SECTION("albuquerque to houston ") {
        CHECK(distance(CityPointsAndTrajectories<TestType>::albuquerque, CityPointsAndTrajectories<TestType>::houston) == Approx(3104.256));
    }
}

TEMPLATE_TEST_CASE_METHOD(CityPointsAndTrajectories, "Testing LatLon Based Point to Trajectory Distance", "[latlon point trajectory]", LonLatPoint, TrajectoryPointLonLat) {

    SECTION("point to trajectory ") {
        CHECK(conversions::radians_to_km(distance(CityPointsAndTrajectories<TestType>::albuquerque, CityPointsAndTrajectories<TestType>::sa_to_hou)) == Approx(975.674));
    }

    SECTION("trajectory to point ") {
        CHECK(conversions::radians_to_km(distance(CityPointsAndTrajectories<TestType>::sa_to_hou, CityPointsAndTrajectories<TestType>::albuquerque)) == Approx(975.674));
    }
}

TEMPLATE_TEST_CASE("Testing Terrestrial Based Point to Trajectory Distance", "[terrestrial point trajectory]", TerrestrialPoint, TerrestrialTrajectoryPoint) {
    double abq_coords[2] = { -106.6504, 35.0844 };
    TestType albuquerque(abq_coords);
    TerrestrialTrajectoryPoint houston({ -74.0060, 29.8168 });
    TerrestrialTrajectoryPoint san_antonio({ -98.6544, 29.4813 });

    TerrestrialTrajectory sa_to_hou;
    sa_to_hou.push_back(san_antonio);
    sa_to_hou.push_back(houston);

    SECTION("point to trajectory ") {
        CHECK(distance(albuquerque, sa_to_hou) == Approx(975.674));
    }

    SECTION("trajectory to point ") {
        CHECK(distance(sa_to_hou, albuquerque) == Approx(975.674));
    }
}

TEST_CASE("Testing LatLon Trajectory Distance", "[latlon  trajectory]") {
    TrajectoryPointLonLat albuquerque({ -106.6504, 35.0844 });
    TrajectoryPointLonLat houston({ -74.0060, 29.8168 });
    TrajectoryPointLonLat san_antonio({ -98.6544, 29.4813 });
    TrajectoryPointLonLat dallas({ -96.8716, 32.820 });
    TrajectoryPointLonLat el_paso({ -106.4850, 31.7619 });

    TrajectoryLonLat sa_to_hou;
    sa_to_hou.push_back(san_antonio);
    sa_to_hou.push_back(houston);

    TrajectoryLonLat ep_to_dal;
    ep_to_dal.push_back(el_paso);
    ep_to_dal.push_back(dallas);

    TrajectoryLonLat sa_to_abq;
    sa_to_abq.push_back(san_antonio);
    sa_to_abq.push_back(albuquerque);

    SECTION("trajectory to trajectory ") {
        CHECK(conversions::radians_to_km(distance(ep_to_dal, sa_to_hou)) == Approx(349.221));
    }

    SECTION("intersecting trajectory ") {
        CHECK(conversions::radians_to_km(distance(ep_to_dal, sa_to_abq)) == Approx(0.0));
    }
}

TEST_CASE("Testing Terrestrial Trajectory Distance", "[terrestrial  trajectory]") {
    TerrestrialTrajectoryPoint albuquerque({ -106.6504, 35.0844 });
    TerrestrialTrajectoryPoint houston({ -74.0060, 29.8168 });
    TerrestrialTrajectoryPoint san_antonio({ -98.6544, 29.4813 });
    TerrestrialTrajectoryPoint dallas({ -96.8716, 32.820 });
    TerrestrialTrajectoryPoint el_paso({ -106.4850, 31.7619 });

    TerrestrialTrajectory sa_to_hou;
    sa_to_hou.push_back(san_antonio);
    sa_to_hou.push_back(houston);

    TerrestrialTrajectory ep_to_dal;
    ep_to_dal.push_back(el_paso);
    ep_to_dal.push_back(dallas);

    TerrestrialTrajectory sa_to_abq;
    sa_to_abq.push_back(san_antonio);
    sa_to_abq.push_back(albuquerque);

    SECTION("trajectory to trajectory ") {
        CHECK(distance(ep_to_dal, sa_to_hou) == Approx(349.221));
    }

    SECTION("intersecting trajectory ") {
        CHECK(distance(ep_to_dal, sa_to_abq) == Approx(0.0));
    }
}

TEST_CASE("Testing Cartesian2D Distance", "[cartesian2D]") {
    TrajectoryCartesian2dPoint point00(0, 0);
    TrajectoryCartesian2dPoint point01(0, 1);
    TrajectoryCartesian2dPoint point11(1, 1);
    TrajectoryCartesian2dPoint point22(2, 2);

    TrajectoryCartesian2d traj1;
    traj1.push_back(point00);
    traj1.push_back(point01);

    TrajectoryCartesian2d traj2;
    traj2.push_back(point11);
    traj2.push_back(point22);

    SECTION("horizontal point to point " ) {
        CHECK(distance(point00, point01) == 1.0);
    }

    SECTION("vertical point to point ") {
        CHECK(distance(point01, point11) == 1.0);
    }

    SECTION("diagonal point to point ") {
        CHECK(distance(point00, point11) == Approx(1.414).epsilon(0.001));
    }

    SECTION("trajectory to trajectory ") {
        CHECK(distance(traj1, traj2) == 1.0);
    }

    SECTION("trajectory to point ") {
        CHECK(distance(traj2, point00) == Approx(1.414).epsilon(0.001));
    }

    SECTION("point to trajectory ") {
        CHECK(distance(point00, traj2) == Approx(1.414).epsilon(0.001));
    }
}

TEST_CASE("Testing Cartesian3D Distance", "[cartesian3D]") {
    TrajectoryCartesian3dPoint point000(0, 0, 0);
    TrajectoryCartesian3dPoint point001(0, 0, 1);
    TrajectoryCartesian3dPoint point010(0, 1, 0);
    TrajectoryCartesian3dPoint point100(1, 0, 0);
    TrajectoryCartesian3dPoint point111(1, 1, 1);
    TrajectoryCartesian3dPoint point222(2, 2, 2);

    TrajectoryCartesian3d traj1;
    traj1.push_back(point000);
    traj1.push_back(point001);

    TrajectoryCartesian3d traj2;
    traj2.push_back(point111);
    traj2.push_back(point222);

    SECTION("x axis point to point ") {
        CHECK(distance(point000, point100) == 1.0);
    }

    SECTION("y axis point to point ") {
        CHECK(distance(point000, point010) == 1.0);
    }

    SECTION("z axis point to point ") {
        CHECK(distance(point000, point001) == 1.0);
    }

    SECTION("diagonal point to point ") {
        CHECK(distance(point000, point111) == Approx(1.732).epsilon(0.001));
    }

    // This doesnt work because boost::geometry::disjoint is not implemented for dimenstions > 2
    //SECTION("trajectory to trajectory ") {
    //    CHECK(distance(traj1, traj2) == 1.0);
    //}

    SECTION("trajectory to point ") {
        CHECK(distance(traj2, point000) == Approx(1.732).epsilon(0.001));
    }

    SECTION("point to trajectory ") {
        CHECK(distance(point000, traj2) == Approx(1.732).epsilon(0.001));
    }
}



