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

/** Logging: configurable log messages in C++
 *
 * Write log messages from C++ code using the following
 * template:
 *
 * @code
 *
 * TRACKTABLE_LOG(<level>) << "My log message!";
 *
 * @endcode
 *
 * where `level` is one of `tracktable::log::trace`,
 * `tracktable::log::debug`, `tracktable::log::info`,
 * `tracktable::log::warning`, `tracktable::log::error`,
 * or `tracktable::log::fatal`.
 *
 * You may want to use 'using namespace tracktable::log' in order to import
 * those symbols and save yourself from typing a lot of colons.
 *
 * Right now there is only a single log sink: standard error. If you need
 * to redirect messages to a file you can use Boost's log module.
 * Treat TRACKTABLE_LOG as if it were BOOST_LOG_TRIVIAL (in fact, it is!)
 * and use Boost's log sinks.
 */

#ifndef __tracktable_Logging_h
#define __tracktable_Logging_h

#include <tracktable/Core/TracktableCoreWindowsHeader.h>
#include <boost/log/trivial.hpp>

#define TRACKTABLE_LOG(lvl)\
    BOOST_LOG_STREAM_WITH_PARAMS(::boost::log::trivial::logger::get(),\
        (::boost::log::keywords::severity = static_cast<::boost::log::trivial::severity_level>(lvl)))



namespace tracktable {

namespace log {
	// Trivial severity levels, borrowed from boost/log/trivial.hpp
	enum severity_level {
		trace,
		debug,
		info,
		warning,
		error,
		fatal
	};
}


/** Set minimum level at which log messages will be displayed
 *
 * By default, any message with a log level of 'info' or above.
 * This may result in too much output for you. In that case,
 * call this function to increase it. For example, if you only
 * want warnings and errors:
 *
 * @code
 *
 * tracktable::set_log_level(tracktable::log::warning);
 *
 * @endcode
 *
 * The available log levels are as follows:
 *
 * - trace:   Extremely verbose output about algorithm execution.
 *            You will only need this if you are debugging
 *            Tracktable's internals.
 *
 * - debug:   Moderately verbose output about algorithm execution.
 *            You will probably never need this, although it is
 *            sometimes useful when you need to track down a problem.
 *
 * - info:    Routine, summary information about what's going on,
 *            including start/end notifications for code that takes
 *            a long time to execute such as DBSCAN clustering.
 *            It is always safe to set the log level higher than
 *            `info`.
 *
 * - warning: Something has gone wrong but execution can continue.
 *            Results may be strange or unusable.
 *
 * - error:   Something has gone wrong and execution probably will not
 *            continue.
 *
 * - fatal:   Something has gone very wrong and execution cannot
 *            continue.
 *
 *	@param [in] new_level: Desired minimum log level. Must be of type
 *         tracktable::log::severity_level, an enum whose members
 *         are the six levels listed above.
 */

void TRACKTABLE_CORE_EXPORT set_log_level(::tracktable::log::severity_level new_level);

/** Get current log level
 *
 * Return the current log level. Log messages with a severity less
 * than this level will not be displayed.
 *
 * @note
 * 		This function will only return accurate results if you
 * 		use `tracktable::set_log_level()` to set the log level. If you
 * 		use Boost calls to go behind the library's back, it will not
 * 		be able to track what you do.
 *
 * @return Current log level (as tracktable::log::severity_level)
 */

log::severity_level TRACKTABLE_CORE_EXPORT log_level();

} // close namespace tracktable


#endif

