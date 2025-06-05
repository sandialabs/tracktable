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

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/Timestamp.h>

#include <iostream>
#include <cassert>

namespace {

/*! \brief Retrieve a property or some default value.
 *
 * This method of retrieving a named property will never fail or throw
 * an exception.  You will either get back the value of the property
 * you requested as your desired type or else you will get back your
 * default value.
 *
 * @param[in] properties     Property map for lookup
 * @param[in] name           Name of property to retrieve
 * @param[in] default_value  Value to return if property is not present or has incorrect type
 *
 * Note: At present, the type of the default value determines the type
 * that will be returned to you.
 */

template<typename T>
T typed_property_with_default(
  tracktable::PropertyMap const& properties,
  tracktable::string_type const& name,
  T const& default_value
  )
{
  bool is_it_there;
  tracktable::PropertyValueT variant_result(tracktable::property(properties, name, &is_it_there));
  if (is_it_there)
    {
    try
      {
      return boost::get<T>(variant_result);
      }
    catch (boost::bad_get e)
      {
      TRACKTABLE_LOG(tracktable::log::warning)
        << "PropertyMap: Property '"
        << name
        << "' is present but is not of the requested type";
      return default_value;
      }
    }
  else
    {
    return default_value;
    }
}
} // close anonymous namespace

