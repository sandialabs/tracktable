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

#ifndef __tracktable_TrajectoryWriter_h
#define __tracktable_TrajectoryWriter_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/PropertyConverter.h>

#include <tracktable/RW/PointWriter.h>
#include <tracktable/RW/TokenWriter.h>

#include <tracktable/RW/detail/HeaderStrings.h>
#include <tracktable/RW/detail/TrajectoryHeader.h>
#include <tracktable/RW/detail/PropertyMapReadWrite.h>

#include <iterator>
#include <iostream>
#include <cassert>
#include <stdexcept>
#include <vector>

namespace tracktable {

/** Write trajectories of any type as delimited text
 *
 * This class writes subclasses of tracktable::Trajectory (including
 * the domain classes) to a stream as delimited text. It will write
 * one trajectory per line. The resulting file will contain enough
 * header information to reconstruct the trajectory exactly as long as
 * the user asks for the correct class.
 */

class TrajectoryWriter
{
public:
  /** Instantiate TrajectoryWriter using a default configuration
   *
   * @copydoc TrajectoryWriter::set_default_configuration()
   */
  TrajectoryWriter()
    : OutputStream(0)
	{
	this->set_default_configuration();
	}

  /** Instantiate a TrajectoryWriter using a `std::ostream` and default configuration
   *
   * @copydoc TrajectoryWriter::set_default_configuration()
   *
   * @param [in] _output Stream to output to
   */
  TrajectoryWriter(std::ostream& _output)
    : OutputStream(&_output)
	{
	this->set_default_configuration();
	}

  /** Copy contructor, create a writer with a copy of another
   *
   * @param [in] other TrajectoryWriter to copy from
   */
  TrajectoryWriter(TrajectoryWriter const& other)
    : CoordinatePrecision(6)
    , FieldDelimiter(other.FieldDelimiter)
    , OutputStream(other.OutputStream)
    , QuoteCharacter(other.QuoteCharacter)
    , RecordDelimiter(other.RecordDelimiter)
    , TimestampFormat(other.TimestampFormat)
    , TrajectoryPointWriter(other.TrajectoryPointWriter)
    { }

  /// Destructor
  virtual ~TrajectoryWriter()
    { }

  /** Assign a TrajectoryWriter to the value of another.
   *
   * @param [in] other TrajectoryWriter to assign value of
   * @return Writer with the new assigned value
   */
  TrajectoryWriter& operator=(TrajectoryWriter const& other)
    {
      this->CoordinatePrecision = other.CoordinatePrecision;
      this->FieldDelimiter = other.FieldDelimiter;
      this->OutputStream = other.OutputStream;
      this->QuoteCharacter = other.QuoteCharacter;
      this->RecordDelimiter = other.RecordDelimiter;
      this->TimestampFormat = other.TimestampFormat;
      this->TrajectoryPointWriter = other.TrajectoryPointWriter;
      return *this;
    }

  /** Check whether one writer is equal to another by comparing all the properties.
   *
   * Two writers are equal if all of their streams are properties.
   *
   * @param [in] other TrajectoryWriter for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(TrajectoryWriter const& other) const
    {
      return (
        this->CoordinatePrecision == other.CoordinatePrecision
        && this->FieldDelimiter == other.FieldDelimiter
        && this->OutputStream == other.OutputStream
        && this->QuoteCharacter == other.QuoteCharacter
        && this->RecordDelimiter == other.RecordDelimiter
        && this->TimestampFormat == other.TimestampFormat
        && this->TrajectoryPointWriter == other.TrajectoryPointWriter
        );
    }

  /** Check whether two TrajectoryWriters are unequal.
   *
   * @param [in] other TrajectoryWriter for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(TrajectoryWriter const& other) const
    {
      return !(*this == other);
    }

  /** Set the stream where points will be written
   *
   * This can be any `std::ostream`.
   *
   * @note
   *    You are resposible for ensuring that the stream does not go
   *    out of scope until you are done writing points.
   *
   * @param [in] out Stream where points will be written
   */
  void set_output(std::ostream& out)
    {
      this->OutputStream = &out;
    }

  /** Return the stream where points will be written
   *
   * @return output stream
   */
  std::ostream& output() const
    {
      return *(this->OutputStream);
    }

  /** Set the field delimiter
   *
   * This string will be inserted between each field as points are
   * written.
   *
   * @param [in] delim Delimiter string
   */
  void set_field_delimiter(string_type const& delim)
    {
      this->FieldDelimiter = delim;
    }

  /** Return the field delimiter
   *
   * @return Field delimiter
   */
  string_type field_delimiter() const
    {
      return this->FieldDelimiter;
    }

  /** Set the record separator (end-of-line string)
   *
   * This string will be written after each point. By default it's
   * `std::endl` (the newline string).
   *
   * @param [in] sep String separator
   */
  void set_record_delimiter(string_type const& delim)
    {
      this->RecordDelimiter = delim;
    }

  /** Retrieve the record separator (end-of-line string)
   *
   * @return Return the record separator (end-of-line string)
   */
  string_type record_delimiter() const
    {
      return this->RecordDelimiter;
    }

