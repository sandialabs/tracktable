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
// Boost.Python code to wrap std::pair.  Needs to be instantiated
// explicitly for each pair type.
//
// This is from
//
// https://stackoverflow.com/questions/16497889/how-to-expose-stdpair-to-python-using-boostpython


#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/PythonWrapping/PairToTupleWrapper.h>

#include <iostream>
#include <algorithm>

template<typename T1, typename T2>
struct PairToPythonConverter
{
  typedef std::pair<T1, T2> pair_type;

  static PyObject* convert(pair_type const& my_pair)
  {
    return boost::python::incref(
      boost::python::make_tuple(my_pair.first, my_pair.second).ptr()
    );
  }
};

template<typename T1, typename T2>
struct PythonToPairConverter
{
  typedef std::pair<T1, T2> pair_type;

  PythonToPairConverter()
  {
    boost::python::converter::registry::push_back(
      &convertible,
      &construct,
      boost::python::type_id<pair_type>()
    );
  }

  static void* convertible(PyObject* obj)
  {
    if (!PyTuple_CheckExact(obj)) return 0;
    if (PyTuple_Size(obj) != 2) return 0;
    return obj;
  }

  static void construct(
    PyObject* obj,
    boost::python::converter::rvalue_from_python_stage1_data* data)
  {
    namespace bp = boost::python;

    bp::tuple tuple(bp::borrowed(obj));
    void* storage = ((bp::converter::rvalue_from_python_storage<pair_type>*) data)->storage.bytes;
    new (storage) pair_type(bp::extract<T1>(tuple[0]),
                            bp::extract<T2>(tuple[1]));
    data->convertible = storage;
  }
};

template<typename number_type>
number_type double_arg(number_type thing)
{
  return thing * static_cast<number_type>(2);
}

template<typename T1, typename T2>
struct DeclarePythonPair
{
  typedef std::pair<T1, T2> pair_type;

  DeclarePythonPair() {};
  boost::python::to_python_converter<
    pair_type, PairToPythonConverter<T1, T2>
    > to_python;
  PythonToPairConverter<T1, T2> from_python;
};

// ----------------------------------------------------------------------

void install_pair_wrappers()
{
  DeclarePythonPair<int, int>();
}