namespace tracktable {

/*! \brief Set a property in a collection
 *
 * @param[in] properties  Property map to alter
 * @param[in] name        Name of property to change
 * @param[in] value       Numeric (double-precision) value to store
 */
void set_property(PropertyMap& properties, string_type const& name, double value)
{
  properties[name] = PropertyValueT(value);
}

/*! \brief Set a property in a collection
 *
 * @param[in] properties  Property map to alter
 * @param[in] name        Name of property to change
 * @param[in] value       String value to store
 */
void set_property(PropertyMap& properties, string_type const& name, string_type const& value)
{
  properties[name] = PropertyValueT(value);
}

/*! \brief Set a property in a collection
 *
 * @param[in] properties  Property map to alter
 * @param[in] name        Name of property to change
 * @param[in] value       Timestamp value to store
 */
void set_property(PropertyMap& properties, string_type const& name, Timestamp const& value)
{
  properties[name] = PropertyValueT(value);
}

/*! \brief Set a property in a collection
 *
 * @param[in] properties  Property map to alter
 * @param[in] name        Name of property to change
 * @param[in] value       NullValue value to store
 */
void set_property(PropertyMap& properties, string_type const& name, NullValue const& value)
{
  properties[name] = PropertyValueT(value);
}

#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
/*! \brief Set a property in a collection
 *
 * @param[in] properties  Property map to alter
 * @param[in] name        Name of property to change
 * @param[in] value       Timestamp value to store
 */
void set_property(PropertyMap& properties, string_type const& name, int64_t value)
{
  properties[name] = PropertyValueT(value);
}
#endif

/*! \brief Set a property in a collection
 *
 * @param[in] properties  Property map to alter
 * @param[in] name        Name of property to change
 * @param[in] value       Timestamp value to store
 */

void set_property(PropertyMap& properties, string_type const& name, PropertyValueT const& value)
{
  properties[name] = value;
}


/*! \brief Check whether a property is present
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to look up
 * @return                 True/false (found or not)
 */
bool has_property(PropertyMap const& properties, string_type const& name)
{
  return (properties.find(name) != properties.end());
}



// ----------------------------------------------------------------------

/*! \brief Retrieve a property regardless of its type
 *
 * This accessor will let you retrieve the value of
 * a named property regardless of its underlying data
 * type.  The catch is that we don't know whether or
 * not the property is there to begin with.  If it
 * isn't there then we can't return anything sensible.
 *
 * We deal with this by letting you pass in an optional pointer
 * to a boolean.  We will set its value to true or false
 * depending on whether or not we found the property
 * you wanted.  If it is true, the return value is
 * guaranteed to be whatever is in the map.  If it is
 * false, the return value will be an empty
 * variant.
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to find
 * @param     is_present   Pointer to boolean
 * @return    Value of desired property (if present)
 */

PropertyValueT property(PropertyMap const& properties, string_type const& name, bool* is_present)
{
  PropertyMap::const_iterator iter = properties.find(name);
  if (iter != properties.end())
    {
    if (is_present) *is_present = true;
    return (*iter).second;
    }
  else
    {
    if (is_present) *is_present = false;
    return PropertyValueT();
    }
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a numeric property
 *
 * This accessor will let you retrieve the value of a numeric
 * property. The catch is that we don't know whether or not the
 * property is there to begin with.  If it isn't there then we can't
 * return anything sensible.
 *
 * We deal with this by letting you pass in an optional pointer to a
 * boolean.  We will set its value to true or false depending on
 * whether or not we found the property you wanted.  If it is true,
 * the return value is guaranteed to be whatever is in the map.  If it
 * is false, the return value will be uninitialized.
 *
 * \note For the purposes of this function, a property that is present
 *       but that has the wrong type is the same as a property that is
 *       not present in the map.
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to find
 * @param     is_present   Pointer to boolean
 * @return    Value of desired property (if present)
 */

double real_property(PropertyMap const& properties, string_type const& name, bool* is_present)
{
  bool is_it_there;
  PropertyValueT tuple_value = property(properties, name, &is_it_there);

  if (is_it_there)
    {
    try
      {
      if (is_present) *is_present = true;
      return boost::get<double>(tuple_value);
      }
    catch (boost::bad_get e)
      {
      TRACKTABLE_LOG(log::warning)
        << "PropertyMap: Property '"
        << name << "' is present but is not real-valued\n";
      if (is_present) *is_present = false;
      return 0;
      }
    }
  else
    {
    if (is_present) *is_present = false;
    return 0;
    }
}

// ----------------------------------------------------------------------

#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)

/*! \brief Retrieve an integer property
 *
 * This accessor will let you retrieve the value of a string
 * property. The catch is that we don't know whether or not the
 * property is there to begin with.  If it isn't there then we can't
 * return anything sensible.
 *
 * We deal with this by letting you pass in an optional pointer to a
 * boolean.  We will set its value to true or false depending on
 * whether or not we found the property you wanted.  If it is true,
 * the return value is guaranteed to be whatever is in the map.  If it
 * is false, the return value will be uninitialized.
 *
 * \note For the purposes of this function, a property that is present
 *       but that has the wrong type is the same as a property that is
 *       not present in the map.
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to find
 * @param     is_present   Pointer to boolean
 * @return    Value of desired property (if present)
 */

int64_t integer_property(PropertyMap const& properties, string_type const& name, bool* is_present)
{
  bool is_it_there;
  PropertyValueT tuple_value = property(properties, name, &is_it_there);

  if (is_it_there)
    {
    try
      {
      if (is_present) *is_present = true;
      return boost::get<int64_t>(tuple_value);
      }
    catch (boost::bad_get e)
      {
      TRACKTABLE_LOG(log::warning)
        << "PropertyMap: Property '"
        << name << "' is present but is not integer-valued";
      if (is_present) *is_present = false;
      return 0;
      }
    }
  else
    {
    if (is_present) *is_present = false;
    return 0;
    }
}

#endif

// ----------------------------------------------------------------------

/*! \brief Retrieve a string property
 *
 * This accessor will let you retrieve the value of a string
 * property. The catch is that we don't know whether or not the
 * property is there to begin with.  If it isn't there then we can't
 * return anything sensible.
 *
 * We deal with this by letting you pass in an optional pointer to a
 * boolean.  We will set its value to true or false depending on
 * whether or not we found the property you wanted.  If it is true,
 * the return value is guaranteed to be whatever is in the map.  If it
 * is false, the return value will be uninitialized.
 *
 * \note For the purposes of this function, a property that is present
 *       but that has the wrong type is the same as a property that is
 *       not present in the map.
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to find
 * @param     is_present   Pointer to boolean
 * @return    Value of desired property (if present)
 */

string_type string_property(PropertyMap const& properties, string_type const& name, bool* is_present)
{
  bool is_it_there;
  PropertyValueT tuple_value = property(properties, name, &is_it_there);

  if (is_it_there)
    {
    try
      {
      if (is_present) *is_present = true;
      return boost::get<string_type>(tuple_value);
      }
    catch (boost::bad_get e)
      {
      TRACKTABLE_LOG(log::warning)
        << "PropertyMap: Property '"
        << name << "' is present but is not a string";
      if (is_present) *is_present = false;
      return string_type();
      }
    }
  else
    {
    if (is_present) *is_present = false;
    return string_type();
    }
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a timestamp property
 *
 * This accessor will let you retrieve the value of a timestamp
 * property. The catch is that we don't know whether or not the
 * property is there to begin with.  If it isn't there then we can't
 * return anything sensible.
 *
 * We deal with this by letting you pass in an optional pointer to a
 * boolean.  We will set its value to true or false depending on
 * whether or not we found the property you wanted.  If it is true,
 * the return value is guaranteed to be whatever is in the map.  If it
 * is false, the return value will be uninitialized.
 *
 * \note For the purposes of this function, a property that is present
 *       but that has the wrong type is the same as a property that is
 *       not present in the map.
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to find
 * @param     is_present   Pointer to boolean
 * @return    Value of desired property (if present)
 */

Timestamp timestamp_property(PropertyMap const& properties, string_type const& name, bool* is_present)
{
  bool is_it_there;
  PropertyValueT tuple_value = property(properties, name, &is_it_there);

  if (is_it_there)
    {
    try
      {
      if (is_present) *is_present = true;
      return boost::get<Timestamp>(tuple_value);
      }
    catch (boost::bad_get e)
      {
      TRACKTABLE_LOG(log::warning)
        << "PropertyMap: Property '"
        << name << "' is present but is not a timestamp";
      if (is_present) *is_present = false;
      return Timestamp();
      }
    }
  else
    {
    if (is_present) *is_present = false;
    return Timestamp();
    }
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a null property
 *
 * This accessor will let you retrieve the value of a null
 * property. The catch is that we don't know whether or not the
 * property is there to begin with.  If it isn't there then we can't
 * return anything sensible.
 *
 * We deal with this by letting you pass in an optional pointer to a
 * boolean.  We will set its value to true or false depending on
 * whether or not we found the property you wanted.  If it is true,
 * the return value is guaranteed to be whatever is in the map.  If it
 * is false, the return value will be uninitialized.
 *
 * \note For the purposes of this function, a property that is present
 *       but that has the wrong type is the same as a property that is
 *       not present in the map.
 *
 * @param[in] properties   Property map to interrogate
 * @param[in] name         Name of property to find
 * @param     is_present   Pointer to boolean
 * @return    Value of desired property (if present)
 */

NullValue nullvalue_property(PropertyMap const& properties, string_type const& name, bool* is_present)
{
  bool is_it_there;
  PropertyValueT tuple_value = property(properties, name, &is_it_there);

  if (is_it_there)
    {
    try
      {
      if (is_present) *is_present = true;
      return boost::get<NullValue>(tuple_value);
      }
    catch (boost::bad_get e)
      {
      TRACKTABLE_LOG(log::warning)
        << "PropertyMap: Property '"
        << name << "' is present but is not a nullvalue";
      if (is_present) *is_present = false;
      return NullValue();
      }
    }
  else
    {
    if (is_present) *is_present = false;
    return NullValue();
    }
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a property or some default value.
 *
 * This method of retrieving a named property will never fail or throw
 * an exception.  You will either get back the value of the property
 * you requested as your desired type or else you will get back your
 * default value.
 *
 * @param[in] properties     Property map for lookup
 * @param[in] name           Name of property to retrieve
 * @param[in] default_value  Value to return if property is not present
 *
 * \note This function works with variants instead of trying to
 *       cast down to a more specific type.  As such, it does not
 *       care what the underlying type is for the requested value, only
 *       whether or not it's there.
 */

PropertyValueT property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  PropertyValueT const& default_value
  )
{
  bool ok;
  PropertyValueT result(property(properties, name, &ok));
  if (ok)
    {
    return result;
    }
  else
    {
    return default_value;
    }
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a numeric property or some default value.
 *
 * This method of retrieving a named property will never fail or throw
 * an exception.  You will either get back the value of the property
 * you requested as your desired type or else you will get back your
 * default value.
 *
 * @param[in] properties     Property map for lookup
 * @param[in] name           Name of property to retrieve
 * @param[in] default_value  Value to return if property is not present
 *
 * \note A property that is present but not numeric is treated as if
 *       the property were not present at all.
 */

double real_property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  double default_value
)
{
  return ::typed_property_with_default<double>(properties, name, default_value);
}


// ----------------------------------------------------------------------

#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)

int64_t integer_property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  int64_t default_value
)
{
  return ::typed_property_with_default<int64_t>(properties, name, default_value);
}

#endif
// ----------------------------------------------------------------------

/*! \brief Retrieve a string property or some default value.
 *
 * This method of retrieving a named property will never fail or throw
 * an exception.  You will either get back the value of the property
 * you requested as your desired type or else you will get back your
 * default value.
 *
 * @param[in] properties     Property map for lookup
 * @param[in] name           Name of property to retrieve
 * @param[in] default_value  Value to return if property is not present
 *
 * \note A property that is present but not numeric is treated as if
 *       the property were not present at all.
 */

string_type string_property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  string_type const& default_value
)
{
  return ::typed_property_with_default<string_type>(properties, name, default_value);
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a timestamp property or some default value.
 *
 * This method of retrieving a named property will never fail or throw
 * an exception.  You will either get back the value of the property
 * you requested as your desired type or else you will get back your
 * default value.
 *
 * @param[in] properties     Property map for lookup
 * @param[in] name           Name of property to retrieve
 * @param[in] default_value  Value to return if property is not present
 *
 * \note A property that is present but not numeric is treated as if
 *       the property were not present at all.
 */

Timestamp timestamp_property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  Timestamp const& default_value
)
{
  return ::typed_property_with_default<Timestamp>(properties, name, default_value);
}

// ----------------------------------------------------------------------

/*! \brief Retrieve a nullvalue property or some default value.
 *
 * This method of retrieving a named property will never fail or throw
 * an exception.  You will either get back the value of the property
 * you requested as your desired type or else you will get back your
 * default value.
 *
 * @param[in] properties     Property map for lookup
 * @param[in] name           Name of property to retrieve
 * @param[in] default_value  Value to return if property is not present
 *
 * \note A property that is present but not numeric is treated as if
 *       the property were not present at all.
 */

NullValue nullvalue_property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  NullValue const& default_value
)
{
  return ::typed_property_with_default<NullValue>(properties, name, default_value);
}

// ----------------------------------------------------------------------

/*! \brief Render a property map's contents as a string
 *
 * This function constructs a human-readable representation of a named
 * property map.
 *
 * @param[in] properties    Property map to write out
 * @return                  Contents of property map as a string_type
 */

string_type property_map_to_string(
  tracktable::PropertyMap const& properties
  )
{
  std::ostringstream outbuf;
  imbue_stream_with_timestamp_output_format(outbuf, default_timestamp_output_format());
  bool first_one = true;

  outbuf << "Properties: ( ";

  for (tracktable::PropertyMap::const_iterator iter = properties.begin();
       iter != properties.end();
       ++iter)
    {
    string_type name = (*iter).first;
    tracktable::PropertyValueT value = (*iter).second;

    if (first_one == false)
      {
      outbuf << ", ";
      }
    first_one = false;

    outbuf << "{" << name << " ["
           << tracktable::property_type_as_string(value)
           << "]: "
           << value << "}";
    }
  outbuf << ")";
  return outbuf.str();
}

// Except for the call to compare() this function is identical to the std::map operator==
TRACKTABLE_CORE_EXPORT bool operator==(const PropertyMap& pm1, const PropertyMap& pm2) {
  // First compare the sizes
  if (pm1.size() != pm2.size())
      return false;

  // Because the property map iterators are sorted on key we can use the iterators
  // to provide an O(n) comparison
  PropertyMap::const_iterator iter1 = pm1.begin();
  PropertyMap::const_iterator iter2 = pm2.begin();

  while (iter1 != pm1.end()) {

    // Compare property names first
    // If any name is different the property maps are different
    if (iter1->first != iter2->first)
        return false;

    // Now we'll use the compare method of the property values
    if (compare(iter1->second, iter2->second) != 0)
        return false;

    iter1++;
    iter2++;
  }

  // So far all the items are equal, and we're done checking pm1 against
  // pm2. But, if pm2 has any more items the two maps aren't equal.
  if (iter2 != pm2.end())
    return false;

  // And, of course, if we haven't found any differences by now, the maps are equal
  return true;
}


} // exit namespace tracktable
