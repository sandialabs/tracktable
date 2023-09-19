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


#ifndef __tracktable_PythonWrapping_PythonTypedObjectWriter_h
#define __tracktable_PythonWrapping_PythonTypedObjectWriter_h

#include <algorithm> // std::copy
#include <iosfwd> // std::streamsize
#include <typeinfo>
#include <boost/iostreams/concepts.hpp>  // boost::iostreams::sink
#include <boost/iostreams/stream.hpp>


#include "PythonFileLikeObjectStreams.h"

namespace tracktable {


template<class base_writer_type, class ObjectToWriteT>
class PythonTypedObjectWriter : public base_writer_type
{
private:
  typedef ObjectToWriteT written_object_type;
  typedef boost::iostreams::stream<PythonWriteSink> WrappedPythonOutputStream;
  typedef boost::shared_ptr<WrappedPythonOutputStream> WrappedStreamSmartPointer;
  typedef base_writer_type Superclass;

public:
  PythonTypedObjectWriter(boost::python::object obj)
    {
      this->set_output_from_python_object(obj);
    }

  PythonTypedObjectWriter() { };
  virtual ~PythonTypedObjectWriter()
    {
    }

  void set_output_from_python_object(boost::python::object obj)
    {
      this->SinkObject = obj;
      this->WrappedOutputStream =
        WrappedStreamSmartPointer(
          new WrappedPythonOutputStream(PythonWriteSink(this->SinkObject)
            ));
      this->set_output(*this->WrappedOutputStream);
    }

  boost::python::object output_as_python_object()
    {
      return this->SinkObject;
    }

  void write_python_sequence(boost::python::object& things_to_write)
    {
      boost::python::stl_input_iterator<written_object_type> begin(things_to_write), end;
      this->Superclass::write(begin, end);
    }

private:
  boost::python::object SinkObject;
  WrappedStreamSmartPointer WrappedOutputStream;
};

} // close namespace tracktable

#endif
