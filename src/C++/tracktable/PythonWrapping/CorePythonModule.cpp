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
// CorePythonModule - Expose core types (PropertyMap and Timestamp) to
// Python

#include <tracktable/Core/MemoryUse.h>

#include <tracktable/PythonWrapping/CommonMapWrappers.h>
#include <tracktable/PythonWrapping/DateTimeWrapper.h>
#include <tracktable/PythonWrapping/FloatVectorWrapper.h>
#include <tracktable/PythonWrapping/PairToTupleWrapper.h>
#include <tracktable/PythonWrapping/PropertyMapWrapper.h>
#include <tracktable/PythonWrapping/TrivialFileReader.h>

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/module.hpp>
#include <Python.h>

void trigger_args_exception(int /*foo*/)
{
  return;
}

BOOST_PYTHON_MODULE(_core_types) {
  install_common_map_wrappers();
  install_float_vector_wrappers();
  install_property_map_wrapper();
  install_datetime_converters();
  install_pair_wrappers();
  install_timestamp_functions();

  using namespace boost::python;
  class_<tracktable::TrivialFileReader>("TrivialFileReader")
    .def(init<>())
    .def("read_from_file", &tracktable::TrivialFileReader::read_from_file)
    ;

  // This function is there so that we can deliberately provoke a
  // Boost.Python.ArgumentError exception.  This lets us get a pointer
  // to it.  I don't know any other way to do that except to make one
  // happen.
  def("trigger_args_exception", trigger_args_exception);

  def("current_memory_use", tracktable::current_memory_use);
  def("peak_memory_use", tracktable::peak_memory_use);

}

