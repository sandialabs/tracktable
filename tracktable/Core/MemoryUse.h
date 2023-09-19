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
 * tracktable/Core/MemoryUsage.h - Get current, max process memory usage
 *
 * This is so heavily platform-dependent that I'm isolating it in its
 * own file but it's useful enough to go through the work of getting
 * it.
 *
 * NOTE: While NTESS holds the copyright for this file,
 * MemoryUsage.cpp has a different owner and a different license. See
 * the file MemoryUsage.cpp for details.
 *
 */

#ifndef __tracktable_MemoryUsage_h
#define __tracktable_MemoryUsage_h

#include <tracktable/Core/TracktableCoreWindowsHeader.h>

#include <cstddef>

namespace tracktable {

/**
 * Returns the peak (maximum so far) resident set size (physical
 * memory use) measured in bytes.
 *
 * @return Maximum memory use in bytes or zero if the value
 *   cannot be determined on this OS.
 */

TRACKTABLE_CORE_EXPORT std::size_t peak_memory_use();

/**
 * Returns the current resident set size (physical memory use)
 * measured in bytes.
 *
 * @return Current memory use in bytes or zero if the value
 *   cannot be determined on this OS.
 */

TRACKTABLE_CORE_EXPORT std::size_t current_memory_use();

};

#endif
