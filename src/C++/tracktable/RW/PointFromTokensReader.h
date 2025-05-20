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

#ifndef __tracktable_point_from_tokens_reader_h
#define __tracktable_point_from_tokens_reader_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/detail/trait_signatures/HasProperties.h>
#include <tracktable/Core/PropertyConverter.h>

#include <tracktable/RW/GenericReader.h>
#include <tracktable/RW/ParseExceptions.h>
#include <tracktable/RW/detail/HeaderStrings.h>
#include <tracktable/RW/detail/PointHeader.h>
#include <tracktable/RW/detail/SetProperties.h>

#include <iterator>
#include <istream>
#include <string>
#include <cassert>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

#include <boost/lexical_cast.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/tokenizer.hpp>
#include <boost/algorithm/string/trim.hpp>

namespace tracktable {

/** Read points from lists of tokens.
 *
 * PointFromTokensReader expects as its input an iterator that will yield
 * iterator ranges. That is, each value of the iterator is a (begin,
 * end) pair of iterators that will produce a set of tokens for one
 * point.
 *
 * Think of it with this common use case. Somewhere upstream you are
 * reading lines from a text file. Your reader takes lines from the
 * file and separates each line into a list of tokens using some
 * delimiter. PointFromTokensReader takes each of those lists of tokens, one
 * list at a time, and turns it into a point of some user-requested
 * type.
 */

template<typename PointT, typename SourceIterT>
class PointFromTokensReader : public GenericReader<PointT>
{
public:
  typedef PointT                                point_type;
  typedef SourceIterT                           source_iterator_type;
  typedef boost::shared_ptr<point_type>         point_shared_ptr_type;

  /// Instantiate a default PointFromTokensReader
  PointFromTokensReader()
    : ObjectIdColumn(-1)
    , TimestampColumn(-1)
    , IgnoreHeader(false)
    , WarningsEnabled(true)
    , PointCountLogEnabled(true)
    , NumPoints(0)
    , NumParseErrors(0)
    {
    }

  /** Copy contructor, create a reader with a copy of another
   *
   * @param [in] other PointFromTokensReader to copy from
   */
  PointFromTokensReader(const PointFromTokensReader& other)
    : SourceBegin(other.SourceBegin)
    , SourceEnd(other.SourceEnd)
    , CoordinateMap(other.CoordinateMap)
    , FieldMap(other.FieldMap)
    , ObjectIdColumn(other.ObjectIdColumn)
    , TimestampColumn(other.TimestampColumn)
    , IgnoreHeader(other.IgnoreHeader)
    , WarningsEnabled(true)
    , PointCountLogEnabled(other.PointLogEnabled)
    , NumPoints(other.NumPoints)
    , NumParseErrors(other.NumParseErrors)
    { }


  /** Instantiate a reader with a start and finish points
   *
   * @param [in] start Iterator to start from
   * @param [in] finish Iterator to end at
   */
  PointFromTokensReader(source_iterator_type const& start, source_iterator_type const& finish)
    : SourceBegin(start)
    , SourceEnd(finish)
    , ObjectIdColumn(-1)
    , TimestampColumn(-1)
    , IgnoreHeader(false)
    , WarningsEnabled(true)
    , PointCountLogEnabled(true)
    , NumPoints(0)
    , NumParseErrors(0)
    { }

  /// Destructor
  virtual ~PointFromTokensReader()
    {
    }

  /** Assign a PointFromTokensReader to the value of another.
   *
   * @param [in] other PointFromTokensReader to assign value of
   * @return Reader with the new assigned value
   */
  PointFromTokensReader& operator=(PointFromTokensReader const& other)
    {
      this->SourceBegin     = other.SourceBegin;
      this->SourceEnd       = other.SourceEnd;
      this->CoordinateMap   = other.CoordinateMap;
      this->FieldMap        = other.FieldMap;
      this->ObjectIdColumn  = other.ObjectIdColumn;
      this->TimestampColumn = other.TimestampColumn;
      this->IgnoreHeader    = other.IgnoreHeader;
      this->WarningsEnabled = other.WarningsEnabled;
      this->PointCountLogEnabled = other.PointCountLogEnabled;
      this->PropertyReadWrite = other.PropertyReadWrite;
      this->NumPoints       = other.NumPoints;
      this->NumParseErrors = other.NumParseErrors;

      return *this;
    }

