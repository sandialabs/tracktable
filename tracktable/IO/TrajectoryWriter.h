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

#ifndef __tracktable_TrajectoryWriter_h
#define __tracktable_TrajectoryWriter_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/PropertyConverter.h>

#include <tracktable/IO/PointWriter.h>
#include <tracktable/IO/TokenWriter.h>

#include <tracktable/IO/detail/HeaderStrings.h>
#include <tracktable/IO/detail/TrajectoryHeader.h>
#include <tracktable/IO/detail/PropertyMapReadWrite.h>

#include <iterator>
#include <iostream>
#include <cassert>
#include <stdexcept>
#include <vector>

namespace tracktable {

/** Write trajectories of any type as delimited text
 *
 * This class writes subclasses of tracktable::Trajectory (including
 * the domain classes) to a stream as delimited text.  It will write
 * one trajectory per line.  The resulting file will contain enough
 * header information to reconstruct the trajectory exactly as long as
 * the user asks for the correct class.
 */

class TrajectoryWriter
{
public:
  TrajectoryWriter()
    : OutputStream(0)
	{
	this->set_default_configuration();
	}

  TrajectoryWriter(std::ostream& output)
    : OutputStream(&output)
	{
	this->set_default_configuration();
	}

  TrajectoryWriter(TrajectoryWriter const& other)
    : CoordinatePrecision(6)
    , FieldDelimiter(other.FieldDelimiter)
    , OutputStream(other.OutputStream)
    , QuoteCharacter(other.QuoteCharacter)
    , RecordDelimiter(other.RecordDelimiter)
    , TimestampFormat(other.TimestampFormat)
    , TrajectoryPointWriter(other.TrajectoryPointWriter)
    { }

  virtual ~TrajectoryWriter()
    { }

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

  bool operator!=(TrajectoryWriter const& other) const
    {
      return !(*this == other);
    }

  void set_output(std::ostream& out)
    {
      this->OutputStream = &out;
    }

  std::ostream& output() const
    {
      return *(this->OutputStream);
    }

  void set_field_delimiter(string_type const& delim)
    {
      this->FieldDelimiter = delim;
    }

  string_type field_delimiter() const
    {
      return this->FieldDelimiter;
    }

  void set_record_delimiter(string_type const& delim)
    {
      this->RecordDelimiter = delim;
    }

  string_type record_delimiter() const
    {
      return this->RecordDelimiter;
    }

  void set_quote_character(string_type const& quote)
    {
      this->QuoteCharacter = quote;
    }

  string_type quote_character() const
    {
      return this->QuoteCharacter;
    }

  void set_timestamp_format(string_type const& format)
  {
    this->TimestampFormat = format;
    this->TrajectoryPointWriter.set_timestamp_format(format);
    this->_TrajectoryHeader.set_timestamp_output_format(this->timestamp_format());
  }

  string_type timestamp_format() const
  {
    return this->TimestampFormat;
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
      this->TrajectoryPointWriter.set_null_value(null_value);
      this->_TrajectoryHeader.set_null_value(null_value);
    }

  string_type null_value() const
    {
      return this->TrajectoryPointWriter.null_value();
    }

  /** Write a single trajectory
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
      this->_TrajectoryHeader.set_decimal_precision(this->coordinate_precision());
    }

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
  io::detail::TrajectoryHeader _TrajectoryHeader;

  template<typename trajectory_type, typename out_iter_type>
  void write_trajectory_header(trajectory_type const& trajectory,
                               out_iter_type output)
    {
      this->_TrajectoryHeader.populate_from_trajectory(trajectory);
      this->_TrajectoryHeader.write_as_tokens(output);
    }

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
