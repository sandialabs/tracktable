#include <tracktable/ThirdParty/TracktableCatch2.h>

#include <tracktable/DataGenerators/PointGenerator.h>
#include <tracktable/Domain/Terrestrial.h>

#include <tracktable/IO/KmlOut.h>

#include <sstream>
#include <iostream>

using tracktable::kml;

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type ;
using PointT = tracktable::PointGenerator<TrajectoryT::point_type>::PointT;

using tracktable::CircularPointGenerator;

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
//This is more of a tripwire than a validation
SCENARIO("KML Tripwire") {
  GIVEN("Generated Trajectories") {
    auto cg1 = std::make_shared<CircularPointGenerator>(lascruces);  // timestamp is an hour later than abq
    auto cg2 = std::make_shared<CircularPointGenerator>(albuquerque);
    cg1->setObjectId("lc");
    cg2->setObjectId("abq");
    TrajectoryT abqTrajectory;
    TrajectoryT lcTrajectory;
    for (auto i = 0u; i < 100; ++i) {
      lcTrajectory.push_back(cg1->next());
      abqTrajectory.push_back(cg2->next());
    }
    AND_GIVEN("An output stream") {
      std::stringstream out;
      WHEN("Written out") {
        out << kml::header;
        out << kml(lcTrajectory);
        out << kml(abqTrajectory);
        out << kml::footer;
        THEN("written Size matches known size") {
          REQUIRE(out.str().size() == 6902);
          //std::cout << out.str(); //Can uncomment to copy and paste for render check
          //TODO: Automated render check
        }
      }
    }
  }
}