  /** Set the quote character
   *
   * This character *may* be used to enclose a field containing lots
   * of characters that would otherwise need to be escaped. We have
   * to know what it is so that we can escape it ourselves when we
   * encounter the quote character inside fields.
   *
   * @param [in] quotes: Zero or one character to be used as
   * quotation marks
   */
  void set_quote_character(string_type const& quote)
    {
      this->QuoteCharacter = quote;
    }

  /** Return the current quote characters
   *
   * @return Current quote character
   */
  string_type quote_character() const
    {
      return this->QuoteCharacter;
    }

  /** Set format for writing timestamps
   *
   * There are as many ways to write timestamps as there are programs
   * to write them. We have our default (YYYY-MM-DD HH:MM:SS) but
   * sometimes you will need to specify some other format for
   * interoperability.
   *
   * This method sets a format string for timestamps using the flags
   * in `boost::date_time::time_facet`.
   *
   * @param [in] format Format string for timestamps
   */
  void set_timestamp_format(string_type const& format)
  {
    this->TimestampFormat = format;
    this->TrajectoryPointWriter.set_timestamp_format(format);
    this->_TrajectoryHeader.set_timestamp_output_format(this->timestamp_format());
  }

  /** Retrieve the timestamp format
   *
   * @return The time timestamp format
   */
  string_type timestamp_format() const
  {
    return this->TimestampFormat;
  }

  /** Set the string representation for nulls
   *
   * Property values that were never set are considered to hold a null
   * value. This method lets you set how nulls will be written to
   * disk. The default value is the empty string "".
   *
   * @param [in] new_null_value   Desired string representation of nulls
   */

  void set_null_value(string_type const& new_null_value)
    {
      this->TrajectoryPointWriter.set_null_value(new_null_value);
      this->_TrajectoryHeader.set_null_value(new_null_value);
    }

  /** Retreive the null value
   *
   * @return The representation of the null value
   */
  string_type null_value() const
    {
      return this->TrajectoryPointWriter.null_value();
    }

  /** Write a single trajectory
   *
   * @param [in] trajectory Trajectory to write our
   */
  template<typename trajectory_type>
  void write(trajectory_type const& trajectory)
    {
      string_vector_type tokens;
      this->write_trajectory_header(trajectory, std::back_inserter(tokens));

      this->TrajectoryPointWriter.set_coordinate_precision(this->coordinate_precision());
      this->TrajectoryPointWriter.write_many_points_to_tokens(trajectory.begin(), trajectory.end(),
                                               std::back_inserter(tokens));

      TokenWriter token_writer(*this->OutputStream);
      token_writer.set_quote_character(this->QuoteCharacter);
      token_writer.set_field_delimiter(this->FieldDelimiter);
      token_writer.set_record_delimiter(this->RecordDelimiter);
      token_writer.write_record(tokens.begin(), tokens.end());
    }

  /** Write many trajectories
   *
   * @param [in] traj_begin Start of trajectories to write out
   * @param [in] traj_end End of trajectories to write out
   */
  template<typename source_iter_type>
  void write(source_iter_type traj_begin, source_iter_type traj_end)
    {
      for ( ; traj_begin != traj_end; ++traj_begin)
        {
        this->write(*traj_begin);
        }
    }

  /** Set the decimal precision for writing coordinates
   *
   * Internally, Tracktable stores coordinates as double-precision
   * floating numbers. It is highly unlikely that trajectory data
   * needs absolutely all of that precision. Since it takes up lots
   * of space when we write data to disk, it is useful to be able to
   * ask for reduced (or increased) precision.
   *
   * @param [in] num_digits   Number of digits of precision
   */
  void set_coordinate_precision(std::size_t num_digits)
    {
      this->CoordinatePrecision = num_digits;
      this->_TrajectoryHeader.set_decimal_precision(this->coordinate_precision());
    }

  /** Retreive the coordinate decimal precision
   *
   * @return The decimal precision
   */
  std::size_t coordinate_precision() const
    {
      return this->CoordinatePrecision;
    }

private:
  typedef std::vector<tracktable::settings::string_type> string_vector_type;

  std::size_t CoordinatePrecision;
  string_type FieldDelimiter;
  std::ostream* OutputStream;
  string_type QuoteCharacter;
  string_type RecordDelimiter;
  string_type TimestampFormat;
  PointWriter TrajectoryPointWriter;
  rw::detail::TrajectoryHeader _TrajectoryHeader;

  /** Write tokens out the header
   *
   * @param [in] trajectory Trajectory with tokens to write to header
   * @param [in] output_iter Iterator to write out
   */
  template<typename trajectory_type, typename out_iter_type>
  void write_trajectory_header(trajectory_type const& trajectory,
                               out_iter_type output_iter)
    {
      this->_TrajectoryHeader.populate_from_trajectory(trajectory);
      this->_TrajectoryHeader.write_as_tokens(output_iter);
    }

  /** Set the default configuration values of the writer
   *
   * Defaults:
   *    * coordinate_precision = 8
   *    * field_delimiter = ","
   *    * quote_character = """
   *    * record_delimiter = "\\n"
   *    * timestamp_format = "%Y-%m-%d %H:%M:%S"
   */
  void set_default_configuration()
  {
    this->set_coordinate_precision(8);
    this->set_field_delimiter(",");
    this->set_quote_character("\"");
    this->set_record_delimiter("\n");
    this->set_timestamp_format("%Y-%m-%d %H:%M:%S");
  }

};

} // close namespace tracktable

#endif
