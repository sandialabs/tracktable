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
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/IO/PointReader.h>

#include <tracktable/ThirdParty/catch2.hpp>

// Bitfield enum for testing multiple fields at a time
enum AssemblerFieldID {
  DISTANCE = 1,
  SECONDS = 1 << 1,
  MINIMUMPOINTS = 1 << 2,
  CLEANUPINTERVAL = 1 << 3,
  AFALL = DISTANCE | SECONDS | MINIMUMPOINTS | CLEANUPINTERVAL
};

enum ReaderFieldID {
  OBJECTIDCOLUMN = 1,
  TIMESTAMPCOLUMN = 1 << 1,
  XCOLUMN = 1 << 2,
  YCOLUMN = 1 << 3,
  DELIMITER = 1 << 4,
  REALFIELD = 1 << 5,
  STRINGFIELD = 1 << 6,
  TSFIELD = 1 << 7,
  INPUT = 1 << 8,
  FIELDS = REALFIELD | STRINGFIELD | TSFIELD,
  COLUMNS = OBJECTIDCOLUMN | TIMESTAMPCOLUMN | XCOLUMN | YCOLUMN,
  RFALL = FIELDS | COLUMNS | DELIMITER | INPUT
};

using tracktable::AssemblerFromCommandLine;
using tracktable::PointReaderFromCommandLine;

// Aliases for readability
using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = TrajectoryT::point_type;
using ReaderT = tracktable::PointReader<PointT>;
using ReaderIteratorT = typename ReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, ReaderIteratorT>;

namespace bpo = boost::program_options;

// Convenience functions for code reuse
void checkDefaults(std::shared_ptr<AssemblerT> _assembler, AssemblerFieldID _fields);
void checkDefaults(std::shared_ptr<ReaderT> _reader, ReaderFieldID _fields);

SCENARIO("Creating Pointer Reader and Assembler", "[PointReaderFromCommandLine][AssemblerFromCommandLine]") {
  std::ofstream testfile("onepoint.txt");
  testfile << "A7067\t2013-07-10 00:00:00\t-112.483\t51.3333\t16500\n";
  testfile.close();
  GIVEN("Unititialized Factories") {
    AssemblerFromCommandLine<TrajectoryT> assemblerFactory;
    PointReaderFromCommandLine<PointT> readerFactory;
    WHEN("Stdin contains onepoint.txt") {
      std::ifstream in("onepoint.txt");
      std::streambuf* cinbuf = std::cin.rdbuf();  // save old buf
      std::cin.rdbuf(in.rdbuf());                 // redirect std::cin to in.txt!
      AND_WHEN("Options are combined") {
        auto combinedOptions = std::make_shared<bpo::options_description>("Available Options");
        readerFactory.addOptions(combinedOptions);
        assemblerFactory.addOptions(combinedOptions);
        auto vm = std::make_shared<bpo::variables_map>();
        readerFactory.setVariables(vm);
        assemblerFactory.setVariables(vm);
        WHEN("command line is empty") {
          int ARGC = 1;
          char* ARGV[] = {(char*)"exec", NULL};
          WHEN("command line is parsed") {
            bpo::store(bpo::command_line_parser(ARGC, ARGV).options(*combinedOptions).run(), *vm);
            bpo::notify(*vm);
            WHEN("reader is created") {
              auto reader = readerFactory.createPointReader();
              WHEN("assembler is created") {
                auto assembler = assemblerFactory.createAssembler(reader);
                THEN("Everything is default and No altitude field should exist ") {
                  checkDefaults(reader, ReaderFieldID::RFALL);
                  checkDefaults(assembler, AssemblerFieldID::AFALL);
                  REQUIRE_FALSE(reader->has_real_field_column("Altitude"));
                }
              }
            }
          }
        }
        // Step 1 in checking that setting options on one does not impact other
        WHEN("args: --separation-distance=42") {
          int ARGC = 2;
          char* ARGV[3]{(char*)"exec", (char*)"--separation-distance=42", nullptr};
          WHEN("command line is parsed") {
            bpo::store(bpo::command_line_parser(ARGC, ARGV).options(*combinedOptions).run(), *vm);
            bpo::notify(*vm);
            WHEN("reader is created") {
              auto reader = readerFactory.createPointReader();
              WHEN("assembler is created") {
                auto assembler = assemblerFactory.createAssembler(reader);
                THEN("Seperation distance on assembler is 42, Everything else is default") {
                  REQUIRE(assembler->separation_distance() == Approx(42.0));
                  checkDefaults(reader, ReaderFieldID::RFALL);
                  checkDefaults(assembler, AssemblerFieldID(~AssemblerFieldID::DISTANCE));
                }
              }
            }
          }
        }
        // Step 2 in checking that setting options on one does not impact other
        WHEN("args: --delimiter='$'") {
          int ARGC = 2;
          char* ARGV[3]{(char*)"exec", (char*)"--delimiter=$", nullptr};
          WHEN("Command Line is parsed") {
            bpo::store(bpo::command_line_parser(ARGC, ARGV).options(*combinedOptions).run(), *vm);
            bpo::notify(*vm);
            WHEN("reader is created") {
              auto reader = readerFactory.createPointReader();
              WHEN("assembler is created") {
                auto assembler = assemblerFactory.createAssembler(reader);
                THEN("Delimiter on point reader is '$' and everything else is default") {
                  REQUIRE(reader->field_delimiter() == "$");
                  checkDefaults(reader, ReaderFieldID(~ReaderFieldID::DELIMITER));
                  checkDefaults(assembler, AssemblerFieldID::AFALL);
                }
              }
            }
          }
        }
      }
      in.close();
    }
  }
}

void checkDefaults(std::shared_ptr<AssemblerT> _assembler, AssemblerFieldID _fields) {
  if (0 != (AssemblerFieldID::DISTANCE & _fields)) {
    REQUIRE(_assembler->separation_distance() == Approx(100.0));
  }
  if (0 != (AssemblerFieldID::SECONDS & _fields)) {
    REQUIRE(_assembler->separation_time() == tracktable::seconds(1200));
  }
  if (0 != (AssemblerFieldID::MINIMUMPOINTS & _fields)) {
    REQUIRE(_assembler->minimum_trajectory_length() == 10);
  }
  if (0 != (AssemblerFieldID::CLEANUPINTERVAL & _fields)) {
    REQUIRE(_assembler->cleanup_interval() == 10000);
  }
}

void checkDefaults(std::shared_ptr<ReaderT> _reader, ReaderFieldID _fields) {
  if (0 != (ReaderFieldID::OBJECTIDCOLUMN & _fields)) {
    REQUIRE(_reader->object_id_column() == 0);
  }
  if (0 != (ReaderFieldID::TIMESTAMPCOLUMN & _fields)) {
    REQUIRE(_reader->timestamp_column() == 1);
  }
  if (0 != (ReaderFieldID::XCOLUMN & _fields)) {
    REQUIRE(_reader->x_column() == 2);
  }
  if (0 != (ReaderFieldID::YCOLUMN & _fields)) {
    REQUIRE(_reader->y_column() == 3);
  }
  if (0 != (ReaderFieldID::DELIMITER & _fields)) {
    REQUIRE(_reader->field_delimiter() == "\t");
  }
  if (0 != (ReaderFieldID::INPUT & _fields)) {
    REQUIRE(&(_reader->input()) == &std::cin);
  }
  if (0 != (ReaderFieldID::REALFIELD & _fields)) {
  }
  if (0 != (ReaderFieldID::STRINGFIELD & _fields)) {
  }
  if (0 != (ReaderFieldID::TSFIELD & _fields)) {
  }
}