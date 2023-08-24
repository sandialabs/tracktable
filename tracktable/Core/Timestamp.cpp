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


#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/TimestampConverter.h>

#include <boost/date_time/time_facet.hpp>

#include <locale>


namespace tracktable {


namespace detail {

string_type DefaultTimestampOutputFormat("%Y-%m-%d %H:%M:%S");
string_type DefaultTimestampInputFormat("%Y-%m-%d %H:%M:%S");
}

Timestamp time_from_string(std::string const& tstring)
{
  static TimestampConverter converter;
  return converter.timestamp_from_string(tstring);
}

std::string time_to_string(Timestamp const& ts)
{
  static TimestampConverter converter;
  return converter.timestamp_to_string(ts);
}

Timestamp no_such_timestamp()
{
  return boost::posix_time::ptime(boost::posix_time::not_a_date_time);
}

bool is_timestamp_valid(Timestamp const& t)
{
  return (false == t.is_not_a_date_time());
}

Timestamp truncate_fractional_seconds(Timestamp const& input)
{
  boost::posix_time::time_duration timeofday = input.time_of_day();
  return input - boost::posix_time::time_duration(0, 0, 0, timeofday.fractional_seconds());
}

Timestamp round_to_nearest_second(Timestamp const& input)
{
  return truncate_fractional_seconds(input + milliseconds(500));
}

Duration hours(int h)
{
  return Duration(h, 0, 0);
}

Duration minutes(int m)
{
  return Duration(0, m, 0);
}

Duration seconds(int s)
{
  return Duration(0, 0, s);
}

Duration milliseconds(int64_t ms)
{
  return boost::posix_time::milliseconds(ms);
}

Duration microseconds(int64_t us)
{
  return boost::posix_time::microseconds(us);
}

Duration days(int d)
{
  return Duration(24 * d, 0, 0);
}

void set_default_timestamp_output_format(string_type const& new_format)
{
  detail::DefaultTimestampOutputFormat = new_format;
}

string_type default_timestamp_output_format()
{
  return detail::DefaultTimestampInputFormat;
}

void set_default_timestamp_input_format(string_type const& new_format)
{
  detail::DefaultTimestampOutputFormat = new_format;
}

string_type default_timestamp_input_format()
{
  return detail::DefaultTimestampInputFormat;
}



END_NAMESPACE(tracktable)
