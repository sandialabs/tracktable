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

// Typesafe code for writing out the property map from a point or
// trajectory.  Uses tag dispatch on tracktable::traits::HasProperties
// so that we can call it on whatever we need to.

#ifndef __tracktable_rw_PropertyMapReadWrite_h
#define __tracktable_rw_PropertyMapReadWrite_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/PropertyConverter.h>

#include <algorithm>

namespace tracktable { namespace rw { namespace detail {

typedef settings::string_type string_type;

class ColumnTypeAssignment
{
public:
  ColumnTypeAssignment()
    : column(0), type(TYPE_UNKNOWN)
    { }

  ColumnTypeAssignment(std::size_t _column, PropertyUnderlyingType _type)
    : column(_column), type(_type)
    { }

  static ColumnTypeAssignment real(std::size_t _column)
    {
      return ColumnTypeAssignment(_column, TYPE_REAL);
    }

  static ColumnTypeAssignment string(std::size_t _column)
    {
      return ColumnTypeAssignment(_column, TYPE_STRING);
    }

  static ColumnTypeAssignment timestamp(std::size_t _column)
    {
      return ColumnTypeAssignment(_column, TYPE_TIMESTAMP);
    }
public:
  std::size_t column;
  PropertyUnderlyingType type;
};

typedef std::map<std::string, ColumnTypeAssignment> PropertyAssignmentMap;

template<bool has_properties>
struct write_property_map_values
{
  template<typename point_or_trajectory_t, typename out_iter_t>
  static inline void apply(point_or_trajectory_t const& /*thing*/,
                           PropertyConverter& /*formatter*/,
                           out_iter_t /*where_to_write*/,
                           std::size_t /*num_properties_expected*/)
    {
      // This is the default version - there are no properties to
      // write
      return;
    }
};

template<>
struct write_property_map_values<true>
{
  template<typename point_or_trajectory_t, typename out_iter_t>
  static inline void apply(point_or_trajectory_t const& thing,
			   PropertyConverter& formatter,
			   out_iter_t where_to_write,
               std::size_t num_properties_expected)
    {
      for (PropertyMap::const_iterator property_iter = thing.__properties().begin();
           property_iter != thing.__properties().end();
           ++property_iter)
        {
	  (*where_to_write++) = formatter.property_to_string((*property_iter).second);
        }
      for (std::size_t i = thing.__properties().size();
           i < num_properties_expected;
           ++i)
        {
        (*where_to_write++) = string_type("");
        }
    }
};

template<bool has_properties>
struct write_property_map_header
{
  template<typename thing_t, typename out_iter_t>
  static inline void apply(thing_t const& /*thing*/, out_iter_t /*dest1*/, out_iter_t /*dest2*/)
    {
      // This is the default version - no properties to write
      return;
    }
};

template<>
struct write_property_map_header<true>
{
  template<typename thing_t, typename out_iter_t>
  static inline void apply(thing_t const& thing_with_properties,
                           out_iter_t name_destination,
                           out_iter_t type_destination)
    {
      for (PropertyMap::const_iterator iter(thing_with_properties.__properties().begin());
           iter != thing_with_properties.__properties().end();
           ++iter)
        {
        (*name_destination++) = (*iter).first;
        PropertyUnderlyingType value_type(property_underlying_type((*iter).second));
        if (value_type != TYPE_NULL)
          {
          (*type_destination++) = boost::lexical_cast<string_type>(value_type);
          }
        else
          {
          PropertyUnderlyingType expected_type = boost::get<NullValue>((*iter).second).ExpectedType;
          (*type_destination++) = boost::lexical_cast<string_type>(expected_type);
          }
        }
    }
};


template<bool has_properties>
struct write_property_map
{
  template<typename point_or_trajectory_t, typename out_iter_t>
  static inline void apply(
    point_or_trajectory_t const& /*thing*/,
    out_iter_t /*where_to_write*/
    )
    {
      // This is the default version - there are no properties to
      // write
      return;
    }
};

template<>
struct write_property_map<true>
{
  template<typename point_or_trajectory_t, typename out_iter_t>
    static inline void apply(point_or_trajectory_t const& thing, out_iter_t where_to_write)
    {
      for (PropertyMap::const_iterator property_iter = thing.__properties().begin();
           property_iter != thing.__properties().end();
           ++property_iter)
        {
        (*where_to_write++) = boost::lexical_cast<string_type>((*property_iter).first);
        PropertyUnderlyingType value_type(property_underlying_type((*property_iter).second));
        if (value_type != TYPE_NULL)
          {
          (*where_to_write++) = boost::lexical_cast<string_type>(value_type);
          }
        else
          {
          PropertyUnderlyingType expected_type = boost::get<NullValue>((*property_iter).second).ExpectedType;
          (*where_to_write++) = boost::lexical_cast<string_type>(expected_type);
          }
        (*where_to_write++) = boost::lexical_cast<string_type>((*property_iter).second);
        }
    }
};


template<bool has_properties>
struct write_property_info_to_header
{
  template<
    typename point_type,
    typename out_iter_type1,
    typename out_iter_type2
    >
  static inline void apply(
    point_type const& /*point*/,
    out_iter_type1 /*dest1*/,
    out_iter_type2 /*dest2*/
    )
    {
      return;
    }
};

template<>
struct write_property_info_to_header<true>
{
  template<
    typename point_type,
    typename out_iter_name_type,
    typename out_iter_type_type
    >
  static inline void apply(point_type const& point,
                           out_iter_name_type names,
                           out_iter_type_type types)
    {
      for (PropertyMap::const_iterator iter = point.__properties().begin();
           iter != point.__properties().end();
           ++iter)
        {
        (*names++) = (*iter).first;
        if (property_underlying_type((*iter).second) != TYPE_NULL)
          {
          (*types++) = property_underlying_type((*iter).second);
          }
        else
          {
          PropertyUnderlyingType expected_type = boost::get<NullValue>((*iter).second).ExpectedType;
          (*types++) = expected_type;
          }
        }
    }
};

template<bool has_properties>
struct read_property_info_from_tokens
{
  template<
    typename in_iter_type,
    typename out_iter_type1,
    typename out_iter_type2
    >
  static inline void apply(in_iter_type /*tokens*/,
                           std::size_t /*num_expected*/,
                           out_iter_type1 /*output1*/,
                           out_iter_type2 /*output2*/)
    { }
};

template<>
struct read_property_info_from_tokens<true>
{
  template<
    typename in_iter_type,
    typename out_iter_name_type,
    typename out_iter_type_type
    >
  static inline void apply(in_iter_type tokens,
                           std::size_t num_expected,
                           out_iter_name_type names,
                           out_iter_type_type types)
    {
      for (std::size_t i = 0; i < num_expected; ++i)
        {
        (*names++) = (*tokens++);
        (*types++) = string_to_property_type(*tokens++);
        }
    }
};

} } } // close namespace tracktable::rw::detail

#endif
