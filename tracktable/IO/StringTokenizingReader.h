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

#ifndef __TRACKTABLE_STRING_TOKENIZING_READER_H
#define __TRACKTABLE_STRING_TOKENIZING_READER_H

#include <tracktable/Core/TracktableCommon.h>

#include <boost/tokenizer.hpp>
#include <algorithm>
#include <iterator>
#include <string>
#include <cassert>
#include <iostream>

namespace tracktable {

/**
 * \class StringTokenizingReader
 * \brief Iterate over a range of input strings and tokenize each one.
 *
 * This is the third of four steps in the pipeline of reading points
 * in from a file.  The first is to read in a file line-by-line.  The
 * second is to filter out those lines that are comments.  The third
 * is to tokenize the lines that survive into little bits that we can
 * then use to populate a point.
 *
 */

template<typename InputLineIteratorT>
class StringTokenizingReader
{
public:
  typedef InputLineIteratorT                      input_line_iter_type;
  typedef typename InputLineIteratorT::value_type string_type;

  /** Initialize an empty reader with default delimiters (space, tab).
   */
  StringTokenizingReader()
    : FieldDelimiter(",")
    , EscapeCharacter("\\")
    , QuoteCharacter("\"")
    {
    }

  /** Initialize a tokenizer with an input range and default delimiters.
   */
  StringTokenizingReader(input_line_iter_type Start, input_line_iter_type Finish)
    : InputLinesBegin(Start)
    , InputLinesEnd(Finish)
    , FieldDelimiter(",")
    , EscapeCharacter("\\")
    , QuoteCharacter("\"")
    {
    }

  /** Initialize a tokenizer with an input range and your own delimiters.
   */
  StringTokenizingReader(
    input_line_iter_type Start,
    input_line_iter_type Finish,
    string_type const& Delim
  )
    : InputLinesBegin(Start)
    , InputLinesEnd(Finish)
    , FieldDelimiter(Delim)
    , EscapeCharacter("\\")
    , QuoteCharacter("\"")
    {
    }

  /** Copy state from another tokenizer.
   */
  StringTokenizingReader(StringTokenizingReader const& other)
    : InputLinesBegin(other.InputLinesBegin)
    , InputLinesEnd(other.InputLinesEnd)
    , FieldDelimiter(other.FieldDelimiter)
    , EscapeCharacter(other.EscapeCharacter)
    , QuoteCharacter(other.QuoteCharacter)
    {
    }

  virtual ~StringTokenizingReader()
    {
    }

  /** Set the delimiter character to use in tokenization.
   *
   * The single character in the string you supply will be used as a
   * field delimiter.
   */
  void set_field_delimiter(string_type const& delim)
  {
    this->FieldDelimiter = delim;
  }

  /** Return the delimiter character currently in use.
   */
  string_type field_delimiter() const
    {
    return this->FieldDelimiter;
    }

  /** Set the escape character to use in tokenization.
   *
   * You must supply a string with either 0 or 1 character to be used
   * as an escape character.  The escape character removes the special
   * properties of whatever character follows, usually a newline,
   * separator or quote character.
   */
  void set_escape_character(string_type const& escape)
  {
    this->EscapeCharacter = escape;
  }

  /** Return the escape characters currently in use.
   */
  string_type escape_character() const
    {
    return this->EscapeCharacter;
    }

  /** Set the quote character to use in tokenization.
   *
   * The single character in the string you supply (assuming it is not
   * empty) will be used as a quote character.  Inside a quoted string
   * (a string that begins and ends with the quote character), field
   * delimiters (e.g. comma) will be ignored.  Also, inside a quoted
   * string, embedded quote characters must be escaped.
   */
  void set_quote_character(string_type const& quote)
    {
      this->QuoteCharacter = quote;
    }

  /** Return the quote characters currently in use.
   */
  string_type quote_character() const
    {
      return this->QuoteCharacter;
    }

  StringTokenizingReader& operator=(StringTokenizingReader const& other)
    {
      this->InputLinesBegin  = other.InputLinesBegin;
      this->InputLinesEnd    = other.InputLinesEnd;
      this->FieldDelimiter   = other.FieldDelimiter;
      this->EscapeCharacter  = other.EscapeCharacter;
      this->QuoteCharacter   = other.QuoteCharacter;
      return *this;
    }

  bool operator==(StringTokenizingReader const& other) const
    {
      return (
        this->InputLinesBegin    == other.InputLinesBegin
        && this->InputLinesEnd   == other.InputLinesEnd
        && this->FieldDelimiter  == other.FieldDelimiter
        && this->EscapeCharacter == other.EscapeCharacter
        && this->QuoteCharacter  == other.QuoteCharacter
        );
    }

  bool operator!=(StringTokenizingReader const& other) const
    {
      return !(*this == other);
    }

  void set_input_range(input_line_iter_type const& start,
                       input_line_iter_type const& finish)
  {
    this->InputLinesBegin = start;
    this->InputLinesEnd = finish;
  }

private:
  input_line_iter_type InputLinesBegin;
  input_line_iter_type InputLinesEnd;
  string_type          FieldDelimiter;
  string_type          EscapeCharacter;
  string_type          QuoteCharacter;

