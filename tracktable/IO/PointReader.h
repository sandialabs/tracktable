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

#ifndef __TRACKTABLE_POINT_READER_H
#define __TRACKTABLE_POINT_READER_H

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointBase.h>

#include <tracktable/IO/LineReader.h>
#include <tracktable/IO/SkipCommentsReader.h>
#include <tracktable/IO/StringTokenizingReader.h>
#include <tracktable/IO/PointFromTokensReader.h>

#include <tracktable/IO/detail/PointReaderDefaultConfiguration.h>

#include <iterator>
#include <iostream>
#include <istream>
#include <string>
#include <cassert>
#include <map>
#include <stdexcept>
#include <vector>

namespace tracktable {

/** Read points from files.
 *
 * This reader wraps the following pipeline:
 *
 * - Read lines from a text file
 *
 * - Skip any lines that begin with a designated comment character ('#' by default)
 *
 * - Tokenize each line using specified delimiters (whitespace by default)
 *
 * - Create a point (user-specified type) from each tokenized line
 *
 * - Return the resulting points via a C++ iterator
 *
 * You will use set_input() to supply an input stream,
 * set_comment_character() to configure which lines to skip,
 * set_delimiter() to specify how to turn lines into tokens, and
 * set_column_for_field() to assign columns in the data file to fields
 * (object ID, longitude, latitude, etc) on the point.
 *
 * Take a look at the test case for this class (in
 * C++/IO/Tests/test_integrated_trajectory_point_reader.cpp) for an
 * example of how to use it.
 */

template<typename PointT>
class PointReader
{
private:
  typedef PointT point_type;
  typedef tracktable::LineReader<> line_reader_type;
  typedef tracktable::SkipCommentsReader<line_reader_type::iterator> skip_comments_reader_type;
  typedef tracktable::StringTokenizingReader<skip_comments_reader_type::iterator> string_tokenizer_type;
  typedef tracktable::PointFromTokensReader<point_type, string_tokenizer_type::iterator> point_reader_type;

public:
  typedef typename point_reader_type::iterator iterator;

  PointReader()
    {
      this->set_default_configuration();
    }

  PointReader(std::istream& infile)
    {
      this->set_input(infile);
      this->set_default_configuration();
    }

  PointReader(PointReader const& other)
    : LineReader(other.LineReader),
      SkipCommentsReader(other.SkipCommentsReader),
      StringTokenizer(other.StringTokenizer),
      PointTokenReader(other.PointTokenReader)
    {
    }

  virtual ~PointReader()
    {
    }

  /** Default reader configuration
   *
   * If you are reading BasePoints, this sets coordinates 0 to d-1 (D
   * is the point's dimension) using columns 0 to d-1.
   *
   *
   * If you are reading TrajectoryPoints, column 0 is the object ID,
   * column 1 is the timestamp, and columns 2 through D+1 (inclusive)
   * are the coordinates.
   *
   * These are the default settings.  You can override any or all of
   * them after you instantiate the reader.
   */

  void set_default_configuration()
    {
      this->set_field_delimiter(",");
      this->set_comment_character("#");
      this->set_timestamp_format("%Y-%m-%d %H:%M:%S");
      
      io::detail::set_default_configuration<
        traits::has_properties<point_type>::value,
        traits::dimension<point_type>::value
                                            >
        ::apply(this);
    }

  /** Specify comment character for skipping lines
   *
   * A line is a comment if and only if its first non-whitespace
   * character is the comment character ('#' by default).  We will
   * skip such lines entirely.  We do not handle inline or trailing
   * comments: a line will either be included in its entirety or
   * skipped completely.
   *
   * @param[in] comment Single character
   */
  void set_comment_character(std::string const& comment)
    {
      this->SkipCommentsReader.set_comment_character(comment);
    }

  /** Retrieve current value of comment character.
   *
   * This function invalidates any outstanding iterators.
   *
   * @return Current value of comment character
   */
  std::string comment_character() const
    {
      return this->SkipCommentsReader.comment_character();
    }

  /** Supply input stream from delimited text source.
   *
   * We read our input from C++ std::istreams.  The stream you supply
   * will be traversed exactly once.
   *
   * @param[in] input Stream from which we will read points
   */
  void set_input(std::istream& input)
    {
      this->LineReader.set_input(input);
      this->SkipCommentsReader.set_input_range(this->LineReader.begin(),
                                               this->LineReader.end());
      this->StringTokenizer.set_input_range(this->SkipCommentsReader.begin(),
                                            this->SkipCommentsReader.end());
      this->PointTokenReader.set_input_range(this->StringTokenizer.begin(),
                                             this->StringTokenizer.end());
    }