  /** Check whether one reader is equal to another by comparing all the properties.
   *
   * Two readers are equal if all of their properties are equal.
   *
   * @param [in] other PointFromTokensReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(PointFromTokensReader const& other) const
    {
      return (
        this->SourceBegin        == other.SourceBegin
        && this->SourceEnd       == other.SourceEnd
        && this->CoordinateMap   == other.CoordinateMap
        && this->FieldMap        == other.FieldMap
        && this->ObjectIdColumn  == other.ObjectIdColumn
        && this->TimestampColumn == other.TimestampColumn
        && this->IgnoreHeader    == other.IgnoreHeader
        && this->WarningsEnabled == other.WarningsEnabled
        && this->PointCountLogEnabled == other.PointCountLogEnabled
	      && this->PropertyReadWrite == other.PropertyReadWrite
        );
    }

  /** Check whether two PointFromTokensReader are unequal.
   *
   * @param [in] other PointFromTokensReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(PointFromTokensReader const& other) const
  {
    return !(*this == other);
  }

  /** Set the column that will be used for object IDs.
   *
   * This column in the input stream will be used to populate the
   * `object_id` field in trajectory points. Column indices start at
   * zero.
   *
   * @param [in] column  Which column contains object IDs
   */
  void set_object_id_column(int column)
    {
      this->ObjectIdColumn = column;
    }

  /** Set the column that will be used for timestamps.
   *
   * This column in the input stream will be used to populate the
   * timestamp field in trajectory points. Column indices start at
   * zero.
   *
   * @param [in] column  Which column contains timestamps
   */
  void set_timestamp_column(int column)
    {
      this->TimestampColumn = column;
    }

  /** Identify the column that will be used for object IDs.
   *
   * Column indices start at zero.
   *
   * @return The column containing the object ID
   */
  int object_id_column() const
    {
      return this->ObjectIdColumn;
    }

  /** Identify the column that will be used for timestamps.
   *
   * Column indices start at zero.
   *
   * @return The column containing the timestamo
   */
  int timestamp_column() const
    {
      return this->TimestampColumn;
    }

  /** Configure the mapping from columns to coordinates
   *
   * This is the lowest-level interface to setting coordinates in the
   * reader. Use `set_x_coordinate_column`/`set_longitude_column` and
   * friends if possible (i.e. if you're in the terrestrial or 2D
   * Cartesian domain).
   *
   * Let's suppose that your X coordinate is in column 12 of your
   * file, your Y coordinate is in column 20 and your Z coordinate is
   * in column 32. The following code snippet illustrates how to set
   * this up in the reader:
   *
   * @code
   *
   * tracktable::PointReader<MyPoint3D> reader;
   * reader.set_coordinate_column(0, 12); // X coordinate
   * reader.set_coordinate_column(1, 20); // Y coordinate
   * reader.set_coordinate_column(2, 32); // Z coordinate
   *
   * @endcode
   *
   * Calling this function invalidates any outstanding iterators.
   *
   * @note Column and coordinate indices start at zero.
   *
   * @param [in] coordinate  Index of coordinate to set
   * @param [in] column      Index of column in list of tokens
   */

  void set_coordinate_column(int coordinate, int column)
    {
      this->CoordinateMap[coordinate] = column;
    }

