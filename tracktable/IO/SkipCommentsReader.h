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

#ifndef __TRACKTABLE_SKIP_COMMENTS_READER_H
#define __TRACKTABLE_SKIP_COMMENTS_READER_H

#include <tracktable/Core/TracktableCommon.h>

#include <iterator>
#include <istream>
#include <string>
#include <cassert>

namespace tracktable {

/**
 * @class SkipCommentsReader
 * @brief Loop over a set of lines and skip comments.
 *
 * Comments in a text file are often denoted by some special character
 * like '#' as the first non-whitespace character on a line. This
 * filter takes a stream of lines and produces a stream that omits all
 * comment lines.
 *
 * Note that we only intercept lines where the comment character is at
 * the beginning of the line. This filter will not detect lines where
 * you attempt to remove data at the end by putting the comment
 * character somewhere in the middle.
 *
 * We do not expect that you will instantiate this class directly.
 * Its main purpose is to be part of the stack that makes up
 * PointReader.
 *
 * @note
 *    Although the CommentCharacter member is a string and can have
 *    arbitrary length, we only care about the first character.
 */

template<typename IteratorT>
class SkipCommentsReader
{
public:
  typedef IteratorT                             inner_iterator_type;
  typedef typename IteratorT::value_type        value_type;
  typedef typename value_type::value_type       char_type;

  /// Instantiate a default SkipCommentsReader
  SkipCommentsReader() 
    : CommentCharacter("#"), 
      NumLinesToSkip(0)
    {
    }

  /** Copy contructor, create a reader with a copy of another
   *
   * @param [in] other SkipCommentsReader to copy from
   */
  SkipCommentsReader(const SkipCommentsReader& other)
    : InnerBegin(other.InnerBegin),
      InnerEnd(other.InnerEnd),
      CommentCharacter(other.CommentCharacter),
      NumLinesToSkip(other.NumLinesToSkip)
    {
    }

  /** Instantiate a reader with a start and finish points along with a comment delimter
   *
   * @param [in] start Iterator to start from
   * @param [in] finish Iterator to end at
   * @param [in] comment Character signifying a comment
   */
  SkipCommentsReader(inner_iterator_type const& start, inner_iterator_type const& finish, std::string const& comment="#")
    : InnerBegin(start),
      InnerEnd(finish),
      CommentCharacter(comment),
      NumLinesToSkip(0)
    {
    }

  /** Instantiate a reader with a start and finish points along with number of header lines to skip
  *
  * @param [in] start Iterator to start from
  * @param [in] finish Iterator to end at
  * @param [in] skip Number of header lines to skip
  */
  SkipCommentsReader(inner_iterator_type const& start, inner_iterator_type const& finish, int const& skip)
      : InnerBegin(start),
      InnerEnd(finish),
      CommentCharacter("#"),
      NumLinesToSkip(skip)
  {
  }

  /// Destructor
  virtual ~SkipCommentsReader()
    {
    }

  /** Specify comment character for skipping lines
   *
   * A line is a comment if and only if its first non-whitespace
   * character is the comment character (`#` by default). We will
   * skip such lines entirely. We do not handle inline or trailing
   * comments: a line will either be included in its entirety or
   * skipped completely.
   *
   * @param [in] comment Single character
   */
  void set_comment_character(std::string const& c)
  {
    this->CommentCharacter = c;
  }

  /** Retrieve current value of comment character.
   *
   * This function invalidates any outstanding iterators.
   *
   * @return Current value of comment character
   */
  std::string const& comment_character() const
  {
    return this->CommentCharacter;
  }

  /** Specify number of header lines to skip
  *
  * In the case where headers are not delimited with a comment
  * character we allow the user to specify how many lines are 
  * skipped at the beginning of a file.
  *
  * @param [in] skips Number of lines to skip
  */
  void set_skip_n_lines(int const& skips)
  {
    this->NumLinesToSkip = skips;
  }

  /** Retrieve number of header lines to skip.
  *
  * This function invalidates any outstanding iterators.
  *
  * @return Current value of number of lines to skip
  */
  int const& num_skips() const
  {
    return this->NumLinesToSkip;
  }

