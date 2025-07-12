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

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>

namespace tracktable {

typedef TrajectoryPoint<PointLonLat> TrajectoryPointLonLat;
typedef Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

}

int test_trajectory()
{
  typedef tracktable::TrajectoryPointLonLat point_type;
  typedef tracktable::TrajectoryLonLat trajectory_type;
  int error_count = 0;

  point_type albuquerque;
  point_type santa_fe;
  point_type roswell;

  std::string test_string_property("This is a test.");
  double test_double_property(12345);
  tracktable::Timestamp test_timestamp_property(tracktable::time_from_string("2014-05-04 15:00:00"));

  std::string obj_id("GreenChileExpress001");
  albuquerque.set_latitude(35.1107);
  albuquerque.set_longitude(-106.6100);
  albuquerque.set_object_id(obj_id);
  albuquerque.set_timestamp(tracktable::time_from_string("2014-05-01 12:00:00"));

  santa_fe.set_latitude(35.6672);
  santa_fe.set_longitude(-105.9644);
  santa_fe.set_object_id(obj_id);
  santa_fe.set_timestamp(tracktable::time_from_string("2014-05-02 13:00:00"));

  roswell.set_latitude(33.3872);
  roswell.set_longitude(-104.5281);
  roswell.set_object_id(obj_id);
  roswell.set_timestamp(tracktable::time_from_string("2014-05-03 14:00:00"));

  trajectory_type path;

  if (path.object_id() != "(empty)")
    {
    std::cerr << "ERROR: Expected trajectory object ID to be empty before points are added\n";
    ++error_count;
    }
  if (path.trajectory_id() != "(empty)")
    {
    std::cerr << "ERROR: Expected trajectory ID to be empty before points are added\n";
    ++error_count;
    }
  if (path.size() != 0)
    {
    std::cerr << "ERROR: Expected path size to be 0 before points are added\n";
    ++error_count;
    }

  path.push_back(albuquerque);
  path.push_back(santa_fe);
  path.push_back(roswell);

//  path.recompute_speed();
//  path.recompute_heading();
  path.set_property("double", test_double_property);
  path.set_property("string", test_string_property);
  path.set_property("timestamp", test_timestamp_property);

  if (path.object_id() != obj_id)
    {
    std::cerr << "ERROR: Expected trajectory object ID to be "
              << obj_id << " after adding points.  Instead it was "
              << path.object_id() << ".\n";
    ++error_count;
    }
  std::ostringstream sbuf;
  tracktable::imbue_stream_with_timestamp_output_format(sbuf, "%Y%m%d%H%M%S");
  sbuf << albuquerque.object_id()
       << "_"
       << albuquerque.timestamp()
       << "_"
       << roswell.timestamp();
  std::string expected_trajectory_id = sbuf.str();
  if (path.trajectory_id() != expected_trajectory_id)
    {
    std::cerr << "ERROR: Expected trajectory ID to be '"
              << expected_trajectory_id << "'.  Instead it was "
              << path.trajectory_id() << ".\n";
    ++error_count;
    }

  trajectory_type path2(path);
  trajectory_type path3 = path2;

  if (path2.trajectory_id() != path.trajectory_id() ||
      path3.trajectory_id() != path.trajectory_id())
    {
    std::cerr << "ERROR: Expected trajectory IDs to be equal after assignment.  Instead, the original is '"
              << path.trajectory_id()
              << "', the one from the copy constructor is '"
              << path2.trajectory_id()
              << "' and the one from operator= is '"
              << path3.trajectory_id() << "'.\n";
    ++error_count;
    }

  if (!path2.has_property("string"))
    {
    std::cerr << "ERROR: Expected copied path to have a string "
              << "property 'string'.  None was found.\n";
    ++error_count;
    }
  else
    {
    bool ok;
    std::string s_prop = path2.string_property("string", &ok);
    if (!ok)
      {
      std::cerr << "ERROR: Retrieving test property 'string' returned "
                << "FALSE for the OK value.\n";
      ++error_count;
      }
    else
      {
      if (s_prop != test_string_property)
        {
        std::cerr << "ERROR: Test string property should have had value '"
                  << test_string_property << "' "
                  << "but instead has '"
                  << s_prop << "'.\n";
        ++error_count;
        }
      }
    }

  if (!path2.has_property("double"))
    {
    std::cerr << "ERROR: Expected copied path to have a numeric "
              << "property 'double'.  None was found.\n";
    ++error_count;
    }
  else
    {
    bool ok;
    double d_prop = path2.real_property("double", &ok);
    if (!ok)
      {
      std::cerr << "ERROR: Retrieving test property 'double' returned "
                << "FALSE for the OK value.\n";
      ++error_count;
      }
    else
      {
      // This floating point comparison is fine because we expect to
      // get back the exact same bits that we put in.
      if (d_prop != test_double_property)
        {
        std::cerr << "ERROR: Test double property should have had value "
                  << test_double_property
                  << " but instead has '"
                  << d_prop << "'.\n";
        ++error_count;
        }
      }
    }

  if (!path2.has_property("timestamp"))
    {
    std::cerr << "ERROR: Expected copied path to have a timestamp "
              << "property 'timestamp'.  None was found.\n";
    ++error_count;
    }
  else
    {
    bool ok;
    tracktable::Timestamp ts_prop = path2.timestamp_property("timestamp", &ok);
    if (!ok)
      {
      std::cerr << "ERROR: Retrieving test property 'timestamp' returned "
                << "FALSE for the OK value.\n";
      ++error_count;
      }
    else
      {
      if (ts_prop != test_timestamp_property)
        {
        std::cerr << "ERROR: Test timestamp property should have had value "
                  << test_timestamp_property
                  << " but instead has '"
                  << ts_prop << "'.\n";
        ++error_count;
        }
      }
    }

  path.clear();

  return error_count;
}

int main(int /*argc*/, char* /*argv*/[])
{
  int error_count = test_trajectory();
  return error_count;
}
