#include <tracktable/DataGenerators/PointGenerator.h>

#include <tracktable/ThirdParty/TracktableCatch2.h>

using tracktable::CircularPointGenerator;
using tracktable::ConstantSpeedPointGenerator;
using tracktable::GridPointGenerator;
using tracktable::MultipleGeneratorCollator;
using tracktable::PointGenerator;

using PointT = PointGenerator<tracktable::domain::terrestrial::trajectory_type::point_type>::PointT;
// 35.0844° N, 106.6504° W
PointT albuquerque(-106.6504, 35.0844);
// 32.3199° N, 106.7637° W
PointT lascruces(-106.7637, 32.3199);

struct SetUp {
  SetUp() {
    albuquerque.set_property("Altitude", 5312.0);
    albuquerque.set_timestamp(boost::posix_time::time_from_string("2020-08-21 12:34:56.000"));
    lascruces.set_property("Altitude", 3900.0);
    lascruces.set_timestamp(boost::posix_time::time_from_string("2020-08-21 13:45:00.000"));
  }
};
static const SetUp setup;
/***
 * These tests apply to all generators
 */
TEMPLATE_TEST_CASE("Generator Creation",
                   "[PointGenerator][ConstantSpeedPointGenerator][CircularPointGenerator]",
                   PointGenerator<tracktable::domain::terrestrial::trajectory_type::point_type>,
                   ConstantSpeedPointGenerator, CircularPointGenerator) {
  using GeneratorT = TestType;
  GIVEN("A default point generator") {
    GeneratorT pg;
    WHEN("Asked for next point") {
      auto pt = pg.next();
      THEN("Point is a default point") { REQUIRE(pt == PointT()); }
      AND_WHEN("Asked for next point again") {
        auto pt2 = pg.next();
        THEN("timestamp increases by default interval") {
          REQUIRE(pt2.timestamp() == (pt.timestamp() + pg.getInterval()));
        }
      }
      WHEN("A new interval is specified") {
        auto interval = tracktable::seconds(42);
        pg.setInterval(interval);
        AND_WHEN("Asked for next point again") {
          auto pt2 = pg.next();
          THEN("timestamp increases by specified interval") {
            REQUIRE(pt2.timestamp() == (pt.timestamp() + interval));
          }
        }
      }
    }
    WHEN("An objectID is set") {
      const std::string id = "TestId";
      pg.setObjectId(id);
      AND_WHEN("asked for a point") {
        auto pt = pg.next();
        THEN("ObjectId matches") { REQUIRE(id == pt.object_id()); }
      }
    }
  }
  GIVEN("An initial point") {
    GeneratorT pg(albuquerque);
    WHEN("asked for next point") {
      auto pt = pg.next();
      THEN("Point matches Initial point") { REQUIRE(pt == albuquerque); }
    }
  }
  GIVEN("An initial point and update interval") {
    auto interval = tracktable::milliseconds(42000);
    GeneratorT pg(lascruces, interval);
    WHEN(" asked for next point") {
      auto pt = pg.next();
      THEN("Point matches initial") {
        REQUIRE(pt == lascruces);
        AND_THEN("interval matches specified") { REQUIRE(pg.getInterval() == interval); }
      }
    }
  }
}

/**
 * Tests for the 'reckon functions'
 **/
SCENARIO("Reckon function", "[reckon][ConstantSpeedPointGenerator]") {
  GIVEN("and origin and a destination") {
    // 35.0844° N, 106.6504° N albuquerque
    // 32.3199° N, 106.7637° W lascruces
    WHEN("You calculate distance and bearing between the two") {
      auto d = tracktable::distance(albuquerque, lascruces) * 1000.0;
      auto b = tracktable::bearing(albuquerque, lascruces);
      AND_WHEN("Use that bearing and distance to calculate destination") {
        auto guess = ConstantSpeedPointGenerator::reckon(albuquerque, d, b);
        THEN("Guess will be the same as destination") {
          CHECK(lascruces.longitude() == Approx(guess.longitude()));
          CHECK(lascruces.latitude() == Approx(guess.latitude()));
        }
      }
      AND_WHEN("Use that bearing and distance to calculate destination") {
        auto guess = ConstantSpeedPointGenerator::reckon2(albuquerque, d, b, tracktable::seconds(1));
        THEN("Guess will be the same as destination") {
          CHECK(lascruces.longitude() == Approx(guess.longitude()).margin(.05));
          CHECK(lascruces.latitude() == Approx(guess.latitude()).margin(.05));
        }
      }
    }
  }
}

