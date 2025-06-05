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
 * This code was inspired by a post on Stack Overflow:
 *
 * http://stackoverflow.com/questions/24225442/converting-python-io-object-to-stdistream-when-using-boostpython
 */


#ifndef __tracktable_PythonWrapping_PythonFileLikeObjectStreams_h
#define __tracktable_PythonWrapping_PythonFileLikeObjectStreams_h

#include <algorithm> // std::copy
#include <iosfwd> // std::streamsize

#include <tracktable/PythonWrapping/GuardedBoostStreamHeaders.h>
#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>


#include <string.h>
#include <iostream>
#include <sstream> // std::stringbuf
#include <string>

namespace tracktable {

class PythonReadSource
  : public boost::iostreams::source
{
public:
  typedef char char_type;
  typedef boost::iostreams::source_tag category;

  explicit
  PythonReadSource(boost::python::object& object_source)
    : object_(object_source),
      python_stream_closed_(false),
      buffer_(0)
    {}

  ~PythonReadSource()
  {
    if (this->buffer_)
    {
      delete this->buffer_;
    }
  }
  //
  // NOTE: PYTHON SUBTLETY BELOW
  //
  // The length argument to Python's read() method has different units 
  // depending on whether we're reading from a stream opened in text
  // or in binary mode.  In binary mode, the units are bytes.  In 
  // text mode, the units are Unicode code points.  Depending on the 
  // particular encoding, a single code point can take anywhere from
  // 1 to 4 8-bit bytes.
  // 
  // The implication here is that we cannot trust that the string we 
  // get back from read() is short enough to fit in the buffer.  Instead,
  // we have to buffer the data internally and pull from our buffered
  // source, which we know is in bytes.

  std::streamsize read(char_type* buffer, std::streamsize buffer_size)
    {
      if (!this->buffer_)
      {
        this->buffer_ = new std::stringbuf;
      }

      if (this->python_stream_closed_ && this->bytes_available() == 0)
      {
        // Indicate stream closed per Source concept
        return -1;
      }

      if (this->bytes_available() < buffer_size && !this->python_stream_closed_)
      {
        this->fill_internal_buffer(buffer_size);
      }

    std::streamsize actual_read_size = this->buffer_->sgetn(buffer, buffer_size);
    return actual_read_size;
    }

  // One would think this method could be const.  The standard library 
  // definition for streambuf says that in_avail() can modify the 
  // buffer object, so that won't fly.
  std::streamsize bytes_available()
  {
    return this->buffer_->in_avail();
  }

  // Read from the Python stream to fill our internal buffer.  This
  // function is also responsible for detecting when the Python 
  // file-like object has no more bytes to offer.
  //
  // Arguments:
  //     `buffer_size`: Minimum number of bytes needed in internal
  //         buffer
  
  void fill_internal_buffer(std::streamsize desired_buffer_size)
  {
    while (this->bytes_available() < desired_buffer_size 
           && !this->python_stream_closed_)
    {
      boost::python::object py_data = this->object_.attr("read")(desired_buffer_size);
      std::string data = boost::python::extract<std::string>(py_data);
      // If the string is empty, then EOF has been reached.
      if (data.empty())
        {
          this->python_stream_closed_ = true;
        }
      else
        {
          this->buffer_->sputn(data.c_str(), data.size());
        }
    }
  }

  boost::python::object object() { return this->object_; }

private:
  boost::python::object object_;
  std::stringbuf *buffer_;
  bool python_stream_closed_;

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
    : Destination(object)
    , Flusher(getattr(object, "flush", boost::python::object()))
    , Writer(getattr(object, "write", boost::python::object()))
  {
    if (this->Writer == boost::python::object())
      {
      TRACKTABLE_LOG(log::error) << "ERROR: PythonWriteSink: Supplied object "
                                 << "has no write() attribute.";
      }
  }

  PythonWriteSink(PythonWriteSink const& other)
    : Destination(other.Destination)
      , Flusher(other.Flusher)
      , Writer(other.Writer)
    { }

  PythonWriteSink& operator=(PythonWriteSink const& other)
    {
      this->Destination = other.Destination;
      this->Flusher = other.Flusher;
      this->Writer = other.Writer;
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

#if PY_MAJOR_VERSION == 2
    boost::python::str data(buffer, n);

    boost::python::object write_result(this->Writer(data));
    boost::python::extract<std::streamsize> bytes_written(write_result);
#else
    boost::python::object data(boost::python::handle<>(PyBytes_FromStringAndSize(buffer, n)));
    boost::python::object write_result(this->Writer(data));
    boost::python::extract<std::streamsize> bytes_written(write_result);
#endif

    return (bytes_written.check() ? bytes_written() : n);
  }

  // Flushable concept.  Refuse to flush if the stream is already closed.
  bool flush()
    {
      if (this->stream_is_closed())
      {
        return true;
      }

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
  boost::python::object Destination;
  boost::python::object Flusher;
  boost::python::object Writer;

  // Check 'stream.closed is True'
  //
  // Every Python object derived from io.IOBase has an attribute 'closed'.
  // This function checks its value while being appropriately careful
  // about whether the attribute exists.
  //
  // If for any reason we cannot determine the value of the attribute,
  // we return false -- that is, as far as we can tell the stream is
  // still open.
  bool stream_is_closed()
  {
    using boost::python::object;
    using boost::python::extract;

    if (this->Destination != object())
    {
      object closed_attr(getattr(this->Destination, "closed", object()));
      if (closed_attr != object())
      {
        extract<bool> get_closed(closed_attr);
        if (get_closed.check())
        {
          return get_closed();
        }
        else
        {
          TRACKTABLE_LOG(log::debug) << "Couldn't convert 'stream.closed' to boolean.";
        }
      }
      else
      {
        TRACKTABLE_LOG(log::debug) << "Couldn't get 'closed' attribute from stream.";
      }
    }
    else
    {
      TRACKTABLE_LOG(log::debug) << "Destination object in write sink is not set.";
    }
    return false;
  }
};

} // close namespace tracktable

#endif
