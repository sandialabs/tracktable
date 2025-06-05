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


#ifndef __tracktable_TokenWriter_h
#define __tracktable_TokenWriter_h

#include <tracktable/Core/TracktableCommon.h>

#include <ostream>
#include <sstream>
#include <string>
#include <iostream>

#include <boost/regex.hpp>
#include <boost/throw_exception.hpp>

namespace tracktable {

/** Write tokens to a stream
 *
 * Supply your tokens in a form that can be converted to strings. Set
 * your record delimiter (usually newline or similar) and your field
 * delimiter (tab, comma or similar). Done.
 */

class TokenWriter
{
public:
  typedef string_type::value_type          char_type;
  typedef boost::basic_regex<char_type>    regex_type;

  /// Instantiate a default token writer
  TokenWriter()
    :
    FieldDelimiter("\t"),
    OutputStream(0),
    QuoteCharacter("\""),
    RecordDelimiter("\n")
    {
      this->rebuild_delimiter_regex();
    }

  /** Instantiate a writer using a `std::ostream`
   *
   * @param [in] _output Stream to output to
   */
  TokenWriter(std::ostream& _output)
    :
    FieldDelimiter("\t"),
    OutputStream(&_output),
    QuoteCharacter("\""),
    RecordDelimiter("\n")
    {
      this->rebuild_delimiter_regex();
    }

  /** Copy contructor, create a writer with a copy of another
   *
   * @param [in] other TokenWriter to copy from
   */
  TokenWriter(TokenWriter const& other)
    : FieldDelimiter(other.FieldDelimiter)
    , OutputStream(other.OutputStream)
    , QuoteCharacter(other.QuoteCharacter)
    , RecordDelimiter(other.RecordDelimiter)
    , DelimiterRegex(other.DelimiterRegex)
    {
    }

  /// Destructor
  ~TokenWriter() { }

  /** Assign a TokenWriter to the value of another.
   *
   * @param [in] other TokenWriter to assign value of
   * @return Writer with the new assigned value
   */
  TokenWriter& operator=(TokenWriter const& other)
    {
      this->FieldDelimiter = other.FieldDelimiter;
      this->OutputStream = other.OutputStream;
      this->QuoteCharacter = other.QuoteCharacter;
      this->RecordDelimiter = other.RecordDelimiter;
      this->DelimiterRegex = other.DelimiterRegex;
      return *this;
    }

  /** Check whether one writer is equal to another by comparing all the properties.
   *
   * Two writers are equal if all of their streams are properties.
   *
   * @param [in] other TokenWriter for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(TokenWriter const& other) const
    {
      return (
        this->OutputStream == other.OutputStream
        && this->FieldDelimiter == other.FieldDelimiter
        && this->RecordDelimiter == other.RecordDelimiter
        && this->QuoteCharacter == other.QuoteCharacter
        );
    }

  /** Check whether two TokenWriter are unequal.
   *
   * @param [in] other TokenWriter for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(TokenWriter const& other) const
    {
      return !(*this == other);
    }

  /** Set the stream where tokens will be written
   *
   * This can be any `std::ostream`.
   *
   * @note
   *    You are resposible for ensuring that the stream does not go
   *    out of scope until you are done writing tokens.
   *
   * @param [in] out Stream where tokens will be written
   */
  void set_output(std::ostream& out)
    {
      this->OutputStream = &out;
    }

  /** Return the stream where tokens will be written
   *
   * @return output stream
   */
  std::ostream& output() const
    {
      return *(this->OutputStream);
    }

  /** Set the field delimiter
   *
   * This string will be inserted between each field as tokens are
   * written.
   *
   * @param [in] delim Delimiter string
   */
  void set_field_delimiter(string_type const& delimiter)
    {
      this->FieldDelimiter = delimiter;
      this->rebuild_delimiter_regex();
    }

  /** Return the field delimiter
   *
   * @return Field delimiter
   */
  string_type field_delimiter() const
    {
      return this->FieldDelimiter;
    }

