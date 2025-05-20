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

#include <boost/timer/timer.hpp>

#include <algorithm>
#include <memory>
#include <string>
#include <vector>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using PointReaderT = tracktable::PointReader<PointT>;
using PointReaderIteratorT = typename PointReaderT::iterator;
using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
The findid example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Reading a list of ids from a file
    - Searching trajectories for specific object ids

Typical use:
    ./assemble --input=/data/flights.tsv --idfile=/data/mapping_ids.txt

Defaults assume a tab separated points file formatted as :

OBJECTID TIMESTAMP LON LAT

And an id file with a single object id per line.

Default output is just a count of how many trajectories were found.
--------------------------------------------------------------------------------)";

int main(int _argc, char* _argv[]) {
    // Set log level to reduce unecessary output
    tracktable::set_log_level(tracktable::log::info);
    // Create a basic command line option with boost
    boost::program_options::options_description commandLineOptions;
    // clang-format off
    commandLineOptions.add_options()
      ("help", "Print help")  // And a command line option for output
      ("idfile",
        bpo::value<std::string>()->default_value("mapping-ids.txt"),
       "file to read ids from")
    ;
    // clang-format on
    // Reader factories, which add lots of command line options
    tracktable::PointReaderFromCommandLine<PointT> readerFactory;
    tracktable::AssemblerFromCommandLine<TrajectoryT> assemblerFactory;
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
        boost::program_options::store(
            boost::program_options::command_line_parser(_argc, _argv).options(commandLineOptions).run(), *vm);
        boost::program_options::notify(*vm);
    } catch (boost::program_options::error& e) {
        std::cerr << helpmsg << "\n\n" << e.what() << "\n\n" << commandLineOptions << std::endl;
        return 1;
    }
    /** Parsing will give an error of an incorrect option is used, but it won't
     * display the help unless we tell it too */
    if (vm->count("help") != 0) {
        std::cerr << helpmsg << commandLineOptions << std::endl;
        return 1;
    }

    // Create Point Reader and assembler
    auto pointReader = readerFactory.createPointReader();
    auto assembler = assemblerFactory.createAssembler(pointReader);

    std::vector<std::shared_ptr<TrajectoryT>> trajectories = {};
    {
        std::cerr << "Assemble Trajectories" << std::endl;
        boost::timer::auto_cpu_timer assembleTimer(std::cerr);
        auto count = 0u;
        std::cerr << std::right;
        for (auto tIter = assembler->begin(); tIter != assembler->end(); ++tIter) {
            std::cerr << "\b\b\b\b\b\b\b\b\b\b" << std::setw(10)  // Using backspaces for in place counter
                      << count++;
            trajectories.push_back(std::make_shared<TrajectoryT>(*tIter));
        }
        std::cerr << std::left << "\nStarting with " << trajectories.size() << " trajectories" << std::endl;
    }

    // Read ObjectIds from file
    auto fileName = (*vm)["idfile"].as<std::string>();
    std::vector<std::string> idList;
    {
        boost::timer::auto_cpu_timer searchTimer(std::cerr);
        std::ifstream idFile(fileName);
        if (!idFile.is_open()) {
            std::cerr << "Could not open id file: " << fileName << std::endl;
        }
        std::string id;
        while (std::getline(idFile, id)) {
            std::cerr << id << std::endl;
            idList.push_back(id);
        }
        std::sort(idList.begin(), idList.end());
        std::cerr << idList.size() << " ids found" << std::endl;
    }

    // separate the trajectories based on whether they are on the id list.
    std::vector<std::shared_ptr<TrajectoryT>> foundTrajectories;

    /*Copy everything except where the lambda is true, this is an alternative to  copy_if
      think of remove_copy_if as dont_copy_if; It only copies if the function returns false*/
    std::remove_copy_if(trajectories.begin(), trajectories.end(), std::back_inserter(foundTrajectories),
                        [&idList /*capture idList*/](const std::shared_ptr<TrajectoryT>& _t) {
                            // search idList for current object id
                            return !std::binary_search(idList.begin(), idList.end(), _t->object_id());
                        });

    /*Remove the copied trajectories, remove_if shifts all unwanted entries to the end of vector and returns
      an iterator to the first 'bad' element, erase takes that iterator and deletes everything after it, the
      lambda is similar to that used above, but is missing the negation(!) and operating on a separate
      vector*/
    std::sort(foundTrajectories.begin(), foundTrajectories.end());
    trajectories.erase(std::remove_if(trajectories.begin(), trajectories.end(),
                                      [&foundTrajectories](const std::shared_ptr<TrajectoryT>& _t) {
                                          return std::binary_search(foundTrajectories.begin(),
                                                                    foundTrajectories.end(), _t);
                                      }),
                       trajectories.end());

    std::cout << "trajectories.size() = " << trajectories.size() << std::endl;
    std::cout << "foundTrajectories.size() = " << foundTrajectories.size() << std::endl;

    return 0;
}