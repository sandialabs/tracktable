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


/*
 * Test serialization/deserialization of a trajectory in the lon/lat
 * domain.  NOTE: You should not be instantiating that class directly,
 * but instead using the wrappers in tracktable::domain::terrestrial.
 */

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>

#include <iostream>
#include <sstream>

template<typename thing_type>
thing_type serialized_copy(thing_type const& input_thing)
{
  thing_type restored_thing;

  std::ostringstream temp_out;
  boost::archive::text_oarchive archive_out(temp_out);
  archive_out << input_thing;

  std::istringstream temp_in(temp_out.str());
  boost::archive::text_iarchive archive_in(temp_in);
  archive_in >> restored_thing;

  return restored_thing;
}

// ----------------------------------------------------------------------

int
test_trajectory_serialization()
{
  typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> trajectory_point_type;
  typedef tracktable::Trajectory<trajectory_point_type> trajectory_type;

  trajectory_point_type initial_point;
  trajectory_type trajectory, copied_trajectory;

  initial_point[0] = -10;
  initial_point[1] = 20;

  initial_point.set_object_id("MyPoint");
  initial_point.set_property("test_int_property", int64_t(12345));
  initial_point.set_property("test_float_property", 456.789);
  initial_point.set_property("test_string_property", "Frodo lives!");
  initial_point.set_property("test_timestamp_property", tracktable::time_from_string("2000-01-02 03:04:05"));
  initial_point.set_timestamp(tracktable::time_from_string("2001-02-03 04:05:06"));

  for (int i = 0; i < 10; ++i)
    {
    trajectory_point_type my_point(initial_point);
    my_point[0] += 0.1 * i;
    my_point[1] += 0.15 * i;
#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
    my_point.set_property("test_int_property",
                          boost::get<int64_t>(my_point.property("test_int_property")) + i);
#endif
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

  copied_trajectory = serialized_copy(trajectory);
  if (copied_trajectory != trajectory)
    {
    std::cerr << "ERROR: Copied trajectory is not the same as original\n";
    return 1;
    }
  else
    {
    return 0;
    }
 }

// ----------------------------------------------------------------------



int
main(int , char **)
{
  int num_errors = 0;

  num_errors += test_trajectory_serialization();

  return num_errors;
}
