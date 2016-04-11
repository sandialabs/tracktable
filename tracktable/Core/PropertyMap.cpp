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
      std::cerr << "WARNING: PropertyMap: Property '"
                << name << "' is present but is not of the requested type\n";
      return default_value;
      }
    }
  else
    {
    return default_value;
    }
}

// ----------------------------------------------------------------------

struct InterpolateProperties : public boost::static_visitor<tracktable::PropertyValueT>
{
public:
  double interpolant;
  tracktable::PropertyValueT SecondValue;

  typedef tracktable::PropertyValueT result_type;

  result_type operator()(tracktable::NullValue const& value1)
    {
      if (interpolant < 0.5)
        {
        return value1;
        }
      else
        {
        return this->SecondValue;
        }
    }

  result_type operator()(double value1)
    {
      double value2 = boost::get<double>(this->SecondValue);
      return tracktable::PropertyValueT((1-this->interpolant) * value1 +
                                        this->interpolant * value2);
    }

  result_type operator()(int64_t value1)
    {
      if (tracktable::is_property_null(this->SecondValue))
        {
        return (this->interpolant < 0.5) ? value1 : this->SecondValue;
        }
      int64_t value2 = boost::get<int64_t>(this->SecondValue);
      int64_t result = static_cast<int64_t>((1-this->interpolant) * value1 + (this->interpolant + value2));
      return tracktable::PropertyValueT(result);
    }

  result_type operator()(tracktable::string_type const& value1)
    {
      if (tracktable::is_property_null(this->SecondValue))
        {
        return (this->interpolant < 0.5) ? value1 : this->SecondValue;
        }
      tracktable::string_type value2(boost::get<tracktable::string_type>(this->SecondValue));
      if (this->interpolant < 0.5)
        {
        return tracktable::PropertyValueT(value1);
        }
      else
        {
        return tracktable::PropertyValueT(value2);
        }
    }

  result_type operator()(tracktable::Timestamp const& value1)
    {
      if (tracktable::is_property_null(this->SecondValue))
        {
        return (this->interpolant < 0.5) ? value1 : this->SecondValue;
        }

      tracktable::Timestamp value2(boost::get<tracktable::Timestamp>(this->SecondValue));
      tracktable::Duration delta_t = (value2 - value1);
      int64_t microseconds = static_cast<int64_t>(delta_t.total_microseconds() * this->interpolant);
      tracktable::Duration interpolated_delta_t = tracktable::microseconds(microseconds);
      return tracktable::PropertyValueT(value1 + interpolated_delta_t);
    }
};

// ----------------------------------------------------------------------

/*! \brief Return a property's data type as a string
 */

tracktable::string_type property_type_as_string(tracktable::PropertyValueT const& p)
{
  switch (tracktable::property_underlying_type(p))
    {
    case tracktable::TYPE_UNKNOWN:
      return "unknown";
    case tracktable::TYPE_REAL:
      return "real";
    case tracktable::TYPE_STRING:
      return "string";
    case tracktable::TYPE_TIMESTAMP:
      return "timestamp";
    case tracktable::TYPE_INTEGER:
      return "integer";
    case tracktable::TYPE_NULL:
      return "null";
    default:
      return "unsupported";
    }
}

// ----------------------------------------------------------------------


template<typename value_type>
struct dispatch_interpolate
{
  static inline tracktable::PropertyValueT apply(tracktable::PropertyValueT const& first,
                                                 tracktable::PropertyValueT const& second,
                                                 double interpolant)
    {
      value_type const *first_value, *second_value;
      if (tracktable::is_property_null(first) && interpolant < 0.5)
        {
        return first;
        }
      else if (tracktable::is_property_null(second) && interpolant > 0.5)
        {
        return second;
        }
      else
        {
        value_type result;
        first_value = boost::get<value_type>(&first);
        second_value = boost::get<value_type>(&second);
        result = tracktable::interpolate<value_type>(*first_value, *second_value, interpolant);
        return tracktable::PropertyValueT(result);
        }
    }
};


// ----------------------------------------------------------------------

