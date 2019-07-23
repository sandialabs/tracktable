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

#ifndef __TRACKTABLE_LINE_READER_H
#define __TRACKTABLE_LINE_READER_H

#include <tracktable/Core/TracktableCommon.h>

#include <iterator>
#include <istream>
#include <string>
#include <cassert>

namespace tracktable {

/** Read data from a stream one line at a time.
 *
 * This class is an adapter that takes a std::istream as input and
 * provides an InputIterator that loops over the lines of the stream.
 * In its current version it delegates to the getline() function to
 * determine when a line has ended.
 *
 * The behavior is meant to be the same as the Python idiom ``for line
 * in file``.
 *
 * We do not expect you to instantiate this class directly.  Instead,
 * it shows up as part of PointReader where you put a stream in one
 * end and get points out the other end.
 */

template<class StringT = std::string>
class LineReader
{
public:
  typedef StringT                                    value_type;
  typedef typename StringT::value_type               char_type;
  typedef typename StringT::traits_type              traits_type;
  typedef std::basic_istream<char_type, traits_type> istream_type;

  LineReader()
    : Stream(0)
    {
    }

  LineReader(const LineReader& other)
    : Stream(other.Stream)
    {
    }

  LineReader(istream_type& stream)
    : Stream(&stream)
    {
    }

  virtual ~LineReader()
    {
    }

  LineReader& operator=(LineReader const& other)
    {
      this->Stream = other.Stream;
      return *this;
    }

  void set_input(istream_type& stream)
    {
      this->Stream = &stream;
    }

  istream_type& input() const
  {
    return *(this->Stream);
  }

  bool operator==(LineReader const& other) const
  {
    return (this->Stream == other.Stream);
  }
  
  bool operator!=(LineReader const& other) const
  {
    return !(*this == other);
  }
  
private:
  istream_type* Stream;

protected:
  class LineReaderIterator : public std::iterator< std::input_iterator_tag,
                                                   StringT,
                                                   std::ptrdiff_t,
                                                   const StringT*,
                                                   StringT const&>
  {
  public:
    typedef StringT                        value_type;
    typedef typename StringT::value_type   char_type;
    typedef typename StringT::traits_type  traits_type;

    LineReaderIterator()
      : Stream(0)
      { }

    LineReaderIterator(istream_type* stream)
      : Stream(stream)
      {
        // When first constructed, the stream has not been read at
        // all. This corresponds to an iterator state before the
        // beginning of the data.  We need to advance once to get to
        // the first record.
        if (stream)
          {
          this->operator++();
          }
      }

    LineReaderIterator(LineReaderIterator const& other)
      : Stream(other.Stream),
        Value(other.Value)
      {
      }

    ~LineReaderIterator()
      { }

    LineReaderIterator& operator=(LineReaderIterator const& other)
      {
        this->Stream = other.Stream;
        this->Value = other.Value;
        return *this;
      }

    value_type const& operator*() const
      {
        return this->Value;
      }

    value_type* operator->() const
      {
        return &(this->Value);
      }

    LineReaderIterator& operator++()
      {
      assert(this->Stream != NULL);
      if (!getline(*this->Stream, this->Value))
        {
        this->Stream = NULL;
        }
      return *this;
      }

    LineReaderIterator& operator++(int)
      {
        LineReaderIterator prev(*this);
        this->operator++();
        return prev;
      }

    bool operator==(LineReaderIterator const& other) const
      {
        return (this->Stream == other.Stream &&
                this->Value == other.Value);
      }

    bool operator!=(LineReaderIterator const& other) const
      {
        return ( !(*this == other) );
      }

  public:
    istream_type* Stream;
    value_type Value;
  };

public:
  typedef LineReaderIterator iterator;
  typedef LineReaderIterator const const_iterator;

  iterator begin() const
    {
      return iterator(this->Stream);
    }

  iterator end() const
    {
      return iterator(NULL);
    }

  const_iterator const_begin() const
    {
      return iterator(this->Stream);
    }

  const_iterator const_end() const
    {
      return iterator(NULL);
    }
};

} // close namespace tracktable

#endif
