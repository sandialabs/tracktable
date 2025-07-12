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

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/Logging.h>
#include <tracktable/Core/MemoryUse.h>
#include <boost/cstdint.hpp>
#include <iostream>

// Import constants for log level
using namespace tracktable::log;

int test_memory_use()
{
  int error_count = 0;

  std::size_t initial_memory_use = tracktable::current_memory_use();
  TRACKTABLE_LOG(info)
            << "test_memory_use: Initial memory use is "
            << initial_memory_use;
  TRACKTABLE_LOG(info)
            << "test_memory_use: Peak memory use at startup is "
            << tracktable::peak_memory_use()
            << "\n";

  const std::size_t num_ints = 10000000;
  std::size_t* big_chunk = new std::size_t[num_ints];
  for (std::size_t i = 0; i < num_ints; ++i)
    {
    big_chunk[i] = i;
    }

  std::size_t current_memory_use = tracktable::current_memory_use();
  std::size_t expected_delta = num_ints * sizeof(std::size_t);

  TRACKTABLE_LOG(info)
            << "test_memory_use: Memory use after allocating "
            << num_ints
            << " integers ("
            << num_ints * sizeof(std::size_t) << " bytes) is "
            << current_memory_use
            << " (delta: " << (static_cast<boost::int64_t>(current_memory_use) -
			       static_cast<boost::int64_t>(initial_memory_use))
            << ")\n";

  if (tracktable::almost_equal(
        static_cast<double>(current_memory_use - initial_memory_use),
        static_cast<double>(expected_delta),
        0.01) == false)
    {
      TRACKTABLE_LOG(error)
        << "ERROR: test_memory_use: Unexpectedly large delta "
		    << "between size of block allocated ("
		    << expected_delta << ") and actual memory use increase ("
		    << (current_memory_use - initial_memory_use)
		    << ")";
      error_count += 1;
    }

  // This line actually matters.  If it's not here, the optimizer
  // will notice that we're not actually doing anything with the
  // contents of big_chunk and never allocate it in the first place.
  // That causes the test to fail because the numbers reported by
  // the OS don't make sense in the context of what we think our
  // code is doing.
  big_chunk[0] = big_chunk[0] * 2;

  std::size_t peak_memory_use = tracktable::peak_memory_use();
  std::size_t final_memory_use = tracktable::current_memory_use();

  TRACKTABLE_LOG(info)
            << "test_memory_use: Memory use after deleting large array: "
            << final_memory_use
            << " (delta "
            << (static_cast<boost::int64_t>(final_memory_use) -
		            static_cast<boost::int64_t>(current_memory_use))
            << ")";

  TRACKTABLE_LOG(info)
            << "test_memory_use: Peak memory use reported is "
            << peak_memory_use;


  return error_count;
}


int main(int , char**)
{
  int error_count = 0;

  error_count += test_memory_use();

  return error_count;
}
