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


#ifndef __tracktable_TimestampConverter_h
#define __tracktable_TimestampConverter_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/TracktableCoreWindowsHeader.h>
#include <sstream>

namespace tracktable {

#if defined(WIN32)
# pragma warning( push )
# pragma warning( disable : 4251 )
#endif

/**
 * TimestampConverter - timestamp to/from string
 *
 * We need to be able to convert strings to `tracktable::Timestamp`
 * instances and the reverse while using custom time input/output
 * facets. There are enough differences in the way locales are
 * implemented across platforms that I insist on encapsulating it in
 * this class. We will use this in readers and writers.
 */
class TRACKTABLE_CORE_EXPORT TimestampConverter
{
 public:
  TimestampConverter();
  virtual ~TimestampConverter();

  TimestampConverter(TimestampConverter const& other);
  TimestampConverter& operator=(TimestampConverter const& other);
  bool operator==(TimestampConverter const& other) const;
  bool operator!=(TimestampConverter const& other) const;

  /** Set format string for parsing timestamps
   *
   * This format string must adhere to the guidelines in the
   * documentation for Boost's date/time input format. See the
   * following page:
   *
   * http://www.boost.org/doc/libs/master/doc/html/date_time/date_time_io.html
   *
   * @param [in] format Format string for timestamp parsing
   */
  void set_input_format(string_type const& format);

  /** Return the current input format
   *
   * @return Format string for timestamp parsing
   */

  string_type input_format() const;

 /** Set format string for writing timestamps to strings
   *
   * This format string must adhere to the guidelines in the
   * documentation for Boost's date/time input format. See the
   * following page:
   *
   * http://www.boost.org/doc/libs/master/doc/html/date_time/date_time_io.html
   *
   * @param [in] format Format string for timestamp output
   */

  void set_output_format(string_type const& format);

  /** Return the current output format
   *
   * @return Format string for timestamp output
   */

  string_type output_format() const;

  /** Convert a timestamp to a string
   *
   * Convert a timestamp to a string according to the current output
   * format.
   *
   * @param [in] timestamp  Timestamp to write
   * @return String representation of timestamp
   */
  string_type timestamp_to_string(Timestamp const& timestamp) const;

  /** Convert a string to a timestamp
   *
   * Parse a string to create a timestamp according to the current
   * input format.
   *
   * @param [in] time_string  Timestamp represented as string
   * @return Timestamp parsed from string
   */
  Timestamp timestamp_from_string(string_type const& time_string) const;

 private:
  string_type InputFormat;
  string_type OutputFormat;

  mutable std::ostringstream OutputBuf;
  mutable std::istringstream InputBuf;

};


#if defined(WIN32)
# pragma warning( pop )
#endif

} // close namespace tracktable

#endif