  /** Configure the mapping from columns to data fields
   *
   * Some points have the ability to store named properties. Use this
   * method to assign columns in the data file to named properties on
   * points.
   *
   * The following lines of code show an example.
   *
   * @code
   *
   * tracktable::PointReader<MyPointType> reader;
   * reader.set_object_id_column(0);
   * reader.set_real_field_column("mileage", 4);
   *
   * @endcode
   *
   * This function invalidates any outstanding iterators.
   *
   * @param [in] field   Name of field to populate on point object
   * @param [in] column  Index of column in list of tokens
   */
  void set_real_field_column(std::string const& field, int column)
  {
    this->FieldMap[field] = rw::detail::ColumnTypeAssignment::real(column);
  }

#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
  void set_integer_field_column(std::string const& field, int column)
  {
    this->FieldMap[field] = rw::detail::ColumnTypeAssignment::integer(column);
  }
#endif

  /** Configure the mapping from columns to data fields
   *
   * Some points have the ability to store named properties. Use this
   * method to assign columns in the data file to named properties on
   * points.
   *
   * The following lines of code show an example.
   *
   * @code
   *
   * tracktable::PointReader<MyPointType> reader;
   * reader.set_object_id_column(0);
   * reader.set_time_field_column("last_seen", 2);
   *
   * @endcode
   *
   * This function invalidates any outstanding iterators.
   *
   * @param [in] field   Name of field to populate on point object
   * @param [in] column  Index of column in list of tokens
   */
  void set_time_field_column(std::string const& field, int column)
  {
    this->FieldMap[field] = rw::detail::ColumnTypeAssignment::timestamp(column);
  }

  /** Configure the mapping from columns to data fields
   *
   * Some points have the ability to store named properties. Use this
   * method to assign columns in the data file to named properties on
   * points.
   *
   * The following lines of code show an example.
   *
   * @code
   *
   * tracktable::PointReader<MyPointType> reader;
   * reader.set_object_id_column(0);
   * reader.set_string_field_column("model_name", 3);
   *
   * @endcode
   *
   * This function invalidates any outstanding iterators.
   *
   * @param [in] field   Name of field to populate on point object
   * @param [in] column  Index of column in list of tokens
   */
  void set_string_field_column(std::string const& field, int column)
  {
    this->FieldMap[field] = rw::detail::ColumnTypeAssignment::string(column);
  }

  /** Return which column has the given corrdinate
   *
   * @return Column that contains the given coordinate
   */
  int coordinate_column(int coordinate) const
    {
      tracktable::IntIntMap::const_iterator iter(this->CoordinateMap.find(coordinate));
      if (iter != this->CoordinateMap.end())
        {
        return (*iter).second;
        }
      else
        {
        return -1;
        }
    }

  /** Retrieve the column assignment for a real-valued field.
   *
   * @param [in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int real_field_column(std::string const& field) const
    {
      if (this->has_real_field_column(field))
        {
        PropertyAssignmentMap::const_iterator iter(this->FieldMap.find(field));
        return (*iter).second.column;
        }
      else
        {
        return -1;
        }
    }

#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
  int integer_field_column(std::string const& field) const
    {
      if (this->has_integer_field_column(field))
        {
        PropertyAssignmentMap::const_iterator iter(this->FieldMap.find(field));
        return (*iter).second.column;
        }
      else
        {
        return -1;
        }
    }
#endif

  /** Retrieve the column assignment for a string field.
   *
   * @param [in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int string_field_column(std::string const& field) const
    {
      if (this->has_string_field_column(field))
        {
        PropertyAssignmentMap::const_iterator iter(this->FieldMap.find(field));
        return (*iter).second.column;
        }
      else
        {
        return -1;
        }
    }

  /** Retrieve the column assignment for a time field.
   *
   * @param [in] field String name of field
   * @return Integer column index for field or -1 if not present
   */
  int time_field_column(std::string const& field) const
  {
    if (this->has_time_field_column(field))
      {
      PropertyAssignmentMap::const_iterator iter(this->FieldMap.find(field));
      return (*iter).second.column;
      }
    else
      {
      return -1;
      }
  }

  /** Check to see if there is a coordindate column
   *
   * @return Boolean indicating that there exists a coordinate column
   */
  bool has_coordinate_column(int coordinate) const
  {
    return (this->CoordinateMap.find(coordinate) != this->CoordinateMap.end());
  }

