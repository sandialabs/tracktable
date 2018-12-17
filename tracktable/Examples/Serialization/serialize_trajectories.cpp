/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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


/* Compare storage costs for various methods of serializing trajectories
 *
 * We have three ways to save trajectories: 
 *
 * 1. tracktable::TrajectoryWriter (C++, Python)
 *    This uses our own home-grown delimited text format.  It is rather
 *    verbose.
 *
 * 2. tracktable.io.read_write_json (Python)
 *    Write to JSON.  This is also rather verbose and has trouble with
 *    incremental loads. 
 *
 * 3. boost::serialization
 *    Write to Boost's archive format (text, binary or XML).  This
 *    should be fairly compact, especially if you choose binary
 *    format, and supports incremental save/load.  It will probably
 *    also be a lot faster.
 *
 * This example runs #1 and #3 on a sample trajectory and compares the
 * storage requirements.
 */

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Domain/Terrestrial.h>

#include <tracktable/IO/TrajectoryWriter.h>

#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/xml_oarchive.hpp>
#include <boost/serialization/vector.hpp>


#include <algorithm>
#include <sstream>

typedef tracktable::domain::terrestrial::trajectory_type trajectory_type;
typedef tracktable::domain::terrestrial::trajectory_point_type trajectory_point_type;

// ----------------------------------------------------------------------

trajectory_type
build_trajectory(int num_points=100)
{
  trajectory_point_type initial_point;
  trajectory_type trajectory;

  initial_point[0] = -10;
  initial_point[1] = 20;

  initial_point.set_object_id("MyPoint");
  initial_point.set_property("test_int_property", 123ll);
  initial_point.set_property("test_float_property", 456.789);
  initial_point.set_property("test_string_property", "Frodo lives!");
  initial_point.set_property("test_timestamp_property", tracktable::time_from_string("2000-01-02 03:04:05"));
  initial_point.set_timestamp(tracktable::time_from_string("2001-02-03 04:05:06"));
    
  for (int i = 0; i < num_points; ++i)
    {
    trajectory_point_type my_point(initial_point);
    my_point[0] += 0.1 * i;
    my_point[1] += 0.15 * i;
    my_point.set_property("test_int_property",
                          boost::get<int64_t>(my_point.property("test_int_property")) + i);
    my_point.set_property("test_float_property",
                          boost::get<double>(my_point.property("test_float_property")) + i * 1.1);
    my_point.set_property("test_timestamp_property",
                          boost::get<tracktable::Timestamp>(my_point.property("test_timestamp_property"))
                          + tracktable::hours(i));
    trajectory.push_back(my_point);
    }

  trajectory.set_property("test_int_property", 12345ll);
  trajectory.set_property("test_float_property", 11456.789);
  trajectory.set_property("test_string_property", "Frodo lives!  So does Gandalf!");
  trajectory.set_property("test_timestamp_property", tracktable::time_from_string("2001-02-03 04:05:06"));

  return trajectory;
}

// ----------------------------------------------------------------------

std::size_t test_tracktable_trajectory_writer_storage(std::vector<trajectory_type> const& trajectories)
{
  std::ostringstream outbuf;
  tracktable::TrajectoryWriter writer(outbuf);
  writer.write(trajectories.begin(), trajectories.end());

  return outbuf.str().size();
}


// ----------------------------------------------------------------------

std::size_t test_boost_text_storage(std::vector<trajectory_type> const& trajectories)
{
  std::ostringstream outbuf;
  boost::archive::text_oarchive archive(outbuf);

  archive & trajectories;
  return outbuf.str().size();
}

// ----------------------------------------------------------------------

std::size_t test_boost_binary_storage(std::vector<trajectory_type> const& trajectories)
{
  std::ostringstream outbuf;
  boost::archive::binary_oarchive archive(outbuf);

  archive & trajectories;
  return outbuf.str().size();
}


// ----------------------------------------------------------------------

std::size_t test_boost_xml_storage(std::vector<trajectory_type> const& trajectories)
{
  std::ostringstream outbuf;
  boost::archive::xml_oarchive archive(outbuf);

  archive << BOOST_SERIALIZATION_NVP(trajectories);
  return outbuf.str().size();
}

// ----------------------------------------------------------------------


int main(int argc, char* argv[])
{
  int num_trajectories = 100;
  int points_per_trajectory = 100;

  trajectory_type base_trajectory = build_trajectory(points_per_trajectory);
  std::vector<trajectory_type> trajectories(num_trajectories, base_trajectory);
  
  std::size_t tracktable_trajectory_writer_storage = test_tracktable_trajectory_writer_storage(trajectories);
  std::size_t boost_text_storage = test_boost_text_storage(trajectories);
  std::size_t boost_binary_storage = test_boost_binary_storage(trajectories);
  std::size_t boost_xml_storage = test_boost_xml_storage(trajectories);

  std::cout << "Storage comparison for different serialization formats\n";
  std::cout << "Trajectories: " << num_trajectories << "\n";
            << "Points per trajectory: " << points_per_trajectory << "\n";
  
  std::cout << "\ttracktable::TrajectoryWriter: " << tracktable_trajectory_writer_storage << "\n";
  std::cout << "\tboost::text_oarchive: " << boost_text_storage << "\n";
  std::cout << "\tboost::binary_oarchive: " << boost_binary_storage << "\n";
  std::cout << "\tboost::xml_oarchive: " << boost_xml_storage << "\n";
  
  return 0;
}
