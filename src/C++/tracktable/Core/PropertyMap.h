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


/*
 * PropertyMap - map from string to string, double, timestamp or null
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
#include <tracktable/Core/PropertyValue.h>

#include <map>
#include <boost/serialization/map.hpp>

namespace tracktable {

/*! @brief Name -> property map
 *
 * We will use this as our container for named properties.
 *
 * @note A `std::unordered_map` (hashtable) would have slightly faster
 *       asymptotic performance but we will probably never have enough
 *       entries in a single property map for it to even be noticeable,
 *       let alone significant.
 */
typedef std::map<std::string, PropertyValueT> PropertyMap;

/*! @brief Check to see whether a given property is present.
 *
 * Check the map to see if it contains the given property. This
 * function will not modify the map in any way.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 */
TRACKTABLE_CORE_EXPORT bool has_property(PropertyMap const& properties, string_type const& name);


/*! @brief Retrieve a property from a map whatever its type.
 *
 * This function will give you back the named property as a
 * `PropertyValueT` (a Boost variant) if it is present in the map. If
 * not, you'll get back an uninitialized PropertyValueT and the bool
 * pointed at by is_present will be set to 'false'.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 * @param [out] is_present Flag indicating if the property is present
 *
 * @return
 *    On success, returns the requested property and sets `*is_present` to
 *    `true`. On failure, returns an uninitialized property and sets
 *    `*is_present` to `false`.
 */
TRACKTABLE_CORE_EXPORT PropertyValueT property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! @brief Retrieve a string-valued property from the map.
 *
 * This function will give you back the named property as a
 * `string_type` if it is present and that is its proper type. It will
 * not attempt to cast other types to `string_type`.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 * @param [out] is_present Flag indicating if the property is present
 *
 * @return
 *    On success, returns the requested property as a `string_type` and
 *    sets `*is_present` to `true`. On failure, returns an uninitialized
 *    `string_type` and sets `*is_present` to `false`.
 */

TRACKTABLE_CORE_EXPORT string_type string_property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! @brief Retrieve a real-valued property from the map.
 *
 * This function will give you back the named property as a
 * double-precision floating point number if it is present and that is
 * its proper type. It will not attempt to cast other types to
 * double.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 * @param [out] is_present Flag indicating if the property is present
 *
 * @return
 *    On success, returns the requested property as a `double` and sets
 *    `*is_present` to `true`. On failure, returns `0` and sets `*is_present` to
 *    `false`.
 */

TRACKTABLE_CORE_EXPORT double real_property(PropertyMap const& properties, string_type const& name, bool* is_present=0);

/*! @brief Retrieve a timestamp-valued property from the map.
 *
 * This function will give you back the named property as a Timestamp
 * if it is present and that is its proper type. It will not attempt
 * to cast other types to Timestamp.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 * @param [out] is_present Flag indicating if the property is present
 *
 * @return
 *    On success, returns the requested property as a `Timestamp` and sets
 *    `*is_present` to `true`. On failure, returns an `uninitialized
 *    timestamp` and sets `*is_present` to `false`.
 */

TRACKTABLE_CORE_EXPORT Timestamp timestamp_property(PropertyMap const& properties,  string_type const& name, bool* is_present=0);

/*! @brief Retrieve a null-valued property from the map.
 *
 * This function will give you back the named property as a NullValue
 * if it is present and that is its proper type. It will not attempt
 * to cast other types to NullValue.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 * @param [out] is_present Flag indicating if the property is present
 *
 * @return
 *    On success, returns the requested property as a `NullValue` and sets
 *    `*is_present` to `true`. On failure, returns an `uninitialized
 *    NullValue` and sets `*is_present` to `false`.
 */

TRACKTABLE_CORE_EXPORT NullValue nullvalue_property(PropertyMap const& properties,  string_type const& name, bool* is_present=0);

