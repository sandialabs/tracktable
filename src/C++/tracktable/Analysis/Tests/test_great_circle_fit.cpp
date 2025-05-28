/* Copyright (c) 2014-2023 National Technology and Engineering
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
#include <tracktable/Analysis/GreatCircleFit.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/DataGenerators/PointGenerator.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/ThirdParty/TracktableCatch2.h>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = TrajectoryT::point_type;
using Point3dT = tracktable::domain::cartesian3d::base_point_type;

const Point3dT NORTH(0.0, 0.0, 1.0);
const Point3dT WEST(0.0, -1.0, 0.0);

constexpr auto NUM_POINTS = 100u;
constexpr auto HEADING_EAST = 90.0;
constexpr auto HEADING_NORTH = 0.0;
constexpr auto SPEED = 30.0;
constexpr auto ALTITUDE = 1000.0;
constexpr auto ZIG = 0.01;
constexpr auto ZAG = -ZIG;
constexpr auto NORMAL_TOLERANCE = 0.0001;

/////////////////////// MINIMIZE //////////////////////////////////
// TODO switch to template test case to run all tracks through it
SCENARIO("Best fit plane Degenerate Case") {
  GIVEN("A trajectory with less than two points") {
    TrajectoryT noPoints;
    WHEN("You try to find a best fit plane") {
      THEN("An TooFewPoints exception is thrown") {
        REQUIRE_THROWS_AS(tracktable::find_best_fit_plane(noPoints), TooFewPoints);
      }
    }
  }
  GIVEN("A trajectory with all identical points") {
    TrajectoryT samePoints;
    PointT p;
    p.set_property("altitude", 0.0);
    samePoints.push_back(p);
    samePoints.push_back(p);
    WHEN("You try to find the best fit plane") {
      THEN("An IdenticalPoints exception is thrown") {
        REQUIRE_THROWS_AS(tracktable::find_best_fit_plane(samePoints), IdenticalPositions);
      }
    }
  }
}

SCENARIO("Best Fit Plane Minimal Case") {
  GIVEN("A two point trajectory going east") {
    TrajectoryT twoPointEast;
    PointT p;
    p.set_property("altitude", ALTITUDE);
    twoPointEast.push_back(p);
    p.set_longitude(10);
    twoPointEast.push_back(p);
    WHEN("You find a best fit plane") {
      auto normal = tracktable::find_best_fit_plane(twoPointEast);
      THEN("It's normal points straight north") {
        REQUIRE(1.0 == tracktable::arithmetic::dot(normal, NORTH));
      }
    }
  }
  GIVEN("A two point trajectory going north") {
    TrajectoryT twoPointNorth;
    PointT p;
    p.set_property("altitude", ALTITUDE);
    twoPointNorth.push_back(p);
    p.set_latitude(10);
    twoPointNorth.push_back(p);
    WHEN("You find a best fit plane") {
      auto normal = tracktable::find_best_fit_plane(twoPointNorth);
      THEN("It's normal points straight west") { REQUIRE(1.0 == tracktable::arithmetic::dot(normal, WEST)); }
    }
  }
}

SCENARIO("More complicated") {
  GIVEN("A hundred point trajectory going straight east") {
    auto p = tracktable::arithmetic::zero<PointT>();
    p.set_property("altitude", ALTITUDE);
    // Generator for a trajectory with a speed of .01(deg/s), an update interval of 60s and a heading of 90deg
    tracktable::ConstantSpeedPointGenerator generatorEast(p, tracktable::minutes(1), SPEED, HEADING_EAST);
    TrajectoryT hundredPointEast;
    for (auto i = 0u; i < NUM_POINTS; ++i) {
      hundredPointEast.push_back(generatorEast.next());
    }
    WHEN("You find a best fit plane") {
      auto normal = tracktable::find_best_fit_plane(hundredPointEast);
      THEN("It's normal points straight north") {
        REQUIRE(1.0 == tracktable::arithmetic::dot(normal, NORTH));
      }
    }
    AND_GIVEN("Those points are zigzagged") {
      // Move half the points up and half the points down a degree
      for (auto i = 0; i < NUM_POINTS; ++i) {
        hundredPointEast[i].set_latitude(hundredPointEast[i].latitude() + ((i % 2) != 0 ? ZIG : ZAG));
      }
      WHEN("You find a best fit plane") {
        auto normal = tracktable::find_best_fit_plane(hundredPointEast);
        THEN("It's normal points straight north") {
          REQUIRE(Approx(1.0).margin(NORMAL_TOLERANCE) == tracktable::arithmetic::dot(normal, NORTH));
        }
      }
    }
  }
  GIVEN("A hundred point trajectory going straight north") {
    auto p = tracktable::arithmetic::zero<PointT>();
    p.set_property("altitude", ALTITUDE);
    // Generator for a trajectory with a speed of .01(deg/s), an update interval of 60s and a heading of 90deg
    tracktable::ConstantSpeedPointGenerator generatorNorth(p, tracktable::minutes(1), SPEED, HEADING_NORTH);
    TrajectoryT hundredPointNorth;
    for (auto i = 0u; i < NUM_POINTS; ++i) {
      hundredPointNorth.push_back(generatorNorth.next());
    }
    WHEN("You find a best fit plane") {
      auto normal = tracktable::find_best_fit_plane(hundredPointNorth);
      THEN("It's normal points straight west") { REQUIRE(1.0 == tracktable::arithmetic::dot(normal, WEST)); }
    }
    AND_GIVEN("Those points are zigzagged") {
      // Move half the points up and half the points down a degree
      for (auto i = 0; i < NUM_POINTS; ++i) {
        hundredPointNorth[i].set_longitude(hundredPointNorth[i].longitude() + ((i % 2) != 0 ? ZIG : ZAG));
      }
      WHEN("You find a best fit plane") {
        auto normal = tracktable::find_best_fit_plane(hundredPointNorth);
        THEN("It's normal points straight west") {
          REQUIRE(Approx(1.0).margin(NORMAL_TOLERANCE) == tracktable::arithmetic::dot(normal, WEST));
        }
      }
    }
  }
}
///////////////////////////////PROJECT////////////////////////////
SCENARIO("Project onto best fit plane degenerate case") {
  GIVEN("A normal pointed north") {
    const auto& normal = NORTH;
    AND_GIVEN("A trajectory with no points") {
      TrajectoryT trajectory;
      WHEN("You try to project") {
        THEN("An exception is thrown") {
          REQUIRE_THROWS_AS(tracktable::project_trajectory_onto_plane(trajectory, normal), TooFewPoints);
        }
      }
    }
  }
  GIVEN("A normal with a magnitude of 0") {
    auto normal = tracktable::arithmetic::zero<Point3dT>();
    AND_GIVEN("A trajectory with one point") {
      TrajectoryT trajectory;
      trajectory.push_back(PointT());
      WHEN("You try to project") {
        THEN("An exception is thrown") {
          REQUIRE_THROWS_AS(tracktable::project_trajectory_onto_plane(trajectory, normal), ZeroNorm);
        }
      }
    }
  }
}

SCENARIO("Project onto best fit plane") {
  GIVEN("A numPoints point trajectory zigzaging east") {
    auto p = tracktable::arithmetic::zero<PointT>();
    p.set_property("altitude", ALTITUDE);
    // Generator for a trajectory with a speed of .01(deg/s), an update interval of 60s and a heading of 90deg
    tracktable::ConstantSpeedPointGenerator generatorEast(p, tracktable::minutes(1), SPEED, HEADING_EAST);
    TrajectoryT hundredPointEast;
    for (auto i = 0u; i < NUM_POINTS; ++i) {
      auto pp = generatorEast.next();
      pp.set_latitude(pp.latitude() + ((i % 2) != 0u ? ZIG : ZAG));
      hundredPointEast.push_back(pp);
    }
    AND_GIVEN("A normal pointing north") {
      const auto& normal = NORTH;
      WHEN("You project the trajectory onto the plane") {
        auto result = hundredPointEast;
        tracktable::project_trajectory_onto_plane(result, normal);
        AND_THEN("The length will decrease") {
          auto l1 = tracktable::length(hundredPointEast);
          auto l2 = tracktable::length(result);
          CHECK(l2 < l1);
        }
        AND_THEN("The altitude will be unchanged") { /*alt before = alt after*/
          for (auto i = 0u; i < result.size(); ++i) {
            CHECK(result[i].real_property("altitude") == hundredPointEast[i].real_property("altitude"));
          }
        }
        AND_THEN("Each point will be on the plane") { /*point DOT normal = 0*/
          for (auto& point : result) {
            CHECK(0.0 ==
                  tracktable::arithmetic::dot(
                      normal, point.ECEF("altitude", tracktable::domain::terrestrial::AltitudeUnits::FEET)));
          }
        }
      }
    }
  }
}

