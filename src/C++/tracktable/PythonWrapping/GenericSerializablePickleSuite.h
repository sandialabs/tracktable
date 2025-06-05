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

/***
 *** GenericSerializablePickleSuite: Delegate Python pickling to
 *** boost::serialization
 ***
 *** Both Python's pickle module and Boost's serialization library aim
 *** to do the same thing: save and restore an object to a byte
 *** stream.  Rather than implement serialization twice for each
 *** object type, we will use this class to delegate Python pickle
 *** support to the underlying Boost serialization support.
 ***
 ***/


#define BP_STRING_TYPE boost::python::str

#ifndef __tracktable_GenericSerializablePickleSuite_h
#define __tracktable_GenericSerializablePickleSuite_h

#include <boost/python.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>

#include <sstream>

namespace tracktable { namespace python_wrapping {

template<class native_object_t>
class GenericSerializablePickleSuite : public boost::python::pickle_suite
{
public:

  static boost::python::tuple getstate(boost::python::object object_to_pickle)
  {
    std::ostringstream outbuf;
    boost::archive::binary_oarchive archive(outbuf);
    native_object_t const& native_object = boost::python::extract<native_object_t const&>(object_to_pickle);

    archive << native_object;
    // Because Boost.Python doesn't provide a way to create a Python
    // bytes object we have to drop through to the C API.
    boost::python::object archive_bytes(
      boost::python::handle<>(
        PyBytes_FromStringAndSize(outbuf.str().c_str(), outbuf.str().size())
      )
    );

    return boost::python::make_tuple(archive_bytes,
                                     object_to_pickle.attr("__dict__"));
  }

  static void setstate(boost::python::object& object_to_restore, boost::python::tuple state)
  {
    using boost::python::dict;
    using boost::python::extract;

    check_tuple_size(state, 2);
    check_for_bytes(state[0]);
    check_for_dict(state[1]);

    // We have already checked to make sure this is a bytes object.
    // Something might still go wrong extracting the bytes as a C
    // string, though.
    boost::python::object bytes_object = state[0];
    PyObject* bytes = bytes_object.ptr();

    const char* bytes_as_c_string = PyBytes_AsString(bytes);
    check_extracted_string(bytes_as_c_string);

    std::string archive_data(bytes_as_c_string, PyBytes_Size(bytes));
    std::istringstream inbuf(archive_data);
    boost::archive::binary_iarchive archive(inbuf);

    dict object_dict = extract<dict>(object_to_restore.attr("__dict__"));
    object_dict.update(state[1]);

    native_object_t& native_object = extract<native_object_t&>(object_to_restore);
    archive >> native_object;
  }

  static bool getstate_manages_dict() { return true; }

  // ----------------------------------------------------------------------
  // Utility functions below here
  // ----------------------------------------------------------------------

  // Does this tuple conform to our expectations?
  static void check_tuple_size(boost::python::object tuple,
                               int expected_size)
  {
    using boost::python::len;

    if (len(tuple) != expected_size)
      {
      PyErr_SetObject(PyExc_ValueError,
                      ("Expected %s-item tuple; got %s" %
                       boost::python::make_tuple(len(tuple), expected_size)).ptr());
      boost::python::throw_error_already_set();
      }
  }

  static void check_extracted_string(const char *extracted_string)
  {
    if (!extracted_string)
      {
      PyErr_SetObject(PyExc_ValueError,
                      boost::python::str("String data extracted from bytes object is null").ptr());
      boost::python::throw_error_already_set();
      }
  }

  static void check_for_dict(boost::python::object maybe_dict)
  {
    using boost::python::dict;
    using boost::python::extract;

    extract<dict> dict_check(maybe_dict);
    if (! dict_check.check())
      {
      PyErr_SetObject(PyExc_TypeError,
                      ("Expected dict as first element of state: got %s" % maybe_dict).ptr());
      boost::python::throw_error_already_set();
      }
  }

  static void check_for_bytes(boost::python::object maybe_bytes)
  {
    using boost::python::dict;
    using boost::python::extract;

    PyObject* bytes = maybe_bytes.ptr();
    if (!PyBytes_Check(bytes))
      {
      PyErr_SetObject(PyExc_ValueError,
                      ("Expected bytes() object in call to __setstate__; got %s" %
                       maybe_bytes).ptr());
      boost::python::throw_error_already_set();
      }
  }
};

} } // namespace tracktable::python_wrapping

#endif
