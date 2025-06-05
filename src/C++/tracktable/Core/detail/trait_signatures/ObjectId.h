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

/*
 * Object ID - is this stored natively (as a class member), in the
 * property map, or not at all?
 *
 * I'm still wondering whether or not these are a good idea.  It might
 * be cleaner to say "everything lives in the property map" the way
 * everything in Python lives in the object's __dict__.
 */

#ifndef __tracktable_core_detail_traits_object_id_h
#define __tracktable_core_detail_traits_object_id_h

#include <boost/mpl/assert.hpp>

namespace tracktable { namespace traits {

template<typename T>
struct object_id
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(T)==0,
    OBJECT_ID_NOT_DEFINED_FOR_THIS_TYPE,
    (types<T>)
    );
};

// Then you can use these two as you choose, whether directly or as
// models.
template<typename T>
struct object_id_is_named_property
{
  static inline std::string get(T const& thing)
    {
      return thing.string_property_without_checking("object_id");
    }
  static inline void set(T& thing, std::string const& value)
    {
      thing.set_property("object_id", value);
    }
};

template<typename T>
struct object_id_is_member
{
  static inline std::string get(T const& thing)
    {
      return thing.object_id();
    }
  static inline void set(T& thing, std::string const& value)
    {
      thing.set_object_id(value);
    }
};

} } // exit namespace tracktable::traits

#endif