/*! @brief Add a value to the map.
 *
 * @fn tracktable::void set_property(PropertyMap& properties, string_type const& name, double value)
 *
 * This function will all add a single value to the map. If the
 * value is already present it will be silently overwritten.
 *
 * @param [in] properties Property map
 * @param [in] name Property to search for in the map
 * @param [out] value Value to set the property to
 */
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, double value);

/**
 * @overload tracktable::void set_property(PropertyMap& properties, string_type const& name, string_type const& value)
 */
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, string_type const& value);

/**
 * @overload tracktable::void set_property(PropertyMap& properties, string_type const& name, Timestamp const& value)
 */
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, Timestamp const& value);

/**
 * @overload tracktable::void set_property(PropertyMap& properties, string_type const& name, NullValue const& value)
 */
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, NullValue const& value);

/**
 * @overload tracktable::void set_property(PropertyMap& properties, string_type const& name, int64_t value)
 */
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, int64_t value);

/**
 * @overload tracktable::void set_property(PropertyMap& properties, string_type const& name, PropertyValueT const& value)
 */
TRACKTABLE_CORE_EXPORT void set_property(PropertyMap& properties, string_type const& name, PropertyValueT const& value);

/*! @brief Retrieve a property value or a default if it's not there.
 */
TRACKTABLE_CORE_EXPORT PropertyValueT property_with_default(PropertyMap const& properties, string_type const& name, PropertyValueT const& default_value);
TRACKTABLE_CORE_EXPORT double real_property_with_default(PropertyMap const& properties, string_type const& name, double default_value);
TRACKTABLE_CORE_EXPORT string_type string_property_with_default(PropertyMap const& properties, string_type const& name, string_type const& default_value);
TRACKTABLE_CORE_EXPORT Timestamp timestamp_property_with_default(PropertyMap const& properties, string_type const& name, Timestamp const& default_value);
TRACKTABLE_CORE_EXPORT NullValue nullvalue_property_with_default(PropertyMap const& properties, string_type const& name, NullValue const& default_value);

TRACKTABLE_CORE_EXPORT string_type property_map_to_string(PropertyMap const& properties);

/** Provides an overloaded equality operator that that accounts for floating point epsilon differences
 *
 * Except for the call to `compare(const PropertyValueT&, const PropertyValueT&, double, bool)`
 * this function is identical to the default `std::map` comparator.
 */
TRACKTABLE_CORE_EXPORT bool operator==(const PropertyMap& pm1, const PropertyMap& pm2);

} // exit namespace tracktable

namespace tracktable { namespace algorithms {

/*! @brief Interpolate between two property maps.
 *
 * Interpolation is well-defined for numbers and for timestamps. For
 * strings, we choose the first string for `t <= 0.5` and the second
 * string for `t > 0.5`.
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
            TRACKTABLE_LOG(log::warning)
                      << "WARNING: interpolate<PropertyMap>: "
                      << "Couldn't retrieve property '"
                      << key << "' (type "
                      << property_underlying_type((*first_iter).second)
                      << ") "
                      << " from second map. "
                      << "Property is present but has type "
                      << property_underlying_type((*second_iter).second)
                      << ". "
                      << "Re-using value from first point.";
            result[key] = (*first_iter).second;
            }
          }
        }
      return result;
    }
};

template<>
struct extrapolate<PropertyMap>
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
                    result[key] = extrapolate_property(
                        (*first_iter).second,
                        (*second_iter).second,
                        t
                    );
                }
                catch (boost::bad_get& /*e*/)
                {
                    TRACKTABLE_LOG(log::warning)
                        << "WARNING: extrapolate<PropertyMap>: "
                        << "Couldn't retrieve property '"
                        << key << "' (type "
                        << property_underlying_type((*first_iter).second)
                        << ") "
                        << " from second map. "
                        << "Property is present but has type "
                        << property_underlying_type((*second_iter).second)
                        << ". "
                        << "Re-using value from first point.";
                    result[key] = (*first_iter).second;
                }
            }
        }
        return result;
    }
};

} } // exit namespace tracktable::algorithms


#endif
