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

#include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/RW/TrajectoryWriter.h>

#include <fstream>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointReaderIteratorT = typename PointReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
The assemble example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Writing trajectories to file for later use

Typical use:
    ./assemble --input=/data/flights.tsv --output=/data/flights.trj

Defaults assume a tab separated file formatted as :

OBJECTID TIMESTAMP LON LAT

Default output is standard out
--------------------------------------------------------------------------------)";

int main(int _argc, char* _argv[]) {
  //Set log level to reduce unecessary output
  tracktable::set_log_level(tracktable::log::info);
  // Create a basic command line option with boost
  boost::program_options::options_description commandLineOptions;
  commandLineOptions.add_options()("help", "Print help");

  // Create command line factories
  tracktable::PointReaderFromCommandLine<PointT> readerFactory;
  tracktable::AssemblerFromCommandLine<TrajectoryT> assemblerFactory;
  // Add options from the factories
  readerFactory.addOptions(commandLineOptions);
  assemblerFactory.addOptions(commandLineOptions);

  // And a command line option for output
  commandLineOptions.add_options()("output", bpo::value<std::string>()->default_value("-"),
                                   "file to write to (use '-' for stdout), overridden by 'separate-kmls'");

  /** Boost program options using a variable map to tie everything together.
   * one parse will have a single variable map. We need to let the factories know
   * about this variable map so they can pull information out of it */
  auto vm = std::make_shared<boost::program_options::variables_map>();
  readerFactory.setVariables(vm);
  assemblerFactory.setVariables(vm);

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

  // Create Point Reader and assembler
  auto pointReader = readerFactory.createPointReader();
  auto assembler = assemblerFactory.createAssembler(pointReader);

  // We default to standard out
  std::ostream* o = &std::cout;
  auto filename = (*vm)["output"].as<std::string>();
  std::cerr << "Writing to ";
  if ("-" != filename) {
    // we swap in a file if a filename is specified
    std::cerr << filename << std::endl;
    o = new std::ofstream(filename);
  } else {
    std::cerr << "standard out" << std::endl;
  }

  // trajectory writer with default options
  tracktable::TrajectoryWriter writer(*o);

  auto count = 0u;
  std::cerr << std::right;
  // We don't need to bother storing trajectories, we can just write them
  for (auto t = assembler->begin(); t != assembler->end(); ++t) {
    writer.write(*t);
    std::cerr << "\b\b\b\b\b\b\b\b\b\b" << std::setw(10)  // Using backspaces for in place counter
              << count++;
  }
  std::cerr << std::endl;
  return 0;
}
