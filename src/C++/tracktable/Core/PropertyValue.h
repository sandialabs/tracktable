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
 * PropertyValueT - variant type for properties we attach to
 * points/trajectories
 *
 * We allow the user to specify named properties on points and
 * trajectories that take one of four types: null, double-precision
 * floating point, string, and timestamp.
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
#include <boost/math/special_functions/relative_difference.hpp>

namespace tracktable {

typedef enum {
  TYPE_UNKNOWN   = 0,
  TYPE_REAL      = 1,
  TYPE_STRING    = 2,
  TYPE_TIMESTAMP = 3,
  TYPE_NULL      = 4
} PropertyUnderlyingType;


class NullValue
{
public:
  friend class boost::serialization::access;

  PropertyUnderlyingType ExpectedType;

  /** Instantiate NullValue using a default type
   */
  NullValue()
    : ExpectedType(TYPE_UNKNOWN)
    { }

  /** Instantiate NullValue with a specified value
   *
   * @param [in] my_type Value to set as null value
   */
  NullValue(PropertyUnderlyingType my_type)
    : ExpectedType(my_type)
    { }

  /** Copy contructor, NullValue with a copy of another
   *
   * @param [in] other NullValue to copy from
   */
  NullValue(NullValue const& other) :
    ExpectedType(other.ExpectedType)
    { }

  /** Assign a NullValue to the value of another.
   *
   * @param [in] other NullValue to assign value of
   * @return NullValue with the new assigned value
   */
  void operator=(NullValue const& other)
    {
      this->ExpectedType = other.ExpectedType;
    }

  /** Check whether one NullValue is equal to another by comparing the properties.
   *
   * Two items are equal if all of their properties are equal.
   *
   * @param [in] other NullValue for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(NullValue const& /*other*/) const
    {
      return false;
    }

  /** Check whether two NullValue are unequal.
   *
   * @param [in] other NullValue for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(NullValue const& /*other*/) const
    {
      return true;
    }

  /** Check whether NullValue is less than another.
   *
   * @param [in] other NullValue for comparison
   * @return Boolean indicating equivalency
   */
  bool operator<(NullValue const& other) const
    {
      return (this->ExpectedType < other.ExpectedType);
    }

private:
  /** Serialize the coordinates to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<typename Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
  {
    ar & BOOST_SERIALIZATION_NVP(this->ExpectedType);
  }

};

/** Write a null value to a stream as a string
 *
 * @param [in] os Stream to write to
 * @param [in] box Box to write to string
 */
TRACKTABLE_CORE_EXPORT std::ostream& operator<<(std::ostream& out, NullValue const& value);


/*! @brief Discriminated union type for properties
 *
 * We support four data types for properties:
 * `double-precision float`, `string`, `timestamp, and `Null`. If you do not
 * initialize a variant then its type will be `Null` by default.
 *
 * Note that there is not a separate integer data type. You'll need
 * to use doubles for that. This is a deliberate decision: we run
 * into compiler troubles trying to serialize and unserialize property
 * values if we allow integers as a distinct type.
 *
 * Under the hood this will probably always be a `boost::variant` but we
 * will provide our own interface so that you don't have to know or care
 * exactly how Boost does it.
 */

// typedef boost::variant<NullValue, int64_t, double, string_type, Timestamp> PropertyValueT;
 typedef boost::variant<
   NullValue,
   double,
   string_type,
   Timestamp
   >
   PropertyValue;
typedef PropertyValue PropertyValueT;

inline PropertyValue make_null(PropertyUnderlyingType null_type)
{
  NullValue my_value(null_type);
  return PropertyValue(my_value);
}

