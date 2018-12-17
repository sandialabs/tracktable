/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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


/*
 * PropertyValueT - variant type for properties we attach to
 * points/trajectories
 *
 * We allow the user to specify named properties on points and
 * trajectories that take one of five types: null, 64-bit signed
 * integer, double-precision floating point, string, and timestamp.
 *
 * NOTE: The name of this type will change from
 * tracktable::PropertyValueT to tracktable::PropertyValue in version
 * 1.2.
 */

#ifndef __tracktable_PropertyValue_h
#define __tracktable_PropertyValue_h

#include <tracktable/Core/TracktableCoreWindowsHeader.h>

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>

#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>
#include <tracktable/Core/detail/algorithm_signatures/Extrapolate.h>

#include <boost/variant.hpp>
#include <boost/serialization/variant.hpp>

namespace tracktable {

typedef enum {
  TYPE_UNKNOWN   = 0,
  TYPE_REAL      = 1,
  TYPE_STRING    = 2,
  TYPE_TIMESTAMP = 3,
  TYPE_INTEGER   = 4,
  TYPE_NULL      = 5
} PropertyUnderlyingType;


class NullValue
{
public:
  friend class boost::serialization::access;
  
  PropertyUnderlyingType ExpectedType;

  NullValue()
    : ExpectedType(TYPE_UNKNOWN)
    { }
  NullValue(PropertyUnderlyingType my_type)
    : ExpectedType(my_type)
    { }
  NullValue(NullValue const& other) :
    ExpectedType(other.ExpectedType)
    { }
  void operator=(NullValue const& other)
    {
      this->ExpectedType = other.ExpectedType;
    }
  bool operator==(NullValue const& /*other*/) const
    {
      return false;
    }
  bool operator!=(NullValue const& /*other*/) const
    {
      return true;
    }
  bool operator<(NullValue const& other) const
    {
      return (this->ExpectedType < other.ExpectedType);
    }

private:
  template<typename Archive>
  void serialize(Archive& ar, const unsigned int version)
  {
    ar & this->ExpectedType;
  }
  
};

TRACKTABLE_CORE_EXPORT std::ostream& operator<<(std::ostream& out, NullValue const& value);


/*! \brief Discriminated union type for properties
 *
 * We support five data types for properties: 64-bit integer,
 * double-precision float, string, timestamp, and Null.  If you do not
 * initialize a variant then its type will be Null by default.
 *
 * Under the hood this will probably always be a boost::variant but we
 * will provide our own interface so that you don't have to know or care
 * exactly how Boost does it.
 */

typedef boost::variant<NullValue, double, int64_t, string_type, Timestamp> PropertyValueT;
typedef boost::variant<NullValue, double, int64_t, string_type, Timestamp> PropertyValue;

inline PropertyValueT make_null(PropertyUnderlyingType null_type)
{
  NullValue my_value(null_type);
  return PropertyValueT(my_value);
}


/*! \brief Check to see whether a property value is null.
 *
 * @return True/false depending on whether or not the supplied value is null
 */

TRACKTABLE_CORE_EXPORT bool is_property_null(PropertyValueT const& value);


/*! \brief Get a property's underlying type.
 *
 * Retrieve a numeric constant that specifies the type stored in a
 * property.  This function is meant to help with serialization.
 */

TRACKTABLE_CORE_EXPORT PropertyUnderlyingType property_underlying_type(PropertyValueT const& value);


/*! \brief Utility method: convert a string to a PropertyUnderlyingType.
 */

template<typename text_type>
PropertyUnderlyingType string_to_property_type(text_type const& input)
{
  int i_property_type = boost::lexical_cast<int>(input);
  return static_cast<PropertyUnderlyingType>(i_property_type);
}

 
/*! \brief Return a property's data type as a string
 */

TRACKTABLE_CORE_EXPORT tracktable::string_type property_type_as_string(tracktable::PropertyValueT const& p);

/*! \brief Utility method: convert a source type (usually a string) to a PropertyValueT.
 *
 */

template<typename source_type>
PropertyValueT to_property_variant(source_type const& source, PropertyUnderlyingType thing_type)
{
  try
    {
    switch (thing_type)
      {
      case TYPE_STRING:
        return PropertyValueT(boost::lexical_cast<string_type>(source));
      case TYPE_REAL:
        return PropertyValueT(boost::lexical_cast<double>(source));
      case TYPE_TIMESTAMP:
        return PropertyValueT(time_from_string(boost::lexical_cast<string_type>(source)));
      case TYPE_INTEGER:
        return PropertyValueT(boost::lexical_cast<int64_t>(source));
      case TYPE_NULL:
      case TYPE_UNKNOWN:
        return PropertyValueT();
      }
    }
  catch (boost::bad_lexical_cast&)
    {
    return make_null(thing_type);
    }
}

} // namespace tracktable

namespace tracktable { namespace algorithms {
    
TRACKTABLE_CORE_EXPORT PropertyValueT interpolate_property(PropertyValueT const& left,
                                                           PropertyValueT const& right,
                                                           double t);
TRACKTABLE_CORE_EXPORT PropertyValueT extrapolate_property(PropertyValueT const& left,
                                                           PropertyValueT const& right,
                                                           double t);
} } // namespace tracktable::algorithms


#endif
