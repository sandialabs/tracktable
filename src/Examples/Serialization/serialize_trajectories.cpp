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

static constexpr auto helpmsg = R"(
--------------------------------------------------------------------------------
Compare storage costs for various methods of serializing trajectories

  We have three ways to save trajectories:

 1. tracktable::TrajectoryWriter (C++, Python)
    This uses our own home-grown delimited text format.  It is rather
    verbose.

  2. tracktable.rw.read_write_json (Python)
     Write to JSON.  This is also rather verbose and has trouble with
     incremental loads.

 3. boost::serialization
    Write to Boost's archive format (text, binary or XML).

 This example runs #1 and #3 on a sample trajectory and compares the
 storage requirements.

 This example demonstrates:
   - use of boost program options
   - use of boost archives
   - use of trajectory writer
   - Manual construction of points and trajectories

Typical use:
    ./serialize_trajectories --trajectory-count=100 --point-count=100
--------------------------------------------------------------------------------)";

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/RW/TrajectoryWriter.h>

#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/xml_oarchive.hpp>
#include <boost/program_options.hpp>
#include <boost/serialization/vector.hpp>

#include <iostream>
#include <locale>
#include <sstream>
#include <vector>

namespace bpo = boost::program_options;

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = tracktable::domain::terrestrial::trajectory_point_type;

/** @brief Creates a trajectory with a set number of points
 * @param _numPoints The number of points to create
 * @return The resulting trajectory */
TrajectoryT build_trajectory(int _numPoints = 100);

/** @brief Get the size of tracktable trajectory writer stored data
 * @param trajectories Vector of trajectories to store
 * @return size of stored data */
std::size_t get_tracktable_trajectory_writer_size(std::vector<TrajectoryT> const& trajectories);

/** @brief Get the size of boost text archive
 * @param trajectories Vector of trajectories to store
 * @return size of stored data */
std::size_t get_boost_text_size(std::vector<TrajectoryT> const& trajectories);

/** @brief Get the size of boost binary archive
 * @param trajectories Vector of trajectories to store
 * @return size of stored data */
std::size_t get_boost_binary_size(std::vector<TrajectoryT> const& trajectories);

/** @brief Get the size of boost xml archive
 * @param trajectories Vector of trajectories to store
 * @return size of stored data */
std::size_t get_boost_xml_size(std::vector<TrajectoryT> const& trajectories);

int main(int _argc, char* _argv[]) {
    auto trajectoryCount = 100u;
    auto pointsPerTrajectory = 100u;

    boost::program_options::options_description commandLineOptions("Options");
    // clang-format off
    commandLineOptions.add_options()
      ("help", "Print help")
      ("trajectory-count",bpo::value(&trajectoryCount)->default_value(100u),
       "number of trajectories to use")
      ("point-count",bpo::value(&pointsPerTrajectory)->default_value(100u),
       "number of points per trajectory")
    ;
    // clang-format on
    auto vm = std::make_shared<boost::program_options::variables_map>();

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

    // Construct test trajectories
    std::vector<TrajectoryT> trajectories;
    for (auto i = 0u; i < trajectoryCount; ++i) {
        trajectories.push_back(build_trajectory(pointsPerTrajectory + (i % 11)));
    }

    auto trajectoryWriterSize = get_tracktable_trajectory_writer_size(trajectories);
    auto boostTextSize = get_boost_text_size(trajectories);
    auto boostBinarySize = get_boost_binary_size(trajectories);
    auto boostXmlSize = get_boost_xml_size(trajectories);

    std::cout.imbue(std::locale(""));  // Add commas to int
    std::cout << "Storage comparison for different serialization formats\n";
    std::cout << "Trajectories: " << trajectoryCount << "\n";
    std::cout << "Points per trajectory: " << pointsPerTrajectory << "\n\n" << std::right;

    std::cout << "\tTrajectoryWriter:       " << std::setw(15) << trajectoryWriterSize << "\n";
    std::cout << "\tboost::text_oarchive:   " << std::setw(15) << boostTextSize << "\n";
    std::cout << "\tboost::binary_oarchive: " << std::setw(15) << boostBinarySize << "\n";
    std::cout << "\tboost::xml_oarchive:    " << std::setw(15) << boostXmlSize << std::endl;

    return 0;
}

TrajectoryT build_trajectory(int _numPoints /* = 100*/) {
    static auto seed = 0;  // Make each trajectory unique but deterministic
    PointT initialPoint;
    TrajectoryT trajectory;

    initialPoint.set_object_id("MyPoint" + std::to_string(seed));
    initialPoint[0] = (seed)-10;
    initialPoint[1] = (seed) + 20;
    initialPoint.set_timestamp(tracktable::time_from_string("2001-02-03 04:05:06") + tracktable::days(seed));

    constexpr auto floatProperty = "test_float_property";
    constexpr auto timestampProperty = "test_timestamp_property";
    constexpr auto stringProperty = "test_string_property";

    initialPoint.set_property(floatProperty, _numPoints + 456.789 / seed);
    initialPoint.set_property(stringProperty, "Frodo lives!");
    // a timestamp property is separate from the timestamp of the point itself.
    initialPoint.set_property(
        timestampProperty, tracktable::time_from_string("2000-01-02 03:04:05") + tracktable::days(seed * 30));

    PointT p(initialPoint);
    for (int i = 0; i < _numPoints; ++i) {
        p[0] += 0.1;
        p[1] += 0.15;
        p.set_timestamp(p.timestamp() + tracktable::seconds(5));
        p.set_property(floatProperty, p.real_property(floatProperty) + 1.1);
        p.set_property(timestampProperty, p.timestamp_property(timestampProperty) + tracktable::hours(1));
        trajectory.push_back(p);  // push_back will copy contents, so we don't have to worry about changing p
    }

    trajectory.set_property(floatProperty, 11456.789 + seed);
    trajectory.set_property(stringProperty, "Frodo lives!  So does Gandalf!");
    trajectory.set_property(timestampProperty,
                            tracktable::time_from_string("2001-02-03 04:05:06") + tracktable::minutes(seed));

    seed += _numPoints;
    return trajectory;
}

std::size_t get_tracktable_trajectory_writer_size(std::vector<TrajectoryT> const& trajectories) {
    std::ostringstream outbuf;
    tracktable::TrajectoryWriter writer(outbuf);
    writer.write(trajectories.begin(), trajectories.end());
    return outbuf.str().size();
}

std::size_t get_boost_text_size(std::vector<TrajectoryT> const& trajectories) {
    std::ostringstream outbuf;
    boost::archive::text_oarchive archive(outbuf);
    archive& trajectories;
    return outbuf.str().size();
}

std::size_t get_boost_binary_size(std::vector<TrajectoryT> const& trajectories) {
    std::ostringstream outbuf;
    boost::archive::binary_oarchive archive(outbuf);

    archive& trajectories;
    return outbuf.str().size();
}

std::size_t get_boost_xml_size(std::vector<TrajectoryT> const& trajectories) {
    std::ostringstream outbuf;
    boost::archive::xml_oarchive archive(outbuf);

    archive << BOOST_SERIALIZATION_NVP(trajectories);
    return outbuf.str().size();
}
