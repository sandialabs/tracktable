/*
 * Copyright (c) 2014, Sandia Corporation.  All rights
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


/*
 * PropertyMap - map from string to string, double or timestamp
 *
 * Rather than clutter the point classes' API with lots of properties
 * that we might or might not ever use we're going to explicitly
 * define a few essentials and leave the rest in a property map
 * defined herein.
 */

#ifndef __tracktable_PropertyMap_h
#define __tracktable_PropertyMap_h

#include <tracktable/Core/TracktableCoreWindowsHeader.h>

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>

#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>

#include <boost/variant.hpp>
#include <map>

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
};

TRACKTABLE_CORE_EXPORT std::ostream& operator<<(std::ostream& out, NullValue const& value);


/*! \brief Discriminated union type for properties
 *
 * In this release we support exactly three data types for properties:
 * a timestamp, a string and a floating-point number.  We will never
 * support less than this.  In the future we might add an integer
 * if it proves necessary.
 *
 * Under the hood this will probably always be a boost::variant but we
 * will provide our own interface so that you don't have to know or care
 * exactly how Boost does it.
 */

typedef boost::variant<NullValue, double, int64_t, string_type, Timestamp> PropertyValueT;

inline PropertyValueT make_null(PropertyUnderlyingType null_type)
{
  NullValue my_value(null_type);
  return PropertyValueT(my_value);
}

/*! \brief Name -> property map
 *
 * We will use this as our container for named properties.
 *
 * \note A std::unordered_map (hashtable) would have slightly faster
 *       asymptotic performance but we will probably never have enough
 *       entries in a single property map for it to even be noticeable,
 *       let alone significant.
 */
typedef std::map<std::string, PropertyValueT> PropertyMap;

/*! \brief Check to see whether a given property is present.
 *
 * Check the map to see if it contains the given property.  This
 * function will not modify the map in any way.
 */
TRACKTABLE_CORE_EXPORT bool has_property(PropertyMap const& properties, string_type const& name);

/*! \brief Check to see whether a property value is null.
 *
 * @return True/false depending on whether or not the supplied value is null
 */

TRACKTABLE_CORE_EXPORT bool is_property_null(PropertyValueT const& value);

/*! \brief Retrieve a property from a map whatever its type.
 *
 * This function will give you back the named property as a
 * PropertyValueT (a Boost variant) if it is present in the map.  If
 * not, you'll get back an uninitialized PropertyValueT and the bool
 * pointed at by is_present will be set to 'false'.
 *
 * On success, returns the requested property and sets *is_present to
 * true.  On failure, returns an uninitialized property and sets
 * *is_present to false.
 */
TRACKTABLE_CORE_EXPORT PropertyValueT property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! \brief Retrieve a string-valued property from the map.
 *
 * This function will give you back the named property as a
 * string_type if it is present and that is its proper type.  It will
 * not attempt to cast other types to string_type.
 *
 * On success, returns the requested property as a string_type and
 * sets *is_present to true.  On failure, returns an uninitialized
 * string_type and sets *is_present to false.
 */

TRACKTABLE_CORE_EXPORT string_type string_property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! \brief Retrieve a real-valued property from the map.
 *
 * This function will give you back the named property as a
 * double-precision floating point number if it is present and that is
 * its proper type.  It will not attempt to cast other types to
 * double.
 *
 * On success, returns the requested property as a double and sets
 * *is_present to true.  On failure, returns 0 and sets *is_present to
 * false.
 */

TRACKTABLE_CORE_EXPORT double real_property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! \brief Retrieve an integer-valued property from the map.
 *
 * This function will give you back the named property as a 64-bit
 * signed integer if it is present and that is its proper type.  It
 * will not attempt to cast other types to int64_t.
 *
 * On success, returns the requested property as an int64_t and sets
 * *is_present to true.  On failure, returns 0 and sets *is_present to
 * false.
 */

