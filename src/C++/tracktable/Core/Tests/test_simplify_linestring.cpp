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

#include <tracktable/Core/Logging.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/PointArithmetic.h>

#include <iostream>
#include <sstream>
#include <typeinfo>

// Import constants for log level
using namespace tracktable::log;

template<typename iter_type>
std::string linestring_to_string(iter_type _begin, iter_type _end)
{
  std::ostringstream out;
  while (_begin != _end)
    {
      out << (*_begin).to_string() << " ||| ";
      ++_begin;
    }
  return out.str();
}

template<typename iter_type, typename out_type>
void dump_linestring(iter_type _begin, iter_type _end, out_type& output)
{
  while (_begin != _end)
    {
    output << (*_begin).to_string() << "\n";
    ++_begin;
    }
}

template<typename point_type>
struct decorate_point
{
  static inline void apply(point_type& /*point*/, int /*dummy*/)
    {
      return;
    }
};

template<typename point_type>
struct decorate_point< tracktable::TrajectoryPoint<point_type> >
{
  template<typename wrapped_point_type>
  static inline void apply(wrapped_point_type& point, int dummy)
    {
      tracktable::Timestamp time(tracktable::time_from_string("2010-01-01 00:00:00") + tracktable::hours(dummy));
      point.set_timestamp(time);
      point.set_object_id("my_object_id");
    }
};

template<typename T>
struct add_properties_to_trajectory
{
  static inline void apply(T& /*thing*/)
    {
      return;
    }
};

template<typename point_type>
struct add_properties_to_trajectory<tracktable::Trajectory<point_type> >
{
  template<typename trajectory_type>
  static inline void apply(trajectory_type& thing)
    {
      thing.set_property("integer_test", 12345);
      thing.set_property("real_test", 3.14159);
      thing.set_property("string_test", "this is a test");
    }
};

template<typename T>
struct check_property_equality
{
  static inline bool apply(T const& /*before*/, T const& /*after*/)
    {
      return true;
    }
};

template<typename point_type>
struct check_property_equality<tracktable::Trajectory<point_type> >
{
  template<typename trajectory_type>
  static inline bool apply(trajectory_type const& before, trajectory_type const& after)
    {
      return (before.__properties() == after.__properties());
    }
};

// ----------------------------------------------------------------------

template<typename linestring_type>
int test_simplify_linestring()
{
  typedef typename linestring_type::value_type point_type;
  linestring_type linestring;

  for (int i = 0; i < 9; ++i)
    {
    point_type next_point = tracktable::arithmetic::zero<point_type>();
    next_point.template set<0>(i);
    if (i == 4)
      {
      next_point.template set<1>(5);
      }
    decorate_point<point_type>::apply(next_point, i);
    linestring.push_back(next_point);
    }

  linestring_type simplified = tracktable::simplify(linestring, 0.01);
  int error_count = 0;
  if (simplified.size() != 5)
    {
      TRACKTABLE_LOG(error)
          << "test_simplify_linestring on "
			    << typeid(linestring_type).name()
			    << ": Simplified linestring has "
			    << simplified.size() << " points.  We were expecting 5.  "
			    << "Simplified geometry:  "
          << linestring_to_string(simplified.begin(), simplified.end());
      ++error_count;
    }

  if (simplified[0] != linestring[0])
    {
      TRACKTABLE_LOG(error)
          << "test_simplify_linestring on "
			    << typeid(linestring_type).name()
			    << ": Expected first point to be the same as from the input.  "
			    << "Original first point: " << linestring[0].to_string()
          << "  "
			    << "Simplified first point: " << simplified[0].to_string();
    ++error_count;
    }


  if (simplified[1] != linestring[3])
    {
    TRACKTABLE_LOG(error)
      << "test_simplify_linestring on "
      << typeid(linestring_type).name()
      << ": Expected second point to be the same as point 3 from the input.  "
      << "Original point: " << linestring[3].to_string()
      << "  "
      << "Simplified first point: " << simplified[1].to_string();
    ++error_count;
    }


  if (simplified[2] != linestring[4])
    {
    TRACKTABLE_LOG(error)
      << "test_simplify_linestring on "
      << typeid(linestring_type).name()
      << ": Expected middle point to be the same as point 4 from the input.  "
      << "Original point: " << linestring[4].to_string()
      << "  "
      << "Simplified first point: " << simplified[2].to_string();
    ++error_count;
    }


  if (simplified[3] != linestring[5])
    {
    TRACKTABLE_LOG(error)
      << "test_simplify_linestring on "
      << typeid(linestring_type).name()
      << ": Expected point 3 to be the same as point 5 from the input.  "
      << "Original point: " << linestring[5].to_string()
      << "  "
      << "Simplified first point: " << simplified[3].to_string();
    ++error_count;
    }


  if (simplified[4] != linestring[8])
    {
    TRACKTABLE_LOG(error)
      << "test_simplify_linestring on "
      << typeid(linestring_type).name()
      << ": Expected point 4 to be the same as point 8 from the input."
      << "Original point: " << linestring[8].to_string()
      << "  "
      << "Simplified first point: " << simplified[4].to_string();
    ++error_count;
    }

  if (check_property_equality<linestring_type>::apply(simplified, linestring) == false)
    {
      TRACKTABLE_LOG(error)
        << "ERROR: test_simplify_linestring on "
        << typeid(linestring_type).name()
        << ": Property maps do not match.";
    ++error_count;
    }

  if (error_count != 0)
    {
    TRACKTABLE_LOG(debug) << "Original linestring: "
                          << linestring_to_string(linestring.begin(), linestring.end());
    TRACKTABLE_LOG(debug) << "Simplified linestring: "
                          << linestring_to_string(simplified.begin(), simplified.end());
    }

  return error_count;

}

// ----------------------------------------------------------------------


int main(int /*argc*/, char* /*argv*/[])
{
  int overall_error_count = 0;

  typedef tracktable::TrajectoryPoint< tracktable::PointLonLat > TrajectoryPointLonLat;
  typedef tracktable::TrajectoryPoint< tracktable::PointCartesian<2> > TrajectoryPointCartesian2D;
  typedef tracktable::TrajectoryPoint< tracktable::PointCartesian<3> > TrajectoryPointCartesian3D;

  overall_error_count += test_simplify_linestring< std::vector<tracktable::PointLonLat> >();
  overall_error_count += test_simplify_linestring< std::vector<tracktable::PointCartesian<2> > >();
  overall_error_count += test_simplify_linestring< std::vector<tracktable::PointCartesian<3> > >();

  overall_error_count += test_simplify_linestring< tracktable::Trajectory< TrajectoryPointLonLat > >();
  overall_error_count += test_simplify_linestring< tracktable::Trajectory< TrajectoryPointCartesian2D> >();
  overall_error_count += test_simplify_linestring< tracktable::Trajectory< TrajectoryPointCartesian3D> >();

  return overall_error_count;
}
