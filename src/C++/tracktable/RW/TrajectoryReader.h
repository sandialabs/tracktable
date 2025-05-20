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

#ifndef __tracktable_TrajectoryReader_h
#define __tracktable_TrajectoryReader_h

#include <tracktable/Core/TracktableCommon.h>

#include <tracktable/RW/GenericReader.h>
#include <tracktable/RW/LineReader.h>
#include <tracktable/RW/SkipCommentsReader.h>
#include <tracktable/RW/StringTokenizingReader.h>
#include <tracktable/RW/PointFromTokensReader.h>

#include <tracktable/RW/detail/TrajectoryHeader.h>
#include <tracktable/RW/detail/PointHeader.h>

#include <iterator>
#include <iostream>
#include <istream>
#include <string>
#include <cassert>
#include <stdexcept>

#include <boost/shared_ptr.hpp>

namespace tracktable {

/** Read trajectories from files.
 *
 * This reader wraps the following pipeline:
 *
 * - Read lines from a text file
 *
 * - Skip any lines that begin with a designated comment character ('#' by default)
 *
 * - Tokenize each line using specified delimiters (whitespace by default)
 *
 * - Create a trajectory (user-specified type) from each tokenized line
 *
 * - Return the resulting points via a C++ iterator
 *
 * You will use set_input() to supply an input stream,
 * set_comment_character() to configure which lines to skip,
 * set_field_delimiter() to specify how to turn lines into fields.
 */

template<typename TrajectoryT>
class TrajectoryReader : public GenericReader<TrajectoryT>
{
private:
  typedef TrajectoryT trajectory_type;
  typedef typename trajectory_type::point_type point_type;
  typedef tracktable::LineReader<> line_reader_type;
  typedef tracktable::SkipCommentsReader<line_reader_type::iterator> skip_comments_reader_type;
  typedef tracktable::StringTokenizingReader<skip_comments_reader_type::iterator> string_tokenizer_type;

public:
  /** Instantiate TrajectoryReader using a default configuration
   *
   * @copydoc TrajectoryReader::set_default_configuration()
   */
  TrajectoryReader()
    {
      this->set_default_configuration();
    }

  /** Instantiate a TrajectoryReader using a `std::istream` and default configuration
   *
   * @copydoc TrajectoryReader::set_default_configuration()
   *
   * @param [in] infile Stream to read input from
   */
  TrajectoryReader(std::istream& infile)
    {
      this->set_input(infile);
      this->set_default_configuration();
    }

  /** Copy contructor, create a reader with a copy of another
   *
   * @param [in] other TrajectoryReader to copy from
   */
  TrajectoryReader(TrajectoryReader const& other)
    : LineReader(other.LineReader)
    , PointReader(other.PointReader)
    , SkipCommentsReader(other.SkipCommentsReader)
    , StringTokenizer(other.StringTokenizer)
    , TimestampFormat(other.TimestampFormat)
    , WarningsEnabled(other.WarningsEnabled)
    , TrajectoriesRead(other.TrajectoriesRead)
    {
    }

  /// Destructor
  virtual ~TrajectoryReader()
    {
    }

  /** Assign a TrajectoryReader to the value of another.
   *
   * @param [in] other TrajectoryReader to assign value of
   * @return Reader with the new assigned value
   */
  TrajectoryReader& operator=(TrajectoryReader const& other)
    {
      this->LineReader         = other.LineReader;
      this->PointReader        = other.PointReader;
      this->SkipCommentsReader = other.SkipCommentsReader;
      this->StringTokenizer    = other.StringTokenizer;
      this->TimestampFormat    = other.TimestampFormat;
      this->WarningsEnabled    = other.WarningsEnabled;
      this->TrajectoriesRead   = other.TrajectoriesRead;
      return *this;
    }

