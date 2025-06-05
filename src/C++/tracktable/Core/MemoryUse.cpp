/*
 * Author:  David Robert Nadeau
 * Site:    http://NadeauSoftware.com/
 * License: Creative Commons Attribution 3.0 Unported License
 *          http://creativecommons.org/licenses/by/3.0/deed.en_US
 *
 * Modified by Andy Wilson (atwilso@sandia.gov) to fit Tracktable
 * coding standards.
 */

#include <tracktable/Core/Logging.h>
#include <tracktable/Core/PlatformDetect.h>
#include <tracktable/Core/MemoryUse.h>

#if defined(TT_WINDOWS)
# include <windows.h>
# include <psapi.h>
#elif defined(TT_OSX)
# include <mach/mach.h>
#elif defined(TT_UNIX)
# include <unistd.h>
# include <sys/resource.h>
# include <stdio.h>
#endif

#include <iostream>




namespace tracktable {

using namespace tracktable::log;

/**
 * Returns the peak (maximum so far) resident set size (physical
 * memory use) measured in bytes, or zero if the value cannot be
 * determined on this OS.
 */
  
std::size_t peak_memory_use()
{
#if defined(TT_WINDOWS)
  /* Windows -------------------------------------------------- */
  PROCESS_MEMORY_COUNTERS info;
  GetProcessMemoryInfo(GetCurrentProcess(), &info, sizeof(info));
  return static_cast<std::size_t>(info.PeakWorkingSetSize);

#elif defined(TT_OSX)
  /* OSX ------------------------------------------------------ */
  kern_return_t task_info_status;
  mach_task_basic_info_data_t info;
  mach_msg_type_number_t info_count = MACH_TASK_BASIC_INFO_COUNT;

  task_info_status = task_info(
    mach_task_self(),
    MACH_TASK_BASIC_INFO,
    reinterpret_cast<task_info_t>(&info),
    &info_count);

  if (task_info_status != KERN_SUCCESS)
    {
    TRACKTABLE_LOG(warning) 
      << "Can't access Mach task info to get peak memory use in "
      << __FILE__;
    return static_cast<std::size_t>(0);
    }
  else
    {
    return static_cast<std::size_t>(info.resident_size_max);
    }

#elif defined(TT_UNIX)
  /* BSD, Linux, and OSX -------------------------------------- */
  struct rusage rusage;
  getrusage(RUSAGE_SELF, &rusage);
  return static_cast<std::size_t>(rusage.ru_maxrss * 1024L);


#else
  /* Unknown OS ----------------------------------------------- */
#warning "GetPeakMemoryUse: Unknown OS."
  return static_cast<std::size_t>(0);
#endif
}



/**
 * Returns the current resident set size (physical memory use) measured
 * in bytes, or zero if the value cannot be determined on this OS.
 */
std::size_t current_memory_use()
{
#if defined(TT_WINDOWS)
  /* Windows -------------------------------------------------- */
  PROCESS_MEMORY_COUNTERS info;
  GetProcessMemoryInfo( GetCurrentProcess( ), &info, sizeof(info) );
  return static_cast<std::size_t>(info.WorkingSetSize);

#elif defined(TT_OSX)
  /* OSX ------------------------------------------------------ */
  kern_return_t task_info_status;
  mach_task_basic_info_data_t info;
  mach_msg_type_number_t info_count = MACH_TASK_BASIC_INFO_COUNT;

  task_info_status = task_info(
    mach_task_self(),
    MACH_TASK_BASIC_INFO,
    reinterpret_cast<task_info_t>(&info),
    &info_count);

  if (task_info_status != KERN_SUCCESS)
    {
    TRACKTABLE_LOG(warning) 
      << "WARNING: Can't access Mach task info to get current memory use in "
      << __FILE__;
    return static_cast<std::size_t>(0);
    }
  else
    {
    return static_cast<std::size_t>(info.resident_size);
    }

#elif defined(TT_LINUX)
  /* Linux ---------------------------------------------------- */
  FILE* fp = NULL;
  fp = fopen("/proc/self/statm", "r");
  if (fp == NULL)
    {
    TRACKTABLE_LOG(warning) 
              << "Can't open /proc/self/statm to get current memory use in "
              << __FILE__;
    return static_cast<std::size_t>(0);
    }
  else
    {
    long rss = 0L;
    int lookup_result = fscanf(fp, "%*s%ld", &rss);
    if (lookup_result != 1)
      {
      TRACKTABLE_LOG(warning) 
        << "Can't read from /proc/self/statm to get current memory use in "
        << __FILE__;
      return static_cast<std::size_t>(0);
      }
    else
      {
      fclose(fp);
      std::size_t page_size_in_bytes = sysconf(_SC_PAGESIZE);
      return static_cast<std::size_t>(rss * page_size_in_bytes);
      }
    }
  
#else
  /* Unknown OS */
#warning "WARNING: GetCurrentMemoryUse: Unsupported OS."
  return static_cast<std::size_t>(0);
#endif
}
  

} // exit namespace tracktable
