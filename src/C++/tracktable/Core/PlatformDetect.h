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
 * tracktable/Core/PlatformDetect.h - Macros to identify what platform we're on
 *
 * In order to provide platform-dependent features like a check on
 * memory usage, we need to determine what platform (operating system)
 * we're on. The cleanest way to do that at compile time is to look
 * at the different symbols defined by the preprocessor.
 *
 * The checks in this header file were written with reference to the
 * following web pages:
 *
 * http://beefchunk.com/documentation/lang/c/pre-defined-c/precomp.html
 * https://sourceforge.net/p/predef/wiki/OperatingSystems
 */

#ifndef __tracktable_PlatformDetect_h
#define __tracktable_PlatformDetect_h

#if defined(_MSC_VER)
# define TT_VISUAL_STUDIO 1
# define TT_WINDOWS 1
// # pragma message("Detected Windows and Visual Studio.")
#endif

#if defined(__MINGW32__) || defined(__MINGW64__)
# define TT_MINGW 1
# define TT_WINDOWS 1
// # pragma message "Detected Windows and MinGW."
#endif

#if defined(__linux) || defined(linux) || defined(__linux__)
# define TT_UNIX 1
# define TT_LINUX 1
// # pragma message "Detected Linux."
#endif

#if defined(__APPLE__)
# define TT_OSX 1
# define TT_UNIX 1
// # pragma message "Detected Mac OS X."
#endif

#if defined(__CYGWIN__)
# define TT_CYGWIN 1
# define TT_WINDOWS 1
// # warning "Detected Windows and Cygwin."
#endif

#if defined(_AIX)
# define TT_AIX 1
# define TT_UNIX 1
// # warning "Detected AIX."
#endif

#if defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__bsdi__) || defined(__DragonFly__)
# define TT_BSD 1
# define TT_UNIX 1
// # warning "Detected BSD."
#endif


#endif