TRACKTABLE_CORE_EXPORT int64_t integer_property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! \brief Retrieve a timestamp-valued property from the map.
 *
 * This function will give you back the named property as a Timestamp
 * if it is present and that is its proper type.  It will not attempt
 * to cast other types to Timestamp.
 *
 * On success, returns the requested property as a Timestamp and sets
 * *is_present to true.  On failure, returns an uninitialized
 * timestamp and sets *is_present to false.
 */

TRACKTABLE_CORE_EXPORT Timestamp timestamp_property(PropertyMap const& properties,  string_type const& name, bool* is_present=0);

/*! \brief Get a property's underlying type.
 *
 * Retrieve a numeric constant that specifies the type stored in a
 * property.  This function is meant to help with serialization.
 */

TRACKTABLE_CORE_EXPORT PropertyUnderlyingType property_underlying_type(PropertyValueT const& value);

/*! \brief Add a value to the map.
 *
 * These functions will all add a single value to the map.  If the
 * value is already present it will be silently overwritten.
 */


TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, double value);
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, string_type const& value);
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, Timestamp const& value);
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, int64_t value);
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, PropertyValueT const& value);

/*! \brief Retrieve a property value or a default if it's not there.
 *
 */

TRACKTABLE_CORE_EXPORT PropertyValueT property_with_default(PropertyMap const& properties, string_type const& name, PropertyValueT const& default_value);
TRACKTABLE_CORE_EXPORT double real_property_with_default(PropertyMap const& properties, string_type const& name, double default_value);
TRACKTABLE_CORE_EXPORT string_type string_property_with_default(PropertyMap const& properties, string_type const& name, string_type const& default_value);
TRACKTABLE_CORE_EXPORT Timestamp timestamp_property_with_default(PropertyMap const& properties, string_type const& name, Timestamp const& default_value);
TRACKTABLE_CORE_EXPORT int64_t integer_property_with_default(PropertyMap const& properties, string_type const& name, int64_t default_value);

TRACKTABLE_CORE_EXPORT string_type property_map_to_string(PropertyMap const& properties);


/*! \brief Utility method: convert a string to a PropertyUnderlyingType.
 */

template<typename text_type>
PropertyUnderlyingType string_to_property_type(text_type const& input)
{
  int i_property_type = boost::lexical_cast<int>(input);
  return static_cast<PropertyUnderlyingType>(i_property_type);
}

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


} // exit namespace tracktable

namespace tracktable { namespace algorithms {

TRACKTABLE_CORE_EXPORT PropertyValueT interpolate_property(PropertyValueT const& left,
                                                           PropertyValueT const& right,
                                                           double t);

/*! \brief Interpolate between two property maps.
 *
 * Interpolation is well-defined for numbers and for timestamps.  For
 * strings, we choose the first string for t <= 0.5 and the second
 * string for t > 0.5.
 */
template<>
struct interpolate<PropertyMap>
{
  static inline PropertyMap
  apply(
    PropertyMap const& first,
    PropertyMap const& second,
    double t
    )
    {
      PropertyMap::const_iterator first_iter, second_iter;
      PropertyMap result;

      for (first_iter = first.begin();
           first_iter != first.end();
           ++first_iter)
        {
        string_type key((*first_iter).first);
        second_iter = second.find(key);
        if (second_iter != second.end())
          {
          try
            {
            result[key] = interpolate_property(
              (*first_iter).second,
              (*second_iter).second,
              t
              );
            }
          catch (boost::bad_get& /*e*/)
            {
            std::cout << "WARNING: interpolate<PropertyMap>: "
                      << "Couldn't retrieve property '"
                      << key << "' (type "
                      << property_underlying_type((*first_iter).second)
                      << ") "
                      << " from second map. ";
            std::cout << "Property is present but has type "
                      << property_underlying_type((*second_iter).second)
                      << ". ";
            std::cout << "Re-using value from first point.\n";
            result[key] = (*first_iter).second;
            }
          }
        }
      return result;
    }
};

} } // exit namespace tracktable::algorithms

#endif
