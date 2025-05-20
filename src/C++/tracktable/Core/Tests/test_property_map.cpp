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

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/PropertyMap.h>

bool
test_property_map()
{
  int error_count = 0;

  tracktable::PropertyMap properties;

  double test_double_input = 3.14159;
  std::string test_string_input("Four score and seven years ago...");
  tracktable::Timestamp test_time_input(tracktable::time_from_string("1969-06-20 16:17:40"));
  tracktable::NullValue test_null_input(tracktable::TYPE_NULL);

  tracktable::set_property(properties, "real_test", test_double_input);
  tracktable::set_property(properties, "string_test", test_string_input);
  tracktable::set_property(properties, "time_test", test_time_input);
  tracktable::set_property(properties, "null_test", test_null_input);

  if (tracktable::has_property(properties, "real_test") == false)
    {
    std::cerr << "ERROR: Property 'real_test' should be present\n";
    ++error_count;
    }
  if (tracktable::has_property(properties, "string_test") == false)
    {
    std::cerr << "ERROR: Property 'string_test' should be present\n";
    ++error_count;
    }
  if (tracktable::has_property(properties, "time_test") == false)
    {
    std::cerr << "ERROR: Property 'time_test' should be present\n";
    ++error_count;
    }
  if (tracktable::has_property(properties, "null_test") == false)
    {
    std::cerr << "ERROR: Property 'null_test' should be present\n";
    ++error_count;
    }
  if (tracktable::has_property(properties, "no_such_property"))
    {
    std::cerr << "ERROR: Property 'no_such_property' should not be present\n";
    ++error_count;
    }

  double test_double;
  std::string test_string;
  tracktable::Timestamp test_time;
  tracktable::NullValue test_null;
  bool ok;

  std::cout << "Retrieving properties with correct types\n";

  test_double = tracktable::real_property(properties, "real_test", &ok);
  if (ok == false)
    {
    std::cerr << "ERROR: OK flag was set to false when retrieving numeric property\n";
    ++error_count;
    }
  if (!tracktable::almost_equal(test_double, test_double_input))
    {
    std::cerr << "ERROR: Test double value was not what we put in.  Started with "
              << test_double_input << ", got back "
              << test_double << "\n";
    ++error_count;
    }


  test_string = tracktable::string_property(properties, "string_test", &ok);
  if (ok == false)
    {
    std::cerr << "ERROR: OK flag was set to false when retrieving string property\n";
    ++error_count;
    }
  if (test_string != test_string_input)
    {
    std::cerr << "ERROR: Test string value was not what we put in.  Started with "
              << test_string_input << ", got back "
              << test_string << "\n";
    ++error_count;
    }


  test_time = tracktable::timestamp_property(properties, "time_test", &ok);
  if (ok == false)
    {
    std::cerr << "ERROR: OK flag was set to false when retrieving time property\n";
    ++error_count;
    }
  if (test_time != test_time_input)
    {
    std::cerr << "ERROR: Test time value was not what we put in.  Started with "
              << test_time_input << ", got back "
              << test_time << "\n";
    ++error_count;
    }

  test_null = tracktable::nullvalue_property(properties, "null_test", &ok);
  if (ok == false)
    {
    std::cerr << "ERROR: OK flag was set to false when retrieving null property\n";
    ++error_count;
    }
  if (!is_property_null(test_null))
    {
    std::cerr << "ERROR: Test null property value was not null.  Value is "
              << test_null << "\n";
    ++error_count;
    }

  std::cout << "Attempting to retrieve properties with incorrect types.  Expect the next four lines to be error messages.\n";

  tracktable::real_property(properties, "time_test", &ok);
  if (ok)
    {
    std::cerr << "REAL ERROR: Property 'time_test' was successfully retrieved as a number according to the OK flag.\n";
    ++error_count;
    }

  tracktable::string_property(properties, "real_test", &ok);
  if (ok)
    {
    std::cerr << "REAL ERROR: Property 'real_test' was successfully retrieved as a string according to the OK flag.\n";
    ++error_count;
    }

  tracktable::timestamp_property(properties, "string_test", &ok);
  if (ok)
    {
    std::cerr << "REAL ERROR: Property 'string_test' was successfully retrieved as a timestamp according to the OK flag.\n";
    ++error_count;
    }

  tracktable::timestamp_property(properties, "null_test", &ok);
  if (ok)
    {
    std::cerr << "REAL ERROR: Property 'null_test' was successfully retrieved as a null according to the OK flag.\n";
    ++error_count;
    }
  return (error_count == 0);
}


int main(int /*argc*/, char* /*argv*/[])
{
  bool result = test_property_map();
  if (result)
    {
    return 0;
    }
  else
    {
    return 1;
    }
}
