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

#ifndef __tracktable_rw_point_header_h
#define __tracktable_rw_point_header_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointTraits.h>

#include <tracktable/RW/detail/HeaderStrings.h>
#include <tracktable/RW/detail/PropertyMapReadWrite.h>
#include <vector>
#include <iostream>

namespace tracktable { namespace rw { namespace detail {

// ----------------------------------------------------------------------

class PointHeader
{
public:
  string_type MagicString;
  string_type Domain;
  std::size_t Dimension;
  bool        HasObjectId;
  bool        HasTimestamp;
  string_vector_type                  PropertyNames;
  std::vector<PropertyUnderlyingType> PropertyTypes;

  PointHeader()
    : MagicString(PointFileMagicString)
    , Domain("unknown")
    , Dimension(0)
    , HasObjectId(false)
    , HasTimestamp(false)
    { }

  PointHeader(PointHeader const& other)
    : MagicString(other.MagicString)
    , Domain(other.Domain)
    , Dimension(other.Dimension)
    , HasObjectId(other.HasObjectId)
    , HasTimestamp(other.HasTimestamp)
    , PropertyNames(other.PropertyNames)
    , PropertyTypes(other.PropertyTypes)
    { }

  virtual ~PointHeader() { }

  PointHeader& operator=(PointHeader const& other)
    {
      this->MagicString   = other.MagicString;
      this->Domain        = other.Domain;
      this->Dimension     = other.Dimension;
      this->HasObjectId   = other.HasObjectId;
      this->HasTimestamp  = other.HasTimestamp;
      this->PropertyNames = other.PropertyNames;
      this->PropertyTypes = other.PropertyTypes;
      return *this;
    }

  bool operator==(PointHeader const& other) const
    {
      return (
        this->MagicString      == other.MagicString
        && this->Domain        == other.Domain
        && this->Dimension     == other.Dimension
        && this->HasObjectId   == other.HasObjectId
        && this->HasTimestamp  == other.HasTimestamp
        && this->PropertyNames == other.PropertyNames
        && this->PropertyTypes == other.PropertyTypes
        );
    }

  bool operator!=(PointHeader const& other) const
    {
      return !(*this == other);
    }

  template<typename point_type>
  void populate_from_point(point_type const& example_point)
    {
      this->Domain = traits::point_domain_name<point_type>::apply();
      this->Dimension = traits::dimension<point_type>::value;
      this->HasObjectId = traits::has_object_id<point_type>::value;
      this->HasTimestamp = traits::has_timestamp<point_type>::value;
      this->populate_properties(example_point);
    }

  template<typename point_type>
  void populate_properties(point_type const& example_point)
    {
      write_property_info_to_header<
        traits::has_properties<point_type>::value
        >::apply(example_point,
                 std::back_inserter(this->PropertyNames),
                 std::back_inserter(this->PropertyTypes)
          );
    }

  template<typename out_iter_type>
  void write_as_tokens(out_iter_type destination) const
    {
      (*destination++) = this->MagicString;
      (*destination++) = this->Domain;
      (*destination++) = boost::lexical_cast<string_type>(this->Dimension);
      (*destination++) = boost::lexical_cast<string_type>(this->HasObjectId);
      (*destination++) = boost::lexical_cast<string_type>(this->HasTimestamp);
      (*destination++) = boost::lexical_cast<string_type>(this->PropertyNames.size());

      for (std::size_t i = 0; i < this->PropertyNames.size(); ++i)
        {
        (*destination++) = this->PropertyNames[i];
        (*destination++) = boost::lexical_cast<string_type>(this->PropertyTypes[i]);
        }
    }

  template<typename in_iter_type>
  void read_from_tokens(in_iter_type current_token, in_iter_type /*last_token*/)
    {
      std::size_t stage = 0;
      std::size_t expected_num_properties = 0;

      ++stage;
      this->MagicString = (*current_token++);
      ++stage;
      this->Domain      = (*current_token++);
      ++stage;
      this->Dimension   = boost::lexical_cast<std::size_t>(*current_token++);
      ++stage;
      this->HasObjectId = boost::lexical_cast<bool>(*current_token++);
      ++stage;
      this->HasTimestamp = boost::lexical_cast<bool>(*current_token++);
      ++stage;
      expected_num_properties = boost::lexical_cast<std::size_t>(*current_token++);
      ++stage;

      for (std::size_t i = 0; i < expected_num_properties; ++i)
        {
        this->PropertyNames.push_back(*current_token++);
        this->PropertyTypes.push_back(string_to_property_type(*current_token++));
        }
    }
};

} } }

#endif
