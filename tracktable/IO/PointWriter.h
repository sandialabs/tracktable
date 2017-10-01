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

/** Write points of any type as delimited text
 *
 * This class writes a sequence of points to a file in delimited text
 * format.  You can control the destination, the delimiter, the record
 * separator (usually newline) and whether or not a header line is
 * written.
 *
 * The header line contains information about the point's dimension,
 * coordinate system, object ID and timestamp (for trajectory points)
 * and custom properties (if any).
 */

#ifndef __TRACKTABLE_POINT_WRITER_H
#define __TRACKTABLE_POINT_WRITER_H

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointTraits.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/PropertyConverter.h>

#include <tracktable/IO/detail/CountProperties.h>
#include <tracktable/IO/detail/PointHeader.h>
#include <tracktable/IO/detail/WriteObjectId.h>
#include <tracktable/IO/detail/WriteTimestamp.h>
#include <tracktable/IO/detail/PropertyMapReadWrite.h>
#include <tracktable/IO/detail/PointHeader.h>
#include <tracktable/IO/TokenWriter.h>

#include <locale>
#include <stdexcept>
#include <boost/lexical_cast.hpp>
#include <boost/throw_exception.hpp>

namespace tracktable { namespace io { namespace detail {

template<typename point_t, typename out_iter_t>
void do_write_coordinates(point_t const& point, std::size_t coordinate_precision, out_iter_t destination)
{
  tracktable::ostringstream_type outbuf;
  outbuf.precision(coordinate_precision);

  for (std::size_t i = 0;
       i < std::size_t(::tracktable::traits::dimension<point_t>::value);
       ++i)
    {
    outbuf << point[i];
    (*destination++) = outbuf.str();
    outbuf.str(tracktable::string_type());
    }
}

template<typename point_t, typename out_iter_t>
void do_write_object_id(point_t const& point, out_iter_t destination)
{
  write_object_id<
    traits::has_object_id<point_t>::value
    >::apply(point, destination);
}

template<typename point_t, typename out_iter_t>
void do_write_timestamp(point_t const& point, TimestampConverter *formatter, out_iter_t destination)
{
  write_timestamp<
    traits::has_timestamp<point_t>::value
    >::apply(point, *formatter, destination);
}

template<typename point_t, typename out_iter_t>
void do_write_properties(point_t const& point, PropertyConverter& formatter, out_iter_t destination, int expected_num_properties)
{
  write_property_map_values<
    traits::has_properties<point_t>::value
    >::apply(point, formatter, destination, expected_num_properties);
}

} } } // close tracktable::io::detail


namespace tracktable {

// XXX Do I need _dllexport / _dllimport for classes with template members?

// XXX What else do I need to change in order to make this work with
// multiple string types?
class PointWriter
{
public:

  PointWriter()
    {
      this->set_default_configuration();
    }

  PointWriter(PointWriter const& other)
    : CoordinatePrecision(other.CoordinatePrecision)
    , PropertyWriter(other.PropertyWriter)
    , TimestampFormat(other.TimestampFormat)
    , TokenSink(other.TokenSink)
    , WriteHeader(other.WriteHeader)
    {
    }

  PointWriter(std::ostream& output)
    {
      this->set_default_configuration();
      this->set_output(output);
    }

  PointWriter& operator=(PointWriter const& other)
    {
      this->TokenSink = other.TokenSink;
      this->WriteHeader = other.WriteHeader;
      this->TimestampFormat = other.TimestampFormat;
      this->CoordinatePrecision = other.CoordinatePrecision;
      this->PropertyWriter = other.PropertyWriter;
      return *this;
    }

  bool operator==(PointWriter const& other) const
    {
      return (
	      this->CoordinatePrecision == other.CoordinatePrecision
	      && this->PropertyWriter == other.PropertyWriter
	      && this->TimestampFormat == other.TimestampFormat
	      && this->TokenSink == other.TokenSink
	      && this->WriteHeader == other.WriteHeader
	      );
    }

