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

#include "Portal.h"
#include "PortalPair.h"

#include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/Terrestrial.h>

#include <boost/timer/timer.hpp>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointReaderIteratorT = typename PointReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
The portal example takes trajectory data and attempts to find origin/destination
pairs. It breaks the USA into a grid, identifies what cells are populated by trajectories
and then refines the grid based on desired parameters. Each level of 'depth' is an
additional layer of refinement of the original grid. Each level is divided into
'bin-count' sections in both longitude and latitude. So each the number of cells:

cells = 12*5*bins^(2+depth)

empty cells are dropped but a cell is only empty if no trajectories pass through it

The portal example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Using boost program options to take parameters from command lines(in addition to the factories)
    - Use of boost::geometry::intersects to test where trajectories overlap regions

Typical use:
    ./portal-- input=/data/flights.tsv --depth=5 --min-value=12 --min-seperation=10 --bin-count=2

Defaults assume a tab separated file formatted as :

OBJECTID TIMESTAMP LON LAT
--------------------------------------------------------------------------------)";

int main(int _argc, char* _argv[]) {
    constexpr auto timerFormat = "\u001b[30;1m %w seconds\u001b[0m\n";
    // Set log level to reduce unecessary output
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
    /** Boost program options using a variable map to tie everything together.
     * one parse will have a single variable map. We need to let the factories know
     * about this variable map so they can pull information out of it */
    auto vm = std::make_shared<boost::program_options::variables_map>();
    readerFactory.setVariables(vm);
    assemblerFactory.setVariables(vm);

    // Portal specific configuration
    auto seperationDistance = 10.0;
    auto depth = 5u;
    auto binSize = 2u;
    auto minValue = 16u;
    boost::program_options::options_description portalOptions("Portals");
    // clang-format off
    portalOptions.add_options()
        ("portal-sep", bpo::value(&seperationDistance)->default_value(10), "Set minimum portal separation distance (in lat-lon)")
        ("depth", bpo::value(&depth)->default_value(5), "Set depth for portal decomposition")
        ("bin-count", bpo::value(&binSize)->default_value(2), "Portal chopping factor (default is 2)")
        ("min-value", bpo::value(&minValue)->default_value(16), "Minumum number of portal pairs (default is 16)")
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

    // Create Point Reader and assembler
    auto pointReader = readerFactory.createPointReader();
    auto assembler = assemblerFactory.createAssembler(pointReader);

    std::vector<std::shared_ptr<TrajectoryT>> trajectories = {};
    // This block exists for easy timing of trajectory assembling using the boost auto timer
    // Note that all feedback to the user is done on std::cerr, this allows us to only
    // put desired results into std::cout, this make processing output easier.
    {
        std::cerr << "Assemble Trajectories" << std::endl;
        boost::timer::auto_cpu_timer assembleTimer(std::cerr, timerFormat);
        auto count = 0u;
        std::cerr << std::right;
        for (auto tIter = assembler->begin(); tIter != assembler->end(); ++tIter) {
            if (tracktable::length(*tIter) < 100) {
                continue;
            }
            std::cerr << "\b\b\b\b\b\b\b\b\b\b" << std::setw(10)  // Using backspaces for in place counter
                      << count++;
            trajectories.push_back(std::make_shared<TrajectoryT>(*tIter));
        }
        std::cerr << std::left << "\nStarting with " << trajectories.size() << " trajectories" << std::endl;
    }

    // Create box for the USA
    PointT lowerLeft(-125.0, 25.0);  // lower left of USA
    PointT upperRight(-65.0, 50.0);  // upper right of USA
    auto USA = std::make_shared<Portal>(boost::geometry::model::box<PointT>(lowerLeft, upperRight));
    USA->level = 0;
    PairHeap pairs;
    pairs.minimumSeperation = seperationDistance;
    pairs.minimumValue = minValue;
    pairs.depth = depth;
    pairs.xDivisions = binSize;
    pairs.yDivisions = binSize;
    {
        std::cerr << "Initializing Pair Heap" << std::endl;
        boost::timer::auto_cpu_timer initializeTimer(std::cerr, timerFormat);
        pairs.initialize(trajectories, USA);
    }
    {
        std::cerr << "Finding Portals" << std::endl;
        boost::timer::auto_cpu_timer findTimer(std::cerr, timerFormat);
        pairs.find_portals();
    }
    return 0;
}