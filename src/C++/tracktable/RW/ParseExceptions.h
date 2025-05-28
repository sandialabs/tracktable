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

#ifndef __tracktable_rw_ParseExceptions_h
#define __tracktable_rw_ParseExceptions_h

#include <stdexcept>
#include <sstream>


namespace tracktable {

/** Simple class to encapsulate IO parsing errors
 */
class ParseError : public std::runtime_error
{
public:

  /// Instantiate an unspecified parse exception
  ParseError()
    : std::runtime_error("unspecified parse error")
    { }

  /** Instantiate an parse exception for a give error string
   *
   * @param [in] err String indicating the type of exception
   */
  ParseError(std::string const& err)
    : std::runtime_error(err)
    { }

  /** Instantiate an parse exception for a give error string
   *
   * @param [in] err Char array indicating the type of exception
   */
  ParseError(const char* err)
    : std::runtime_error(err)
    { }

};

// ----------------------------------------------------------------------

/** Simple class to encapsulate empty coordinate parsing error
 */
class EmptyCoordinateError : public ParseError
{
public:
  /** Instantiate a empty coordinate exception for a give error string
   *
   * @param [in] which_coordinate Value indicating which coordinate was empty
   */
  EmptyCoordinateError(std::size_t which_coordinate)
    : ParseError(format_empty_coordinate_message(which_coordinate))
    { }

private:
  /** Format the output error string for the empty coordinate
   *
   * @param [in] which_coordinate Which coordinate is empty
   */
  static std::string format_empty_coordinate_message(std::size_t which_coordinate)
    {
      std::ostringstream errbuf;
      errbuf << "Parse failure: String for coordinate " << which_coordinate << " is empty.";
      return errbuf.str();
    }
};

// ----------------------------------------------------------------------

/** Simple class to encapsulate empty field parsing error
 */
class EmptyFieldError : public ParseError
{
public:
  /** Instantiate a empty field exception for a give error string
   *
   * @param [in] field_name String indicating which field was empty
   */
  EmptyFieldError(std::string const& field_name)
    : ParseError(format_empty_field_message(field_name))
    { }

private:
  /** Format the output error string for the empty field
   *
   * @param [in] which_coordinate Which coordinate is empty
   */
  static std::string format_empty_field_message(std::string const& field_name)
    {
      std::ostringstream errbuf;
      errbuf << "Parse failure: String for coordinate " << field_name << " is empty.";
      return errbuf.str();
    }
};



// ----------------------------------------------------------------------

/** Simple class to encapsulate lexical cast error
 */
class LexicalCastError : public ParseError
{
public:
  /** Instantiate a empty lexical cast exception for a give error string
   *
   * @param [in] field_name Name of the field that was going to be ccoverted
   * @param [in] string_value String that was going to be converted
   * @param [in] expected_type Type that the string_value was going to be coverted to
   */
  LexicalCastError(
    std::string const& field_name,
    std::string const& string_value,
    std::string const& expected_type
    )
    : ParseError(format_convert_error_message(field_name, string_value, expected_type))
    { }

private:
  /** Format the output error string for the lexical cast error
   *
   * @param [in] field_name Name of the field that was going to be ccoverted
   * @param [in] string_value String that was going to be converted
   * @param [in] expected_type Type that the string_value was going to be coverted to
   */
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