  bool operator!=(PointWriter const& other) const
    {
      return ( (*this == other) == false );
    }

  /** Set the stream where points will be written
   *
   * This can be any std::ostream.
   *
   * NOTE: You are resposible for ensuring that the stream does not go
   * out of scope until you are done writing points.
   *
   * @param[in] output_stream Stream where points will be written
   */

  void set_output(std::ostream& out)
    {
      this->TokenSink.set_output(out);
    }

  /** Return the stream where points will be written
   *
   */
  std::ostream& output() const
    {
      return this->TokenSink.output();
    }

  /** Set the field delimiter
   *
   * This string will be inserted between each field as points are
   * written.
   *
   * @param[in] delimiter Delimiter string
   */

  void set_field_delimiter(string_type const& delim)
    {
      this->TokenSink.set_field_delimiter(delim);
    }

  /** Return the field delimiter
   */
  string_type field_delimiter() const
    {
      return this->TokenSink.field_delimiter();
    }

  /** Set the record separator (end-of-line string)
   *
   * This string will be written after each point.  By default it's
   * std::endl (the newline string).
   *
   * @param[in] separator: String separator
   */
  void set_record_delimiter(string_type const& sep)
    {
      this->TokenSink.set_record_delimiter(sep);
    }

  /** Set format for writing timestamps
   *
   * There are as many ways to write timestamps as there are programs
   * to write them.  We have our default (YYYY-MM-DD HH:MM:SS) but
   * sometimes you will need to specify some other format for
   * interoperability.
   *
   * This method sets a format string for timestamps using the flags
   * in boost::date_time::time_facet.  If you do not call it,
   *
   * @param[in] format Format string for timestamps
   */

   void set_timestamp_format(string_type const& format)
   {
     this->TimestampFormat = format;
     this->PropertyWriter.set_timestamp_output_format(format);
   }

  string_type timestamp_format() const
  {
    return this->TimestampFormat;
  }

  /** Return the record separator (end-of-line string)
   */

  string_type record_delimiter() const
    {
      return this->TokenSink.record_delimiter();
    }

  /** Set the quote character
   *
   * This character *may* be used to enclose a field containing lots
   * of characters that would otherwise need to be escaped.  We have
   * to know what it is so that we can escape it ourselves when we
   * encounter the quote character inside fields.
   *
   * @param[in] quotes: Zero or one character to be used as
   * quotation marks
   */
  void set_quote_character(string_type const& quotes)
    {
      this->TokenSink.set_quote_character(quotes);
    }

  /** Return the current quote characters
   */

  string_type quote_character() const
    {
      return this->TokenSink.quote_character();
    }

  /** Set whether or not to write a header
   *
   * The header string describes the contents of a point: coordinate
   * system, properties (if any), number of coordinates.  By default
   * it will be written at the beginning of a sequence of points.  You
   * can turn it off with this function.
   *
   * @param[in] onoff Boolean flag
   */
  void set_write_header(bool onoff)
    {
      this->WriteHeader = onoff;
    }

  /** Return whether or not the header will be written
   */
  bool write_header() const
    {
      return this->WriteHeader;
    }

  template<typename point_iter_type>
  int write(point_iter_type point_begin,
            point_iter_type point_end)
    {
      typedef typename point_iter_type::value_type point_type;

      if (point_begin == point_end)
        {
        // We can't even write a header without points to work with
        return 0;
        }

      // The difference between write() and write_to_tokens() is that
      // write() inserts record separators after the header and after
      // each point.  Otherwise we would just call write_to_tokens()
      // here.
      string_vector_type tokens;
      if (this->WriteHeader)
        {
        this->write_point_header_tokens(*point_begin,
                                        std::back_inserter(tokens));
        }
      this->write_tokens_to_stream(tokens.begin(), tokens.end());

      int num_points_written = 0;
      while (point_begin != point_end)
        {
        tokens.clear();
        int num_properties_expected = io::detail::count_properties<
          traits::has_properties<point_type>::value
          >::apply(*point_begin);
        this->write_point_tokens(*point_begin, std::back_inserter(tokens),
                                 num_properties_expected);
        this->write_tokens_to_stream(tokens.begin(), tokens.end());
        ++point_begin;
        ++num_points_written;
        }
	return num_points_written;
    }

