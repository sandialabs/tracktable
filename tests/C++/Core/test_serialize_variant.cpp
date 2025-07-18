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

#include <tracktable/Core/PropertyValue.h>

#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>

#include <boost/serialization/variant.hpp>

#include <iostream>
#include <sstream>


template<typename thing_type>
thing_type serialized_copy(thing_type const& thing)
{
  thing_type restored_thing;

  std::ostringstream temp_out;
  boost::archive::text_oarchive archive_out(temp_out);
  archive_out << thing;

  std::istringstream temp_in(temp_out.str());
  boost::archive::text_iarchive archive_in(temp_in);
  archive_in >> restored_thing;

  return restored_thing;
}

// ----------------------------------------------------------------------

int check_for_error(std::string const& variant_type,
                    tracktable::PropertyValueT const& original,
                    tracktable::PropertyValueT const& restored)
{
  if (original != restored)
    {
    std::cerr << "ERROR: "
              << variant_type << " did not survive replication. "
              << "Original value is " << original
              << " and restored value is " << restored
              << " (claims type is "
              << tracktable::property_type_as_string(restored)
              << ").\n";
    return 1;
    }
  else
    {
    return 0;
    }
}

// ----------------------------------------------------------------------

int
test_property_variant_serialization()
{
  tracktable::PropertyValueT int32_variant(static_cast<int64_t>(1<<20));
  tracktable::PropertyValueT int64_variant(123456789012345ll);
  tracktable::PropertyValueT float_variant(3.14159);
  tracktable::PropertyValueT null_variant;
  tracktable::PropertyValueT string_variant("this is a test");
  tracktable::PropertyValueT timestamp_variant(
    tracktable::time_from_string("2010-01-02 03:04:05")
  );

  tracktable::PropertyValueT restored_int32_variant;
  tracktable::PropertyValueT restored_int64_variant;
  tracktable::PropertyValueT restored_float_variant;
  tracktable::PropertyValueT restored_null_variant;
  tracktable::PropertyValueT restored_string_variant;
  tracktable::PropertyValueT restored_timestamp_variant;

  restored_int32_variant = serialized_copy(int32_variant);
  restored_int64_variant = serialized_copy(int64_variant);
  restored_float_variant = serialized_copy(float_variant);
  restored_null_variant = serialized_copy(null_variant);
  restored_string_variant = serialized_copy(string_variant);
  restored_timestamp_variant = serialized_copy(timestamp_variant);

  int error_count = 0;
  error_count += check_for_error("int32", int32_variant, restored_int32_variant);
  error_count += check_for_error("int64", int64_variant, restored_int64_variant);
  error_count += check_for_error("float", float_variant, restored_float_variant);
  error_count += check_for_error("string", string_variant, restored_string_variant);
  error_count += check_for_error("timestamp", timestamp_variant, restored_timestamp_variant);

  // Nulls are never supposed to equal one another
  if (null_variant == restored_null_variant)
    {
    std::cerr << "ERROR: Restored null variant equals saved one.  "
              << "This shouldn't happen -- nulls can never equal each other.\n";
    error_count += 1;
    }

  return error_count;
}

// ----------------------------------------------------------------------



int
main(int , char **)
{
  int num_errors = 0;

  num_errors += test_property_variant_serialization();

  return num_errors;
}
