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


// \defgroup Tracktable_CPP C++ components of Tracktable


#ifndef __TRACKTABLE_COMMON_H
#define __TRACKTABLE_COMMON_H


#include <boost/cstdint.hpp>

#include <map>
#include <sstream>
#include <string>
#include <vector>

#include <tracktable/Core/Logging.h>
#include <tracktable/Core/UnfortunateWorkarounds.h>
#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>

#if defined(WIN32)
// This warning shows up when you call std::copy with pointer
// arguments. The Visual C++ compiler is being extra careful because
// it can't do range checking on bare pointers the way it might be
// able to with iterators. Caution is well and good but this idiom
// shows up in many places in Boost... leading to a great many
// spurious warnings that make it hard to find the real problems.
// Hence this change.
# pragma warning( push )
# pragma warning( disable : 4996 )
#endif

namespace tracktable {

namespace settings {

/// This will be used in all point classes.
typedef double point_coordinate_type;

/// This will be used in all point classes.
typedef std::string string_type;

}

typedef settings::string_type string_type;
typedef std::vector<string_type> string_vector_type;
typedef std::basic_ostringstream<string_type::value_type> ostringstream_type;
typedef std::basic_istringstream<string_type::value_type> istringstream_type;

typedef std::map<int, int> IntIntMap;
typedef std::map<std::size_t, std::size_t> SizeSizeMap;
typedef std::map<string_type, int> StringIntMap;

} // exit namespace tracktable

#ifndef BEGIN_NAMESPACE
# define BEGIN_NAMESPACE(x) namespace x {
# define END_NAMESPACE(x) }
#endif

namespace tracktable { namespace algorithms {

// This is so basic as to be needed everywhere.

template<>
struct interpolate<std::string> : interpolate_nearest_neighbor<std::string>
{ };

} } // exit namespace tracktable::algorithms

// ----------------------------------------------------------------------


#endif