  /** Retrieve the current input stream.
   *
   * BUG: We currently have no way to indicate whether the stream is
   * valid.
   *
   * @return Stream being used for input.
   */
  std::istream& input() const
    {
      return this->LineReader.input();
    }

  /** Set one character for use as a field delimiter.
   *
   * The character in the argument to this function will be treated
   * as a field delimiter in the input.
   *
   * This function invalidates any outstanding iterators.
   *
   * @param[in] delimiter String containing desired delimiter character
   */
  void set_field_delimiter(string_type const& delimiter)
    {
      this->StringTokenizer.set_field_delimiter(delimiter);
      this->PointTokenReader.set_input_range(this->StringTokenizer.begin(),
                                             this->StringTokenizer.end());
    }
  /** Retrieve the current field delimiter character.
   *
   * @return String containing delimiter
   */
  string_type field_delimiter() const
    {
      return this->StringTokenizer.field_delimiter();
    }

  /** Identify the column that will be the X coordinate.
   *
   * @param[in] column Column number in the input file to use (starts at 0)
   */

  void set_x_column(int column)
    {
      this->set_coordinate_column(0, column);
    }

  /** Identify the column that will be the Y coordinate.
   *
   * @param[in] column Column number in the input file to use (starts at 0)
   */

  void set_y_column(int column)
    {
      this->set_coordinate_column(1, column);
    }

  /** Identify the column that will be the Z coordinate.
   *
   * @param[in] column Column number in the input file to use (starts at 0)
   */

  void set_z_column(int column)
    {
      this->set_coordinate_column(2, column);
    }

  /** Identify the column that will be the longitude coordinate.
   *
   * @param[in] column Column number in the input file to use (starts at 0)
   */

  void set_longitude_column(int column)
    {
      this->set_coordinate_column(0, column);
    }

  /** Identify the column that will be the latitude coordinate
   *
   * @param[in] column Column number in the input file to use (starts at 0)
   */

  void set_latitude_column(int column)
    {
      this->set_coordinate_column(1, column);
    }

  /** Get the column number that will be the X coordinate.
   *
   * @return Column number in the input file (starts at 0)
   */

  int x_column() const
    {
      return this->coordinate_column(0);
    }

  /** Get the column number that will be the Y coordinate.
   *
   * @return Column number in the input file (starts at 0)
   */

  int y_column() const
    {
      return this->coordinate_column(1);
    }

  /** Get the column number that will be the Z coordinate.
   *
   * @return Column number in the input file (starts at 0)
   */

  int z_column() const
    {
      return this->coordinate_column(2);
    }

  /** Get the column number that will be the longitude coordinate.
   *
   * @return Column number in the input file (starts at 0)
   */

  int longitude_column() const
    {
      return this->coordinate_column(0);
    }

  /** Get the column number that will be the latitude coordinate.
   *
   * @return Column number in the input file (starts at 0)
   */

  int latitude_column() const
    {
      return this->coordinate_column(1);
    }

  /** Configure the mapping from columns to coordinates
   *
   * This is the lowest-level interface to setting coordinates in the
   * reader.  Use set_x_coordinate_column/set_longitude_column and
   * friends if possible (i.e. if you're in the terrestrial or 2D
   * Cartesian domain).
   *
   * Let's suppose that your X coordinate is in column 12 of your
   * file, your Y coordinate is in column 20 and your Z coordinate is
   * in column 32.  The following code snippet illustrates how to set
   * this up in the reader:
   *
   * \code
   *
   * tracktable::PointReader<MyPoint3D> reader;
   * reader.set_coordinate_column(0, 12); // X coordinate
   * reader.set_coordinate_column(1, 20); // Y coordinate
   * reader.set_coordinate_column(2, 32); // Z coordinate
   *
   * \endcode
   *
   * Calling this function invalidates any outstanding iterators.
   *
   * \note Column and coordinate indices start at zero.
   *
   * @param[in] coordinate  Index of coordinate to set
   * @param[in] column      Index of column in list of tokens
   */
  void set_coordinate_column(std::size_t coordinate, int column)
    {
      this->PointTokenReader.set_coordinate_column(coordinate, column);
    }

  bool has_coordinate_column(int coordinate) const
    {
      return this->PointTokenReader.has_coordinate_column(coordinate);
    }

  int coordinate_column(int coordinate) const
    {
      return this->PointTokenReader.coordinate_column(coordinate);
    }

  void clear_coordinate_assignments()
    {
      this->PointTokenReader.clear_coordinate_assignments();
    }

  /** Identify the column that will be used for object IDs.
   *
   * This column in the input stream will be used to populate the
   * object_id field in trajectory points.  Column indices start at
   * zero.
   *
   * @param[in] column  Which column contains object IDs
   */

  void set_object_id_column(int column)
    {
      this->PointTokenReader.set_object_id_column(column);
    }