  /** Check to see where a real field is present in the field map.
   *
   * @param [in] field String name of field
   * @return `True`/`False` depending on whether field is present or not
   */
  bool has_real_field_column(std::string const& field) const
  {
    PropertyAssignmentMap::const_iterator iter = this->FieldMap.find(field);
    return (iter != this->FieldMap.end() &&
            (*iter).second.type == TYPE_REAL);
  }

#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
  bool has_integer_field_column(std::string const& field) const
    {
      PropertyAssignmentMap::const_iterator iter = this->FieldMap.find(field);
      return (iter != this->FieldMap.end() &&
              (*iter).second.type == TYPE_INTEGER);
    }
#endif

  /** Check to see where a string field is present in the field map.
   *
   * @param [in] field String name of field
   * @return `True`/`False` depending on whether field is present or not
   */
  bool has_string_field_column(std::string const& field) const
  {
    PropertyAssignmentMap::const_iterator iter = this->FieldMap.find(field);
    return (iter != this->FieldMap.end() &&
            (*iter).second.type == TYPE_STRING);
  }

  /** Check to see where a time field is present in the field map.
   *
   * @param [in] field String name of field
   * @return `True`/`False` depending on whether field is present or not
   */
  bool has_time_field_column(std::string const& field) const
  {
    PropertyAssignmentMap::const_iterator iter = this->FieldMap.find(field);
    return (iter != this->FieldMap.end() &&
            (*iter).second.type == TYPE_TIMESTAMP);
  }

