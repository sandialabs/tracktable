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

// Templates for setting the default configuration.  These respect
// whether or not the point type being read is a BasePoint or a
// TrajectoryPoint.

#ifndef __tracktable_PointReaderDefaultConfiguration_h
#define __tracktable_PointReaderDefaultConfiguration_h

namespace tracktable { namespace rw { namespace detail {

template<bool point_type_has_properties, std::size_t i>
struct set_default_configuration
{
  template<class reader_type>
  inline static void apply(reader_type* reader)
    {
      reader->set_coordinate_column(i-1, i-1);
      set_default_configuration<point_type_has_properties, i-1>::apply(reader);
    }
};

template<std::size_t i>
struct set_default_configuration<true, i>
{
  template<class reader_type>
  inline static void apply(reader_type* reader)
    {
      reader->set_coordinate_column(i-1, i+1);
      set_default_configuration<true, i-1>::apply(reader);
    }
};

template<>
struct set_default_configuration<false, 0>
{
  template<class reader_type>
  inline static void apply(reader_type* /*reader*/)
    {
      return;
    }
};

template<>
struct set_default_configuration<true, 0>
{
  template<class reader_type>
  inline static void apply(reader_type* reader)
    {
      reader->set_object_id_column(0);
      reader->set_timestamp_column(1);
    }
};


} } } // namespace tracktable::rw::detail

#endif