/**
 * These test apply to all Constant Speed generators
 **/
TEMPLATE_TEST_CASE("ConstantSpeed Generators", "[ConstantSpeedPointGenerator][CircularPointGenerator",
                   ConstantSpeedPointGenerator, CircularPointGenerator, GridPointGenerator) {
  using GeneratorT = TestType;
  GIVEN("A default point generator") {
    GeneratorT pg;
    THEN("speed is set to default;") {
      REQUIRE(pg.getSpeed() == Approx(44.704));  //~100Mi/h in m/s
    }
    AND_THEN("Heading is set to default;") { REQUIRE(pg.getHeading() == Approx(0.0)); }
    WHEN("assigned a specific speed") {
      constexpr double speed = 42.0;
      pg.setSpeed(speed);
      THEN("Speed matches new speed") { REQUIRE(pg.getSpeed() == Approx(speed)); }
    }
    WHEN("assigned a specific heading") {
      constexpr double heading = 180.0;
      pg.setHeading(heading);
      THEN("heading matches new heading") { REQUIRE(pg.getHeading() == Approx(heading)); }
    }
    WHEN("assigned 0 speed") {
      pg.setSpeed(0.0);
      WHEN("next is called twice") {
        auto p1 = pg.next();
        auto p2 = pg.next();
        THEN("distance between p1 and p2 should be 0") {
          auto d = tracktable::distance(p1, p2);
          REQUIRE(d == Approx(0.0).margin(0.0000001));
        }
      }
    }
    WHEN("next is called twice") {
      auto heading = pg.getHeading();
      auto p1 = pg.next();
      auto p2 = pg.next();
      THEN("bearing from p1 to p2 should match heading") {
        CHECK(heading == Approx(tracktable::bearing(p1, p2)).margin(.5));
        AND_THEN("distance should match speed*interval") {
          auto d1 = tracktable::distance(p1, p2);  // in km
          constexpr auto m_per_km = 1000.0;
          constexpr auto ms_per_s = 1000.0;
          auto d2 = pg.getInterval().total_milliseconds() * pg.getSpeed() / m_per_km / ms_per_s;  // m ->km
          CHECK(d1 == Approx(d2).margin(.001));
        }
      }
    }
  }
  GIVEN("An Origin, update interval, initial speed and heading") {
    const auto interval = tracktable::minutes(2);
    constexpr auto speed = 42.0;     // m/s
    constexpr auto heading = 181.0;  // deg
    GeneratorT pg(lascruces, interval, speed, heading);
    THEN("speed matches") {
      REQUIRE(pg.getSpeed() == Approx(speed));
      AND_THEN("heading matches") { REQUIRE(pg.getHeading() == Approx(heading)); }
    }
  }
}

/**
 * These tests apply to the Constant Speed base class
 */
