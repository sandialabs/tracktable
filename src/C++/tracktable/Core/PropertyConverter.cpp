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

#include <tracktable/Core/PropertyConverter.h>
#include <boost/lexical_cast.hpp>
#include <locale>

namespace tracktable {

PropertyConverter::PropertyConverter()
{
  this->set_null_value("");
  this->set_timestamp_input_format("%Y-%m-%d %H:%M:%S");
  this->set_timestamp_output_format("%Y-%m-%d %H:%M:%S");
  this->set_decimal_precision(8);
}

PropertyConverter::~PropertyConverter()
{
}

PropertyConverter::PropertyConverter(PropertyConverter const& other)
  : DecimalPrecision(other.DecimalPrecision),
    NullValue(other.NullValue),
    TimestampReadWrite(other.TimestampReadWrite)
{
  this->InputBuf.imbue(other.InputBuf.getloc());
  this->OutputBuf.imbue(other.OutputBuf.getloc());
}

PropertyConverter& PropertyConverter::operator=(PropertyConverter const& other)
{
  this->DecimalPrecision = other.DecimalPrecision;
  this->NullValue = other.NullValue;
  this->TimestampReadWrite = other.TimestampReadWrite;
  this->InputBuf.imbue(other.InputBuf.getloc());
  this->OutputBuf.imbue(other.OutputBuf.getloc());

  return *this;
}

bool PropertyConverter::operator==(PropertyConverter const& other) const
{
  return (
	  this->DecimalPrecision == other.DecimalPrecision
          && this->NullValue == other.NullValue
	  && this->TimestampReadWrite == other.TimestampReadWrite
	  );
}

bool PropertyConverter::operator!=(PropertyConverter const& other) const
{
  return !(*this == other);
}

string_type PropertyConverter::property_to_string(PropertyValueT const& prop)
{
  switch (property_underlying_type(prop))
    {
    case TYPE_TIMESTAMP:
      return this->TimestampReadWrite.timestamp_to_string(boost::get<Timestamp>(prop));
    case TYPE_REAL:
      {
	this->OutputBuf.str(string_type());
	this->OutputBuf << boost::get<double>(prop);
	return this->OutputBuf.str();
      };
#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
    case TYPE_INTEGER:
      {
	this->OutputBuf.str(string_type());
	this->OutputBuf << boost::get<int64_t>(prop);
	return this->OutputBuf.str();
      };
#endif
    case TYPE_STRING:
      return boost::get<string_type>(prop);
    case TYPE_NULL:
      return this->NullValue;
    case TYPE_UNKNOWN:
      TRACKTABLE_LOG(log::error) << "ERROR: PropertyConverter::property_to_string: "
                                 << "Don't know what to make of property " << prop;
      return this->NullValue;
    }
  return this->NullValue;
}

PropertyValueT PropertyConverter::property_from_string(
               string_type const& prop_value,
               PropertyUnderlyingType desired_type)
  {
    // TRACKTABLE_LOG(debug) << "property_from_string: raw_value is '" << prop_value << "', type is " << desired_type << "\n";
    PropertyValueT result;

    if (prop_value == this->NullValue)
      {
      return make_null(desired_type);
      }

    switch (desired_type)
      {
      case TYPE_STRING:
	      {
	      result = PropertyValueT(prop_value);
	      }; break;
      case TYPE_REAL:
	      {
	      // Why doesn't the following code work?
	      // this->InputBuf.str(prop_value);
	      // double actual_value = 0;
	      // this->InputBuf >> actual_value;
	      double actual_value = boost::lexical_cast<double>(prop_value);
	      result = PropertyValueT(actual_value);
	      }; break;
#if defined(PROPERTY_VALUE_INCLUDES_INTEGER)
      case TYPE_INTEGER:
	      {
	      int64_t actual_value = boost::lexical_cast<int64_t>(prop_value);
	      result = PropertyValueT(actual_value);
	      }; break;
#endif
      case TYPE_TIMESTAMP:
	      {
	      result = PropertyValueT(this->TimestampReadWrite.timestamp_from_string(prop_value));
	      }; break;
      case TYPE_UNKNOWN:
      case TYPE_NULL:
        {
        TRACKTABLE_LOG(log::error)
	         << "ERROR: property_from_string: Don't know what to do with value '"
	         << prop_value << " and desired type " << desired_type << ".";
	      return PropertyValueT();
        }
      }
    return result;
  }

  // ----------------------------------------------------------------------

  void PropertyConverter::set_decimal_precision(std::size_t num_digits)
  {
    this->DecimalPrecision = num_digits;
    this->OutputBuf.precision(static_cast<std::streamsize>(num_digits));
  }

  // ----------------------------------------------------------------------

  std::size_t PropertyConverter::decimal_precision() const
  {
    return this->DecimalPrecision;
  }

  // ----------------------------------------------------------------------

  void PropertyConverter::set_timestamp_input_format(string_type const& format)
  {
    this->TimestampReadWrite.set_input_format(format);
  }

  // ----------------------------------------------------------------------

  void PropertyConverter::set_timestamp_output_format(string_type const& format)
  {
    this->TimestampReadWrite.set_output_format(format);
  }

  //----------------------------------------------------------------------

  string_type PropertyConverter::timestamp_input_format() const
  {
    return this->TimestampReadWrite.input_format();
  }

  // ----------------------------------------------------------------------

  string_type PropertyConverter::timestamp_output_format() const
  {
    return this->TimestampReadWrite.output_format();
  }

  // ----------------------------------------------------------------------

  TimestampConverter* PropertyConverter::timestamp_converter()
  {
    return & (this->TimestampReadWrite);
  }

  // ----------------------------------------------------------------------

void PropertyConverter::set_null_value(string_type const& value)
{
  this->NullValue = value;
}

// ----------------------------------------------------------------------

string_type PropertyConverter::null_value() const
{
  return this->NullValue;
}

}
