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

#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/RW/PointWriter.h>

#include <boost/iterator/filter_iterator.hpp>
#include <boost/timer/timer.hpp>

#include <fstream>
#include <string>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointWriterT = tracktable::PointWriter;
using PointReaderIteratorT = typename PointReaderT::iterator;

namespace bpo = boost::program_options;

/** Function object
 * Created with two timestamps
 * Callable with a point argument
 * returns true if the point is between the two timestamps
 **/
template <typename pointT>
struct DateBetween {
 public:
  DateBetween(tracktable::Timestamp const& _startTime, tracktable::Timestamp const& _endTime)
      : startTime(_startTime), endTime(_endTime) {}
  DateBetween() = delete;

  bool operator()(pointT const& _point)  // const& not copied (reference), not alterable
  {
    return (_point.timestamp() >= this->startTime && _point.timestamp() <= this->endTime);
  }

 private:
  const tracktable::Timestamp startTime;
  const tracktable::Timestamp endTime;
};

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
This program takes an input file of points and filters for points that fall within
two given timestamps

The filter_time example demonstrates:
    - Using command line factories to read points
    - Using 'required' options
    - Using a function object to filter those points
    - Using a point writer to output those points.

Typical use:
    ./filter_time --input=/data/flights.tsv --output=/results/filtered.tsv --start=2013-07-10-00:00:05 --stop=2013-07-10-00:01:05

Defaults assume a tab separated points file formatted as :

OBJECTID TIMESTAMP LON LAT
--------------------------------------------------------------------------------)";

int main(int _argc, char* _argv[]) {
  // Set log level to reduce unecessary output
  tracktable::set_log_level(tracktable::log::info);
  // Create a basic command line option with boost
  boost::program_options::options_description commandLineOptions("Options");
  commandLineOptions.add_options()("help", "Print help");

  // Create command line factories
  tracktable::PointReaderFromCommandLine<PointT> readerFactory;
  // Add options from the factories
  readerFactory.addOptions(commandLineOptions);

  // And a command line option for output
  commandLineOptions.add_options()("output", bpo::value<std::string>()->default_value("-"),
                                   "file to write to (use '-' for stdout), overridden by 'separate-kmls'");

  /** Boost program options using a variable map to tie everything together.
   * one parse will have a single variable map. We need to let the factories know
   * about this variable map so they can pull information out of it */
  auto vm = std::make_shared<boost::program_options::variables_map>();
  readerFactory.setVariables(vm);

  // And a command line option for output
  commandLineOptions.add_options()("output", bpo::value<std::string>()->default_value("-"),
                                   "file to write to (use '-' for stdout), overridden by 'separate-kmls'");

  // Add command line option for start and stop timestamps, noticed they are 'required'
  // clang-format off
  std::string startString("");
  std::string stopString("");
  commandLineOptions.add_options()
      ("start", bpo::value<std::string>(&startString)->required()," timestamp to start at")\
      ("stop", bpo::value<std::string>(&stopString)->required(), "timestamp to stop at")
  ;
  // clang-format on
  // Parse the command lines, don't forget the 'notify' after
  try {
    // We use this try/catch to automatically display help when an unknown option is used
    boost::program_options::store(
        boost::program_options::command_line_parser(_argc, _argv).options(commandLineOptions).run(), *vm);
    boost::program_options::notify(*vm);
  } catch (boost::program_options::error e) {
    std::cerr << e.what();
    std::cerr << helpmsg << "\n\n";
    std::cerr << commandLineOptions << std::endl;
    return 1;
  }
  /** Parsing will give an error of an incorrect option is used, but it won't
   * display the help unless we tell it too */
  if (vm->count("help") != 0) {
    std::cerr << helpmsg << "\n\n";
    std::cerr << commandLineOptions << std::endl;
    return 1;
  }
  // Attempt to parse time from the command line
  tracktable::Timestamp startTime(tracktable::time_from_string(startString));
  tracktable::Timestamp endTime(tracktable::time_from_string(stopString));

  // Create Point Reader
  auto pointReader = readerFactory.createPointReader();

  // Using an oldstyle pointer here in order to be able to swap out for file if needed
  std::ostream* out = &std::cout;

  // Check the output file argument, if it is default '-', then use std::cout, otherwise try to open a file
  auto filename = (*vm)["output"].as<std::string>();
  if ("-" != filename) {
    out = new std::ofstream(filename);
    if (!out->good()) {
      std::cerr << "\n\nCould not open " << filename << std::endl;
      return 1;
    }
    std::cerr << "Writing to: " << filename << std::endl;
  } else {
    std::cerr << "Writing to: standard out" << std::endl;
  }
  PointWriterT pointWriter;
  // Match input format as much as possible
  pointWriter.set_field_delimiter(pointReader->field_delimiter());
  pointWriter.set_timestamp_format(pointReader->timestamp_format());
  pointWriter.set_null_value(pointReader->null_value());

  pointWriter.set_output(*out);

  std::cerr << " Filtered to include only updates between " << startString << " and " << stopString << "."
            << std::endl;

  DateBetween<PointT> dateFilter(startTime, endTime);

  // Use Boost filter iterator to process points as a stream and skip those that
  // don't match our filter criteria (between two timestamps)
  using FilterIteratorT = boost::filter_iterator<DateBetween<PointT>, PointReaderIteratorT>;
  FilterIteratorT start(dateFilter, pointReader->begin());
  FilterIteratorT finish(dateFilter, pointReader->end());
  {
    boost::timer::auto_cpu_timer filterTimer(std::cerr);
    pointWriter.write(start, finish);
  }
  std::cerr << "Done" << std::endl;
  return 0;
}