SCENARIO("ConstantSpeedPointGenerator", "[ConstantSpeedPointGenerator]") {
  using GeneratorT = ConstantSpeedPointGenerator;
  GIVEN("an Origin and destination in mind ") {
    // 35.0844° N, 106.6504° N albuquerque
    constexpr auto speed = 42.0;
    const auto heading = tracktable::bearing(albuquerque, lascruces);
    GeneratorT pg(albuquerque, tracktable::seconds(60), speed, heading);
    WHEN("next is called 100 times") {
      auto p1 = pg.next();
      for (auto i = 0u; i < 98; ++i) {
        pg.next();
      }
      auto p2 = pg.next();
      THEN("bearing from p1 to p2 should match heading") {
        CHECK(heading == Approx(tracktable::bearing(p1, p2)).margin(.5));
        AND_THEN("distance should match 99*speed*interval") {
          auto d1 = tracktable::distance(p1, p2);  // km
          auto d2 = pg.getInterval().total_seconds() * speed * 99.0 / 1000.0;
          CHECK(d1 == Approx(d2).margin(.05));
          AND_THEN("delta t should match interval*99") {
            auto intervalSeconds = 99.0 * pg.getInterval().total_milliseconds() / 1000.0;
            auto dt = (p2.timestamp() - p1.timestamp()).total_milliseconds() / 1000.0;
            CHECK(intervalSeconds == dt);
          }
        }
      }
    }
  }
}

/**
 * Circular point generator
 */
SCENARIO("CircularPointGenerator", "[CircularPointGenerator]") {
  using GeneratorT = CircularPointGenerator;
  GIVEN("A default Generator ") {
    GeneratorT pg;
    // 35.0844° N, 106.6504° N albuquerque
    THEN("Turn rate is set to default;") {
      REQUIRE(pg.getTurnRate() == Approx(.6));  //~100Mi/h in m/s
    }
    WHEN("assigned a specific turn rate") {
      constexpr double turnRate = 42.0;
      pg.setTurnRate(turnRate);
      THEN("rate matches new rate") { REQUIRE(pg.getTurnRate() == Approx(turnRate)); }
    }
    WHEN("next is called twice") {
      const auto heading = pg.getHeading();
      const auto turnRate = pg.getTurnRate();
      auto p1 = pg.next();
      auto p2 = pg.next();
      THEN("Heading should have changed by turn rate * 60") {
        REQUIRE(pg.getHeading() == Approx(heading + turnRate * 60));
      }
    }
    WHEN("next is called 61 times") {
      const auto heading = pg.getHeading();
      auto p1 = pg.next();
      for (auto i = 0u; i < 59; ++i) {
        pg.next();
      }
      auto p2 = pg.next();
      THEN("Headings should match") {
        REQUIRE(pg.getHeading() == Approx(heading));
        AND_THEN("Should be back at start point") {
          REQUIRE(tracktable::distance(p1, p2) == Approx(0.0).margin(0.000001));
        }
      }
    }
  }
  GIVEN("a starting point, invterval, speed, heading, and turn rate") {
    const auto interval = tracktable::minutes(2);
    constexpr auto speed = 42.0;     // m/s
    constexpr auto heading = 181.0;  // deg
    constexpr auto turnRate = .1;    // deg/s
    GeneratorT pg(lascruces, interval, speed, heading, turnRate);
    THEN("Turn rate matches") { REQUIRE(pg.getTurnRate() == Approx(turnRate)); }
  }
}

SCENARIO("GridPointGenerator", "[GridPointGenerator]") {
  using GeneratorT = GridPointGenerator;
  GIVEN("A Default Generator") {
    GeneratorT pg;
    WHEN("next is called 11 times") {
      auto h1 = pg.getHeading();
      auto pt1 = pg.next();
      for (auto i = 0u; i < 9; ++i) {
        pg.next();
      }
      auto pt2 = pg.next();
      auto h2 = pg.getHeading();
      THEN("heading should turn right") { REQUIRE(std::abs(h1 - h2) == Approx(90.0)); }
      AND_WHEN("called another 10 times") {
        for (auto i = 0u; i < 9; ++i) {
          pg.next();
        }
        auto pt3 = pg.next();
        auto h3 = pg.getHeading();
        THEN("heading should be off from origin 180 deg") { REQUIRE(std::abs(h3 - h1) == Approx(180.0)); }
        AND_WHEN("called another 9 times") {
          for (auto i = 0u; i < 8; ++i) {
            pg.next();
          }
          auto pt4 = pg.next();
          auto h4 = pg.getHeading();
          THEN("The heading should match pt3") { REQUIRE(std::abs(h4 - h3) == Approx(0.0)); }
          AND_WHEN("called once more") {
            auto pt5 = pg.next();
            auto h5 = pg.getHeading();
            THEN("Heading increments 90 deg") { REQUIRE(std::abs(h5 - h4) == Approx(90.0)); }
            AND_WHEN("called 10 times more") {
              for (auto i = 0u; i < 9; ++i) {
                pg.next();
              }
              auto pt6 = pg.next();
              auto h6 = pg.getHeading();
              THEN("Heading matches original") {
                REQUIRE(std::abs(h6 - h1) == Approx(0.0));
                AND_THEN("At Original point") {
                  REQUIRE(tracktable::distance(pt6, pt1) == Approx(0.0).margin(.0000001));
                }
              }
            }
          }
        }
      }
    }
  }
}

