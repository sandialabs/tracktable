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

/** Simple wrapper class to adapt Python filestreams.
 *
 * We will be calling PointReader from Python using a Python file-like
 * object as input.  We have an adapter class (PythonStreambuf) that
 * will wrap an object and make it look like a std::istream.  This
 * class lets us wrap PointReader and add our own member to store the
 * stream.
 */

#ifndef __tracktable_PythonAwarePointReader_h
#define __tracktable_PythonAwarePointReader_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/RW/PointReader.h>
#include <tracktable/PythonWrapping/PythonFileLikeObjectStreams.h>
#include <boost/iostreams/stream.hpp>
#include <boost/shared_ptr.hpp>

#include <cassert>
#include <iostream>

namespace tracktable {

template<class base_reader_type>
class PythonAwarePointReader : public base_reader_type
{
private:
  typedef base_reader_type Superclass;
  typedef boost::iostreams::stream<PythonReadSource> WrappedPythonStream;
  typedef boost::shared_ptr<WrappedPythonStream> WrappedStreamSmartPointer;

public:
  typedef typename base_reader_type::iterator iterator;

  PythonAwarePointReader()
    { }

  virtual ~PythonAwarePointReader()
    {
    }


  PythonAwarePointReader(std::istream& infile)
    {
      this->set_input(infile);
    }

  PythonAwarePointReader(boost::python::object file_like_object)
    {
      this->set_input_from_python_object(file_like_object);
    }


  void set_input_from_python_object(boost::python::object& thing)
    {
      this->SourceObject = thing;
      this->WrappedInputStream = WrappedStreamSmartPointer(new WrappedPythonStream(PythonReadSource(thing)));
      this->set_input(*(this->WrappedInputStream));
    }

  boost::python::object input_as_python_object()
    {
      return this->SourceObject;
    }


  tracktable::IntIntMap& __coordinate_assignments() { return this->Superclass::__coordinate_assignments(); }

  void __set_coordinate_assignments(tracktable::IntIntMap const& cmap)
    {
      this->Superclass::__set_coordinate_assignments(cmap);
    }

private:
  boost::python::object SourceObject;

  WrappedStreamSmartPointer WrappedInputStream;


public:
  // These should never be called but Boost insists on being able to
  // instantiate them.
  PythonAwarePointReader(PythonAwarePointReader const& /*other*/)
    {
      assert(1==0);
    }

  PythonAwarePointReader& operator=(PythonAwarePointReader const& /*other*/)
    {
      assert(1==0);
    }

};

} // exit namespace tracktable

#endif