  /** Set the decimal precision for writing coordinates
   *
   * Internally, Tracktable stores coordinates as double-precision
   * floating numbers.  It is highly unlikely that trajectory data
   * needs absolutely all of that precision.  Since it takes up lots
   * of space when we write data to disk, it is useful to be able to
   * ask for reduced (or increased) precision.
   *
   * @param[in] num_digits   Number of digits of precision
   */
  void set_coordinate_precision(std::size_t num_digits)
    {
      this->CoordinatePrecision = num_digits;
      this->PropertyWriter.set_decimal_precision(num_digits);
    }

  std::size_t coordinate_precision() const
    {
      return this->CoordinatePrecision;
    }

  /** Set the string representation for nulls
   *
   * Property values that were never set are considered to hold a null
   * value.  This method lets you set how nulls will be written to
   * disk.  The default value is the empty string "".
   *
   * @param[in] null_value   Desired string representation of nulls
   */

  void set_null_value(string_type const& null_value)
    {
      this->PropertyWriter.set_null_value(null_value);
    }

  string_type null_value() const
    {
      return this->PropertyWriter.null_value();
    }

private:
  friend class TrajectoryWriter;

  std::size_t                  CoordinatePrecision;
  PropertyConverter            PropertyWriter;
  string_type                  TimestampFormat;
  TokenWriter                  TokenSink;
  bool                         WriteHeader;

  void set_default_configuration()
    {
      this->set_coordinate_precision(8);
      this->set_field_delimiter(",");
      this->set_null_value("");
      this->set_quote_character("\"");
      this->set_record_delimiter("\n");
      this->set_timestamp_format("%Y-%m-%d %H:%M:%S");
      this->set_write_header(true);
    }

  //
  // Header structure:
  //
  // 1.  Header token (currently *P*)
  // 2.  Domain
  // 3.  Dimension
  // 4.  HasObjectId
  // 5.  HasTimestamp
  // 6.  Number of properties
  // 7, 8: name, type of custom property #1
  // 9, 10: name, type of custom property #2
  // (etc)

  template<typename point_type, typename out_iter_type>
  void write_point_header_tokens(point_type const& example_point,
                                 out_iter_type output)
    {
      io::detail::PointHeader header;
      header.populate_from_point(example_point);
      header.write_as_tokens(output);
    }

  // ----------------------------------------------------------------------

  template<typename point_iter_type, typename out_iter_type>
  int write_many_points_to_tokens(point_iter_type point_begin,
                                  point_iter_type point_end,
                                  out_iter_type output)
    {
      if (this->WriteHeader)
        {
	  this->write_point_header_tokens(*point_begin, output);
        }

      int num_properties_expected = io::detail::count_properties<
        traits::has_properties<typename point_iter_type::value_type>::value
        >::apply(*point_begin);
      int num_points_written = 0;
      for (point_iter_type here = point_begin;
           here != point_end;
           ++here)
        {
        this->write_point_tokens(*here, output, num_properties_expected);
        ++num_points_written;
        }
      return num_points_written;
    }

  // ----------------------------------------------------------------------

  template<typename point_type, typename out_iter_type>
  void write_point_tokens(point_type const& point,
                          out_iter_type output,
                          int num_properties_expected)
    {
      io::detail::do_write_object_id(point, output);
      io::detail::do_write_timestamp(point, this->PropertyWriter.timestamp_converter(), output);
      io::detail::do_write_coordinates(point, this->CoordinatePrecision, output);
      io::detail::do_write_properties(point, this->PropertyWriter, output, num_properties_expected);
    }

  template<typename token_iter_type>
  void write_tokens_to_stream(token_iter_type begin, token_iter_type end)
    {
      this->TokenSink.write_record(begin, end);
    }

};

} // close namespace tracktable

#endif
