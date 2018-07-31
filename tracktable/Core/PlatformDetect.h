#ifndef __tracktable_PlatformDetect_h
#define __tracktable_PlatformDetect_h

/* These pages are your friends:
 *
 * http://beefchunk.com/documentation/lang/c/pre-defined-c/precomp.html
 * https://sourceforge.net/p/predef/wiki/OperatingSystems
 */

#if defined(_MSC_VER)
# define TT_VISUAL_STUDIO 1
# define TT_WINDOWS 1
#endif

#if defined(__MINGW32__) || defined(__MINGW64__)
# define TT_MINGW 1
# define TT_WINDOWS 1
#endif

#if defined(__linux) || defined(linux) || defined(__linux__)
# define TT_UNIX 1
# define TT_LINUX 1
#endif

#if defined(__APPLE__) && defined(__MACOSX__)
# define TT_OSX 1
# define TT_UNIX 1
#endif

#if defined(__CYGWIN__)
# define TT_CYGWIN 1
# define TT_WINDOWS 1
#endif

#if defined(_AIX)
# define TT_AIX 1
# define TT_UNIX 1
#endif

#if defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__bsdi__) || defined(__DragonFly__)
# define TT_BSD 1
# define TT_UNIX 1
#endif


#if 0
#define TT_UNIX 1
#endif

#endif