  /** Clear all of the coordinate assignments
   */
  void clear_coordinate_assignments()
    {
      this->CoordinateMap.clear();
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

  /** Check whether to see if the header should be ignored when reading input
   *
   * @return Boolean whether or not the header should be ignored
   */
  bool ignore_header() const
    {
      return this->IgnoreHeader;
    }

  /** Enable/disable ignoring the header during parsing.
   *
   * @param [in] onoff  Header parsing on / off
   */
  void set_ignore_header(bool onoff)
    {
      this->IgnoreHeader = onoff;
    }

  /** Set the beginning and the end of the input range
   *
   * @param [in] my_begin The iterator to use for the start of input
   * @param [in] my_end The iterator to use for the end of input
   */
  void set_input_range(source_iterator_type my_begin, source_iterator_type my_end)
  {
    this->SourceBegin = my_begin;
    this->SourceEnd = my_end;
  }

  /** Set the format of the timestamp
   *
   * @param [in] format String containing the format of the time stamp
   */
  void set_timestamp_format(string_type const& format)
  {
    this->PropertyReadWrite.set_timestamp_input_format(format);
  }

  /** Retrieve the format of the timestamp
   *
   * @return The timestamp format
   */
  string_type timestamp_format() const
  {
    return this->PropertyReadWrite.timestamp_input_format();
  }

  /** Set the format of the timestamp
   *
   * @param [in] value String value to use for NULL
   */
  void set_null_value(string_type const& value)
    {
      this->PropertyReadWrite.set_null_value(value);
    }

  /** Retrieve the null value
   *
   * @return The null value
   */
  string_type null_value() const
    {
      return this->PropertyReadWrite.null_value();
    }

  /** This method is for the Python wrappers.
   *
   * In C++-land this explicitly breaks encapsulation. DON'T USE IT!
   *
   * In Python-land it make for a much more Pythonic interface.
   */
  tracktable::IntIntMap& __coordinate_assignments()
    {
      return this->CoordinateMap;
    }

  /** This method is for the Python wrappers.
   *
   * In C++-land this explicitly breaks encapsulation. DON'T USE IT!
   *
   * In Python-land it make for a much more Pythonic interface.
   */
  void __set_coordinate_assignments(tracktable::IntIntMap const& cmap)
    {
      this->CoordinateMap = cmap;
    }

  /** Enable/disable logging of point count on read
   *
   * When set to true (the default), the point reader will print out
   * the number of points successfully read and the number of errors
   * to the info log channel when the end of the input is reached.
   *
   * This function is provided because there are cases like the
   * trajectory reader where this results in thousands of lines of
   * spam because the reader is invoked for every trajectory
   * separately.
   *
   * @param [in] onoff Boolean flag: 'true' means 'yes, log statistics'
   */

  void set_point_count_log_enabled(bool onoff)
  {
    this->PointCountLogEnabled = onoff;
  }

  /** Get the status of the point count log
   *
   * Retrieve PointCountLogEnabled.  When set to true, this flag will
   * print out how many points are read successfully and how many are
   * lost due to error.
   *
   * @return Whether or not point count logging is enabled
   */

  bool point_count_log_enabled() const
  {
    return this->PointCountLogEnabled;
  }

protected:
  typedef rw::detail::PropertyAssignmentMap PropertyAssignmentMap;
  typedef std::vector<settings::string_type> string_vector_type;

  IntIntMap             CoordinateMap;
  PropertyAssignmentMap FieldMap;

  source_iterator_type  SourceBegin;
  source_iterator_type  SourceEnd;

  int                   ObjectIdColumn;
  int                   TimestampColumn;

  bool                  IgnoreHeader;
  bool                  WarningsEnabled;
  bool                  PointCountLogEnabled;

  PropertyConverter     PropertyReadWrite;

  int                   NumPoints;
  int                   NumParseErrors;

  /** Increment the iterator the next item to be read in
   *
   * @return The next item
   */
  point_shared_ptr_type next_item()
    {
      point_shared_ptr_type NextPoint;

      std::size_t required_num_tokens =
        this->CoordinateMap.size()
        + this->FieldMap.size()
        + static_cast<std::size_t>(traits::has_object_id<point_type>::value)
        + static_cast<std::size_t>(traits::has_timestamp<point_type>::value)
        ;

      for (IntIntMap::iterator iter = this->CoordinateMap.begin();
           iter != this->CoordinateMap.end();
           ++iter)
        {
        if (iter->second == -1)
          {
          -- required_num_tokens;
          }
        }

      while (this->SourceBegin != this->SourceEnd)
        {
        try
          {
          string_vector_type _tokens;
          this->get_tokens_from_input(_tokens);

#if defined(COPIOUS_DEBUG_OUTPUT)
          std::ostringstream outbuf;
          outbuf << "Token list has " << _tokens.size() << " entries: ";
          for (string_vector_type::iterator iter = _tokens.begin();
               iter != _tokens.end();
               ++iter)
            {
            outbuf << "'" << *iter << "' ("
                   << iter->size() << ") ";
            }
          TRACKTABLE_LOG(log::trace) << outbuf.str();
#endif
          if (_tokens.size() == 0)
            {
            // Skip empty lines. Should this even be possible?
            TRACKTABLE_LOG(log::debug) << "Skipping empty line.";
            ++(this->SourceBegin);
            continue;
            }

          if (_tokens[0] == rw::detail::PointFileMagicString && this->IgnoreHeader)
            {
            TRACKTABLE_LOG(log::trace) << "Found point header but IgnoreHeader is enabled.\n";
            }

          if (_tokens[0] == rw::detail::PointFileMagicString
              && !this->IgnoreHeader)
            {
            TRACKTABLE_LOG(log::debug) << "Configuring point reader from header.";
            this->configure_reader_from_header(_tokens);
            ++(this->SourceBegin);

            // We just updated the reader based on the header found
            // That means we also need to update the number of required tokens
            required_num_tokens =
              this->CoordinateMap.size()
              + this->FieldMap.size()
              + static_cast<std::size_t>(traits::has_object_id<point_type>::value)
              + static_cast<std::size_t>(traits::has_timestamp<point_type>::value)
              ;

            TRACKTABLE_LOG(log::debug)
              << "Required tokens (" << required_num_tokens << ") calculation: coordmap=" << this->CoordinateMap.size()
              << " propmap=" << this->FieldMap.size()
              << " objid=" << static_cast<std::size_t>(traits::has_object_id<point_type>::value)
              << " timestamp=" << static_cast<std::size_t>(traits::has_timestamp<point_type>::value);
            continue;
            }
          else
            {
            // It's a token list that isn't a header. Let's try to
            // parse it as a point.
            if (_tokens.size() >= required_num_tokens)
              {
              /*TRACKTABLE_LOG(log::trace) << "Parsing list of "
                  << _tokens.size() << " tokens ("
                  << required_num_tokens << " required) "
                  << "as point.";*/
              NextPoint = point_shared_ptr_type(new point_type);
              this->populate_coordinates_from_tokens(_tokens, NextPoint);
              this->populate_properties_from_tokens(_tokens, NextPoint);
              ++(this->SourceBegin);
              ++(this->NumPoints);

              return NextPoint;
              }
            else
              {
              TRACKTABLE_LOG(log::debug)
                << "WARNING: Not enough tokens to assemble point. Expected "
                << required_num_tokens << ", found " << _tokens.size()
                << ". Point will be skipped.";
              ++(this->SourceBegin);
              ++(this->NumParseErrors);
              }
            }
          }
        catch (ParseError const& e)
          {
          TRACKTABLE_LOG(log::debug) << e.what() << "\n";
          NextPoint = point_shared_ptr_type();
          ++(this->SourceBegin);
          ++(this->NumParseErrors);
          }
        catch (boost::bad_lexical_cast& e)
          {
          TRACKTABLE_LOG(log::debug) << "Cast error while parsing point: " << e.what();
          ++(this->SourceBegin);
          ++(this->NumParseErrors);
          }
        catch (std::exception& e)
          {
          TRACKTABLE_LOG(log::warning) << "Exception while parsing point: " << e.what();
          ++(this->SourceBegin);
          ++(this->NumParseErrors);
          }
        }
      if (NextPoint == 0 && this->PointCountLogEnabled)
        {
          TRACKTABLE_LOG(log::info) << "Done reading points. "
                                    << "Generated " << this->NumPoints << " points correctly and "
                                    << "discarded " << this->NumParseErrors << " due to parse errors.\n";
        }
      return NextPoint;
    }

  // ----------------------------------------------------------------------

  /** Configure the reader based on information contained in the input header
   *
   * @param [in] tokens Tokens from the header to be read in
   */
  void configure_reader_from_header(string_vector_type const& tokens)
    {
      rw::detail::PointHeader header;
      header.read_from_tokens(tokens.begin(), tokens.end());

      if (
        header.Dimension != std::size_t(traits::dimension<point_type>::value)
        )
        {
        TRACKTABLE_LOG(log::warning)
                  << "PointFromTokensIterator: Header indicates points with dimension "
                  << header.Dimension << " but reader's point type has dimension "
                  << traits::dimension<point_type>::value << ".";
        }

      if (header.HasObjectId)
        {
        this->ObjectIdColumn = 0;
        }
      if (header.HasTimestamp)
        {
        this->TimestampColumn = 1;
        }

      this->configure_coordinate_assignments(header.HasObjectId,
                                             header.HasTimestamp,
                                             header.Dimension);

      std::size_t first_property_column_in_point_data =
        static_cast<std::size_t>(header.HasObjectId)
        + static_cast<std::size_t>(header.HasTimestamp)
        + header.Dimension;
/*
      std::size_t first_property_assignment_column =
        1 // header token
        + 1 // domain
        + 1 // dimension
        + static_cast<std::size_t>(header.HasObjectId)
        + static_cast<std::size_t>(header.HasTimestamp)
        + 1 // number of properties
        ;
*/
      this->configure_field_assignments(header,
                                        first_property_column_in_point_data);
    }

  // ----------------------------------------------------------------------

  /** Configure the coordinates based on information parsed from the input header
   *
   * @param [in] object_id_present Boolean indicating if object ID is present
   * @param [in] timestamp_present Boolean indicating if timestamp is present
   * @param [in] expected_dimension Dimension coordinates are expected to be in
   */
  void configure_coordinate_assignments(bool object_id_present,
                                        bool timestamp_present,
                                        std::size_t expected_dimension)
    {
      this->CoordinateMap.clear();

      std::size_t first_coordinate_column = 0;
      first_coordinate_column += static_cast<std::size_t>(object_id_present);
      first_coordinate_column += static_cast<std::size_t>(timestamp_present);
      for (std::size_t d = 0; d < expected_dimension; ++d)
        {
        this->CoordinateMap[static_cast<int>(d)] = static_cast<int>(first_coordinate_column + d);
        }
    }

  // ----------------------------------------------------------------------

  /** Configure the fields based on information parsed from the input header
   *
   * @param [in] header Header containing the field information
   * @param [in] first_property_column First column containing a property
   */
  void configure_field_assignments(rw::detail::PointHeader const& header,
                                   std::size_t first_property_column)
    {
      this->FieldMap.clear();

      for (std::size_t i = 0; i < header.PropertyNames.size(); ++i)
        {
        string_type property_name(header.PropertyNames[i]);
        PropertyUnderlyingType property_type(header.PropertyTypes[i]);

        this->FieldMap[property_name] = rw::detail::ColumnTypeAssignment(first_property_column + i, property_type);
        }
      TRACKTABLE_LOG(log::debug) << "Adjusted property map size = " << this->FieldMap.size() << ".";

    }

  // ----------------------------------------------------------------------

  /** Get specified tokens from the input
   *
   * @param [in] tokens Tokens to get from input
   */
  void get_tokens_from_input(string_vector_type& tokens)
    {
      typedef typename source_iterator_type::value_type token_iterator_range;
      token_iterator_range token_range(*this->SourceBegin);
      tokens.assign(token_range.first, token_range.second);
      for (string_vector_type::iterator iter = tokens.begin();
           iter != tokens.end();
           ++iter)
        {
        boost::algorithm::trim(*iter);
        }
    }

  // ----------------------------------------------------------------------

  /** Populated the coordinates from input tokens
   *
   * @param [in] tokens Tokens to use for population
   * @param [in] point Point containing coordinates
   */
  void populate_coordinates_from_tokens(string_vector_type const& tokens,
                                        point_shared_ptr_type point)
    {
      for (IntIntMap::const_iterator iter = this->CoordinateMap.begin();
           iter != this->CoordinateMap.end();
           ++iter)
        {
        int coord = (*iter).first;
        int column = (*iter).second;

        if (tokens.at(column).size() == 0)
          {
          throw EmptyCoordinateError(coord);
          }
        try
          {
          if (iter->second == -1) continue; // skip missing coordinates
          settings::point_coordinate_type value(boost::lexical_cast<settings::point_coordinate_type>(tokens.at(column)));
          (*point)[coord] = value;
          }
        catch (const boost::bad_lexical_cast& e)
          {
          std::ostringstream fieldbuf;
          fieldbuf << "coordinate " << coord;
          throw LexicalCastError(fieldbuf.str(), tokens.at(column), "double");
          }
        }
    }

  // ----------------------------------------------------------------------

  /** Populated the properties from input tokens
   *
   * @param [in] tokens Tokens to use for population
   * @param [in] point Point containing properties
   */
  void populate_properties_from_tokens(string_vector_type const& tokens,
                                       point_shared_ptr_type point)
    {
      rw::detail::set_properties<
        point_type,
        traits::has_properties<point_type>::value
        >::apply(*point, tokens, this->FieldMap, this->PropertyReadWrite);

      if (this->ObjectIdColumn != -1)
        {
        rw::detail::set_object_id<
          point_type,
          traits::has_object_id<point_type>::value
          >::apply(*point, tokens, this->ObjectIdColumn);
        }

      if (this->TimestampColumn != -1)
        {
        rw::detail::set_timestamp<
          point_type,
          traits::has_timestamp<point_type>::value
          >::apply(*point, tokens, this->TimestampColumn, this->PropertyReadWrite.timestamp_converter());
        }
    }
};

} // close namespace tracktable

#endif
