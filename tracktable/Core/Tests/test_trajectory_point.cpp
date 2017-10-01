/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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

#include <tracktable/Core/TrajectoryPoint.h>
#include <iostream>

bool test_surface_trajectory_point()
{
  tracktable::TrajectoryPoint my_point;
  int error_count = 0;

  my_point.set_object_id("MyPoint");

  my_point.set_latitude(35.1107);
  my_point.set_longitude(-106.6100);

  tracktable::TrajectoryPoint other_point = my_point;

  my_point.set_heading(45);
  my_point.set_speed(100);

  if (other_point == my_point)
    {
    std::cerr << "ERROR: Points should not test equal after post-assignment changes\n";
    ++error_count;
    }

  std::cout << "Due northwest from Albuquerque: "
            << my_point << "\n";

  my_point.set_property("color", "green");
  my_point.set_property("power_level", 9000);


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
    std::cout << "Power level of point: " << my_point.numeric_property("power_level", &present) << "\n";
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
  double foo = my_point.numeric_property("color");
  std::string bar = my_point.string_property("power_level");

  return (error_count == 0);
}


int main(int argc, char* argv[])
{
  bool status = test_surface_trajectory_point();
  if (status)
    {
    return 0;
    }
  else
    {
    return 1;
    }
}