  /** Identify the column that will be used for timestamps.
   *
   * This column in the input stream will be used to populate the
   * timestamp field in trajectory points.  Column indices start at
   * zero.
   *
   * @param[in] column  Which column contains timestamps
   */

  void set_timestamp_column(int column)
    {
      this->PointTokenReader.set_timestamp_column(column);
    }

  int object_id_column() const
    {
      return this->PointTokenReader.object_id_column();
    }

  int timestamp_column() const
    {
      return this->PointTokenReader.timestamp_column();
    }

  /** Configure the mapping from columns to data fields
   *
   * Some points have the ability to store named properties.  Use this
   * method to assign columns in the data file to named properties on
   * points.
   *
   * The following lines of code show an example.
   *
   * \code
   *
   * tracktable::PointReader<MyPointType> reader;
   * reader.set_object_id_column(0);
   * reader.set_integer_field_column("model_year", 1);
   * reader.set_time_field_column("last_seen", 2);
   * reader.set_string_field_column("model_name", 3);
   * reader.set_real_field_column("mileage", 4);
   *
   * \endcode
   *
   * This function invalidates any outstanding iterators.
   *
   * @param[in] field   Name of field to populate on point object
   * @param[in] column  Index of column in list of tokens
   */

  void set_string_field_column(std::string const& field, int column)
    {
      this->PointTokenReader.set_string_field_column(field, column);
    }


  void set_real_field_column(std::string const& field, int column)
    {
      this->PointTokenReader.set_real_field_column(field, column);
    }

  void set_integer_field_column(std::string const& field, int column)
    {
      this->PointTokenReader.set_integer_field_column(field, column);
    }

  void set_time_field_column(std::string const& field, int column)
    {
      this->PointTokenReader.set_time_field_column(field, column);
    }


  /** Check to see where a field is present in the field map.
   *
   * @param[in] field String name of field
   * @return True/false depending on whether field is present or not
   */
  bool has_string_field_column(std::string const& field) const
    {
      return this->PointTokenReader.has_string_field_column(field);
    }

  bool has_real_field_column(std::string const& field) const
    {
      return this->PointTokenReader.has_real_field_column(field);
    }

  bool has_integer_field_column(std::string const& field) const
    {
      return this->PointTokenReader.has_integer_field_column(field);
    }

  bool has_time_field_column(std::string const& field) const
    {
      return this->PointTokenReader.has_time_field_column(field);
    }

  /** Retrieve the column assignment for a real-valued field.
   *
   * @param[in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int real_field_column(std::string const& field) const
    {
      return this->PointTokenReader.real_field_column(field);
    }
  
  /** Retrieve the column assignment for an integer-valued field.
   *
   * @param[in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int integer_field_column(std::string const& field) const
    {
      return this->PointTokenReader.integer_field_column(field);
    }

  /** Retrieve the column assignment for a string field.
   *
   * @param[in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int string_field_column(std::string const& field) const
    {
      return this->PointTokenReader.string_field_column(field);
    }

  /** Retrieve the column assignment for a string field.
   *
   * @param[in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int time_field_column(std::string const& field) const
    {
      return this->PointTokenReader.time_field_column(field);
    }

  /** Return an iterator to the first parsed point.
   *
   * This will take the parameters you've established for the input
   * stream, comment character, delimiters and field/column mapping
   * and start up the whole parsing pipeline.  You can iterate through
   * in the standard C++ fashion until you reach the end().
   *
   * Note that any changes you make to the parser configuration will
   * invalidate existing iterators.
   *
   * @return Iterator to first parsed point
   */
  iterator begin()
    {
      return this->PointTokenReader.begin();
    }

  /** Return an iterator to detect when parsing has ended.
   *
   * This iterator is guaranteed to not point at any valid
   * TrajectoryPoint.  The only time when ``begin() == end()`` will be
   * when all points have been parsed from the input stream.
   *
   * @return Iterator past end of point sequence
   */
  iterator end()
    {
      return this->PointTokenReader.end();
    }

  IntIntMap& __coordinate_assignments()
    {
      return this->PointTokenReader.__coordinate_assignments();
    }

  void __set_coordinate_assignments(IntIntMap const& cmap)
    {
      this->PointTokenReader.__set_coordinate_assignments(cmap);
    }

  void set_timestamp_format(string_type const& format)
  {
    this->PointTokenReader.set_timestamp_format(format);
  }

  void set_null_value(string_type const& value)
    {
      this->PointTokenReader.set_null_value(value);
    }

  string_type null_value() const
    {
      return this->PointTokenReader.null_value();
    }
  
private:
  line_reader_type LineReader;
  skip_comments_reader_type SkipCommentsReader;
  string_tokenizer_type StringTokenizer;
  point_reader_type PointTokenReader;
};

} // close namespace tracktable

#endif
