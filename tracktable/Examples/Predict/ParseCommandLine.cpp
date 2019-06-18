/*
 * Copyright (c) 2015-2017 National Technology and Engineering
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


/* Assemble points to make trajectories
 *
 * This process is the prerequisite for most of the analysis and
 * rendering that Tracktable can do.  By reading pre-assembled
 * trajectories we can save a lot of time when working with a data set
 * more than once.
 */

//#include <tracktable/Core/TracktableCommon.h>
//#include <tracktable/Core/CommonTypes.h>
//#include <tracktable/Core/Timestamp.h>

//#include <tracktable/Analysis/AssembleTrajectories.h>

//#include <tracktable/Domain/Cartesian2D.h>
//#include <tracktable/Domain/Terrestrial.h>

//#include <tracktable/IO/TrajectoryWriter.h>
//#include <tracktable/IO/PointReader.h>

//#include <boost/program_options.hpp>

#include <algorithm>

#include "CommandLineOptions.h"
#include "PairArgument.h"

CommandLineOptions ParseCommandLine(int argc, char* argv[])
{
  CommandLineOptions result;

  namespace bpo = boost::program_options;
  bpo::options_description switch_options("Allowed Options");
  switch_options.add_options()
    ("help", "Produce help message")
    ("separation-distance", bpo::value<double>(&result.SeparationDistance)->default_value(100), "Set maximum separation distance for trajectory points")
    ("separation-seconds", bpo::value<double>(&result.SeparationSeconds)->default_value(1200), "Set maximum separation time (in seconds) for trajectory points")
    ("num_samples", bpo::value<std::size_t>(&result.NumSamples)->default_value(10), "Number of samples")
    ("domain", bpo::value<tt_string_type>(&result.Domain)->default_value("cartesian2d"), "Set point domain ('terrestrial' or 'cartesian2d')")
    ("input", bpo::value<tt_string_type>(&result.InputFilename)->default_value("-"), "Filename for input (use '-' for standard input)")
    ("dest", bpo::value<tt_string_type>(&result.Destination)->default_value(""), "Destination")
    ("output", bpo::value<tt_string_type>(&result.OutputDirectory)->default_value("output"), "directory for output")
    ("real-field", multiple_tokens_value<string_vector_type>(2, 2), "Field name and column number for a real-valued point field")
    ("string-field", multiple_tokens_value<string_vector_type>(2, 2), "Field name and column number for a string point field")
    ("timestamp-field", multiple_tokens_value<string_vector_type>(2, 2), "Field name and column number for a timestamp point field")
    ("object-id-column", bpo::value<std::size_t>(&result.ObjectIdColumn)->default_value(0), "Column containing object ID for points")
    ("timestamp-column", bpo::value<std::size_t>(&result.TimestampColumn)->default_value(1), "Column containing timestamp for points")
    ("x-column", bpo::value<std::size_t>(&result.FirstCoordinateColumn)->default_value(2), "Column containing X / longitude coordinate")
    ("y-column", bpo::value<std::size_t>(&result.SecondCoordinateColumn)->default_value(3), "Column containing Y / latitude coordinate")
    ("delimiter", bpo::value<tt_string_type>(&result.FieldDelimiter)->default_value("\t"), "Delimiter for fields in input file")
    ("min-points", bpo::value<std::size_t>(&result.MinimumNumPoints)->default_value(10), "Trajectories shorter than this will be discarded")
    ;

  bpo::positional_options_description positional_options;
  positional_options.add("input", 1);
  positional_options.add("output", 1);

  bpo::variables_map retrieved_variables;
  bpo::store(bpo::command_line_parser(argc, argv)
             .options(switch_options)
             .positional(positional_options)
             .run(), retrieved_variables);
  bpo::notify(retrieved_variables);

  if (retrieved_variables.count("help"))
    {
//    std::cout << switch_options << "\n";
    exit(1);
    }

  // Parse out the field assignments
  if (retrieved_variables.count("real-field"))
    {
    string_vector_type field_args(retrieved_variables["real-field"].as<string_vector_type>());
    for (std::size_t i = 0; i < field_args.size(); i += 2)
      {
      field_assignment_type assignment( field_args[i],
                                        boost::lexical_cast<std::size_t>(field_args[i+1]) );
      result.RealFields.push_back(assignment);
      }
    }

  if (retrieved_variables.count("string-field"))
    {
    string_vector_type field_args(retrieved_variables["string-field"].as<string_vector_type>());
    for (std::size_t i = 0; i < field_args.size(); i += 2)
      {
      field_assignment_type assignment( field_args[i],
                                        boost::lexical_cast<std::size_t>(field_args[i+1]) );
      result.StringFields.push_back(assignment);
      }
    }

  if (retrieved_variables.count("timestamp-field"))
    {
    string_vector_type field_args(retrieved_variables["timestamp-field"].as<string_vector_type>());
    for (std::size_t i = 0; i < field_args.size(); i += 2)
      {
      field_assignment_type assignment( field_args[i],
                                        boost::lexical_cast<std::size_t>(field_args[i+1]) );
      result.TimestampFields.push_back(assignment);
      }
    }

  if (result.FieldDelimiter == "tab")
    {
    result.FieldDelimiter = "\t";
    }

  return result;

}
