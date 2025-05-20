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

#include "AssignHeadings.h"
#include "Mapping.h"
#include "TrackFilter.h"

#include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Core/Geometry.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/RW/KmlOut.h>

#include <boost/timer/timer.hpp>

#include <algorithm>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointReaderIteratorT = typename PointReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;
constexpr auto length = tracktable::length<TrajectoryT>;

using tracktable::kml;

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
The classify example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Using boost program options to take parameters from command lines(in addition to the factories)
    - Filtering trajectories on any combination of the following:
      - length
      - curvature
      - hull-gyration ratio
      - length ratio
      - hull-aspect ratio
      - straightness
      - number of turn arounds
    - A few different methods of applying these filters are demonstrated int he code
    - Writing trajectories as KML

Typical use:
    ./ classify-- input=/data/flights.tsv --min-turn-arounds=10 --output =/results/mappingflights.kml

Defaults assume a tab separated file formatted as :

OBJECTID TIMESTAMP LON LAT

Default output is standard out
--------------------------------------------------------------------------------)";

int main(int _argc, char* _argv[]) {
    tracktable::set_log_level(tracktable::log::info);
    boost::program_options::options_description commandLineOptions;
    commandLineOptions.add_options()("help", "Print help");
    boost::program_options::options_description classifyOptions("Classify");
    // clang-format off
    /** Here we manually add some filter options
    *     This is a syntax created by boost program options using some clever tricks.
    *     This is legal C++ but it should look weird to most users. */
    classifyOptions.add_options()
      ("assign-headings",
      "Assign headings to points")
      ("min-length",
        bpo::value<double>(), //We intentionally leave off default, this allows us to skip filtering if no value
      "minimum length of trajectory")
      ("max-length",
        bpo::value<double>(),
      "maximum length of trajectory")
      ("min-curvature",
        bpo::value<double>(),
      "minimum curvature of trajectory")
      ("max-curvature",
        bpo::value<double>(),
      "maximum curvature of trajectory")
    ;
    // clang-format on
    /** We can use the Trackfilter class to help us with the repetitive task of filtering
     *   We provide the TrackFilter with a lambda that corresponds to the 'ShouldKeep'
     *   scenario the filter. */
    MinMaxTrackFilter<double> hullGyrationFilter("hull-gyration-ratio", [](const TrajectoryT& _t) {
        return tracktable::convex_hull_area(_t) / tracktable::radius_of_gyration(_t);
    });
    hullGyrationFilter.addOptions(classifyOptions);

    MinMaxTrackFilter<double> lengthRatioFilter("length-ratio", [](const TrajectoryT& _t) {
        return tracktable::end_to_end_distance(_t) / tracktable::length(_t);
    });
    lengthRatioFilter.addOptions(classifyOptions);

    MinMaxTrackFilter<double> hullAspectRatioFilter("hull-aspect-ratio",
                                                    tracktable::convex_hull_aspect_ratio<TrajectoryT>);
    hullAspectRatioFilter.addOptions(classifyOptions);

    MinMaxTrackFilter<double> straightnessFilter("straightness", StraightFraction);
    straightnessFilter.addOptions(classifyOptions);

    MinMaxTrackFilter<unsigned int> turnAroundsFilter("turn-arounds", TurnArounds);
    turnAroundsFilter.addOptions(classifyOptions);

    commandLineOptions.add(classifyOptions);

    // Reader factories, which add lots of command line options
    tracktable::PointReaderFromCommandLine<PointT> readerFactory;
    tracktable::AssemblerFromCommandLine<TrajectoryT> assemblerFactory;
    readerFactory.addOptions(commandLineOptions);
    assemblerFactory.addOptions(commandLineOptions);

    // By creating separate program options objects, we are creating groups for the
    //   help menu.
    boost::program_options::options_description outputOptions("Output Options");
    // clang-format off
    // We manually add options for output
    outputOptions.add_options()
      ("no-output",
      "specifies no output is wanted")
      ("separate-kmls",
      "indicate whether to separate output to different kmls in [result-dir]")
      ("result-dir",
        bpo::value<std::string>()->default_value("result/"),
      "directory to store separate kmls")
      ("output",
        bpo::value<std::string>()->default_value("-"),
        "file to write to (use '-' for stdout), overridden by 'separate-kmls'"
      )
    ;
    // clang-format on
    commandLineOptions.add(outputOptions);

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

    std::vector<TrajectoryT> trajectories = {};
    // This block exists for easy timing of trajectory assembling using the boost auto timer
    // Note that all feedback to the user is done on std::cerr, this allows us to only
    // put desired results into std::cout, this make processing output easier.
    {
        std::cerr << "Assemble Trajectories" << std::endl;
        boost::timer::auto_cpu_timer timer3(std::cerr);
        auto count = 0u;
        std::cerr << std::right;
        for (auto tIter = assembler->begin(); tIter != assembler->end(); ++tIter) {
            std::cerr << "\b\b\b\b\b\b\b\b\b\b" << std::setw(10)  // Using backspaces for in place counter
                      << count++;
            trajectories.push_back(*tIter);
        }
        std::cerr << std::left << "\nStarting with " << trajectories.size() << " trajectories" << std::endl;
    }

    // Filter tracks based on length
    // This is the typical method, fairly compact and reasonably efficient
    // we can check if an option was used by checking its 'count' in the variable map
    if (vm->count("min-length") != 0 || vm->count("max-length") != 0) {
        std::cerr << "Filtering based on length" << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        auto lower = vm->count("min-length") != 0 ? (*vm)["min-length"].as<double>() : 0.0;
        auto upper = vm->count("max-length") != 0 ? (*vm)["max-length"].as<double>()
                                                  : std::numeric_limits<double>::max();
        // We use remove_if to move all trajectories where the lambda returns true to the end
        // remove_if returns the end of the list of kept items.
        // we then erase everything from that point to the 'end()'
        trajectories.erase(std::remove_if(trajectories.begin(), trajectories.end(),
                                          [&](const TrajectoryT& _t) {
                                              auto l = length(_t);
                                              return (upper < l) || (l < lower);
                                          }),
                           trajectories.end());
        std::cerr << trajectories.size() << " trajectories after filtering for length" << std::endl;
    }

    // Filter tracks based on curvature
    // This can be used to looks for loops.
    // This method is identical to that above but the steps are seperated out for demonstration
    if (vm->count("min-curvature") != 0 || vm->count("max-curvature") != 0) {
        std::cerr << "Filtering based on curvature" << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        auto lower = vm->count("min-curvature") != 0 ? (*vm)["min-curvature"].as<double>() : 0.0;
        auto upper = vm->count("max-curvature") != 0 ? (*vm)["max-curvature"].as<double>()
                                                     : std::numeric_limits<double>::max();
        // Create and save a lambda to use as filter predicate
        auto filterFunc = [&](const TrajectoryT& _t) {
            auto c = std::abs(TotalCurvature(_t));
            return (upper < c) || (c < lower);
        };
        // we save the result of remove if to use in the erase
        auto lastGood = std::remove_if(trajectories.begin(), trajectories.end(), filterFunc);
        // we then erase everything from that point to the 'end()'
        trajectories.erase(lastGood, trajectories.end());
        std::cerr << trajectories.size() << " trajectories after filtering for curvature" << std::endl;
    }

    // use track filter object, we still manually check options ot skip if not asked for.
    // The track filter object uses the same method as above, but centralizes the code
    // for improved reliability and maintenance.
    if (vm->count("min-hull-gyration-ratio") != 0 || vm->count("max-hull-gyration-ratio") != 0) {
        auto& filter = hullGyrationFilter;
        std::cerr << "Filtering based on " << filter.getName() << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        filter(trajectories);
        std::cerr << trajectories.size() << " trajectories after filtering for " << filter.getName()
                  << std::endl;
    }

    // This ratio represents the directness of a flight
    if (vm->count("min-length-ratio") != 0 || vm->count("max-length-ratio") != 0) {
        auto& filter = lengthRatioFilter;
        std::cerr << "Filtering based on " << filter.getName() << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        filter(trajectories);
        std::cerr << trajectories.size() << " trajectories after filtering for " << filter.getName()
                  << std::endl;
    }

    if (vm->count("min-hull-aspect-ratio") != 0 || vm->count("max-hull-aspect-ratio") != 0) {
        auto& filter = hullAspectRatioFilter;
        std::cerr << "Filtering based on " << filter.getName() << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        filter(trajectories);
        std::cerr << trajectories.size() << " trajectories after filtering for " << filter.getName()
                  << std::endl;
    }
    // Apply headings if needed
    if (0 != (vm->count("assign-headings") + vm->count("min-straightness") + vm->count("max-straightness") +
              vm->count("min-turn-arounds") + vm->count("max-turn-arounds"))) {
        AssignTrajectoryHeadings(trajectories);
    }
    // Mapping flights will have a high straightness with a high number of turn arounds
    if (vm->count("min-straightness") != 0 || vm->count("max-straightness") != 0) {
        auto& filter = straightnessFilter;
        std::cerr << "Filtering based on " << filter.getName() << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        filter(trajectories);
        std::cerr << trajectories.size() << " trajectories after filtering for " << filter.getName()
                  << std::endl;
    }
    if (vm->count("min-turn-arounds") != 0 || vm->count("max-turn-arounds") != 0) {
        auto& filter = turnAroundsFilter;
        std::cerr << "Filtering based on " << filter.getName() << std::endl;
        boost::timer::auto_cpu_timer t(std::cerr);
        filter(trajectories);
        std::cerr << trajectories.size() << " trajectories after filtering for " << filter.getName()
                  << std::endl;
    }

    if (0 != vm->count("no-output")) {
        std::cerr << "No Output" << std::endl;
        return 0;
    }
    if (0 != vm->count("separate-kmls")) {
        auto resultsDirectory = (*vm)["result-dir"].as<std::string>();
        std::cerr << "Writing separate kml files to " << resultsDirectory << std::endl;
        kml::writeToSeparateKmls(trajectories, resultsDirectory);
        return 0;
    }
    auto filename = (*vm)["output"].as<std::string>();
    if ("-" != filename) {
        std::ofstream outfile(filename);
        std::cerr << "Writing to " << filename << std::endl;
        outfile << kml(trajectories);
        outfile.close();
        return 0;
    }
    std::cerr << "Writing to stdout" << std::endl;
    std::cout << kml::header;
    std::cout << kml(trajectories);
    std::cout << kml::footer;
    return 0;
}