/** Provides a total order comparison of all PropertyValue instances allowing for floating point epsilon differences
 *
 * Compares two property values to provide a total ordering.
 *
 * When the property values are of different types the relationship between their
 * underlying value types will be returned based on the ordering of the parameters.
 *
 * When the property values are of the same type a logical comparison of the values is performed.
 *
 * When the parameters contain double values the parameters difference and `is_epsilon_difference`
 * will control tests of equality. Machine epsilon is an upper bound on the rounding error that
 * can occur in floating point arithmetic for a specific type.
 *
 * Also see:
 *
 * https://en.wikipedia.org/wiki/Floating-point_arithmetic#Accuracy_problems
 * https://en.wikipedia.org/wiki/Machine_epsilon
 * https://www.boost.org/doc/libs/1_72_0/libs/math/doc/html/math_toolkit/float_comparison.html
 * Knuth D.E. The art of computer programming, vol II, section 4.2, Floating-Point Comparison 4.2.2, pages 198-220
 *
 * @param [in] value1 The first property value instance to compare
 * @param [in] value2 The second property value instance to compare
 * @param [in] difference The allowed difference between doubles to still maintain equality. The meaning of this parameter is controlled by is_epsilon_difference
 * @param [in] is_epsilon_difference If true, difference will be treated as the machine specific epsilon difference and if false as a relative difference
 * @return -1 if value1 < value2, 0 if value1 == value2, 1 if value1 > value2
 */
TRACKTABLE_CORE_EXPORT int compare(const PropertyValue& value1, const PropertyValue& value2, double difference=1.0, bool is_epsilon_difference=true);

/*! @brief Check to see whether a property value is null.
 *
 * @return True/false depending on whether or not the supplied value is null
 */

TRACKTABLE_CORE_EXPORT bool is_property_null(PropertyValue const& value);


/*! @brief Get a property's underlying type.
 *
 * Retrieve a numeric constant that specifies the type stored in a
 * property. This function is meant to help with serialization.
 */

TRACKTABLE_CORE_EXPORT PropertyUnderlyingType property_underlying_type(PropertyValue const& value);


/*! @brief Utility method: convert a string to a PropertyUnderlyingType.
 */

template<typename text_type>
PropertyUnderlyingType string_to_property_type(text_type const& input)
{
  int i_property_type = boost::lexical_cast<int>(input);
  return static_cast<PropertyUnderlyingType>(i_property_type);
}


/*! @brief Return a property's data type as a string
 */

TRACKTABLE_CORE_EXPORT tracktable::string_type property_type_as_string(tracktable::PropertyValue const& p);

/*! @brief Utility method: convert a source type (usually a string) to a PropertyValue.
 *
 */

template<typename source_type>
PropertyValue to_property_variant(source_type const& source, PropertyUnderlyingType thing_type)
{
  try
    {
    switch (thing_type)
      {
      case TYPE_STRING:
        return PropertyValue(boost::lexical_cast<string_type>(source));
      case TYPE_REAL:
        return PropertyValue(boost::lexical_cast<double>(source));
      case TYPE_TIMESTAMP:
        return PropertyValue(time_from_string(boost::lexical_cast<string_type>(source)));
      case TYPE_NULL:
      case TYPE_UNKNOWN:
        return PropertyValue();
      }
    }
  catch (boost::bad_lexical_cast&)
    {
    return make_null(thing_type);
    }
}

} // namespace tracktable

namespace tracktable { namespace algorithms {

TRACKTABLE_CORE_EXPORT PropertyValue interpolate_property(PropertyValue const& left,
                                                           PropertyValue const& right,
                                                           double t);
TRACKTABLE_CORE_EXPORT PropertyValue extrapolate_property(PropertyValue const& left,
                                                           PropertyValue const& right,
                                                           double t);
} } // namespace tracktable::algorithms


namespace boost { namespace serialization {

template<typename Archive>
void save(Archive& ar, tracktable::PropertyUnderlyingType const& value, const unsigned int /*version*/)
{
  ar & static_cast<int>(value);
}

template<typename Archive>
void load(Archive& ar, tracktable::PropertyUnderlyingType& value, const unsigned int /*version*/)
{
  int value_as_int;
  ar & value_as_int;

  switch (value_as_int)
    {
    case 0: {
    value = tracktable::TYPE_UNKNOWN;
    }; break;
    case 1: {
    value = tracktable::TYPE_REAL;
    }; break;
    case 2: {
    value = tracktable::TYPE_STRING;
    }; break;
    case 3: {
    value = tracktable::TYPE_TIMESTAMP;
    }; break;
    case 5: {
    value = tracktable::TYPE_NULL;
    }; break;
    }
}

} } // namespace boost::serialization

BOOST_SERIALIZATION_SPLIT_FREE(tracktable::PropertyUnderlyingType)

#endif
