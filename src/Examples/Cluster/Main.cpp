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

#include "Correlation.h"

#include <tracktable/Analysis/ComputeDBSCANClustering.h>
#include <tracktable/Analysis/DistanceGeometry.h>
#include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
#include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>
#include <tracktable/Domain/FeatureVectors.h>
#include <tracktable/Domain/Terrestrial.h>

#include <boost/timer/timer.hpp>

using FeatureVectorT = tracktable::domain::feature_vectors::FeatureVector<10>;

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointReaderIteratorT = typename PointReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
The cluster example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Create features using distance geometries
    - Cluster and and assign membership using dbscan

Typical use:
    ./cluster --input=/data/flights.tsv

Defaults assume a tab separated points file formatted as :

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

    std::vector<std::shared_ptr<TrajectoryT>> trajectories = {};
    {
        std::cerr << "Assemble Trajectories" << std::endl;
        boost::timer::auto_cpu_timer assembleTimer(std::cerr, timerFormat);
        auto count = 0u;
        std::cerr << std::right;
        for (auto tIter = assembler->begin(); tIter != assembler->end(); ++tIter) {
            if (tracktable::length(*tIter) < 100) {  // filter out standing still
                continue;
            }
            std::cerr << "\b\b\b\b\b\b\b\b\b\b" << std::setw(10)  // Using backspaces for in place counter
                      << count++;
            trajectories.push_back(std::make_shared<TrajectoryT>(*tIter));
        }
        std::cerr << std::left << "\nStarting with " << trajectories.size() << " trajectories" << std::endl;
    }

    /* Create a set of features. distance geometry produces a vector of doubles
     * and must be transferred to feature vectors to be consumed by certain functions */
    std::vector<FeatureVectorT> features;
    {
        std::cerr << "Build features" << std::endl;
        boost::timer::auto_cpu_timer featuretTimer(std::cerr, timerFormat);
        for (auto& t : trajectories) {
            auto v = tracktable::distance_geometry_by_distance(*t, 4);
            FeatureVectorT f;
            for (auto i = 0u; i < features.size() && i < v.size(); ++i) {
                f[i] = v[i];
            }
            features.push_back(f);
        }
    }

    using ClusterLabelT = std::pair<int, int>;
    using ClusterLabelVectorT = std::vector<ClusterLabelT>;
    using IdVectorT = std::vector<int>;

    FeatureVectorT search_box;
    for (auto i = 0u; i < search_box.size(); ++i) {
        search_box[i] = 0.1;
    }

    ClusterLabelVectorT vertex_cluster_labels;
    {
        std::cerr << "Cluster with dbscan" << std::endl;
        boost::timer::auto_cpu_timer clusterTimer(std::cerr, timerFormat);
        tracktable::cluster_with_dbscan(features.begin(), features.end(), search_box, 3,
                                        std::back_inserter(vertex_cluster_labels));
    }

    std::vector<IdVectorT> membership;
    {
        std::cerr << "Build Cluster membership List" << std::endl;
        boost::timer::auto_cpu_timer membershiptTimer(std::cerr, timerFormat);
        tracktable::build_cluster_membership_lists(vertex_cluster_labels.begin(), vertex_cluster_labels.end(),
                                                   std::back_inserter(membership));
    }

    for (unsigned int i = 0; i < membership.size(); ++i) {
        std::cerr << i << "(" << std::setw(3) << membership[i].size() << "):";
        FeatureVectorT avg;
        avg = tracktable::arithmetic::zero<FeatureVectorT>();
        for (unsigned int j = 0; j < membership[i].size(); ++j) {
            //      std::cout << trajectories[membership[i][j]].object_id() << " ";
            tracktable::arithmetic::add_in_place(avg, features[membership[i][j]]);
        }
        tracktable::arithmetic::divide_scalar_in_place(avg, static_cast<double>(membership[i].size()));
        std::cerr << avg;
        std::cerr << std::endl;
    }

    std::cerr << "------------------------- Correlation --------------------------\n";
    std::cerr << Correlation(features) << std::endl;

    return 0;
}
