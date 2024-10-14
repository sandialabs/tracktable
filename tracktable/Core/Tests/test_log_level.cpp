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

// Test setting log levels.  Make sure log messages with lower severity
// than the current log level do not get printed.

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Logging.h>

#include <boost/log/core.hpp>
#include <boost/log/sinks/text_ostream_backend.hpp>
#include <boost/log/sinks/sync_frontend.hpp>

#include <boost/core/null_deleter.hpp>
#include <boost/make_shared.hpp>
#include <boost/shared_ptr.hpp>

#include <sstream>


typedef boost::shared_ptr<std::ostringstream> ostringstream_ptr;

int check_for_log_message(
	tracktable::log::severity_level probe_level,
	bool expect_log_message,
	ostringstream_ptr outbuf
	)
{
	// Reset the stream to be empty with no errors
	outbuf->str("");
	outbuf->clear();

	// Log a message with whatever level the user wants
	TRACKTABLE_LOG(probe_level) << "Testing";
	std::cout << "Outbuf contents: " << outbuf->str() << "\n";

	bool did_print = (outbuf->str().size() > 0);
	if (did_print != expect_log_message)
	{
		if (did_print)
		{
			std::cerr << "ERROR: check_for_log_message: Log message at level "
					  << probe_level << " printed unexpectedly.\n";
		}
		else
		{
			std::cerr << "ERROR: check_for_log_message: Log message at level "
			          << probe_level << " should have printed but didn't.\n";
		}
		return 1;
	}

	return 0;
}


int test_log_level(tracktable::log::severity_level level,
  				   ostringstream_ptr outbuf)
{
	namespace tl = tracktable::log;

 	int num_errors = 0;
 	std::cerr << "test_log_level: Testing level " << level << "\n";
 	tracktable::set_log_level(level);

 	num_errors += check_for_log_message(tl::trace, (tl::trace >= level), outbuf);
 	num_errors += check_for_log_message(tl::debug, (tl::debug >= level), outbuf);
 	num_errors += check_for_log_message(tl::info, (tl::info >= level), outbuf);
 	num_errors += check_for_log_message(tl::warning, (tl::warning >= level), outbuf);
 	num_errors += check_for_log_message(tl::error, (tl::error >= level), outbuf);
 	num_errors += check_for_log_message(tl::fatal, (tl::fatal >= level), outbuf);

 	return num_errors;
}


int main(int /*argc*/, char** /*argv*/)
{
	// We want Boost to write log messages to a std::ostringstream so that we
	// can examine what's been written.
	namespace sinks = boost::log::sinks;
	typedef sinks::synchronous_sink< sinks::text_ostream_backend > text_sink;
    boost::shared_ptr< text_sink > sink = boost::make_shared< text_sink >();

	std::ostringstream outbuf;
 	ostringstream_ptr outbuf_ptr(&outbuf, boost::null_deleter());
	sink->locked_backend()->add_stream(outbuf_ptr);
	boost::log::core::get()->add_sink(sink);

	int num_errors = 0;

	num_errors += test_log_level(tracktable::log::trace, outbuf_ptr);
	num_errors += test_log_level(tracktable::log::debug, outbuf_ptr);
	num_errors += test_log_level(tracktable::log::info, outbuf_ptr);
	num_errors += test_log_level(tracktable::log::warning, outbuf_ptr);
	num_errors += test_log_level(tracktable::log::error, outbuf_ptr);
	num_errors += test_log_level(tracktable::log::fatal, outbuf_ptr);

	return num_errors;
}