class RetrieveUnderlyingType : public boost::static_visitor<>
{
public:
  tracktable::PropertyUnderlyingType value;

  RetrieveUnderlyingType()
    { this->value = tracktable::TYPE_UNKNOWN; }

  void operator()(double /*value*/)
    {
      this->value = tracktable::TYPE_REAL;
    }

  void operator()(tracktable::string_type const& /*value*/)
    {
      this->value = tracktable::TYPE_STRING;
    }

  void operator()(tracktable::Timestamp const& /*ts*/)
    {
      this->value = tracktable::TYPE_TIMESTAMP;
    }

  void operator()(int64_t /*value*/)
    {
      this->value = tracktable::TYPE_INTEGER;
    }

  void operator()(tracktable::NullValue const& /*value*/)
    {
      this->value = tracktable::TYPE_NULL;
    }
};

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
 * @param[in] value       Timestamp value to store
 */
void set_property(PropertyMap& properties, string_type const& name, int64_t value)
{
  properties[name] = PropertyValueT(value);
}

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

/*! \brief Check whether a particular property is null
 *
 * @param[in] value    Property value to check
 * @return             True/false (null or not)
 */

bool is_property_null(PropertyValueT const& value)
{
  return (property_underlying_type(value) == TYPE_NULL);
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

PropertyUnderlyingType property_underlying_type(PropertyValueT const& pv)
{
  ::RetrieveUnderlyingType visitor;
  boost::apply_visitor(visitor, pv);

  return visitor.value;
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
      std::cerr << "WARNING: PropertyMap: Property '"
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
      std::cerr << "WARNING: PropertyMap: Property '"
                << name << "' is present but is not integer-valued\n";
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
      std::cerr << "WARNING: PropertyMap: Property '"
                << name << "' is present but is not a string\n";
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
      std::cerr << "WARNING: PropertyMap: Property '"
                << name << "' is present but is not a timestamp\n";
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

int64_t integer_property_with_default(
  PropertyMap const& properties,
  string_type const& name,
  int64_t default_value
)
{
  return ::typed_property_with_default<int64_t>(properties, name, default_value);
}

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
           << ::property_type_as_string(value)
           << "]: "
           << value << "}";
    }
  outbuf << ")";
  return outbuf.str();
}

std::ostream& operator<<(std::ostream& out, NullValue const& value)
{
  std::ostringstream outbuf;
  outbuf << "(null ";

  switch (value.ExpectedType)
    {
    case tracktable::TYPE_UNKNOWN:
      outbuf <<  "unknown";
    case tracktable::TYPE_REAL:
      outbuf <<  "real";
    case tracktable::TYPE_STRING:
      outbuf << "string";
    case tracktable::TYPE_TIMESTAMP:
      outbuf <<  "timestamp";
    case tracktable::TYPE_INTEGER:
      outbuf << "integer";
    case tracktable::TYPE_NULL:
      outbuf << "null";
    default:
      outbuf << "unsupported";
    }

  outbuf << ")";
  out << outbuf.str();
  return out;
}


} // exit namespace tracktable

// ----------------------------------------------------------------------

namespace tracktable { namespace algorithms {

/*! \brief Interpolate between two properties
 *
 * For timestamps and numeric properties, this function will give you
 * a linear interpolation between the start and end points.  For
 * strings, this function will give you the first string at less than
 * 0.5 and the second string at greater than 0.5.
 *
 * You will probably never need to call this function directly.  It
 * will be invoked when you try to interpolate between two points that
 * have property maps attached.
 *
 * @param[in] first   Starting value for interpolation
 * @param[in] second  Ending value for interpolation
 * @param[in] t       Interpolant; 0 means first value, 1 means second value
 * @return            Linearly-interpolated version of property
 */

PropertyValueT interpolate_property(
  PropertyValueT const& first,
  PropertyValueT const& second,
  double t
)
{
  if (t <= 0) return first;
  if (t >= 1) return second;

  ::InterpolateProperties calculator;
  calculator.interpolant = t;
  calculator.SecondValue = second;

  return boost::apply_visitor(calculator, first);
}

} } // exit namespace tracktable::algorithms