  /** Assign a SkipCommentsReader to the value of another.
   *
   * @param [in] other SkipCommentsReader to assign value of
   * @return Reader with the new assigned value
   */
  SkipCommentsReader& operator=(SkipCommentsReader const& other)
    {
      this->InnerBegin = other.InnerBegin;
      this->InnerEnd = other.InnerEnd;
      this->CommentCharacter = other.CommentCharacter;
      this->NumLinesToSkip = other.NumLinesToSkip;
      return *this;
    }

  /** Check whether one reader is equal to another by comparing all the properties.
   *
   * Two readers are equal if all of their properties are equal.
   *
   * @param [in] other SkipCommentsReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(SkipCommentsReader const& other) const
    {
      return (this->InnerBegin == other.InnerBegin &&
              this->InnerEnd == other.InnerEnd &&
              this->CommentCharacter == other.CommentCharacter &&
              this->NumLinesToSkip == other.NumLinesToSkip);
    }

  /** Check whether two SkipCommentsReader are unequal.
   *
   * @param [in] other SkipCommentsReader for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(SkipCommentsReader const& other) const
    {
      return !(*this == other);
    }

  /** Set the beginning and the end of the input range
   *
   * @param [in] start The iterator to use for the start of input
   * @param [in] finish The iterator to use for the end of input
   */
  void set_input_range(inner_iterator_type const& start,
                       inner_iterator_type const& finish)
  {
    this->InnerBegin = start;
    this->InnerEnd = finish;
  }

private:
  inner_iterator_type InnerBegin;
  inner_iterator_type InnerEnd;
  std::string         CommentCharacter;
  int                 NumLinesToSkip;

protected:
  /*
   * @class SkipCommentsIterator
   * @brief This does the actual work of filtering lines.
   */
  class SkipCommentsIterator : public std::iterator< std::input_iterator_tag,
                                                     typename inner_iterator_type::value_type,
                                                     std::ptrdiff_t,
                                                     const typename inner_iterator_type::value_type*,
                                                     typename inner_iterator_type::value_type const&>
  {
  public:
    typedef typename inner_iterator_type::value_type             value_type;
    typedef typename inner_iterator_type::value_type::value_type char_type;

    /// Instantiate an default SkipCommentsIterator
    SkipCommentsIterator()
      : CommentCharacter("#"),
        NumLinesToSkip(0)
      {}

  /** Instantiate a reader with a start and finish points along with a comment delimter
   *
   * @param [in] Begin Iterator to start from
   * @param [in] End Iterator to end at
   * @param [in] Comment Character signifying a comment
   * @param [in] Number of header lines to skip
   */
    SkipCommentsIterator(inner_iterator_type Begin, inner_iterator_type End, std::string const& Comment, int const& Skips)
      : InnerIterator(Begin),
        InnerEnd(End),
        CommentCharacter(Comment),
        NumLinesToSkip(Skips)
      {
        // Position the iterator on the first string to be returned.
        std::advance(this->InnerIterator, this->NumLinesToSkip);
        this->_advance_to_valid_string();
      }

  /** Copy contructor, create a reader with a copy of another
   *
   * @param [in] other SkipCommentsIterator to copy from
   */
    SkipCommentsIterator(SkipCommentsIterator const& other)
      : InnerIterator(other.InnerIterator),
        InnerEnd(other.InnerEnd),
        CommentCharacter(other.CommentCharacter),
        NumLinesToSkip(other.NumLinesToSkip)
      {}

    /// Destructor
    ~SkipCommentsIterator()
      { }

    /** Assign a SkipCommentsIterator to the value of another.
     *
     * @param [in] other SkipCommentsReader to assign value of
     * @return Reader with the new assigned value
     */
    SkipCommentsIterator& operator=(SkipCommentsIterator const& other)
      {
        this->InnerIterator = other.InnerIterator;
        this->InnerEnd = other.InnerEnd;
        this->CommentCharacter = other.CommentCharacter;
        this->NumLinesToSkip = other.NumLinesToSkip;
        return *this;
      }

    /** Multiply an iterator.
     *
     * @return Result of the multiplication
     */
    value_type const& operator*() const
      {
        return *(this->InnerIterator);
      }

    /** Get the current iterator object.
     *
     * @return Current iterator
     */
    value_type const* operator->() const
      {
        return this->InnerBegin.operator->();
      }

    /** Advance the iterator to the next position in the sequence.
     *
     * @return Pointer to the next iterator in the sequence
     */
    SkipCommentsIterator& operator++()
      {
        assert(this->InnerIterator != this->InnerEnd);
       
        ++ (this->InnerIterator);

        this->_advance_to_valid_string();
        return *this;
      }

    /** Advance the iterator to the next position in the sequence.
     *
     * @return Pointer to the next iterator in the sequence
     */
    SkipCommentsIterator& operator++(int)
      {
        SkipCommentsIterator prev(*this);
        
        this->operator++();
        return prev;
      }

    /** Check whether one SkipCommentsReader is equal to another by comparing all the properties.
     *
     * Two SkipCommentsReaders are equal if all of their properties are equal.
     *
     * @param [in] other SkipCommentsReader for comparison
     * @return Boolean indicating equivalency
     */
    bool operator==(SkipCommentsIterator const& other) const
      {
        return (this->InnerIterator == other.InnerIterator &&
                this->InnerEnd == other.InnerEnd &&
                this->CommentCharacter == other.CommentCharacter);
      }

    /** Check whether two iterators are unequal.
     *
     * @param [in] other Iterator for comparison
     * @return Boolean indicating equivalency
     */
    bool operator!=(SkipCommentsIterator const& other) const
      {
        return ( !(*this == other) );
      }

  private:
    inner_iterator_type InnerIterator;
    inner_iterator_type InnerEnd;
    std::string         CommentCharacter;
    int                 NumLinesToSkip;

    /** @internal
    */
    void _advance_to_valid_string()
      {
        value_type next_string = this->operator*();
        while (this->_string_is_comment(next_string) &&
               this->InnerIterator != this->InnerEnd)
          {
          
          ++(this->InnerIterator);
          next_string = this->operator*();
          }
      }

    /** @internal
    */
    bool _string_is_comment(value_type const& test_string) const
      {
        for (typename value_type::const_iterator iter = test_string.begin();
             iter != test_string.end();
             ++iter)
          {
          if (! iswblank(*iter))
            {
            if (*iter != this->CommentCharacter[0])
              {
              // The first non-whitespace character is not a comment
              // character.
              return false;
              }
            else
              {
              // The first non-whitespace character in the string is
              // our comment character.
              return true;
              }
            }
          }
        // If we get to this point then the string is entirely blank,
        // which is not a comment string. The caller can decide what to
        // do with it.
        return false;
      }
  };

public:
  typedef SkipCommentsIterator iterator;
  typedef SkipCommentsIterator const const_iterator;

