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

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Logging.h>

#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>

namespace {
tracktable::log::severity_level current_log_level = tracktable::log::info;
}

namespace tracktable {

tracktable::log::severity_level log_level()
{
	return current_log_level;
}

void set_log_level(::tracktable::log::severity_level new_level)
{
	using boost::log::trivial::severity_level;

	// The filter expression here is actually a boost::phoenix lambda
	// expression.  There is magic going on here.  The filter function
	// gets a set of named arguments.  The symbol 'boost::log::trivial::
	// severity' refers to one of them; the symbol 'boost_level' is the
	// local variable we define here.
	//
	// The expression below gets turned into a functor that knows how to
	// extract named arguments from the arguments to its operator().
	//
	// See the documentation for boost::phoenix and the filter capability
	// in boost::log for more information.  The critical header file
	// is <boost/log/expressions.hpp>.

	current_log_level = new_level;
	severity_level boost_level = static_cast<severity_level>(new_level);
	boost::log::core::get()->set_filter(
		boost::log::trivial::severity >= boost_level
		);
}

} // close namespace tracktable