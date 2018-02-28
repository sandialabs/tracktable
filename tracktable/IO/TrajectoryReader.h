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

#ifndef __tracktable_TrajectoryReader_h
#define __tracktable_TrajectoryReader_h

#include <tracktable/Core/TracktableCommon.h>

#include <tracktable/IO/GenericReader.h>
#include <tracktable/IO/LineReader.h>
#include <tracktable/IO/SkipCommentsReader.h>
#include <tracktable/IO/StringTokenizingReader.h>
#include <tracktable/IO/PointFromTokensReader.h>

#include <tracktable/IO/detail/TrajectoryHeader.h>
#include <tracktable/IO/detail/PointHeader.h>

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
  TrajectoryReader()
    {
      this->set_default_configuration();
    }

  TrajectoryReader(std::istream& infile)
    {
      this->set_input(infile);
      this->set_default_configuration();
    }

  TrajectoryReader(TrajectoryReader const& other)
    : LineReader(other.LineReader)
    , PointReader(other.PointReader)
    , SkipCommentsReader(other.SkipCommentsReader)
    , StringTokenizer(other.StringTokenizer)
    , TimestampFormat(other.TimestampFormat)
    , WarningsEnabled(other.WarningsEnabled)
    {
    }

  TrajectoryReader& operator=(TrajectoryReader const& other)
    {
      this->LineReader         = other.LineReader;
      this->PointReader        = other.PointReader;
      this->SkipCommentsReader = other.SkipCommentsReader;
      this->StringTokenizer    = other.StringTokenizer;
      this->TimestampFormat    = other.TimestampFormat;
      this->WarningsEnabled    = other.WarningsEnabled;
      return *this;
    }

  virtual ~TrajectoryReader()
    {
    }

  bool operator==(TrajectoryReader const& other) const
    {
      return (
              // this->LineReader            == static_cast<const line_reader_type>(other.LineReader)
              true
        && this->SkipCommentsReader == other.SkipCommentsReader
        && this->StringTokenizer    == other.StringTokenizer
	&& this->TimestampFormat    == other.TimestampFormat
        && this->WarningsEnabled    == other.WarningsEnabled
        );
    }

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
   * These are the default settings.  You can override any or all of
   * them after you instantiate the reader.
   */

  void set_default_configuration()
    {
      this->set_null_value("");
      this->set_field_delimiter(",");
      this->set_comment_character("#");
      this->set_warnings_enabled(true);
      this->set_timestamp_format("%Y-%m-%d %H:%M:%S");
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
   * @param[in] null_value String to interpret as null
   */
  void set_null_value(string_type const& null_value)
    {
      this->ParseTrajectoryHeader.set_null_value(null_value);
      this->PointReader.set_null_value(null_value);
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
      this->TokenizedInputBegin = this->StringTokenizer.begin();
      this->TokenizedInputEnd   = this->StringTokenizer.end();

      this->ParseTrajectoryHeader.set_timestamp_input_format(this->TimestampFormat);
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

  /** Enable/disable warnings during parsing.
   *
   * We may run into type mismatches and bad casts while we're parsing
   * headers and data.  This flag determines whether or not warnings
   * will be printed.
   *
   * @param[in] onoff  Warnings are on / off
   */

  void set_warnings_enabled(bool onoff)
    {
      this->WarningsEnabled = onoff;
    }

  /** Check whether warnings are enablde
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
   * as a potential field delimiter.  If you supply ``",|"`` as your
   * delimiter then both the comma and the exclamation point will be
   * used to tokenize field.
   *
   * This function invalidates any outstanding iterators.
   *
   * @param[in] delimiters String containing all desired delimiter characters
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

  void set_timestamp_format(string_type const& format)
  {
    this->TimestampFormat = format;
    this->PointReader.set_timestamp_format(this->TimestampFormat);
  }

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
  io::detail::TrajectoryHeader ParseTrajectoryHeader;

  trajectory_shared_ptr_type next_item()
    {
      while (this->TokenizedInputBegin != this->TokenizedInputEnd)
        {
        string_vector_type tokens((*this->TokenizedInputBegin).first,
                                  (*this->TokenizedInputBegin).second);

        if (tokens[0] == io::detail::TrajectoryFileMagicString)
          {
          trajectory_shared_ptr_type NextTrajectory =
            this->parse_trajectory(tokens);

          if (NextTrajectory)
            {
            ++ this->TokenizedInputBegin;
            return NextTrajectory;
            }
          }
        ++ this->TokenizedInputBegin;
        }

      return trajectory_shared_ptr_type();
    }

  trajectory_shared_ptr_type
  parse_trajectory(string_vector_type const& tokens)
    {
      try
        {
        trajectory_shared_ptr_type trajectory(new trajectory_type);

//        io::detail::TrajectoryHeader header(this->PropertyReadWrite);
//	this->ParseTrajectoryHeader.set_timestamp_input_format(this->TimestampFormat);

        this->ParseTrajectoryHeader.read_from_tokens(tokens.begin(), tokens.end());
        trajectory->__set_properties(this->ParseTrajectoryHeader.Properties);
#if 0
        std::cout << "DEBUG: parse_trajectory: Header contains "
                  << header.Properties.size() << " properties\n";

        std::cout << "DEBUG: parse_trajectory: Expecting "
                  << header.NumPoints << " points\n";
#endif
        string_vector_type::const_iterator points_begin = tokens.begin();
        string_vector_type::const_iterator points_end = tokens.end();

        // Advance past all the things in the header
        std::advance(points_begin,
                     4 + 3 * this->ParseTrajectoryHeader.Properties.size());

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
        if (this->WarningsEnabled)
          {
          std::cerr << "WARNING: Error parsing trajectory: "
                    << e.what() << "\n";
          }
        return trajectory_shared_ptr_type();
        }
    }

  // ----------------------------------------------------------------------

  void populate_trajectory_points(token_iter_type token_begin,
                                  token_iter_type token_end,
                                  std::size_t num_points,
                                  trajectory_shared_ptr_type trajectory)
    {
      // We already have the parsed tokens so we can skip the first
      // several stages of the point reader.  However, the token
      // reader expects its input one line at a time.  In order to
      // separate those out we need to read the point header.
      io::detail::PointHeader header;
      header.read_from_tokens(token_begin, token_end);
#if 0
      std::cout << "DEBUG: Point header says that we have "
                << header.PropertyNames.size() << " properties per point\n";
#endif
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
      int num_tokens_in_point_record = header.Dimension
        + header.HasObjectId
        + header.HasTimestamp
        + header.PropertyNames.size();

      while (point_range_begin != token_end)
        {
        token_iter_type point_range_end = point_range_begin;
        if (std::distance(point_range_end, token_end) < num_tokens_in_point_record)
          {
          std::cout << "ERROR: Trajectory reader fell off the end of tokens for points.  There is probably a missing property value in one of the point records.\n";
          std::cout << "DEBUG: Trajectory tokens:\n";
          for (; point_range_begin != token_end; ++point_range_begin)
            {
            std::cout << *point_range_begin << " ||| ";
            }
          std::cout << "\n";
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
        std::cout << "ERROR: Trajectory reader tried to populate a new trajectory from tokens but got "
                  << trajectory->size()
                  << " points.  We were expecting "
                  << num_points << ".\n";
        }
    }

  // ----------------------------------------------------------------------

  void populate_trajectory_points_from_token_ranges(
    token_range_vector_type::iterator input_range_begin,
    token_range_vector_type::iterator input_range_end,
    trajectory_shared_ptr_type trajectory
    )
    {
      this->PointReader.set_input_range(input_range_begin,
                                        input_range_end);
      trajectory->assign(this->PointReader.begin(), this->PointReader.end());
#if 0
      std::cout << "DEBUG: populate_trajectory_points: Trajectory now contains "
                << trajectory->size() << " points\n";
#endif
    }




};

} // close namespace tracktable

#endif
