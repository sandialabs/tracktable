/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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
 * This file does not have the usual Sandia copyright because the code
 * is not originally mine.  It came from a post on Stack Overflow:
 *
 *
 * http://stackoverflow.com/questions/24225442/converting-python-io-object-to-stdistream-when-using-boostpython
 *
 * TODO: Contact the author and ask him for explicit permission to use
 * his stuff.
 */


#ifndef __tracktable_PythonWrapping_PythonFileLikeObjectStreams_h
#define __tracktable_PythonWrapping_PythonFileLikeObjectStreams_h

#include <algorithm> // std::copy
#include <iosfwd> // std::streamsize

#include <tracktable/PythonWrapping/GuardedBoostStreamHeaders.h>
#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>


#include <string.h>
#include <iostream>

namespace tracktable {

class PythonReadSource
  : public boost::iostreams::source
{
public:
  typedef char char_type;
  typedef boost::iostreams::source_tag category;

  explicit
  PythonReadSource(boost::python::object& object)
    : object_(object)
    {}

  std::streamsize read(char_type* buffer, std::streamsize buffer_size)
    {
      namespace python = boost::python;
      // Read data through the Python object's API.  The following is
      // is equivalent to:
      //   data = object_.read(buffer_size)
      boost::python::object py_data = object_.attr("read")(buffer_size);
      std::string data = python::extract<std::string>(py_data);
      // If the string is empty, then EOF has been reached.
      if (data.empty())
        {
        return -1; // Indicate end-of-sequence, per Source concept.
        }

      // Otherwise, copy data into the buffer.
      std::copy(data.begin(), data.end(), buffer);
      return data.size();
    }

  boost::python::object object() { return this->object_; }

private:
  boost::python::object object_;
};

// ----------------------------------------------------------------------

class PythonWriteSink
{
public:
  struct category
    : boost::iostreams::sink_tag
    , boost::iostreams::flushable_tag
  {};

  typedef char char_type;

  explicit
  PythonWriteSink(boost::python::object object)
    : Writer(getattr(object, "write", boost::python::object()))
    , Flusher(getattr(object, "flush", boost::python::object()))
  {
    if (this->Writer == boost::python::object())
      {
      std::cerr << "ERROR: PythonWriteSink: Supplied object has no write() attribute.\n";
      }
  }

  PythonWriteSink(PythonWriteSink const& other)
    : Writer(other.Writer)
    , Flusher(other.Flusher)
    { }

  PythonWriteSink& operator=(PythonWriteSink const& other)
    {
      this->Writer = other.Writer;
      this->Flusher = other.Flusher;
      return *this;
    }

  virtual ~PythonWriteSink()
    { }

  // Sink concept
  std::streamsize write(const char_type* buffer, std::streamsize n)
  {
    // Since Python's write() method doesn't return anything, all we
    // can do is dump the data out, claim it was all written and
    // hope for the best.

    boost::python::str data(buffer, n);

    boost::python::object write_result(this->Writer(data));
    boost::python::extract<std::streamsize> bytes_written(write_result);

    return (bytes_written.check() ? bytes_written() : n);
  }

  // Flushable concept
  bool flush()
    {
      if (this->Flusher != boost::python::object())
        {
        if (!this->Flusher.is_none())
          {
          this->Flusher();
          }
        }
      return true;
    }

private:
  boost::python::object Writer;
  boost::python::object Flusher;

};

} // close namespace tracktable

#endif