/////////////////////////////////SANITY/////////////////////////////////////////
SCENARIO("TOP DOWN SANITY") {
  GIVEN("A normal") {
    const auto& normal = NORTH;
    WHEN("You generate points along the suface defined by that normal") {
      auto random1 = Point3dT(1, 2, 3);
      auto u1 = tracktable::arithmetic::cross_product(normal, random1);
      auto u2 = tracktable::arithmetic::cross_product(normal, u1);
      // TODO combine u1 and u2 to create a set of points, then convert those to lat/lon (need to implement
      // fromECEF() function )
      AND_WHEN("You Find a best fit plane for those points") {
        THEN("The fit-normal should be parallel to the original normal") { /*|fit| == fit DOT N*/
        }
      }
    }
  }
  GIVEN("A 100 point trajectory zigzaging east") {
    auto p = tracktable::arithmetic::zero<PointT>();
    p.set_property("altitude", ALTITUDE);
    // Generator for a trajectory with a speed of .01(deg/s), an update interval of 60s and a heading of 90deg
    tracktable::ConstantSpeedPointGenerator generatorEast(p, tracktable::minutes(1), SPEED, HEADING_EAST);
    TrajectoryT hundredPointEast;
    for (auto i = 0u; i < NUM_POINTS; ++i) {
      auto pp = generatorEast.next();
      pp.set_latitude(pp.latitude() + ((i % 2) != 0u ? ZIG : ZAG));
      hundredPointEast.push_back(pp);
    }
    WHEN("You find a best fit plane") {
      auto n1 = tracktable::find_best_fit_plane(hundredPointEast);
      AND_WHEN("You project a trajectory on to that plane") {
        tracktable::project_trajectory_onto_plane(hundredPointEast, n1);
        AND_WHEN("You find a best fit plane for the projected trajectory") {
          auto n2 = tracktable::find_best_fit_plane(hundredPointEast);
          THEN("That plane should align with the original fit") {
            for (auto u = 0u; u < Point3dT::size(); ++u) {
              CHECK(n1[u] == Approx(n2[u]));
            }
          }
        }
      }
    }
  }
}