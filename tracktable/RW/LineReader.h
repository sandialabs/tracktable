/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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
 * This class is an adapter that takes a `std::istream` as input and
 * provides an InputIterator that loops over the lines of the stream.
 * In its current version it delegates to the `getline()` function to
 * determine when a line has ended.
 *
 * The behavior is meant to be the same as the Python idiom `for line
 * in file`.
 *
 * We do not expect you to instantiate this class directly. Instead,
 * it shows up as part of `PointReader` where you put a stream in one
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

  /// Instantiate an empty line reader
  LineReader()
    : Stream(0)
    {
    }

  /** Copy contructor, create a reader with a copy of another
   *
   * @param [in] other Line reader to copy from
   */
  LineReader(const LineReader& other)
    : Stream(other.Stream)
    {
    }

  /** Instantiate a line reader with `std::basic_istream`
   *
   * @param [in] stream Stream to read lines in
   */
  LineReader(istream_type& stream)
    : Stream(&stream)
    {
    }

  /// Destructor for a line reader
  virtual ~LineReader()
    {
    }

  /** Assign a LineReader to the value of another.
   *
   * @param [in] other LineReader to assign value of
   * @return Stream with the new assigned value
   */
  LineReader& operator=(LineReader const& other)
    {
      this->Stream = other.Stream;
      return *this;
    }

  /** Set the input for the LineReader stream to that of the given istream
   *
   * @param [in] stream The input to use for input
   */
  void set_input(istream_type& stream)
    {
      this->Stream = &stream;
    }

  /** Get the input value of the stream
   *
   * @return The stream input value
   */
  istream_type& input() const
  {
    return *(this->Stream);
  }

  /** Check whether one stream is equal to another by comparing all the items.
   *
   * Two reader are equal if all of their streams are equal.
   *
   * @param [in] other LineReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(LineReader const& other) const
  {
    return (this->Stream == other.Stream);
  }

  /** Check whether two LineReaders are unequal.
   *
   * @param [in] other LineReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(LineReader const& other) const
  {
    return !(*this == other);
  }

private:
  istream_type* Stream;

protected:
  /** Line Reader iterator class
   *
   * Generates a iterator that can traverse the given parent
   * LineReader
   */
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

    /// Instantiate an empty reader iterator
    LineReaderIterator()
      : Stream(0),
        Counter(0)
      { }

    /// Copy contructor, create a line reader iterator with a copy of a `std::basic_istream`
    LineReaderIterator(istream_type* stream)
      : Stream(stream),
        Counter(0),
        Value("")
      {
        // When first constructed, the stream has not been read at
        // all. This corresponds to an iterator state before the
        // beginning of the data. We need to advance once to get to
        // the first record.
        if (stream)
          {
            this->operator++();
          }
      }

    /// Copy contructor, create a line reader iterator with a copy of another
    LineReaderIterator(LineReaderIterator const& other)
      : Stream(other.Stream),
        Counter(other.Counter),
        Value(other.Value)
      {
      }

    /// Destructor for a line reader iterator
    ~LineReaderIterator()
      { }

    /** Assign a LineReaderIterator to the value of another.
     *
     * @param [in] other LineReaderIterator to assign value of
     * @return Iterator with the new assigned value
     */
    LineReaderIterator& operator=(LineReaderIterator const& other)
      {
        this->Stream = other.Stream;
        this->Value = other.Value;
        return *this;
      }

    /** Multiply an iterator.
     *
     * @return Result of the multiplication
     */
    value_type const& operator*() const
      {
        return this->Value;
      }

    /** Get the current iterator value.
     *
     * @return Current iterator value
     */
    value_type* operator->() const
      {
        return &(this->Value);
      }

    /** Advance the iterator to the next line.
     *
     * @return Pointer to the next line
     */
    LineReaderIterator& operator++()
      {
        if (!getline(*this->Stream, this->Value))
          {
            this->Stream = NULL;
          }
        else 
          {
            TRACKTABLE_LOG(tracktable::log::debug) << "Read Line #" << ++(this->Counter);
          }
        return *this;
      }

    /** Advance the iterator to the next line.
     *
     * @return Pointer to the next line
     */
    LineReaderIterator& operator++(int)
      {
        LineReaderIterator prev(*this);
        this->operator++();
        return prev;
      }

    /** Check whether one iterator is equal to another by comparing the values and streams.
     *
     * Two items are equal if all of their values and streams are equal.
     *
     * @param [in] other Iterator for comparison
     * @return Boolean indicating equivalency
     */
    bool operator==(LineReaderIterator const& other) const
      {
        return (this->Stream == other.Stream &&
                this->get_value() == other.get_value());
      }

    /** Check whether two iterators are unequal.
     *
     * @param [in] other Iterator for comparison
     * @return Boolean indicating equivalency
     */
    bool operator!=(LineReaderIterator const& other) const
      {
        return ( !(*this == other) );
      }

    /** Get the stored value
    *
    * This is to handle the case where the stream is NULL
    * but there wasn't a new line at the end of the file.
    * In that case we return an empty value so that 
    * comparisons evaluate properly.
    *
    * @return Value unless the Stream is Null,
    * in which case we return an empty value
    */
    value_type get_value() const 
    {
        if (this->Stream == NULL) return "";
        return this->Value;
    }

  public:
    istream_type* Stream;
    value_type Value;
    int Counter;
  };

public:
  typedef LineReaderIterator iterator;
  typedef LineReaderIterator const const_iterator;

  /** Get an iterator pointing to the beginning of the stream
   *
   * @return Iterator pointing to current stream
   */
  iterator begin() const
    {
      return iterator(this->Stream);
    }

  /** Get an iterator pointing to the end of the stream
   *
   * @return Iterator pointing to end of current stream
   */
  iterator end() const
    {
      return iterator(NULL);
    }

  /** Get an iterator pointing to the beginning of the stream
   *
   * @return Iterator pointing to current stream
   */
  const_iterator const_begin() const
    {
      return iterator(this->Stream);
    }

  /** Get an iterator pointing to the end of the stream
   *
   * @return Iterator pointing to end of current stream
   */
  const_iterator const_end() const
    {
      return iterator(NULL);
    }
};

} // close namespace tracktable

#endif
