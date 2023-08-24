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

#ifndef __tracktable_rw_trajectory_header_h
#define __tracktable_rw_trajectory_header_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointTraits.h>
#include <tracktable/Core/PropertyConverter.h>
#include <tracktable/Core/UUID.h>

#include <tracktable/RW/detail/HeaderStrings.h>
#include <tracktable/RW/detail/PropertyMapReadWrite.h>

#include <vector>


namespace tracktable { namespace rw { namespace detail {

// ----------------------------------------------------------------------

class TrajectoryHeader
{
public:
  string_type MagicString;
  uuid_type UUID;
  string_type Domain;
  std::size_t NumPoints;
  PropertyMap Properties;
  PropertyConverter PropertyReadWrite;

  TrajectoryHeader()
    : MagicString(TrajectoryFileMagicString),
      UUID(),
      Domain("unknown")
    { }

  TrajectoryHeader(TrajectoryHeader const& other)
    : MagicString(other.MagicString),
      UUID(),
      Domain(other.Domain),
      Properties(other.Properties),
      PropertyReadWrite(other.PropertyReadWrite)
    { }

  virtual ~TrajectoryHeader() { }

  TrajectoryHeader& operator=(TrajectoryHeader const& other)
    {
      this->MagicString    = other.MagicString;
      this->UUID           = other.UUID;
      this->Domain         = other.Domain;
      this->NumPoints      = other.NumPoints;
      this->Properties     = other.Properties;
      this->PropertyReadWrite = other.PropertyReadWrite;
      return *this;
    }

  bool operator==(TrajectoryHeader const& other) const
    {
      return (
           this->MagicString    == other.MagicString
        && this->UUID           == other.UUID
        && this->Domain         == other.Domain
        && this->NumPoints      == other.NumPoints
        && this->Properties     == other.Properties
	&& this->PropertyReadWrite == other.PropertyReadWrite
        );
    }

  bool operator!=(TrajectoryHeader const& other) const
    {
      return !(*this == other);
    }

  void set_timestamp_input_format(string_type const& format)
  {
    this->PropertyReadWrite.set_timestamp_input_format(format);
  }

  void set_timestamp_output_format(string_type const& format)
  {
    this->PropertyReadWrite.set_timestamp_output_format(format);
  }

  void set_decimal_precision(std::size_t digits)
  {
    this->PropertyReadWrite.set_decimal_precision(digits);
  }

  void set_null_value(string_type const& value)
    {
      this->PropertyReadWrite.set_null_value(value);
    }

  string_type null_value() const
    {
      return this->PropertyReadWrite.null_value();
    }

  template<typename trajectory_type>
  void populate_from_trajectory(trajectory_type const& trajectory)
    {
      this->UUID = trajectory.uuid();
      this->Domain = traits::point_domain_name<typename trajectory_type::point_type>::apply();
      this->NumPoints = trajectory.size();
      this->Properties = trajectory.__properties();
    }

  template<typename out_iter_type>
  void write_as_tokens(out_iter_type destination)
    {
      (*destination++) = this->MagicString;
      (*destination++) = boost::lexical_cast<string_type>(this->UUID);
      (*destination++) = this->Domain;
      (*destination++) = boost::lexical_cast<string_type>(this->NumPoints);
      (*destination++) = boost::lexical_cast<string_type>(this->Properties.size());

      for (PropertyMap::const_iterator iter = this->Properties.begin();
           iter != this->Properties.end();
           ++iter)
        {
        (*destination++) = (*iter).first;
        (*destination++) = boost::lexical_cast<string_type>(property_underlying_type((*iter).second));
        (*destination++) = this->PropertyReadWrite.property_to_string((*iter).second);
		}
    }

  /**
   * Reads the header from a stream of tokens
   *
   * @return The number of tokens consumed
   */
  template<typename in_iter_type>
  std::size_t read_from_tokens(in_iter_type current_token, in_iter_type /*last_token*/)
    {
      std::size_t stage = 0;
      std::size_t consumed = 0;
      std::size_t expected_num_properties = 0;

      ++stage;
      this->MagicString = (*current_token++);
      consumed++;
      ++stage;
      try {
          // If the token can't be parsed as a UUID that means this is an older file without UUIDs
          // In that case we will handle the default UUID in the exception clause, but we won't
          // consume the token unless we successfully parse.
          this->UUID = boost::lexical_cast<uuid_type>(*current_token);
          current_token++;
          consumed++;
      } catch(boost::bad_lexical_cast &) {
          // If this is an older file without UUIDs, let's generate a new one moving forward
          this->UUID = ::tracktable::automatic_uuid_generator()->generate_uuid();
      }
      ++stage;
      this->Domain      = (*current_token++);
      consumed++;
      ++stage;
      this->NumPoints   = boost::lexical_cast<std::size_t>(*current_token++);
      consumed++;
      ++stage;
      expected_num_properties = boost::lexical_cast<std::size_t>(*current_token++);

      this->Properties.clear();
      for (std::size_t i = 0; i < expected_num_properties; ++i)
        {
        string_type prop_name(*current_token++);
        PropertyUnderlyingType prop_type = string_to_property_type(*current_token++);
        this->Properties[prop_name] = this->PropertyReadWrite.property_from_string(*current_token++, prop_type);
        consumed += 3;
        }

      return consumed;
    }
};

} } }

#endif
