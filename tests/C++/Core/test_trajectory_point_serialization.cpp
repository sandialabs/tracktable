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

#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/TrajectoryPoint.h>

#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>

#include <iostream>
#include <sstream>


template<typename point_type>
point_type serialized_copy(point_type const& input_point)
{
  point_type restored_point;

  std::ostringstream temp_out;
  boost::archive::text_oarchive archive_out(temp_out);
  archive_out << input_point;

  std::istringstream temp_in(temp_out.str());
  boost::archive::text_iarchive archive_in(temp_in);
  archive_in >> restored_point;

  return restored_point;
}

// ----------------------------------------------------------------------

int
test_trajectory_point_lonlat_serialization()
{
  typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> trajectory_point_type;

  trajectory_point_type point, point_copy;

  point[0] = -10;
  point[1] = 20;

  point.set_object_id("MyPoint");
//  point.set_property("test_int_property", 123L);
  point.set_property("test_float_property", 456.789);
  point.set_property("test_string_property", "Frodo lives!");
  point.set_property("test_timestamp_property", tracktable::time_from_string("2000-01-02 03:04:05"));
  point.set_timestamp(tracktable::time_from_string("2001-02-03 04:05:06"));

  point_copy = serialized_copy(point);
  if (point != point_copy)
    {
    std::cerr << "ERROR: Serialization/deserialization of "
              << "tracktable::TrajectoryPoint<PointLonLat> failed.  Original "
              << "point was "
              << point
              << " and restored point was "
              << point_copy << ".\n";
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

  num_errors += test_trajectory_point_lonlat_serialization();
//  num_errors += test_point_cartesian2d_serialization();
//  num_errors += test_point_cartesian3d_serialization();

  return num_errors;
}
