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
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>

#include <tracktable/ThirdParty/catch2.hpp>

// Bitfield enum for testing multiple fields at a time
enum FieldID {
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
  ALL = FIELDS | COLUMNS | DELIMITER | INPUT
};


using tracktable::PointReaderFromCommandLine;
// Aliases for readability
using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = TrajectoryT::point_type;
using ReaderT = tracktable::PointReader<PointT>;

// Convenience functions for code reuse
void checkColumnValue(std::shared_ptr<ReaderT> _reader, FieldID _id, size_t _val);
void checkDefaults(std::shared_ptr<ReaderT> _reader, FieldID _fields);
void checkColumnOption(PointReaderFromCommandLine<PointT>& _factory, std::string _optionString, size_t _pos,
                       FieldID _id);

SCENARIO("Creating Point Reader", "[PointReaderFromCommandLine]") {
  std::ofstream testfile("onepoint.txt");
  testfile << "A7067\t2013-07-10 00:00:00\t-112.483\t51.3333\t16500\n";
  testfile.close();
  GIVEN("Unititialized Factory") {
    PointReaderFromCommandLine<PointT> factory;
    WHEN("Stdin contains onepoint.txt") {
      std::ifstream in("onepoint.txt");
      std::streambuf* cinbuf = std::cin.rdbuf();  // save old buf
      std::cin.rdbuf(in.rdbuf());                 // redirect std::cin to in.txt!
      WHEN("create is called before parse") {
        THEN("a runtime error is thrown") {
          REQUIRE_THROWS_WITH(factory.createPointReader(), "Create Called With No Variable Map");
        }
      }
      WHEN("command line is empty") {
        int ARGC = 1;
        char* ARGV[] = {(char*)"exec", NULL};
        AND_WHEN("command line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          AND_WHEN("reader is created") {
            auto reader = factory.createPointReader();
            THEN("Everything is default;No altitude field should exist") {
              checkDefaults(reader, FieldID::ALL);
              REQUIRE_FALSE(reader->has_real_field_column("Altitude"));
            }
          }
        }
      }
      checkColumnOption(factory, "--x-column=42", 42, FieldID::XCOLUMN);
      checkColumnOption(factory, "--y-column=43", 43, FieldID::YCOLUMN);
      checkColumnOption(factory, "--object-id-column=44", 44, FieldID::OBJECTIDCOLUMN);
      checkColumnOption(factory, "--timestamp-column=45", 45, FieldID::TIMESTAMPCOLUMN);
      WHEN("args: --delimiter='$'") {
        int ARGC = 2;
        char* ARGV[3]{(char*)"exec", (char*)"--delimiter=$", nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("reader is created") {
            auto reader = factory.createPointReader();
            THEN("delimiter set to '$'; Rest are default") {
              REQUIRE(reader->field_delimiter() == "$");
              checkDefaults(reader, FieldID(~FieldID::DELIMITER));
            }
          }
        }
      }

      WHEN("args: --x-column=42 --y-column=43 --object-id-column=44 --timestamp-column=45 --delimiter=$") {
        int ARGC = 6;
        char* ARGV[] = {(char*)"exec",
                        (char*)"--x-column=42",
                        (char*)"--y-column=43",
                        (char*)"--object-id-column=44",
                        (char*)"--timestamp-column=45",
                        (char*)"--delimiter=$",
                        nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("reader is created") {
            auto reader = factory.createPointReader();
            THEN("Collumns are set;Rest are default") {
              checkColumnValue(reader, FieldID::XCOLUMN, 42);
              checkColumnValue(reader, FieldID::YCOLUMN, 43);
              checkColumnValue(reader, FieldID::OBJECTIDCOLUMN, 44);
              checkColumnValue(reader, FieldID::TIMESTAMPCOLUMN, 45);
              REQUIRE(reader->field_delimiter() == "$");
              checkDefaults(reader, FieldID(~(FieldID::COLUMNS | FieldID::DELIMITER)));
            }
          }
        }
      }
      WHEN("args: --real-field=Altitude 9") {
        int ARGC = 3;
        char* ARGV[] = {(char*)"exec", (char*)"--real-field=Altitude", (char*)"9", nullptr};
        WHEN("Command Line is parsed") {
          factory.parseCommandLine(ARGC, ARGV);
          WHEN("reader is created") {
            auto reader = factory.createPointReader();
            THEN("Real Field exist;Rest are default") {
              REQUIRE(reader->has_real_field_column("Altitude"));
              checkDefaults(reader, FieldID(~FieldID::REALFIELD));
            }
          }
        }
      }
      std::cin.rdbuf(cinbuf);
      in.close();
    }
  }
}

void checkColumnValue(std::shared_ptr<ReaderT> _reader, FieldID _id, size_t _val) {
  if (0 != (FieldID::OBJECTIDCOLUMN & _id)) {
    REQUIRE(_reader->object_id_column() == _val);
  } else if (0 != (FieldID::TIMESTAMPCOLUMN & _id)) {
    REQUIRE(_reader->timestamp_column() == _val);
  } else if (0 != (FieldID::XCOLUMN & _id)) {
    REQUIRE(_reader->x_column() == _val);
  } else if (0 != (FieldID::YCOLUMN & _id)) {
    REQUIRE(_reader->y_column() == _val);
  }
}

void checkDefaults(std::shared_ptr<ReaderT> _reader, FieldID _fields) {
  if (0 != (FieldID::OBJECTIDCOLUMN & _fields)) {
    REQUIRE(_reader->object_id_column() == 0);
  }
  if (0 != (FieldID::TIMESTAMPCOLUMN & _fields)) {
    REQUIRE(_reader->timestamp_column() == 1);
  }
  if (0 != (FieldID::XCOLUMN & _fields)) {
    REQUIRE(_reader->x_column() == 2);
  }
  if (0 != (FieldID::YCOLUMN & _fields)) {
    REQUIRE(_reader->y_column() == 3);
  }
  if (0 != (FieldID::DELIMITER & _fields)) {
    REQUIRE(_reader->field_delimiter() == "\t");
  }
  if (0 != (FieldID::INPUT & _fields)) {
    REQUIRE(&(_reader->input()) == &std::cin);
  }
  if (0 != (FieldID::REALFIELD & _fields)) {
  }
  if (0 != (FieldID::STRINGFIELD & _fields)) {
  }
  if (0 != (FieldID::TSFIELD & _fields)) {
  }
}

void checkColumnOption(PointReaderFromCommandLine<PointT>& _factory, std::string _optionString, size_t _pos,
                       FieldID _id) {
  int ARGC = 2;
  char* ARGV[3]{(char*)"exec", nullptr, nullptr};
  ARGV[1] = const_cast<char*>(_optionString.c_str());
  WHEN("args: " + _optionString) {
    WHEN("Command Line is parsed") {
      _factory.parseCommandLine(ARGC, ARGV);
      WHEN("reader is created") {
        auto reader = _factory.createPointReader();
        THEN(std::string("column set to ") << _pos << "; Rest are default") {
          checkColumnValue(reader, _id, _pos);
          checkDefaults(reader, FieldID(~_id));
        }
      }
    }
  }
}