  /** Check whether one reader is equal to another by comparing all the properties.
   *
   * Two readers are equal if all of their properties are equal.
   *
   * @param [in] other TrajectoryReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(TrajectoryReader const& other) const
    {
      return (
        this->LineReader            == other.LineReader
        && this->SkipCommentsReader == other.SkipCommentsReader
        && this->StringTokenizer    == other.StringTokenizer
	&& this->TimestampFormat    == other.TimestampFormat
        && this->WarningsEnabled    == other.WarningsEnabled
        && this->TrajectoriesRead   == other.TrajectoriesRead
        );
    }

  /** Check whether two TrajectoryReaders are unequal.
   *
   * @param [in] other TrajectoryReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(TrajectoryReader const& other) const
    {
      return !(*this == other);
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
   * These are the default settings. You can override any or all of
   * them after you instantiate the reader.
   */

  void set_default_configuration()
    {
      this->set_null_value("");
      this->set_field_delimiter(",");
      this->set_comment_character("#");
      this->set_warnings_enabled(true);
      this->set_timestamp_format("%Y-%m-%d %H:%M:%S");
      this->PointReader.set_point_count_log_enabled(false);
    }


  /** Specify comment character for skipping lines
   *
   * A line is a comment if and only if its first non-whitespace
   * character is the comment character ('#' by default). We will
   * skip such lines entirely. We do not handle inline or trailing
   * comments: a line will either be included in its entirety or
   * skipped completely.
   *
   * @param [in] comment Single character
   */
  void set_comment_character(string_type const& comment)
    {
      this->SkipCommentsReader.set_comment_character(comment);
    }

  /** Retrieve current value of comment character.
   *
   * This function invalidates any outstanding iterators.
   *
   * @return Current value of comment character
   */
  string_type comment_character() const
    {
      return this->SkipCommentsReader.comment_character();
    }

  /** Specify string value to be interpreted as null
   *
   * @param [in] _null_value String to interpret as null
   */
  void set_null_value(string_type const& _null_value)
    {
      this->ParseTrajectoryHeader.set_null_value(_null_value);
      this->PointReader.set_null_value(_null_value);
    }

  /** Get string value for nulls
   *
   * @return Current string that will be interpreted as null
   */

  string_type null_value() const
    {
      return this->PointReader.null_value();
    }

  /** Supply input stream from delimited text source.
   *
   * We read our input from C++ std::istreams. The stream you supply
   * will be traversed exactly once.
   *
   * @param [in] _input Stream from which we will read points
   */
  void set_input(std::istream& _input)
    {
      this->LineReader.set_input(_input);
      this->SkipCommentsReader.set_input_range(this->LineReader.begin(),
                                               this->LineReader.end());
      this->StringTokenizer.set_input_range(this->SkipCommentsReader.begin(),
                                            this->SkipCommentsReader.end());
      this->TokenizedInputBegin = this->StringTokenizer.begin();
      this->TokenizedInputEnd   = this->StringTokenizer.end();

      this->ParseTrajectoryHeader.set_timestamp_input_format(this->TimestampFormat);
      this->TrajectoriesRead = 0;
    }

  /** Retrieve the current input stream.
   *
   * @bug
   *    We currently have no way to indicate whether the stream is valid.
   *
   * @return Stream being used for input.
   */
  std::istream& input() const
    {
      return this->LineReader.input();
    }

  /** Enable/disable warnings during parsing.
   *
   * We may run into type mismatches and bad casts while we're parsing
   * headers and data. This flag determines whether or not warnings
   * will be printed.
   *
   * @param [in] onoff  Warnings are on / off
   */

  void set_warnings_enabled(bool onoff)
    {
      this->WarningsEnabled = onoff;
    }

  /** Check whether warnings are enable
   *
   * @return Whether or not warnings are on
   */

  bool warnings_enabled() const
    {
      return this->WarningsEnabled;
    }

  /** Set one or more characters as field delimiters.
   *
   * Each character in the argument to this function will be treated
   * as a potential field delimiter. If you supply `",|"` as your
   * delimiter then both the comma and the exclamation point will be
   * used to tokenize field.
   *
   * This function invalidates any outstanding iterators.
   *
   * @param [in] delimiters String containing all desired delimiter characters
   */

  void set_field_delimiter(string_type const& delimiters)
    {
      this->StringTokenizer.set_field_delimiter(delimiters);
    }

