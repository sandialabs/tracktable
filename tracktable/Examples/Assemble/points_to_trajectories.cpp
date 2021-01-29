/*
 * Copyright (c) 2014-2021 National Technology and Engineering
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

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>

#include <tracktable/Analysis/AssembleTrajectories.h>

#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Terrestrial.h>

#include <tracktable/RW/TrajectoryWriter.h>
#include <tracktable/RW/PointReader.h>

#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/ShadowedDeclaration.h>
#include <boost/program_options.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

#include <algorithm>

#include "PairArgument.h"

typedef tracktable::string_vector_type string_vector_type;
typedef std::pair<tracktable::string_type, std::size_t> field_assignment_type;


// A helper function to simplify the main part.
template<class T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& v)
{
  std::copy(v.begin(), v.end(), std::ostream_iterator<T>(os, " "));
  return os;
}


struct CommandLineOptions
{
  tracktable::string_type InputFilename;
  tracktable::string_type OutputFilename;
  tracktable::string_type Domain;
  tracktable::string_type FieldDelimiter;
  double      SeparationDistance;
  double      SeparationSeconds;
  std::size_t ObjectIdColumn;
  std::size_t TimestampColumn;
  std::size_t FirstCoordinateColumn;
  std::size_t SecondCoordinateColumn;
  std::size_t MinimumNumPoints;
  std::vector<field_assignment_type> RealFields;
  std::vector<field_assignment_type> TimestampFields;
  std::vector<field_assignment_type> StringFields;
};


CommandLineOptions parse_command_line(int argc, char* argv[])
{
  CommandLineOptions result;

  namespace bpo = boost::program_options;
  bpo::options_description switch_options("Allowed Options");
  switch_options.add_options()
    ("help", "Produce help message")
    ("separation-distance", bpo::value<double>(&result.SeparationDistance)->default_value(100), "Set maximum separation distance for trajectory points")
    ("separation-seconds", bpo::value<double>(&result.SeparationSeconds)->default_value(1200), "Set maximum separation time (in seconds) for trajectory points")
    ("domain", bpo::value<tracktable::string_type>(&result.Domain)->default_value("terrestrial"), "Set point domain ('terrestrial' or 'cartesian2d')")
    ("input", bpo::value<tracktable::string_type>(&result.InputFilename)->default_value("-"), "Filename for input (use '-' for standard input)")
    ("output", bpo::value<tracktable::string_type>(&result.OutputFilename)->default_value("-"), "Filename for output (use '-' for standard output)")
    ("real-field", multiple_tokens_value<string_vector_type>(2, 2), "Field name and column number for a real-valued point field")
    ("string-field", multiple_tokens_value<string_vector_type>(2, 2), "Field name and column number for a string point field")
    ("timestamp-field", multiple_tokens_value<string_vector_type>(2, 2), "Field name and column number for a timestamp point field")
    ("object-id-column", bpo::value<std::size_t>(&result.ObjectIdColumn)->default_value(0), "Column containing object ID for points")
    ("timestamp-column", bpo::value<std::size_t>(&result.TimestampColumn)->default_value(1), "Column containing timestamp for points")
    ("x-column", bpo::value<std::size_t>(&result.FirstCoordinateColumn)->default_value(2), "Column containing X / longitude coordinate")
    ("y-column", bpo::value<std::size_t>(&result.SecondCoordinateColumn)->default_value(3), "Column containing Y / latitude coordinate")
    ("delimiter", bpo::value<tracktable::string_type>(&result.FieldDelimiter)->default_value(","), "Delimiter for fields in input file")
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
    std::cout << switch_options << "\n";
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
      result.StringFields.push_back(assignment);
      }
    }

  if (result.FieldDelimiter == "tab")
    {
    result.FieldDelimiter = "\t";
    }

  return result;

}

// ----------------------------------------------------------------------

template<typename trajectory_type>
void build_trajectories(CommandLineOptions const& options)
{
  typedef typename trajectory_type::point_type point_type;
  typedef tracktable::PointReader<point_type> point_reader_type;
  typedef tracktable::AssembleTrajectories<trajectory_type, typename point_reader_type::iterator> assembler_type;
  typedef tracktable::TrajectoryWriter trajectory_writer_type;


  point_reader_type point_reader;
  trajectory_writer_type trajectory_writer;
  std::ifstream infile;
  std::ofstream outfile;

  if (options.InputFilename == "-")
    {
    point_reader.set_input(std::cin);
    }
  else
    {
    infile.open(options.InputFilename.c_str());
    if (!infile)
      {
      std::cerr << "ERROR: Cannot open file "
                << options.InputFilename
                << " for input.\n";
      exit(1);
      }

    point_reader.set_input(infile);
    }

  if (options.OutputFilename == "-")
    {
    trajectory_writer.set_output(std::cout);
    }
  else
    {
    outfile.open(options.OutputFilename.c_str());
    if (!outfile)
      {
      std::cerr << "ERROR: Cannot open file "
                << options.OutputFilename
                << " for output.\n";
      exit(1);
      }
    trajectory_writer.set_output(outfile);
    }

  point_reader.set_object_id_column(boost::numeric_cast<int>(options.ObjectIdColumn));
  point_reader.set_timestamp_column(boost::numeric_cast<int>(options.TimestampColumn));
  point_reader.set_x_column(boost::numeric_cast<int>(options.FirstCoordinateColumn));
  point_reader.set_y_column(boost::numeric_cast<int>(options.SecondCoordinateColumn));
  point_reader.set_field_delimiter(options.FieldDelimiter);

  for (typename std::vector<field_assignment_type>::const_iterator iter = options.RealFields.begin();
       iter != options.RealFields.end();
       ++iter)
    {
    point_reader.set_real_field_column((*iter).first, boost::numeric_cast<int>((*iter).second));
    }

  for (typename std::vector<field_assignment_type>::const_iterator iter = options.StringFields.begin();
       iter != options.StringFields.end();
       ++iter)
    {
    point_reader.set_string_field_column((*iter).first, boost::numeric_cast<int>((*iter).second));
    }

  for (typename std::vector<field_assignment_type>::const_iterator iter = options.TimestampFields.begin();
       iter != options.TimestampFields.end();
       ++iter)
    {
    point_reader.set_time_field_column((*iter).first, boost::numeric_cast<int>((*iter).second));
    }

  assembler_type trajectory_assembler(point_reader.begin(), point_reader.end());
  trajectory_assembler.set_separation_distance(options.SeparationDistance);
  trajectory_assembler.set_separation_time(tracktable::seconds(options.SeparationSeconds));
  trajectory_assembler.set_minimum_trajectory_length(options.MinimumNumPoints);

  trajectory_writer.write(trajectory_assembler.begin(), trajectory_assembler.end());

}

// ----------------------------------------------------------------------


int main(int argc, char* argv[])
{
  CommandLineOptions options = parse_command_line(argc, argv);

  if (options.Domain == "terrestrial")
    {
    build_trajectories<tracktable::domain::terrestrial::trajectory_type>(options);
    }
  else if (options.Domain == "cartesian2d")
    {
    build_trajectories<tracktable::domain::cartesian2d::trajectory_type>(options);
    }
  else
    {
    std::cerr << "ERROR: Unsupported point domain '"
              << options.Domain << "'\n";
    return 1;
    }


  return 0;
}