  /** Get an iterator pointing to the current sequence
   *
   * @return Iterator pointing to current sequence
   */
  iterator begin() const
    {
      return SkipCommentsIterator(this->InnerBegin, this->InnerEnd, this->CommentCharacter, this->NumLinesToSkip);
    }

  /** Get an iterator pointing past the end of the sequence
   *
   * @return Iterator pointing to end of sequence
   */
  iterator end() const
    {
      return SkipCommentsIterator(this->InnerEnd, this->InnerEnd, this->CommentCharacter, 0);
    }

  /** Get an iterator pointing to the beginning of the stream
   *
   * @return Iterator pointing to current stream
   */
  const_iterator const_begin() const
    {
      return this->begin();
    }

  /** Get an iterator pointing to the end of the stream
   *
   * @return Iterator pointing to end of current stream
   */
  const_iterator const_end() const
    {
      return this->end();
    }
};

/** Create the SkipCommentsReader for a given range
 *
 * @param [in] start_iter Iterator to start from
 * @param [in] end_iter Iteratror to end at
 */
template<typename iter_type>
SkipCommentsReader<iter_type>
  make_skip_comments_reader(iter_type start_iter, iter_type end_iter)
  {
  return SkipCommentsReader<iter_type>(start_iter, end_iter);
  }

} // close namespace tracktable

#endif