  /** Set the record separator (end-of-line string)
   *
   * This string will be written after each token. By default it's
   * `std::endl` (the newline string).
   *
   * @param [in] sep String separator
   */
  void set_record_delimiter(string_type const& end_of_line)
    {
      this->RecordDelimiter = end_of_line;
      this->rebuild_delimiter_regex();
    }

  /** Retrieve the record separator (end-of-line string)
   *
   * @return Return the record separator (end-of-line string)
   */
  string_type record_delimiter() const
    {
      return this->RecordDelimiter;
    }

  /** Set the quote character
   *
   * This character *may* be used to enclose a field containing lots
   * of characters that would otherwise need to be escaped. We have
   * to know what it is so that we can escape it ourselves when we
   * encounter the quote character inside fields.
   *
   * @param [in] quotes: Zero or one character to be used as
   * quotation marks
   */
  void set_quote_character(string_type const& quotes)
    {
      this->QuoteCharacter = quotes;
      this->rebuild_delimiter_regex();
    }

  /** Return the current quote characters
   *
   * @return Current quote character
   */
  string_type quote_character() const
    {
      return this->QuoteCharacter;
    }

  /** Write the tokens to the ouput stream
   *
   * @param [in] begin Point to start writing at
   * @param [in] end Point to stop writing at
   */
  template<typename token_iter_t>
  void write_record(token_iter_t begin, token_iter_t end)
    {
      std::basic_ostringstream<char_type> outbuf;

      for (token_iter_t here = begin; here != end; ++here)
        {
        if (here != begin)
          {
          outbuf << this->FieldDelimiter;
          }
        outbuf << escape_delimiters(*here);
        }
      outbuf << this->RecordDelimiter;

      (*this->OutputStream) << outbuf.str();
      this->OutputStream->flush();
    }

private:
  /** Escape delimiters when writing
   *
   * @param [in] string_to_escape Delimiter to escape
   * @return The escaped delimiter
   */
  string_type escape_delimiters(string_type const& string_to_escape) const
    {
      const string_type replacement("\\\\&");

      string_type result = boost::regex_replace(string_to_escape, this->DelimiterRegex, replacement,
                                                boost::match_default | boost::format_sed);
      return result;
    }

  /** Build the delimiter regex with the field, record and quote delimiters
   */
  void rebuild_delimiter_regex()
    {
      std::basic_ostringstream<string_type::value_type> outbuf;

      outbuf << "[";

      outbuf << this->escape_characters_for_set(this->FieldDelimiter);
      outbuf << this->escape_characters_for_set(this->RecordDelimiter);
      outbuf << this->escape_characters_for_set(this->QuoteCharacter);

      outbuf << "]";

      this->DelimiterRegex = regex_type(outbuf.str());
    }

  /** Escape characters for a given set
   *
   * @param [in] in_string String to escape character from
   */
  string_type
  escape_characters_for_set(string_type const& in_string)
    {
      std::basic_ostringstream<string_type::value_type> frontbuf, mainbuf, rearbuf;

      for (string_type::const_iterator char_iter = in_string.begin();
           char_iter != in_string.end();
           ++char_iter)
        {
        switch (*char_iter)
          {
          case 0x0a: // newline
            mainbuf << "\\n"; break;
          case 0x09: // tab
            mainbuf << "\\t"; break;
          case '-':
            frontbuf << "\\-"; break;
          case '[':
            rearbuf << "\\["; break;
          case ']':
            rearbuf << "\\]"; break;
          case '^':
            rearbuf << "\\^"; break;
          default:
            mainbuf << *char_iter; break;
          }
        }

      frontbuf << mainbuf.str();
      frontbuf << rearbuf.str();
      return frontbuf.str();
    }

  string_type   FieldDelimiter;
  std::ostream* OutputStream;
  string_type   QuoteCharacter;
  string_type   RecordDelimiter;
  regex_type    DelimiterRegex;



};

} // close namespace tracktable

#endif
