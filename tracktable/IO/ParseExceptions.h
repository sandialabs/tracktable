/*
 * Copyright (c) 2015, Sandia Corporation.  All rights reserved.
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

#ifndef __tracktable_io_ParseExceptions_h
#define __tracktable_io_ParseExceptions_h

#include <stdexcept>
#include <sstream>


namespace tracktable {

class ParseError : public std::runtime_error
{
public:
  ParseError()
    : std::runtime_error("unspecified parse error")
    { }

  ParseError(std::string const& err)
    : std::runtime_error(err)
    { }

  ParseError(const char* err)
    : std::runtime_error(err)
    { }

};

// ----------------------------------------------------------------------

class EmptyCoordinateError : public ParseError
{
public:
  EmptyCoordinateError(std::size_t which_coordinate)
    : ParseError(format_empty_coordinate_message(which_coordinate))
    { }

private:
  static std::string format_empty_coordinate_message(std::size_t which_coordinate)
    {
      std::ostringstream errbuf;
      errbuf << "Parse failure: String for coordinate " << which_coordinate << " is empty.";
      return errbuf.str();
    }
};

// ----------------------------------------------------------------------


class EmptyFieldError : public ParseError
{
public:
  EmptyFieldError(std::string const& field_name)
    : ParseError(format_empty_field_message(field_name))
    { }

private:
  static std::string format_empty_field_message(std::string const& field_name)
    {
      std::ostringstream errbuf;
      errbuf << "Parse failure: String for coordinate " << field_name << " is empty.";
      return errbuf.str();
    }
};



// ----------------------------------------------------------------------

class LexicalCastError : public ParseError
{
public:
public:
  LexicalCastError(
    std::string const& field_name,
    std::string const& string_value,
    std::string const& expected_type
    )
    : ParseError(format_convert_error_message(field_name, string_value, expected_type))
    { }

private:
  static std::string format_convert_error_message(
    std::string const& field_name,
    std::string const& string_value,
    std::string const& expected_type
    )
    {
      std::ostringstream errbuf;
      errbuf << "Parse failure: Couldn't convert string '"
             << string_value << "' to type "
             << expected_type
             << " for field "
             << field_name;
      return errbuf.str();
    }
};

} // close namespace tracktable

#endif
