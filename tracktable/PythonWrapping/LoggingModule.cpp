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


// Tracktable Trajectory Library
//
// Boost.Python wrappers for C++ logging
//

#include <tracktable/Core/Logging.h>
#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

int log_level_cpp_to_python(tracktable::log::severity_level cpp_level)
{
	switch (cpp_level)
	{
		case tracktable::log::trace:
			return 5;
		case tracktable::log::debug:
			return 10;
		case tracktable::log::info:
			return 20;
		case tracktable::log::warning:
			return 30;
		case tracktable::log::error:
			return 40;
		case tracktable::log::fatal:
			return 50;
		default:
			TRACKTABLE_LOG(tracktable::log::warning)
				<< "Impossible log level "
				<< static_cast<int>(cpp_level)
				<< " encountered in log_level_cpp_to_python.  Assuming 'error'.";
			return 40;
	}
}

tracktable::log::severity_level log_level_python_to_cpp(int python_level)
{
	switch (python_level)
	{
		case 10:
			return tracktable::log::debug;
		case 20:
			return tracktable::log::info;
		case 30:
			return tracktable::log::warning;
		case 40:
			return tracktable::log::error;
		case 50:
			return tracktable::log::fatal;
		default:
		{
			// Round to the next lower log level.
			if (python_level < 10)
				return tracktable::log::trace;
			else if (python_level < 20)
				return tracktable::log::debug;
			else if (python_level < 30)
				return tracktable::log::info;
			else if (python_level < 40)
				return tracktable::log::warning;
			else if (python_level < 50)
				return tracktable::log::error;
			else
				return tracktable::log::fatal;
		}
	}
}

void set_cpp_log_level(int python_level)
{
	tracktable::set_log_level(log_level_python_to_cpp(python_level));
}

int cpp_log_level_for_python()
{
	return log_level_cpp_to_python(tracktable::log_level());
}

BOOST_PYTHON_MODULE(_logging)
{
	using namespace boost::python;

	def("set_cpp_log_level", set_cpp_log_level);
	def("cpp_log_level", cpp_log_level_for_python);
}
