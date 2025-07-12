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
#include <boost/date_time/gregorian/gregorian.hpp>
#include <time.h>

int test_timestamp_io(std::string const& time_as_string,
		      tracktable::Timestamp const& expected,
		      std::string const& format)
{
  int error_count = 0;
  tracktable::TimestampConverter converter;

  converter.set_input_format(format);
  converter.set_output_format(format);

  std::cout << "Reading timestamp from string '" << time_as_string
            << " with format " << format << ".\n";
  tracktable::Timestamp in_time = converter.timestamp_from_string(time_as_string);
  if (in_time != expected)
  {
    std::cout << "ERROR: Expected parsed time to be "
	      << expected << " but got " << in_time
	      << ".\n";
    ++error_count;
  }
  else
    {
      std::cout << "Read OK.\n";
  }
  std::cout << "Writing timestamp back to string.\n";
  std::string out_time = converter.timestamp_to_string(in_time);

  if (out_time != time_as_string)
  {
    std::cout << "ERROR: Expected time output to be '"
	      << time_as_string << "' but got '"
	      << out_time << "'.\n";
    ++error_count;
  }
  else
    {
      std::cout << "Write OK.\n";
    }

  return error_count;
}

int test_timestamp_format()
{
  std::string time1("2014-04-05 12:34:56");
  std::string time2("2014:04:05::12:34:56");
  std::string time3("Apr 05 2014 12:34:56");

  std::string format1("%Y-%m-%d %H:%M:%S");
  std::string format2("%Y:%m:%d::%H:%M:%S");
  std::string format3("%b %d %Y %H:%M:%S");

  using boost::gregorian::date;

  tracktable::Timestamp expected_result(tracktable::Date(2014, 04, 05), tracktable::Duration(12, 34, 56));

  int error_count = 0;

  error_count += test_timestamp_io(time1, expected_result, format1);
  error_count += test_timestamp_io(time2, expected_result, format2);
  error_count += test_timestamp_io(time3, expected_result, format3);

  return error_count;
}

int main(int /*argc*/, char* /*argv*/[])
{
  return test_timestamp_format();
}
