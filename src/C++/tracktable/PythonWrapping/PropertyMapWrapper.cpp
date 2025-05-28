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


// Tracktable Trajectory Library
//
// Implementation details for Python wrapper for our property map.
//


#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/ShadowedDeclaration.h>
#include <boost/serialization/split_free.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>
#include <tracktable/Core/PropertyValue.h>

#include <boost/variant/apply_visitor.hpp>


#include <map>
#include <iostream>
#include <typeinfo>

#include <tracktable/Core/PropertyMap.h>
#include <tracktable/PythonWrapping/GenericSerializablePickleSuite.h>
#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>
#include <tracktable/PythonWrapping/PropertyMapWrapper.h>

// These have to come after GuardedBoostPythonHeaders because they
// rely on Python.h
#include <datetime.h>
#include <patchlevel.h>

namespace bp = boost::python;

/// Convert a PropertyValueT (boost::variant) to a Python object
struct property_value_to_python_object : public boost::static_visitor<PyObject *>
{
  result_type operator()(tracktable::NullValue const&) const
    {
      Py_RETURN_NONE;
    }

  template< typename T >
  result_type operator()(T const& t) const
    {
      return bp::incref(bp::object(t).ptr());
    }

  static PyObject*
  convert(tracktable::PropertyValueT const& v)
    {
      return boost::apply_visitor(property_value_to_python_object(), v);
    }
};

// ----------------------------------------------------------------------

/// Convert a Python object back to a boost::variant.
struct object_to_property_value
{
  object_to_property_value()
    {
      boost::python::converter::registry::push_back(
        &convertible,
        &construct,
        boost::python::type_id<tracktable::PropertyValueT>());
    }

  static void* convertible(PyObject* obj_ptr)
    {
      if (obj_ptr == Py_None ||
          PyFloat_Check(obj_ptr) ||
          PyBytes_Check(obj_ptr) ||
          PyUnicode_Check(obj_ptr) ||
          PyDateTime_Check(obj_ptr))
        {
          return obj_ptr;
        }
      else
        {
          return 0;
        }
    }

  static void construct(PyObject* obj_ptr,
                        boost::python::converter::rvalue_from_python_stage1_data* data)
    {
      tracktable::PropertyValueT c_value;
      if (obj_ptr == Py_None)
        {
        c_value = tracktable::PropertyValueT();
        }
      else if (PyFloat_Check(obj_ptr))
        {
        c_value = tracktable::PropertyValueT(PyFloat_AsDouble(obj_ptr));
        }
#if PY_MAJOR_VERSION == 2
      else if (PyString_Check(obj_ptr))
        {
        c_value = tracktable::PropertyValueT(std::string(PyString_AsString(obj_ptr)));
        }
#else
      else if (PyBytes_Check(obj_ptr))
        {
        c_value = tracktable::PropertyValueT(PyBytes_AS_STRING(obj_ptr));
        }
      else if (PyUnicode_Check(obj_ptr))
        {
        PyObject* encoded_bytes = PyUnicode_AsEncodedString(obj_ptr, "utf-8", "replace");
        if (encoded_bytes != 0)
          {
          c_value = tracktable::PropertyValueT(PyBytes_AS_STRING(encoded_bytes));
          Py_DECREF(encoded_bytes);
          }
        else
          {
          // Couldn't encode string as UTF-8 -- fall back to ASCII
          encoded_bytes = PyUnicode_AsEncodedString(obj_ptr, "ASCII", "replace");
          if (encoded_bytes != 0)
            {
            c_value = tracktable::PropertyValueT(PyBytes_AS_STRING(encoded_bytes));
            Py_DECREF(encoded_bytes);
            }
          else
            {
            TRACKTABLE_LOG(tracktable::log::error) << "Couldn't encode Python string as UTF-8 or ASCII\n";
            c_value = tracktable::PropertyValueT();
            }
          }
        }
#endif
      else if (PyDateTime_Check(obj_ptr))
        {
        PyDateTime_DateTime const* pydate = reinterpret_cast<PyDateTime_DateTime*>(obj_ptr);
        boost::gregorian::date _date(PyDateTime_GET_YEAR(pydate),
                                     PyDateTime_GET_MONTH(pydate),
                                     PyDateTime_GET_DAY(pydate));
        boost::posix_time::time_duration _duration(PyDateTime_DATE_GET_HOUR(pydate),
                                                   PyDateTime_DATE_GET_MINUTE(pydate),
                                                   PyDateTime_DATE_GET_SECOND(pydate),
                                                   0);
        _duration += boost::posix_time::microseconds(PyDateTime_DATE_GET_MICROSECOND(pydate));

        boost::posix_time::ptime full_time(_date, _duration);
        c_value = tracktable::PropertyValueT(full_time);
        }

      void* storage = ((boost::python::converter::rvalue_from_python_storage<tracktable::PropertyValueT>*)data)->storage.bytes;
      new (storage) tracktable::PropertyValueT(c_value);
      data->convertible = storage;
    }
};

// ----------------------------------------------------------------------

/// Create a boost::variant with a string value.
tracktable::PropertyValueT make_string_variant(std::string const& value)
{
  return tracktable::PropertyValueT(value);
}

/// Create a boost::variant with a double value.
tracktable::PropertyValueT make_double_variant(double value)
{
  return tracktable::PropertyValueT(value);
}

// ----------------------------------------------------------------------

// Retrieve all the keys from a map.

bp::list keys(tracktable::PropertyMap const& pmap)
{
  bp::list result;

  for (tracktable::PropertyMap::const_iterator iter = pmap.begin();
       iter != pmap.end();
       ++iter)
    {
    result.append((*iter).first);
    }
  return result;
}

//----------------------------------------------------------------------

bp::list values(tracktable::PropertyMap const& pmap)
{
  bp::list result;

  for (tracktable::PropertyMap::const_iterator iter = pmap.begin();
       iter != pmap.end();
       ++iter)
    {
    result.append((*iter).second);
    }
  return result;
}

// ----------------------------------------------------------------------

bp::list items(tracktable::PropertyMap const& pmap)
{
  bp::list result;
  for (tracktable::PropertyMap::const_iterator iter = pmap.begin();
       iter != pmap.end();
       ++iter)
    {
    result.append( bp::make_tuple(iter->first, iter->second) );
    }
  return result;
}

// ----------------------------------------------------------------------

/// Register our converters for property maps and values.
void install_property_map_wrapper()
{
  bp::to_python_converter< tracktable::PropertyValueT,
                       property_value_to_python_object >();

  bp::implicitly_convertible<int64_t, tracktable::PropertyValueT>();
  bp::implicitly_convertible<double, tracktable::PropertyValueT>();
  bp::implicitly_convertible<std::string, tracktable::PropertyValueT>();
  bp::implicitly_convertible<tracktable::Timestamp, tracktable::PropertyValueT>();

  object_to_property_value();

  bp::class_< tracktable::PropertyMap >("PropertyMap")
    .def(boost::python::map_indexing_suite< tracktable::PropertyMap, true > ())
//    .def_pickle(tracktable::traits::property_map_pickle_suite())
    .def_pickle(tracktable::python_wrapping::GenericSerializablePickleSuite<tracktable::PropertyMap>())
    .def("keys", keys)
    .def("values", values)
    .def("items", items)
    ;
}
