/*
 * Copyright (c) 2014, Sandia Corporation.  All rights
 * reserved.
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
 * \class SkipCommentsReader
 * \brief Loop over a set of lines and skip comments.
 *
 * Comments in a text file are often denoted by some special character
 * like '#' as the first non-whitespace character on a line.  This
 * filter takes a stream of lines and produces a stream that omits all
 * comment lines.
 *
 * Note that we only intercept lines where the comment character is at
 * the beginning of the line.  This filter will not detect lines where
 * you attempt to remove data at the end by putting the comment
 * character somewhere in the middle.
 *
 * We do not expect that you will instantiate this class directly.
 * Its main purpose is to be part of the stack that makes up
 * PointReader.
 *
 * NOTE: Although the CommentCharacter member is a string and can have
 * arbitrary length, we only care about the first character.
 */

template<typename IteratorT>
class SkipCommentsReader
{
public:
  typedef IteratorT                             inner_iterator_type;
  typedef typename IteratorT::value_type        value_type;
  typedef typename value_type::value_type       char_type;

  SkipCommentsReader() : CommentCharacter("#")
    {
    }

  SkipCommentsReader(const SkipCommentsReader& other)
    : InnerBegin(other.InnerBegin),
      InnerEnd(other.InnerEnd),
      CommentCharacter(other.CommentCharacter)
    {
    }

  SkipCommentsReader(inner_iterator_type const& start, inner_iterator_type const& finish, std::string const& comment="#")
    : InnerBegin(start),
      InnerEnd(finish),
      CommentCharacter(comment)
    {
    }

  virtual ~SkipCommentsReader()
    {
    }

  void set_comment_character(std::string const& c)
  {
    this->CommentCharacter = c;
  }

  std::string const& comment_character() const
  {
    return this->CommentCharacter;
  }

  SkipCommentsReader& operator=(SkipCommentsReader const& other)
    {
      this->InnerBegin = other.InnerBegin;
      this->InnerEnd = other.InnerEnd;
      this->CommentCharacter = other.CommentCharacter;
      return *this;
    }

  bool operator==(SkipCommentsReader const& other) const
    {
      return (this->InnerBegin == other.InnerBegin &&
              this->InnerEnd == other.InnerEnd &&
              this->CommentCharacter == other.CommentCharacter);
    }

  bool operator!=(SkipCommentsReader const& other) const
    {
      return !(*this == other);
    }

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

protected:
  /*
   * \class SkipCommentsIterator
   * \brief This does the actual work of filtering lines.
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

    SkipCommentsIterator() : CommentCharacter("#")
      { }

    SkipCommentsIterator(inner_iterator_type Begin, inner_iterator_type End, std::string const& Comment)
      : InnerIterator(Begin),
        InnerEnd(End),
        CommentCharacter(Comment)
      {
        // Position the iterator on the first string to be returned.
        this->_advance_to_valid_string();
      }

    SkipCommentsIterator(SkipCommentsIterator const& other)
      : InnerIterator(other.InnerIterator),
        InnerEnd(other.InnerEnd),
        CommentCharacter(other.CommentCharacter)
      { }

    ~SkipCommentsIterator()
      { }

    SkipCommentsIterator& operator=(SkipCommentsIterator const& other)
      {
        this->InnerIterator = other.InnerIterator;
        this->InnerEnd = other.InnerEnd;
        this->CommentCharacter = other.CommentCharacter;
        return *this;
      }

    value_type const& operator*() const
      {
        return *(this->InnerIterator);
      }

    value_type const* operator->() const
      {
        return this->InnerBegin.operator->();
      }

    SkipCommentsIterator& operator++()
      {
        assert(this->InnerIterator != this->InnerEnd);
        ++ (this->InnerIterator);
        this->_advance_to_valid_string();
        return *this;
      }

    SkipCommentsIterator& operator++(int)
      {
        SkipCommentsIterator prev(*this);
        this->operator++();
        return prev;
      }

    bool operator==(SkipCommentsIterator const& other) const
      {
        return (this->InnerIterator == other.InnerIterator &&
                this->InnerEnd == other.InnerEnd &&
                this->CommentCharacter == other.CommentCharacter);
      }

    bool operator!=(SkipCommentsIterator const& other) const
      {
        return ( !(*this == other) );
      }

  private:
    inner_iterator_type InnerIterator;
    inner_iterator_type InnerEnd;
    std::string         CommentCharacter;

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
        // which is not a comment string.  The caller can decide what to
        // do with it.
        return false;
      }
  };

public:
  typedef SkipCommentsIterator iterator;
  typedef SkipCommentsIterator const const_iterator;

  iterator begin() const
    {
      return SkipCommentsIterator(this->InnerBegin, this->InnerEnd, this->CommentCharacter);
    }

  iterator end() const
    {
      return SkipCommentsIterator(this->InnerEnd, this->InnerEnd, this->CommentCharacter);
    }

  const_iterator const_begin() const
    {
      return this->begin();
    }

  const_iterator const_end() const
    {
      return this->end();
    }
};

template<typename iter_type>
SkipCommentsReader<iter_type>
  make_skip_comments_reader(iter_type start_iter, iter_type end_iter)
  {
  return SkipCommentsReader<iter_type>(start_iter, end_iter);
  }

} // close namespace tracktable

#endif