SCENARIO("MultipleGeneratorCollator", "[MultipleGeneratorCollator]") {
  GIVEN("Default Collator") {
    MultipleGeneratorCollator<PointT> mgc;
    WHEN("You add a nullptr") {
      THEN("You get an exception") {
        REQUIRE_THROWS_WITH(mgc.addGenerator(std::shared_ptr<PointGenerator<PointT>>()),
                            "Pointer is nullptr");
        AND_THEN("Count is 0") { REQUIRE(mgc.getGeneratorCount() == 0); }
      }
    }
    WHEN("You ask for a point") {
      THEN("You get an exception") { REQUIRE_THROWS_WITH(mgc.next(), "No generated points"); }
    }
    WHEN("You generate points") {
      THEN("You get an exception") { REQUIRE_THROWS_WITH(mgc.generate(), "No generators"); }
    }
    WHEN("You add a generator") {
      mgc.addGenerator(std::make_shared<PointGenerator<PointT>>());
      THEN("Count is 1") { REQUIRE(mgc.getGeneratorCount() == 1); }
      AND_WHEN("You generate points") {
        mgc.generate();
        AND_WHEN("you ask for a point") {
          auto pt = mgc.next();
          THEN("you will get a default point") { REQUIRE(pt == PointT()); }
          AND_WHEN("You ask for a second point") {
            auto pt2 = mgc.next();
            THEN("Timestamp advances") { REQUIRE_FALSE(pt.timestamp() == pt2.timestamp()); }
          }
        }
      }
    }
    WHEN("add two similar generators with different object-ids") {
      auto cg1 = std::make_shared<CircularPointGenerator>(albuquerque);
      auto cg2 = std::make_shared<CircularPointGenerator>(albuquerque);
      cg1->setObjectId("cg1");
      cg2->setObjectId("cg2");
      mgc.addGenerator(cg1);
      mgc.addGenerator(cg2);
      AND_WHEN("You generate points") {
        mgc.generate();
        WHEN("get two points") {
          auto pt1 = mgc.next();
          auto pt2 = mgc.next();
          THEN("The objectIds do not match") { REQUIRE_FALSE(pt1.object_id() == pt2.object_id()); }
        }
      }
    }
    WHEN("add two generators where the second starts before the first") {
      auto cg1 = std::make_shared<CircularPointGenerator>(lascruces);  // timestamp is an hour later than abq
      auto cg2 = std::make_shared<CircularPointGenerator>(albuquerque);
      mgc.addGenerator(cg1);
      mgc.addGenerator(cg2);
      AND_WHEN("You generate 100 points") {
        mgc.generate(100);
        AND_WHEN("get 200 points") {
          std::vector<decltype(mgc.next())> points;
          for (auto i = 0u; i < 200u; ++i) {
            points.push_back(mgc.next());
          }
          THEN("each timestamp will be >= the previous") {
            for (auto i = 1u; i < 100u; ++i) {
              REQUIRE(points[i].timestamp() >= points[i - 1].timestamp());
            }
          }
          AND_WHEN("You get another ") {
            THEN("You get an exception") { REQUIRE_THROWS_WITH(mgc.next(), "No generated points"); }
          }
        }
      }
    }
  }
}