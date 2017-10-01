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

/** boost::program_options argument type to allow "--switch arg1 arg2"
 *
 * Inspired by http://stackoverflow.com/questions/8175723/vector-arguments-in-boost-program-options
 *
 */


#ifndef __tracktable_examples_PairArgument_h
#define __tracktable_examples_PairArgument_h

#include <boost/program_options.hpp>

namespace bpo = boost::program_options;

template< typename T, typename charT = char >
class multiple_tokens_typed_value : public bpo::typed_value< T, charT >
{
public:
  typedef tracktable::string_type string_type;
  typedef bpo::typed_value< T, charT > base_type;

  // I feel queasy about using 'unsigned' as a bare type but that's
  // what's in the boost headers
  // (boost/program_options/value_semantic.hpp).

  multiple_tokens_typed_value(T *t, unsigned min_count, unsigned max_count)
    : base_type(t), MinTokenCount(min_count)
    , MaxTokenCount(max_count)
//    , base_type(t)
    {
      this->base_type::multitoken();
    }

  virtual multiple_tokens_typed_value* min_tokens(unsigned count)
    {
      this->MinTokenCount = count;
      return this;
    }

  virtual multiple_tokens_typed_value* max_tokens(unsigned count)
    {
      this->MaxTokenCount = count;
      return this;
    }

  unsigned min_tokens() const { return this->MinTokenCount; }
  unsigned max_tokens() const { return this->MaxTokenCount; }

  base_type* zero_tokens()
    {
      this->MinTokenCount = 0;
      this->MaxTokenCount = 0;
      this->base_type::zero_tokens();
      return *this;
    }

private:

  std::size_t MinTokenCount;
  std::size_t MaxTokenCount;
};


template< typename T >
multiple_tokens_typed_value<T> *
multiple_tokens_value(std::size_t low, std::size_t high)
{
  return new multiple_tokens_typed_value<T>(0, low, high);
}

template< typename T >
multiple_tokens_typed_value<T> *
multiple_tokens_value(T* t, std::size_t low, std::size_t high)
{
  return new multiple_tokens_typed_value<T>(t, low, high);
}

#endif
