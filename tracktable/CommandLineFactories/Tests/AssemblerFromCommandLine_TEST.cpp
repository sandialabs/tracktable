/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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
#include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/IO/PointReader.h>

#include <tracktable/ThirdParty/catch2.hpp>

// Bitfield enum for testing multiple fields at a time
enum FieldID {
  DISTANCE = 1,
  SECONDS = 1 << 1,
  MINIMUMPOINTS = 1 << 2,
  CLEANUPINTERVAL = 1 << 3,
  ALL = DISTANCE | SECONDS | MINIMUMPOINTS | CLEANUPINTERVAL
};

using tracktable::AssemblerFromCommandLine;

// Aliases for readability
using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = TrajectoryT::point_type;
using ReaderT = tracktable::PointReader<PointT>;
using ReaderIteratorT = typename ReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, ReaderIteratorT>;

// Convenience functions for code reuse
void checkDefaults(std::shared_ptr<AssemblerT> _assembler, FieldID _fields);

SCENARIO("Creating Assembler", "[AssemblerFromCommandLine]") {
  std::ofstream testfile("onepoint.txt");
  testfile << "A7067\t2013-07-10 00:00:00\t-112.483\t51.3333\t16500\n";
  testfile.close();
  GIVEN("Unititialized Factory") {
    AssemblerFromCommandLine<TrajectoryT> factory;
    WHEN("PointReader for onepoint.txt is created") {
      std::ifstream readfile("onepoint.txt");
      REQUIRE(readfile.is_open());
      auto reader = std::make_shared<ReaderT>(readfile);
      reader->set_object_id_column(0);
      reader->set_timestamp_column(1);
      reader->set_x_column(2);
      reader->set_y_column(3);
      reader->set_real_field_column("Altitude", 4);
      reader->set_field_delimiter("\t");
      WHEN("create is called before parse") {
        THEN("a runtime error is thrown") {
          REQUIRE_THROWS_WITH(factory.createAssembler(reader), "Create Called With No Variable Map");
        }
      }
      WHEN("command line is empty") {
        int ARGC = 1;
        char* ARGV[] = {(char*)"exec", NULL};
        AND_WHEN("command line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          AND_WHEN("assembler is created") {
            auto assembler = factory.createAssembler(reader);
            THEN("Everything is default") { checkDefaults(assembler, FieldID::ALL); }
          }
        }
      }
      WHEN("args: --separation-distance=42") {
        int ARGC = 2;
        char* ARGV[3]{(char*)"exec", (char*)"--separation-distance=42", nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("assembler is created") {
            auto assembler = factory.createAssembler(reader);
            THEN("separation distance is set to 42; Rest are default") {
              REQUIRE(assembler->separation_distance() == Approx(42.0));
              checkDefaults(assembler, FieldID(~FieldID::DISTANCE));
            }
          }
        }
      }
      WHEN("args: --separation-seconds=43") {
        int ARGC = 2;
        char* ARGV[3]{(char*)"exec", (char*)"--separation-seconds=43", nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("assembler is created") {
            auto assembler = factory.createAssembler(reader);
            THEN("separation time is set to 43; Rest are default") {
              REQUIRE(assembler->separation_time() == tracktable::seconds(43));
              checkDefaults(assembler, FieldID(~FieldID::SECONDS));
            }
          }
        }
      }
      WHEN("args: --min-points=44") {
        int ARGC = 2;
        char* ARGV[3]{(char*)"exec", (char*)"--min-points=44", nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("assembler is created") {
            auto assembler = factory.createAssembler(reader);
            THEN("minimum points is set to 44; Rest are default") {
              REQUIRE(assembler->minimum_trajectory_length() == 44);
              checkDefaults(assembler, FieldID(~FieldID::MINIMUMPOINTS));
            }
          }
        }
      }
      WHEN("args: --clean-up-interval=45") {
        int ARGC = 2;
        char* ARGV[3]{(char*)"exec", (char*)"--clean-up-interval=45", nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("assembler is created") {
            auto assembler = factory.createAssembler(reader);
            THEN("cleanup interval is set to 45; Rest are default") {
              REQUIRE(assembler->cleanup_interval() == 45);
              checkDefaults(assembler, FieldID(~FieldID::CLEANUPINTERVAL));
            }
          }
        }
      }

      WHEN("args: --separation-distance=42 --separation-seconds=43 --min-points=44 --clean-up-interval=45") {
        int ARGC = 5;
        char* ARGV[6]{(char*)"exec",
                      (char*)"--separation-distance=42",
                      (char*)"--separation-seconds=43",
                      (char*)"--min-points=44",
                      (char*)"--clean-up-interval=45",
                      nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("assembler is created") {
            auto assembler = factory.createAssembler(reader);
            THEN("Values match args") {
              REQUIRE(assembler->separation_distance() == Approx(42.0));
              REQUIRE(assembler->separation_time() == tracktable::seconds(43));
              REQUIRE(assembler->minimum_trajectory_length() == 44);
              REQUIRE(assembler->cleanup_interval() == 45);
            }
          }
        }
      }
      readfile.close();
    }
  }
}

void checkDefaults(std::shared_ptr<AssemblerT> _assembler, FieldID _fields) {
  if (0 != (FieldID::DISTANCE & _fields)) {
    REQUIRE(_assembler->separation_distance() == Approx(100.0));
  }
  if (0 != (FieldID::SECONDS & _fields)) {
    REQUIRE(_assembler->separation_time() == tracktable::seconds(1200));
  }
  if (0 != (FieldID::MINIMUMPOINTS & _fields)) {
    REQUIRE(_assembler->minimum_trajectory_length() == 10);
  }
  if (0 != (FieldID::CLEANUPINTERVAL & _fields)) {
    REQUIRE(_assembler->cleanup_interval() == 10000);
  }
}