  typedef boost::escaped_list_separator<typename input_line_iter_type::value_type::value_type> separator_type;
  typedef boost::tokenizer<separator_type> tokenizer_type;

  typedef std::pair<
    typename tokenizer_type::iterator,
    typename tokenizer_type::iterator
    > token_iterator_pair;

protected:

  class TokenizedStringIterator : public std::iterator<
    std::input_iterator_tag,
    token_iterator_pair,
    std::ptrdiff_t,
    const token_iterator_pair *,
    token_iterator_pair  const&
  >
  {
  private:
    tokenizer_type* Tokenizer;
    token_iterator_pair TokenRangeCurrentString;
    input_line_iter_type InputLinesBegin;
    input_line_iter_type InputLinesEnd;
    string_type FieldDelimiter;
    string_type EscapeCharacter;
    string_type QuoteCharacter;

    void _tokenize_this_line()
    {
      if (this->InputLinesBegin == this->InputLinesEnd) return;

      separator_type separator(this->EscapeCharacter,
                               this->FieldDelimiter,
                               this->QuoteCharacter);
      this->Tokenizer = new tokenizer_type(*(this->InputLinesBegin), separator);
      this->TokenRangeCurrentString.first = this->Tokenizer->begin();
      this->TokenRangeCurrentString.second = this->Tokenizer->end();
    }

  public:
    typedef typename tokenizer_type::iterator iterator;
    typedef token_iterator_pair value_type;

    TokenizedStringIterator()
      : Tokenizer(0)
      { }

    ~TokenizedStringIterator()
      {
      delete this->Tokenizer;
      }

  TokenizedStringIterator(
    input_line_iter_type Begin,
    input_line_iter_type End,
    string_type const& Delim,
    string_type const& Escape,
    string_type const& Quote
    )
    : Tokenizer(0),
      InputLinesBegin(Begin),
      InputLinesEnd(End),
      FieldDelimiter(Delim),
      EscapeCharacter(Escape),
      QuoteCharacter(Quote)
      {
        this->_tokenize_this_line();
      }

    TokenizedStringIterator(TokenizedStringIterator const& other)
      : Tokenizer(0),
        TokenRangeCurrentString(other.TokenRangeCurrentString),
        InputLinesBegin(other.InputLinesBegin),
        InputLinesEnd(other.InputLinesEnd),
        FieldDelimiter(other.FieldDelimiter),
        EscapeCharacter(other.EscapeCharacter),
        QuoteCharacter(other.QuoteCharacter)
        {
        // We set up our own tokenization because otherwise we will have
        // a shared pointer to the tokenizer with no way to resolve who
        // gets to delete it and who has to stay away.
        this->_tokenize_this_line();
        }

    TokenizedStringIterator& operator=(TokenizedStringIterator const& other)
      {
        this->InputLinesBegin  = other.InputLinesBegin;
        this->InputLinesEnd    = other.InputLinesEnd;
        this->FieldDelimiter   = other.FieldDelimiter;
        this->EscapeCharacter  = other.EscapeCharacter;
        this->QuoteCharacter   = other.QuoteCharacter;
        this->_tokenize_this_line();
        return *this;
      }

    token_iterator_pair const& operator*() const
      {
        return this->TokenRangeCurrentString;
      }

    token_iterator_pair const* operator->() const
      {
        return &(this->TokenRangeCurrentString);
      }

    TokenizedStringIterator& operator++()
      {
        assert(this->InputLinesBegin != this->InputLinesEnd);
        delete this->Tokenizer;
        this->Tokenizer = 0;
        ++ (this->InputLinesBegin);
        this->_tokenize_this_line();
        return *this;
      }

    TokenizedStringIterator& operator++(int)
      {
        TokenizedStringIterator prev(*this);
        this->operator++();
        return prev;
      }

    bool operator==(TokenizedStringIterator const& other) const
      {
        return (this->InputLinesBegin  == other.InputLinesBegin &&
                this->InputLinesEnd    == other.InputLinesEnd &&
                this->FieldDelimiter   == other.FieldDelimiter &&
                this->EscapeCharacter  == other.EscapeCharacter &&
                this->QuoteCharacter   == other.QuoteCharacter);
      }

    bool operator!=(TokenizedStringIterator const& other) const
      {
        return ( !(*this == other) );
      }
  };

  // End of iterator class; now back to StringTokenizingReader

public:
  typedef TokenizedStringIterator iterator;
  typedef TokenizedStringIterator const const_iterator;

  iterator begin() const
    {
      return TokenizedStringIterator(this->InputLinesBegin, this->InputLinesEnd, this->FieldDelimiter, this->EscapeCharacter, this->QuoteCharacter);
    }

  iterator end() const
    {
      return TokenizedStringIterator(this->InputLinesEnd, this->InputLinesEnd, this->FieldDelimiter, this->EscapeCharacter, this->QuoteCharacter);
    }

  const_iterator const_begin() const
    {
      return this->begin();
    }

  const_iterator const_end() const
    {
      return this->end();
    }
}; // End of StringTokenizingReader

} // close namespace tracktable

#endif