  /** Retrieve the current set of delimiter characters.
   *
   * @return String containing all delimiters
   */
  string_type field_delimiter() const
    {
      return this->StringTokenizer.field_delimiter();
    }

  /** Set the format of the timestamp
   *
   * @param [in] format String containing the format of the time stamp
   */
  void set_timestamp_format(string_type const& format)
  {
    this->TimestampFormat = format;
    this->PointReader.set_timestamp_format(this->TimestampFormat);
  }

  /** Retrieve the format of the timestamp
   *
   * @return The timestamp format
   */
  string_type timestamp_format() const
  {
    return this->TimestampFormat;
  }

private:
  typedef boost::shared_ptr<trajectory_type> trajectory_shared_ptr_type;
  typedef string_vector_type::const_iterator token_iter_type;
  typedef std::pair<token_iter_type, token_iter_type> token_range_type;
  typedef std::vector<token_range_type> token_range_vector_type;
  typedef PointFromTokensReader<point_type, token_range_vector_type::iterator> point_reader_type;

  line_reader_type LineReader;
  point_reader_type PointReader;
  skip_comments_reader_type SkipCommentsReader;
  string_tokenizer_type StringTokenizer;
  string_type TimestampFormat;
  string_tokenizer_type::iterator TokenizedInputBegin;
  string_tokenizer_type::iterator TokenizedInputEnd;
  bool WarningsEnabled;
  int TrajectoriesRead;
  rw::detail::TrajectoryHeader ParseTrajectoryHeader;

  /** Increment the iterator the next item to be read in
   *
   * @return The next item
   */
  trajectory_shared_ptr_type next_item()
    {
      while (this->TokenizedInputBegin != this->TokenizedInputEnd)
        {
        string_vector_type tokens((*this->TokenizedInputBegin).first,
                                  (*this->TokenizedInputBegin).second);

        if (tokens[0] == rw::detail::TrajectoryFileMagicString)
          {
          trajectory_shared_ptr_type NextTrajectory =
            this->parse_trajectory(tokens);

          if (NextTrajectory)
            {
            ++ this->TokenizedInputBegin;
            ++ this->TrajectoriesRead;
            return NextTrajectory;
            }
          }
        ++ this->TokenizedInputBegin;
        }


      auto plural_trajectory = [](int discriminator) {
        if (discriminator == 1) {
          return std::string("trajectory");
        } else {
          return std::string("trajectories");
        }
      };

      TRACKTABLE_LOG(log::info) << "Read a total of "
          << this->TrajectoriesRead << " "
          << plural_trajectory(this->TrajectoriesRead)
          << ".";

      return trajectory_shared_ptr_type();
    }

  /** Parse the read in trajectory
   *
   * @param tokens Tokens that are read in and parsed
   */
  trajectory_shared_ptr_type
  parse_trajectory(string_vector_type const& tokens)
    {
      try
        {
        // Create a new trajectory object, but we won't spend time generating a uuid
        trajectory_shared_ptr_type trajectory(new trajectory_type(false));

        // rw::detail::TrajectoryHeader header(this->PropertyReadWrite);
        this->ParseTrajectoryHeader.set_timestamp_input_format(this->TimestampFormat);

        std::size_t tokens_consumed_by_header = this->ParseTrajectoryHeader.read_from_tokens(tokens.begin(), tokens.end());
        trajectory->set_uuid(this->ParseTrajectoryHeader.UUID);
        trajectory->__set_properties(this->ParseTrajectoryHeader.Properties);

        string_vector_type::const_iterator points_begin = tokens.begin();
        string_vector_type::const_iterator points_end = tokens.end();

        // Advance past all the things in the header
        std::advance(points_begin, tokens_consumed_by_header+1);

        this->populate_trajectory_points(points_begin, points_end,
                                         this->ParseTrajectoryHeader.NumPoints,
                                         trajectory);
        assert(trajectory != 0);
        if (trajectory->size() == 0)
          {
          return trajectory_shared_ptr_type();
          }
        return trajectory;
        }
      catch (std::exception& e)
        {
          TRACKTABLE_LOG(log::warning)
           << "Error parsing trajectory: " << e.what();
           return trajectory_shared_ptr_type();
        }
    }

