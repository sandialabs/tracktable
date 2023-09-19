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

#include "Predict.h"

#include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>

#include <boost/timer/timer.hpp>

#include <string>
#include <vector>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointReaderIteratorT = typename PointReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;

bool has_tail_number(const TrajectoryT &_trajectory);
bool has_destination(const TrajectoryT &_trajectory);

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
This example demonstrates using feature vectors to measure similarities between
trajectories via an Rtree

The predict example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Using boost program options to take parameters from command lines(in addition to the factories)
    - Conditioning trajectories based on length and objectid
    - Using boost rtree to locate similar trajectories based on cartesian distance in feature space

Typical use: '--string-field=dest x' is required

    ./predict --input=/data/SampleASDI.csv --delimiter=, --string-field=dest 30 --num-samples=10

--------------------------------------------------------------------------------)";
int main(int _argc, char *_argv[]) {
    auto numSamples = 10u;

    // Set log level to reduce unecessary output
    tracktable::set_log_level(tracktable::log::info);
    // Create a basic command line option with boost
    bpo::options_description commandLineOptions("Options");
    // clang-format off
    commandLineOptions.add_options()
      ("help", "Print help")
      ("num-samples", bpo::value(&numSamples)->default_value(10),
        "Number of samples")
    ;
    // clang-format on

    // Create command line factories
    tracktable::PointReaderFromCommandLine<PointT> readerFactory;
    tracktable::AssemblerFromCommandLine<TrajectoryT> assemblerFactory;
    // Add options from the factories
    readerFactory.addOptions(commandLineOptions);
    assemblerFactory.addOptions(commandLineOptions);

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

    std::vector<std::shared_ptr<TrajectoryT>> trajectories = {};
    // This block exists for easy timing of trajectory assembling using the boost auto timer
    // Note that all feedback to the user is done on std::cerr, this allows us to only
    // put desired results into std::cout, this make processing output easier.
    {
        std::cerr << "Assemble Trajectories" << std::endl;
        boost::timer::auto_cpu_timer timer3(std::cerr);
        auto count = 0u;
        std::cerr << std::right;
        for (auto tIter = assembler->begin(); tIter != assembler->end(); ++tIter) {
            if (has_tail_number(*tIter)) {  // Skip tail number flights
                continue;
            }
            if (!has_destination(*tIter)) {  // Skip flights without destination or errors
                continue;
            }
            std::cerr << "\b\b\b\b\b\b\b\b\b\b" << std::setw(10)  // Using backspaces for in place counter
                      << count++;
            trajectories.push_back(std::make_shared<TrajectoryT>(*tIter));
        }
        std::cerr << std::left << "\nStarting with " << trajectories.size() << " trajectories" << std::endl;
    }

    // This routine does a prediction based on destination airport
    Predict(trajectories, numSamples);

    return 0;
}

bool has_tail_number(const TrajectoryT &_trajectory) {
    auto s = _trajectory.object_id();
    return !((s[0] != 'N') || (s[1] < '0') || (s[1] > '9'));
}

bool has_destination(const TrajectoryT &_trajectory) {
    return !_trajectory.front().string_property("dest").empty() &&
           (_trajectory.front().string_property("dest") == _trajectory.back().string_property("dest"));
}
