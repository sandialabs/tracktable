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

#include <tracktable/Core/PropertyValue.h>

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

#if defined(PROPERTY_VALUE_INCLUDES_INT)
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
#endif

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

template<typename value_type>
struct dispatch_extrapolate
{
    static inline tracktable::PropertyValueT apply(tracktable::PropertyValueT const& first,
        tracktable::PropertyValueT const& second,
        double interpolant)
    {
        value_type const *first_value, *second_value;
        value_type result;
        first_value = boost::get<value_type>(&first);
        second_value = boost::get<value_type>(&second);
        result = tracktable::extrapolate<value_type>(*first_value, *second_value, interpolant);
        return tracktable::PropertyValueT(result);
    }
};

// ----------------------------------------------------------------------

class RetrieveUnderlyingType : public boost::static_visitor<tracktable::PropertyUnderlyingType>
{
public:
  tracktable::PropertyUnderlyingType operator()(double /*value*/) const
    {
      return tracktable::TYPE_REAL;
    }

  tracktable::PropertyUnderlyingType operator()(tracktable::string_type const& /*value*/) const
    {
      return tracktable::TYPE_STRING;
    }

  tracktable::PropertyUnderlyingType operator()(tracktable::Timestamp const& /*ts*/) const
    {
      return tracktable::TYPE_TIMESTAMP;
    }

  tracktable::PropertyUnderlyingType operator()(const tracktable::NullValue& /*value*/) const
    {
      return tracktable::TYPE_NULL;
    }

  template<typename T>
  tracktable::PropertyUnderlyingType operator()(const T& /*value*/) const
    {
      return tracktable::TYPE_UNKNOWN;
    }

};



namespace tracktable {


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
    case tracktable::TYPE_NULL:
      return "null";
    default:
      return "unsupported";
    }
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

PropertyUnderlyingType property_underlying_type(PropertyValueT const& pv)
{
  return boost::apply_visitor(::RetrieveUnderlyingType(), pv);
}

std::ostream& operator<<(std::ostream& out, NullValue const& value)
{
  std::ostringstream outbuf;
  outbuf << "(null ";

  switch (value.ExpectedType)
    {
    case tracktable::TYPE_UNKNOWN:
      outbuf <<  "unknown"; break;
    case tracktable::TYPE_REAL:
      outbuf <<  "real"; break;
    case tracktable::TYPE_STRING:
      outbuf << "string"; break;
    case tracktable::TYPE_TIMESTAMP:
      outbuf <<  "timestamp"; break;
    case tracktable::TYPE_NULL:
      outbuf << "null"; break;
    default:
      outbuf << "unsupported"; break;
    }

  outbuf << ")";
  out << outbuf.str();
  return out;
}

/** Implements a static binary visitor for comparing two property values
 *
 * This class imposes a total ordering on all property comparisons.
 *
 * Logical comparisons are only performed between variants of the same type, although
 * it would be possible to extend this class with comparisons between Timestamps and
 * strings by supplying the appropriate overloaded operator().
 *
 * For each of the logical comparisons an overload of the binary operator() is
 * supplied. For all other forms without a specific overload the template
 * form will be selected that will use enums of the underlying types.
 *
 * Some local storage is necessary to allow for customization of the
 * epsilon closeness or actual distance between two doubles.
 */
class PropertyComparator : public boost::static_visitor<int>
{
public:
    double difference;
    bool is_epsilon_difference;

    PropertyComparator(double difference=1.0, bool is_epsilon_difference=true) {
        this->difference = difference;
        this->is_epsilon_difference = is_epsilon_difference;
    }

    // Compares two doubles using either epsilon or actual differences
    int operator()(double v1, double v2) const {
      if (this->is_epsilon_difference && boost::math::epsilon_difference(v1, v2) <= this->difference)
        return 0;
      if (!this->is_epsilon_difference && boost::math::relative_difference(v1, v2) <= this->difference)
        return 0;
      if (v1 < v2) return -1;
      return 1;
    }

    // Compares two timestamps using the gt and lt operators
    int operator()(const Timestamp& v1, const Timestamp& v2) const {
        if (v1 < v2) return -1;
        if (v1 > v2) return 1;
        return 0;
    }

    // Compares two strings using lexicographical comparison
    int operator()(const std::string& v1, const std::string& v2) const {
        return v1.compare(v2);
    }

    // All null values are equal
    int operator()(const NullValue& /*v1*/, const NullValue& /*v2*/) const {
        return 0;
    }

    // ^^^^^^^ WHEN EXTENDING PropertyValueT WITH NEW TYPES ADD SPECIFIC FORMS ABOVE HERE

    // This template will catch all other forms that do not have explicit forms above.
    // This also means the template will return 1 if new types are added to PropertyValueT and
    // a specific form of operator() is not supplied above.
    template<typename T1, typename T2>
    int operator()(const T1& v1, const T2& v2) const {
      return (property_underlying_type(v1) < property_underlying_type(v2)) ? -1 : 1;
    }

};

TRACKTABLE_CORE_EXPORT int compare(const PropertyValueT& value1, const PropertyValueT& value2, double difference, bool is_epsilon_difference) {
  // To access the underlying values an instance of a static visitor is used
  int result = boost::apply_visitor(PropertyComparator(difference, is_epsilon_difference), value1, value2);
  return result;
}


} // namespace tracktable



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

PropertyValueT extrapolate_property(
    PropertyValueT const& first,
    PropertyValueT const& second,
    double t
)
{
    ::InterpolateProperties calculator;
    calculator.interpolant = t;
    calculator.SecondValue = second;

    return boost::apply_visitor(calculator, first);
}

} } // exit namespace tracktable::algorithms
