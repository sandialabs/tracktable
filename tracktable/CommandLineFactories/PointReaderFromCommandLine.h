#ifndef PointReaderFromCommandLine_h
#define PointReaderFromCommandLine_h
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
#include "CommandLineFactory.h"

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/IO/PointReader.h>

#include <fstream>

namespace bpo = boost::program_options;
namespace tracktable {

template <typename PointT>
class PointReaderFromCommandLine : public CommandLineFactory {
 protected:
  using ThisType = PointReaderFromCommandLine<PointT>;
  using BaseType = CommandLineFactory;

 private:
  using StringType = tracktable::string_type;
  using StringVectorType = tracktable::string_vector_type;
  using FieldAssignmentType = std::pair<StringType, size_t>;

 public:
  struct PointReaderSettings : public CommandLineSettings {
    StringType FieldDelimiter;
    size_t ObjectIdColumn = 0;
    size_t TimestampColumn = 0;
    size_t FirstCoordinateColumn = 0;
    size_t SecondCoordinateColumn = 0;
    std::vector<FieldAssignmentType> RealFields;
    std::vector<FieldAssignmentType> TimestampFields;
    std::vector<FieldAssignmentType> StringFields;
    void print(std::ostream& _o) {
      _o << "InputFilename: " << InputFilename << std::endl;
      _o << "FieldDelimiter: '" << FieldDelimiter << "'" << std::endl;
      _o << "ObjectIdColumn: " << ObjectIdColumn << std::endl;
      _o << "TimestampColumn: " << TimestampColumn << std::endl;
      _o << "FirstCoordinateColumn: " << FirstCoordinateColumn << std::endl;
      _o << "SecondCoordinateColumn: " << SecondCoordinateColumn << std::endl;
      _o << "RealFields: " << std::endl;
      for (auto& field : RealFields) {
        _o << "  " << field.first << ": " << field.second << std::endl;
      }
      _o << "TimestampFields: " << std::endl;
      for (auto& field : TimestampFields) {
        _o << "  " << field.first << ": " << field.second << std::endl;
      }
      _o << "StringFields: " << std::endl;
      for (auto& field : StringFields) {
        _o << "  " << field.first << ": " << field.second << std::endl;
      }
    }
  };

 private:
  void initializeSettings() override {}
  void processVariables() override {
    auto settings = std::static_pointer_cast<PointReaderSettings>(settingsPtr);
    if (0 != parsedVariables->count("real-field")) {
      StringVectorType field_args((*parsedVariables)["real-field"].template as<StringVectorType>());
      for (auto i = 0U; i < field_args.size(); i += 2) {
        FieldAssignmentType assignment(field_args[i], boost::lexical_cast<size_t>(field_args[i + 1]));
        settings->RealFields.push_back(assignment);
      }
    }

    if (0 != parsedVariables->count("string-field")) {
      StringVectorType field_args((*parsedVariables)["string-field"].template as<StringVectorType>());
      for (auto i = 0U; i < field_args.size(); i += 2) {
        FieldAssignmentType assignment(field_args[i], boost::lexical_cast<size_t>(field_args[i + 1]));
        settings->StringFields.push_back(assignment);
      }
    }

    if (0 != parsedVariables->count("timestamp-field")) {
      StringVectorType field_args((*parsedVariables)["timestamp-field"].template as<StringVectorType>());
      for (auto i = 0U; i < field_args.size(); i += 2) {
        FieldAssignmentType assignment(field_args[i], boost::lexical_cast<size_t>(field_args[i + 1]));
        settings->TimestampFields.push_back(assignment);
      }
    }
  }

 public:
  using BaseType::addOptions;
  void addOptions(bpo::options_description& _options) override {
    auto settings = std::static_pointer_cast<PointReaderSettings>(settingsPtr);
    // clang-format off
    bpo::options_description readerOptions("Point Reader");
    readerOptions.add_options()
    ("input",
      bpo::value<StringType>(&settings->InputFilename)->default_value("-"),
     "Filename for input (use '-' for standard input)")
    ("real-field",
      bpo::value<StringVectorType>()->multitoken(),
     "Field name and column number for a real-valued point field")
    ("string-field",
      bpo::value<StringVectorType>()->multitoken(),
     "Field name and column number for a string point field")
    ("timestamp-field",
      bpo::value<StringVectorType>()->multitoken(),
     "Field name and column number for a timestamp point field")
    ("object-id-column",
      bpo::value<size_t>(&settings->ObjectIdColumn)->default_value(0),
     "Column containing object ID for points")
    ("timestamp-column",
      bpo::value<size_t>(&settings->TimestampColumn)->default_value(1),
     "Column containing timestamp for points")
    ("x-column",
      bpo::value<size_t>(&settings->FirstCoordinateColumn)->default_value(2),
     "Column containing X / longitude coordinate")
    ("y-column",
      bpo::value<size_t>(&settings->SecondCoordinateColumn)->default_value(3),
     "Column containing Y / latitude coordinate")
    ("delimiter",
      bpo::value<StringType>(&settings->FieldDelimiter)->default_value("\t"),
     "Delimiter for fields in input file")
    ;
    _options.add(readerOptions);
    // clang-format on
  }
  PointReaderFromCommandLine() {
    settingsPtr = std::make_shared<PointReaderSettings>();
    addOptions(commandLineOptions);
    positionalCommandLineOptions->add("input", 1);
  }

  std::shared_ptr<tracktable::PointReader<PointT>> createPointReader() {
    if (nullptr == parsedVariables) {
      throw std::runtime_error("Create Called With No Variable Map");
    }
    processVariables();
    auto settings = std::static_pointer_cast<PointReaderSettings>(settingsPtr);
    // settings->print(std::cout);
    auto reader = std::make_shared<tracktable::PointReader<PointT>>();
    if (settings->InputFilename == "-") {
      reader->set_input(std::cin);
    } else {
      if (infile.is_open()) {
        throw std::runtime_error(
            "ERROR: Trying to create second point reader which is not supported at this time\n");
      }
      infile.open(settings->InputFilename.c_str());
      if (!infile.is_open()) {
        throw std::runtime_error("ERROR: Cannot open file " + settings->InputFilename + " for input.\n");
      }
      reader->set_input(infile);
    }
    reader->set_object_id_column(settings->ObjectIdColumn);
    reader->set_timestamp_column(settings->TimestampColumn);
    reader->set_x_column(settings->FirstCoordinateColumn);
    reader->set_y_column(settings->SecondCoordinateColumn);
    reader->set_field_delimiter(settings->FieldDelimiter);

    for (const auto& r : settings->RealFields) {
      reader->set_real_field_column(r.first, r.second);
    }

    for (const auto& s : settings->StringFields) {
      reader->set_string_field_column(s.first, s.second);
    }

    for (const auto& t : settings->TimestampFields) {
      reader->set_time_field_column(t.first, t.second);
    }
    return reader;
  }

  ~PointReaderFromCommandLine() {
    if (infile.is_open()) {
      infile.close();
    }
  }

 private:
  std::ifstream infile;
};

}  // namespace tracktable

#endif  // PointReaderFromCommandLine_h
