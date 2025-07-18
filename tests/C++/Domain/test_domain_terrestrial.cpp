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

#include <tracktable/Domain/Terrestrial.h>

using tracktable::domain::terrestrial::base_point_type;
using tracktable::domain::terrestrial::trajectory_point_type;
using tracktable::domain::terrestrial::trajectory_type;


int test_base_point_type()
{
  base_point_type albuquerque;
  base_point_type santa_fe;
  base_point_type roswell;

  albuquerque.set_latitude(35.1107);
  albuquerque.set_longitude(-106.6100);

  santa_fe.set_latitude(35.6672);
  santa_fe.set_longitude(-105.9644);

  roswell.set_latitude(33.3872);
  roswell.set_longitude(-104.5281);

  // The distance from Albuquerque to Santa Fe is about 100km.  The
  // distance from Santa Fe to Roswell is about 320 km.
  double abq_sf_distance = tracktable::distance(albuquerque, santa_fe);
  double sf_rw_distance = tracktable::distance(santa_fe, roswell);

  std::cout << "Distances:\n";
  std::cout << "\tAlbuquerque - Santa Fe: "
            << abq_sf_distance << " km\n";
  std::cout << "\tSanta Fe - Roswell: "
            << sf_rw_distance << " km\n";

  return 0;
}

// ----------------------------------------------------------------------

int test_trajectory_point_type()
{
  trajectory_point_type albuquerque;
  trajectory_point_type santa_fe;
  trajectory_point_type roswell;

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

  // The distance from Albuquerque to Santa Fe is about 100km.  The
  // distance from Santa Fe to Roswell is about 320 km.
  double abq_sf_distance = tracktable::distance(albuquerque, santa_fe);
  double sf_rw_distance = tracktable::distance(santa_fe, roswell);
  double abq_sf_speed = tracktable::speed_between(albuquerque, santa_fe);
  double sf_rw_speed = tracktable::speed_between(santa_fe, roswell);

  std::cout << "Distances:\n";
  std::cout << "\tAlbuquerque - Santa Fe: "
            << abq_sf_distance << " km\n";
  std::cout << "\tSanta Fe - Roswell: "
            << sf_rw_distance << " km\n";

  std::cout << "Speeds (expect same as distance):\n";
  std::cout << "\tAlbuquerque - Santa Fe: "
            << abq_sf_speed << " km/h\n";
  std::cout << "\tSanta Fe - Roswell: "
            << sf_rw_speed << " km/h\n";

  return 0;
}

// ----------------------------------------------------------------------

int test_trajectory_type()
{
  trajectory_point_type albuquerque;
  trajectory_point_type santa_fe;
  trajectory_point_type roswell;
  trajectory_type path;

  std::string obj_id("GreenChileExpress001");
  albuquerque.set_latitude(35.1107);
  albuquerque.set_longitude(-106.6100);
  albuquerque.set_object_id(obj_id);
  albuquerque.set_timestamp(tracktable::time_from_string("2014-05-01 12:00:00"));

  santa_fe.set_latitude(35.6672);
  santa_fe.set_longitude(-105.9644);
  santa_fe.set_object_id(obj_id);
  santa_fe.set_timestamp(tracktable::time_from_string("2014-05-01 13:00:00"));

  roswell.set_latitude(33.3872);
  roswell.set_longitude(-104.5281);
  roswell.set_object_id(obj_id);
  roswell.set_timestamp(tracktable::time_from_string("2014-05-01 14:00:00"));

  path.push_back(albuquerque);
  path.push_back(santa_fe);
  path.push_back(roswell);

  return 0;
}


// ----------------------------------------------------------------------

int test_domain()
{
  int error_count = 0;
  error_count += test_base_point_type();
  error_count += test_trajectory_point_type();
  error_count += test_trajectory_type();

  return error_count;
}

// ----------------------------------------------------------------------

int main(int /*argc*/, char* /*argv*/[])
{
  return test_domain();
}



