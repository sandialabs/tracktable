/*
 * Copyright (c) 2015, Sandia Corporation.  All rights
 * reserved.
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


/*
 * PropertyConverter - PropertyValueT to/from string
 *
 * We need to be able to convert strings to PropertyValueT instances
 * and the reverse while using custom settings for decimal precision
 * and time format.  There are enough differences in the way locales
 * are implemented across platforms that I insist on encapsulating it
 * in this class.  We will use this in readers and writers.
 */

#ifndef __tracktable_PropertyConverter_h
#define __tracktable_PropertyConverter_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/TimestampConverter.h>
#include <tracktable/Core/TracktableCoreWindowsHeader.h>
#include <sstream>

namespace tracktable {


#if defined(WIN32)
# pragma warning( push )
# pragma warning( disable : 4251 )
#endif

class TRACKTABLE_CORE_EXPORT PropertyConverter
{
 public:

  PropertyConverter();
  virtual ~PropertyConverter();

  PropertyConverter(PropertyConverter const& other);
  PropertyConverter& operator=(PropertyConverter const& other);
  bool operator==(PropertyConverter const& other) const;
  bool operator!=(PropertyConverter const& other) const;

  /** Set format string for parsing timestamps
   *
   * This format string must adhere to the guidelines in the
   * documentation for Boost's date/time input format.  See the
   * following page:
   *
   * http://www.boost.org/doc/libs/master/doc/html/date_time/date_time_io.html
   *
   * @param[in] format Format string for timestamp parsing
   */
  void set_timestamp_input_format(string_type const& format);

  /** Return the current input format
   *
   * @return Format string for timestamp parsing
   */

  string_type timestamp_input_format() const;

 /** Set format string for writing timestamps to strings
   *
   * This format string must adhere to the guidelines in the
   * documentation for Boost's date/time input format.  See the
   * following page:
   *
   * http://www.boost.org/doc/libs/master/doc/html/date_time/date_time_io.html
   *
   * @param[in] format Format string for timestamp output
   */

  void set_timestamp_output_format(string_type const& format);

  /** Return the current output format
   *
   * @return Format string for timestamp output
   */

  string_type timestamp_output_format() const;

  /** Set string that represents null values
   *
   * @param[in] null_value String to stand in for nulls
   */

  void set_null_value(string_type const& null_value);

  /** Get string that represents null values
   *
   * @return String representing null
   */

  string_type null_value() const;

  /** Set number of digits of precision for writing real numbers
   *
   * @param[in] digits Number of digits to use
   */

  void set_decimal_precision(std::size_t digits);


  /** Get number of digits of precision for writing real numbers
   *
   * @return Number of digits in use
   */

  std::size_t decimal_precision() const;

  /** Convert a property to a string
   *
   * Convert a property to a string according to the current output
   * format.
   *
   * @param[in] property  Value to write
   * @return String representation of timestamp
   */
  string_type property_to_string(PropertyValueT const& property);

  /** Convert a string and type ID to a property
   *
   * Parse a string to create a property value according to the
   * current input formats and the requested output type.
   *
   * @param[in] prop_string  Property represented as string
   * @param[in] prop_type    Property type (see tracktable::PropertyUnderlyingType)
   * @return Property parsed from string
   */
  PropertyValueT property_from_string(string_type const& prop_string,
				      PropertyUnderlyingType prop_type);


  TimestampConverter* timestamp_converter();

 private:
  std::size_t DecimalPrecision;
  std::string NullValue;
  TimestampConverter TimestampReadWrite;
  std::ostringstream OutputBuf;
  std::istringstream InputBuf;
};


#if defined(WIN32)
# pragma warning( pop )
#endif

} // close namespace tracktable

#endif
