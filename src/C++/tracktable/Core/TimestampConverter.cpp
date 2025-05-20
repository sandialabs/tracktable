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

#include <locale>
#include <boost/date_time/posix_time/posix_time.hpp>

namespace tracktable {

TimestampConverter::TimestampConverter()
{
  this->set_input_format(default_timestamp_input_format());
  this->set_output_format(default_timestamp_output_format());
}

TimestampConverter::~TimestampConverter()
{
}

TimestampConverter::TimestampConverter(TimestampConverter const& other)
  : InputFormat(other.InputFormat)
  , OutputFormat(other.OutputFormat)
{
  this->InputBuf.imbue(other.InputBuf.getloc());
  this->OutputBuf.imbue(other.OutputBuf.getloc());
}

  TimestampConverter& TimestampConverter::operator=(TimestampConverter const& other)
{
  this->InputFormat = other.InputFormat;
  this->OutputFormat = other.OutputFormat;
  this->InputBuf.imbue(other.InputBuf.getloc());
  this->OutputBuf.imbue(other.OutputBuf.getloc());

  return *this;
}

bool TimestampConverter::operator==(TimestampConverter const& other) const
{
  return (
	  this->InputFormat == other.InputFormat
	  && this->OutputFormat == other.OutputFormat
	  );
}

bool TimestampConverter::operator!=(TimestampConverter const& other) const
{
  return !(*this == other);
}

  string_type TimestampConverter::timestamp_to_string(Timestamp const& timestamp) const
  {
    this->OutputBuf.str(string_type());
    this->OutputBuf << timestamp;
    return this->OutputBuf.str();
  }

  Timestamp TimestampConverter::timestamp_from_string(string_type const& in_string) const
  {
    this->InputBuf.str(in_string);
    Timestamp ts;
    this->InputBuf >> ts;
    return ts;
  }

  void TimestampConverter::set_input_format(string_type const& format)
  {
    this->InputFormat = format;

    typedef boost::posix_time::time_input_facet input_facet_t;
    input_facet_t* facet = new input_facet_t(format.c_str());
    this->InputBuf.imbue(std::locale(this->InputBuf.getloc(), facet));
  }

  void TimestampConverter::set_output_format(string_type const& format)
  {
    this->OutputFormat = format;

    typedef boost::posix_time::time_facet output_facet_t;
    output_facet_t* facet = new output_facet_t(format.c_str());
    this->OutputBuf.imbue(std::locale(this->OutputBuf.getloc(), facet));
  }

  string_type TimestampConverter::input_format() const
  {
    return this->InputFormat;
  }

  string_type TimestampConverter::output_format() const
  {
    return this->OutputFormat;
  }
}
