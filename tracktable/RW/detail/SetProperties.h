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

#ifndef __tracktable_rw_SetProperties_h
#define __tracktable_rw_SetProperties_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/PropertyConverter.h>
#include "PropertyMapReadWrite.h"

namespace tracktable { namespace rw { namespace detail {

typedef std::vector<std::string> string_vector_type;

// ----------------------------------------------------------------------

template<typename PointT, bool HasProperties>
struct set_properties
{
  typedef PointT point_type;

  inline static void apply(
    point_type& point,
    string_vector_type const& /*tokens*/,
    PropertyAssignmentMap const& field_map,
    PropertyConverter& /*converter*/
    )
    {
      if (field_map.size() > 0)
        {
        TRACKTABLE_LOG(log::warning)
          << "You are attempting to set "
          << "properties on a point of type "
          << typeid(point).name()
          << ", which does not have properties "
          << "(or at least does not have the "
          << "has_properties tag defined).";
        }
    }
};

// ----------------------------------------------------------------------

template<typename PointT>
struct set_properties<PointT, true>
{
  typedef PointT point_type;

  inline static void apply(point_type& point,
                           string_vector_type const& tokens,
                           PropertyAssignmentMap const& field_map,
			   PropertyConverter& converter)
    {
      for (PropertyAssignmentMap::const_iterator iter = field_map.begin();
           iter != field_map.end();
           ++iter)
        {
        std::string field_name((*iter).first);
        std::size_t column((*iter).second.column);

        tracktable::PropertyUnderlyingType type((*iter).second.type);

        std::string raw_value(tokens.at(column));
        try
          {
	    point.set_property(field_name,
			       converter.property_from_string(raw_value, type));
          }
        catch (std::exception& e)
          {
          TRACKTABLE_LOG(log::debug)
            << "WARNING: Parse error while trying to set field '"
            << field_name << "' from string '"
            << raw_value << "': "
            << e.what();
          }
        }
    }
};

// ----------------------------------------------------------------------

template<typename PointT, bool HasProperties>
struct set_object_id
{
  typedef PointT point_type;

  inline static void apply(
    point_type& point,
    string_vector_type const& /*tokens*/,
    std::size_t ObjectIdColumn
    )
    {
      /*TODO:: The is the 'HasProperties' == false implementation, do we need to bother checking
      if the column, which is already checked in the calling function */
      if (ObjectIdColumn != std::numeric_limits<decltype(ObjectIdColumn)>::max())
        {
        TRACKTABLE_LOG(log::warning)
                  << "WARNING: You are attempting to set "
                  << "an object ID on a point of type "
                  << typeid(point).name()
                  << ", which does not have properties "
                  << "(or at least does not have the "
                  << "has_object_id tag defined).";
        }
    }
};

template<typename PointT>
struct set_object_id<PointT, true>
{
  typedef PointT point_type;

  inline static void apply(
    point_type& point,
    string_vector_type const& tokens,
    std::size_t ObjectIdColumn
    )
    {
      point.set_object_id(tokens[ObjectIdColumn]);
    }
};

// ----------------------------------------------------------------------

template<typename PointT, bool HasProperties>
struct set_timestamp
{
  typedef PointT point_type;

  inline static void apply(
    point_type& point,
    string_vector_type const& /*tokens*/,
    std::size_t TimestampColumn,
    TimestampConverter* /*converter*/
    )
    {
      /*TODO:: The is the 'HasProperties' == false implementation, do we need to bother checking
      if the timestamp column, which is already checked in the calling function */
      if (TimestampColumn != std::numeric_limits<decltype(TimestampColumn)>::max())
        {
        TRACKTABLE_LOG(log::warning)
                  << "WARNING: You are attempting to set "
                  << "a timestamp on a point of type "
                  << typeid(point).name()
                  << ", which does not have properties "
                  << "(or at least does not have the "
                  << "has_timestamp tag defined).";
        }
    }
};

template<typename PointT>
struct set_timestamp<PointT, true>
{
  typedef PointT point_type;

  inline static void apply(
    point_type& point,
    string_vector_type const& tokens,
    std::size_t TimestampColumn,
    TimestampConverter* converter
    )
    {
      try
        {
	  string_type raw_value(tokens[TimestampColumn]);
	  Timestamp timestamp(converter->timestamp_from_string(raw_value));
	  point.set_timestamp(timestamp);
        }
      catch (std::exception& e)
        {
        TRACKTABLE_LOG(log::warning)
                  << "Error while setting timestamp: "
                  << e.what() << "\n"
                  << "Timestamp string was '"
                  << tokens[TimestampColumn]
                  << "'.";
        }
    }
};

} } }

#endif

