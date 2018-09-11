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

/** Write tokens to a stream
 *
 * Supply your tokens in a form that can be converted to strings.  Set
 * your record delimiter (usually newline or similar) and your field
 * delimiter (tab, comma or similar).  Done.
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

class TokenWriter
{
public:
  typedef string_type::value_type          char_type;
  typedef boost::basic_regex<char_type>    regex_type;

  TokenWriter()
    :
    FieldDelimiter("\t"),
    OutputStream(0),
    QuoteCharacter("\""),
    RecordDelimiter("\n")
    {
      this->rebuild_delimiter_regex();
    }

  TokenWriter(std::ostream& _output)
    :
    FieldDelimiter("\t"),
    OutputStream(&_output),
    QuoteCharacter("\""),
    RecordDelimiter("\n")
    {
      this->rebuild_delimiter_regex();
    }

  ~TokenWriter() { }

  TokenWriter(TokenWriter const& other)
    : FieldDelimiter(other.FieldDelimiter)
    , OutputStream(other.OutputStream)
    , QuoteCharacter(other.QuoteCharacter)
    , RecordDelimiter(other.RecordDelimiter)
    , DelimiterRegex(other.DelimiterRegex)
    {
    }

  TokenWriter& operator=(TokenWriter const& other)
    {
      this->FieldDelimiter = other.FieldDelimiter;
      this->OutputStream = other.OutputStream;
      this->QuoteCharacter = other.QuoteCharacter;
      this->RecordDelimiter = other.RecordDelimiter;
      this->DelimiterRegex = other.DelimiterRegex;
      return *this;
    }

  bool operator==(TokenWriter const& other) const
    {
      return (
        this->OutputStream == other.OutputStream
        && this->FieldDelimiter == other.FieldDelimiter
        && this->RecordDelimiter == other.RecordDelimiter
        && this->QuoteCharacter == other.QuoteCharacter
        );
    }

  bool operator!=(TokenWriter const& other) const
    {
      return !(*this == other);
    }

  void set_output(std::ostream& out)
    {
      this->OutputStream = &out;
    }

  std::ostream& output() const
    {
      return *(this->OutputStream);
    }

  void set_field_delimiter(string_type const& delimiter)
    {
      this->FieldDelimiter = delimiter;
      this->rebuild_delimiter_regex();
    }

  string_type field_delimiter() const
    {
      return this->FieldDelimiter;
    }

  void set_record_delimiter(string_type const& end_of_line)
    {
      this->RecordDelimiter = end_of_line;
      this->rebuild_delimiter_regex();
    }

  string_type record_delimiter() const
    {
      return this->RecordDelimiter;
    }

  void set_quote_character(string_type const& quotes)
    {
      this->QuoteCharacter = quotes;
      this->rebuild_delimiter_regex();
    }

  string_type quote_character() const
    {
      return this->QuoteCharacter;
    }

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
  string_type escape_delimiters(string_type const& string_to_escape) const
    {
      const string_type replacement("\\\\&");

      string_type result = boost::regex_replace(string_to_escape, this->DelimiterRegex, replacement,
                                                boost::match_default | boost::format_sed);
      return result;
    }

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