  // ----------------------------------------------------------------------

  /** Populate the trajectorie's points
   *
   * @param [in] token_begin Start of tokens read in
   * @param [in] token_end End of tokens read in
   * @param [in] num_points Num of points expected to be in trajectory
   * @param [in] trajectory Trajectory to populate
   */
  void populate_trajectory_points(token_iter_type token_begin,
                                  token_iter_type token_end,
                                  std::size_t num_points,
                                  trajectory_shared_ptr_type trajectory)
    {
      // We already have the parsed tokens so we can skip the first
      // several stages of the point reader. However, the token
      // reader expects its input one line at a time. In order to
      // separate those out we need to read the point header.
      rw::detail::PointHeader header;
      header.read_from_tokens(token_begin, token_end);

      TRACKTABLE_LOG(log::trace)
        << "DEBUG: Point header says that we have "
        << header.PropertyNames.size() << " properties per point";

      typedef std::pair<token_iter_type, token_iter_type> token_range_type;
      typedef std::vector<token_range_type> token_range_vector_type;

      token_range_vector_type token_ranges;

      // First token range is the header
      token_iter_type header_end_token = token_begin;
      std::advance(header_end_token,
                   6 + 2 * header.PropertyNames.size());
      token_range_type header_tokens(token_begin, header_end_token);
      token_ranges.push_back(header_tokens);

      token_iter_type point_range_begin = header_end_token;
      std::size_t num_tokens_in_point_record = header.Dimension
        + header.HasObjectId
        + header.HasTimestamp
        + header.PropertyNames.size();

      while (point_range_begin != token_end)
        {
        token_iter_type point_range_end = point_range_begin;
        auto d = std::distance(point_range_end, token_end);
        assert(d>=0);//TODO: consider a nother warning in the event of too many tokens?
        if (static_cast<std::make_unsigned<decltype(d)>::type>(std::abs(d)) < num_tokens_in_point_record)
          {
          TRACKTABLE_LOG(log::warning)
             << "Trajectory reader fell off the end of tokens for points. "
             << "There is probably a missing property value in one of the point records.\n";
          std::ostringstream outbuf;
          outbuf << "Trajectory tokens: ";
          for (; point_range_begin != token_end; ++point_range_begin)
            {
            outbuf << *point_range_begin << " ||| ";
            }
          TRACKTABLE_LOG(log::debug) << outbuf.str();
          trajectory->clear();
          return;
          }

        std::advance(point_range_end, num_tokens_in_point_record);
        token_range_type line_range(point_range_begin, point_range_end);
        token_ranges.push_back(line_range);
        point_range_begin = point_range_end;
        }

      this->populate_trajectory_points_from_token_ranges(token_ranges.begin(),
                                                         token_ranges.end(),
                                                         trajectory);
      if (trajectory != 0 && trajectory->size() != num_points)
        {
        TRACKTABLE_LOG(log::error)
                  << "Trajectory reader tried to populate a new trajectory from tokens but got "
                  << trajectory->size()
                  << " points. We were expecting "
                  << num_points << ".\n";
        }
    }

  // ----------------------------------------------------------------------

  /** Populate the trajectories points from token ranges
   *
   * @param [in] input_range_begin Start of range to read in
   * @param [in] input_range_end End of range to read in
   * @param [in] trajectory Trajectory to populate
   */
  void populate_trajectory_points_from_token_ranges(
    token_range_vector_type::iterator input_range_begin,
    token_range_vector_type::iterator input_range_end,
    trajectory_shared_ptr_type trajectory
    )
    {
      this->PointReader.set_input_range(input_range_begin,
                                        input_range_end);
      trajectory->assign(this->PointReader.begin(), this->PointReader.end());
      TRACKTABLE_LOG(log::trace)
                << "populate_trajectory_points: Trajectory now contains "
                << trajectory->size() << " points\n";
    }




};

} // close namespace tracktable

#endif
