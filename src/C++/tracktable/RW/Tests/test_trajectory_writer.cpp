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

#include <tracktable/RW/TrajectoryWriter.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PropertyMap.h>

#include <iostream>
#include <iomanip>
#include <cassert>

// ----------------------------------------------------------------------

template<class thing_with_properties>
void add_real_property(std::size_t property_index, thing_with_properties& destination)
{
  tracktable::ostringstream_type namebuf;
  namebuf << "test_real_property_" << property_index;
  destination.set_property(namebuf.str(), 1.1 * property_index*property_index);
}


template<class thing_with_properties>
void add_string_property(std::size_t property_index, thing_with_properties& destination)
{
  tracktable::ostringstream_type namebuf, valuebuf;
  namebuf << "test_string_property_" << property_index;

  valuebuf << "Test: \t," << property_index;

  destination.set_property(namebuf.str(), valuebuf.str());
}

template<class thing_with_properties>
void add_timestamp_property(std::size_t property_index, thing_with_properties& destination)
{
  tracktable::ostringstream_type namebuf, valuebuf;
  namebuf << "test_timestamp_property_" << property_index;

  valuebuf << "2014-03-04 12:"
           << std::setw(2) << std::setfill('0')
           << (property_index % 60)
           << ":"
           << std::setw(2) << std::setfill('0')
           << ((2*property_index) % 60);

  destination.set_property(namebuf.str(), tracktable::time_from_string(valuebuf.str()));
}

// ----------------------------------------------------------------------

template<class thing_with_properties>
void generate_arbitrary_properties(std::size_t how_many,
                                   thing_with_properties& destination)
{

  for (std::size_t i = 0; i < how_many; ++i)
    {
    int i_property_type = (i % 3) + 1;
    tracktable::PropertyUnderlyingType property_type = static_cast<tracktable::PropertyUnderlyingType>(i_property_type);
    switch (property_type)
      {
      // XXX FIXME add null types
      case tracktable::TYPE_REAL:
        add_real_property(i, destination); break;
      case tracktable::TYPE_STRING:
        add_string_property(i, destination); break;
      case tracktable::TYPE_TIMESTAMP:
        add_timestamp_property(i, destination); break;
      default:
        assert(1==0 && "Unhandled variant type in generate_arbitrary_properties");
      }
    }
}

// ----------------------------------------------------------------------

template<class point_type>
void generate_arbitrary_coordinates(std::size_t meaningless_integer,
                                    point_type& point)
{
  for (std::size_t d = 0;
       d < point.size();
       ++d)
    {
    point[d] = meaningless_integer + 10*d;
    }
}

// ----------------------------------------------------------------------

template<typename point_type>
tracktable::Trajectory<
  tracktable::TrajectoryPoint<
    point_type
    > >
generate_trajectory(int /*trajectory_index*/,
                    size_t num_points,
                    int num_point_properties,
                    int num_trajectory_properties)
{
  typedef tracktable::TrajectoryPoint<point_type> trajectory_point_type;
  typedef tracktable::Trajectory<trajectory_point_type> trajectory_type;

  trajectory_type trajectory;

  generate_arbitrary_properties(num_trajectory_properties, trajectory);

  for (auto i = 0u; i < num_points; ++i)
    {
    tracktable::ostringstream_type id_buf, timestamp_buf;
    trajectory_point_type next_point;
    id_buf << "TestObject";
    std::size_t hour = i / 60;
    std::size_t minute = i % 60;
    timestamp_buf << "2000-12-24 "
                  << std::setw(2) << std::setfill('0')
                  << hour
                  << std::setw(2) << std::setfill('0')
                  << minute
                  << std::setw(2) << std::setfill('0')
                  << "00";

    next_point.set_object_id(id_buf.str());
    next_point.set_timestamp(tracktable::time_from_string(timestamp_buf.str()));
    generate_arbitrary_properties(num_point_properties, next_point);
    generate_arbitrary_coordinates(i, next_point);
    trajectory.push_back(next_point);
    }

  return trajectory;
}

// ----------------------------------------------------------------------

template<typename point_type>
void test_trajectory_writer(std::size_t /*howmany*/)
{
  typedef tracktable::TrajectoryPoint<point_type> trajectory_point_type;
  typedef tracktable::Trajectory<trajectory_point_type> trajectory_type;

  trajectory_type my_trajectory(generate_trajectory<point_type>(0, 10, 6, 12));

  std::cout << "Trajectory has "
            << my_trajectory.__properties().size() << " properties set\n";

  tracktable::ostringstream_type outbuf;
  tracktable::TrajectoryWriter writer(outbuf);
  writer.write(my_trajectory);
  std::cout << "Trajectory writer output:\n";
  std::cout << outbuf.str();
  std::cout << "(end)\n";

}

int
main(int , char**)
{
  test_trajectory_writer<tracktable::PointLonLat>(1);
  return 0;
}

