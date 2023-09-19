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
#include <iostream>

using tracktable::domain::terrestrial::base_point_type;
using tracktable::domain::terrestrial::trajectory_point_type;

int test_turn_angle()
{
  std::string obj_id("GreenChileExpress02");
  trajectory_point_type albuquerque, santa_fe, roswell;
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

  std::cout << "Turn angle from ABQ to Santa Fe to Roswell: "
            << signed_turn_angle(albuquerque, santa_fe, roswell)
            << "\n";
  return 0;
}

int test_terrestrial_trajectory_point()
{
  trajectory_point_type my_point;
  int error_count = 0;

  my_point.set_object_id("MyPoint");

  my_point.set_latitude(35.1107);
  my_point.set_longitude(-106.6100);

  trajectory_point_type other_point = my_point;

  my_point.set_property("heading", 45.f);
  my_point.set_property("speed", 100.f);

  if (other_point == my_point)
    {
    std::cerr << "ERROR: Points should not test equal after post-assignment changes\n";
    ++error_count;
    }

  std::cout << "Due northwest from Albuquerque: "
            << my_point << "\n";

  my_point.set_property("color", "green");
  my_point.set_property("power_level", 9000.f);


  std::cout << "Due northwest from Albuquerque after adding properties: "
            << my_point << "\n";

  other_point = my_point;

  if (other_point != my_point)
    {
    std::cerr << "ERROR: Points should test equal after reassignment\n";
    ++error_count;
    }

  bool present;

  if (my_point.has_property("color"))
    {
    std::cout << "Color of point: " << my_point.string_property("color", &present) << "\n";
    if (present == false)
      {
      std::cerr << "ERROR: Presence flag for color set to false\n";
      ++error_count;
      }
    }
  else
    {
    std::cerr << "ERROR: Couldn't find color property in point\n";
    ++error_count;
    }

  if (my_point.has_property("power_level"))
    {
    std::cout << "Power level of point: " << my_point.real_property("power_level", &present) << "\n";
    if (present == false)
      {
      std::cerr << "ERROR: Presence flag for power_level set to false\n";
      ++error_count;
      }
    }
  else
    {
    std::cerr << "ERROR: Couldn't find power_level property in point\n";
    ++error_count;
    }

  if (my_point.has_property("no_such_property"))
    {
    std::cerr << "ERROR: Property no_such_property erroneously claimed to be present\n";
    ++error_count;
    }

  tracktable::PropertyValueT my_variant(my_point.property("color", &present));
  if (!present)
    {
    std::cerr << "ERROR: Direct access to 'color' property returned present==false\n";
    ++error_count;
    }
  std::cout << "Direct access to color property: "
            << boost::get<std::string>(my_variant) << "\n";


  std::cout << "Trying to access properties with wrong type.  Expect error messages here.  The program will crash if it doesn't work.\n";
  my_point.real_property("color");
  my_point.string_property("power_level");

  error_count += test_turn_angle();
  return error_count;

}


int main(int /*argc*/, char* /*argv*/[])
{
  return test_terrestrial_trajectory_point();
}
