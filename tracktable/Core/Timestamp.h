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
 * Timestamp - just boost::posix::ptime renamed
 *
 * Time is notoriously difficult to deal with even if you aren't a
 * Time Lord. Rather than reimplement this from scratch I'm going to
 * use the Boost implementation and (hopefully) get it right much more
 * quickly.
 */

#ifndef __tracktable_Timestamp_h
#define __tracktable_Timestamp_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>
#include <tracktable/Core/detail/algorithm_signatures/Extrapolate.h>

#include <tracktable/Core/TracktableCoreWindowsHeader.h>

#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/CommonBoostWarnings.h>
#include <boost/serialization/serialization.hpp>
#include <boost/serialization/split_free.hpp>
#include <boost/date_time.hpp>
#include <boost/serialization/split_free.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>
#include <boost/date_time/gregorian/greg_serialize.hpp>
#include <boost/date_time/posix_time/ptime.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/posix_time/time_serialize.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

#include <iostream>
#include <locale>

namespace tracktable {

/*! @brief Use Boost timestamps in Tracktable
 *
 * Date/time math is such a pain to get right. We will be much
 * happier and will spend much more time on trajectories if we
 * delegate this to someone else who is more passionate about
 * dates and times than moving objects.
 *
 * This may be a part of our API where the underlying
 * implementation shows through -- you may need to use Boost
 * constructs if you want to do time arithmetic on hours, minutes
 * and seconds. There is room for improvement here.
 */
typedef boost::posix_time::ptime Timestamp;
typedef boost::posix_time::time_duration Duration;

/*! @brief Use Boost Gregorian dates in Tracktable
 *
 * As above, but worse. The notion of dividing a day into 24
 * equal parts has been around for at least a couple thousand
 * years. Indexing those days, though... Gregorian? Julian?
 * Babylonian? Mayan?  Hebrew?  Which calendar system do you
 * use?
 *
 * We throw up our hands in existential dismay and adopt the
 * Gregorian calendar as the least terrible option.
 */

typedef boost::gregorian::date Date;

/*! @brief Beginning of time
 *
 * We're going to use this as our standard "before any reasonable
 * timestamp" value. This is because we can't actually use time `t =
 * 0`.
 */
const Date jan_1_1900(1900, boost::date_time::Jan, 1);
const Timestamp BeginningOfTime(jan_1_1900);


/*! @brief Construct a timestamp from a `std::string`
 *
 * This function will convert a string such as `"2014-03-05 13:44:06"`
 * into a Timestamp that represents `March 5, 2014 at 13:44:06`.
 *
 * The date/time format for this particular function is fixed. If you
 * need more flexible parsing, please use the Boost date/time IO
 * routines:
 *
 * http://www.boost.org/doc/libs/1_55_0/doc/html/date_time/date_time_io.html
 *
 * We will provide a friendlier way to do this in an upcoming version.
 *
 * @param [in] tstring String containing formatted time
 * @return Timestamp derived from string
 *
 */

TRACKTABLE_CORE_EXPORT Timestamp time_from_string(std::string const& tstring);

/*! @brief Convert a timestamp to a `std::string`
 *
 * This function will convert a timestamp that represents `March 5, 2014 at 13:44:06`
 * in to a string such as `"2014-03-05 13:44:06"`
 *
 * The date/time format for this particular function is fixed. If you
 * need more flexible parsing, please use the Boost date/time IO
 * routines:
 *
 * http://www.boost.org/doc/libs/1_55_0/doc/html/date_time/date_time_io.html
 *
 * We will provide a friendlier way to do this in an upcoming version.
 *
 * @param [in] ts Timestamp to be converted to a string
 * @return String derived from Timestamp
 *
 */
TRACKTABLE_CORE_EXPORT string_type time_to_string(Timestamp const& ts);

/*! @brief Return a timestamp containing `boost::posix_time::not_a_date_time`
 *
 * We may need to create an invalid timestamp to signal "not yet
 * initialized". This function does that.
 *
 * @note
 *    I think this will fail to translate into a Python datetime. Need to test this.
 */

TRACKTABLE_CORE_EXPORT Timestamp no_such_timestamp();

/*! @brief Check to see whether a timestamp is valid
 *
 * Boost's date/time library can return timestamps that do not
 * represent any real date. This function tells you whether you've
 * got a "real" timestamp or one of those special values.
 *
 * @param [in] ts Timestamp to checked for validity
 * @return Boolean indicating valid/invalid Timestamp
 */

TRACKTABLE_CORE_EXPORT bool is_timestamp_valid(Timestamp const& ts);

/*! @brief Truncate a timestamp downward to the nearest second.
 *
 * We have sub-second precision on these timestamps -- all the way
 * down to nanoseconds if we really want -- but there are often
 * cases when we only care about precision to a single second.
 * This gives us a clean way to get there.
 *
 * @param [in] input Timestamp with fractional seconds to be truncated
 * @return Timestamp without truncated seconds
 */

TRACKTABLE_CORE_EXPORT Timestamp truncate_fractional_seconds(Timestamp const& input);

/*! @brief Round a timestamp to the nearest second.
 *
 * A time with a fractional component of at least 500 milliseconds
 * will be rounded up to the next whole second. A time with a
 * fractional component of fewer than 500 milliseconds will be rounded
 * down to the previous whole second.
 *
 * @param [in] input Timestamp with to be rounds to nearest seconds
 * @return Rounded Timestamp
 */

TRACKTABLE_CORE_EXPORT Timestamp round_to_nearest_second(Timestamp const& input);

/*! @brief Create a duration measured in hours
 *
 * This is a convenience method to create a Duration that is an
 * integral number of hours.
 *
 * @param [in] num_hours Number of hours to assigned to the duration
 * @return Duration with new number of hours
 */

TRACKTABLE_CORE_EXPORT Duration hours(int num_hours);

/*! @brief Create a duration measured in minutes
 *
 * This is a convenience method to create a Duration that is an
 * integral number of minutes.
 *
 * @param [in] num_minutes Number of minutes to assigned to the duration
 * @return Duration with new number of minutes
 */

TRACKTABLE_CORE_EXPORT Duration minutes(int num_minutes);

/*! @brief Create a duration measured in seconds
 *
 * This is a convenience method to create a Duration that is an
 * integral number of seconds.
 *
 * @param [in] num_seconds Number of seconds to assigned to the duration
 * @return Duration with new number of seconds
 */

TRACKTABLE_CORE_EXPORT Duration seconds(int num_seconds);

/*! @brief Create a duration measured in milliseconds
 *
 * This is a convenience method to create a Duration that is an
 * integral number of milliseconds.
 *
 * @param [in] num_milliseconds Number of milliseconds to assigned to the duration
 * @return Duration with new number of milliseconds
 */

TRACKTABLE_CORE_EXPORT Duration milliseconds(int64_t num_milliseconds);

/*! @brief Create a duration measured in microseconds
 *
 * This is a convenience method to create a Duration that is an
 * integral number of seconds.
 *
 * @param [in] num_microseconds Number of microseconds to assigned to the duration
 * @return Duration with new number of microseconds
 */

TRACKTABLE_CORE_EXPORT Duration microseconds(int64_t num_microseconds);

/*! @brief Create a duration measured in days
 *
 * This is a convenience method to create a Duration that is an
 * integral number of days.
 *
 * @param [in] num_days Number of days to assigned to the duration
 * @return Duration with new number of days
 */

TRACKTABLE_CORE_EXPORT Duration days(int num_days);

/*! @brief Change the string format for timestamp parsing
 *
 * This function will change the format used to parse
 * timestamps. The effect is process-wide.
 *
 * There are many flags available for use in the format. The
 * following web page documents them all:
 *
 * http://www.boost.org/doc/libs/1_55_0/doc/html/date_time/date_time_io.html
 *
 * The default value is `"%Y-%m-%d %H:%M:%S"`, corresponding to
 * timestamps such as `"2014-04-05 12:33:40"`.
 *
 * @param [in] stream Stream to add timestamp information to
 * @param [in] format The format of the timestamp
 */
 template<typename stream_type>
 void imbue_stream_with_timestamp_output_format(stream_type& stream, std::string const& format)
 {
   typedef boost::posix_time::time_facet facet_t;
   facet_t* facet(new facet_t(format.c_str()));
   stream.imbue(std::locale(stream.getloc(), facet));
 }

/*! @brief Set the default format for timestamp output
 *
 * This format will be used when printing timestamps in (for example)
 * trajectory points.
 *
 * @param [in] format Format string to use
 */

TRACKTABLE_CORE_EXPORT void set_default_timestamp_output_format(string_type const& format);

/*! @brief Get the default format for timestamp output
 *
 * This format will be used when printing timestamps in (for example)
 * trajectory points.
 *
 * @return Format string currently set as default
 */

TRACKTABLE_CORE_EXPORT string_type default_timestamp_output_format();


/*! @brief Set the default format for timestamp input
 *
 * This format will be used when printing timestamps in (for example)
 * trajectory points unless otherwise overridden.
 *
 * @param [in] format Format string to use
 */

TRACKTABLE_CORE_EXPORT void set_default_timestamp_input_format(string_type const& format);

/*! @brief Get the default format for timestamp input
 *
 * This format will be used when parsing timestamps.
 *
 * @return Format string currently set as default
 */

TRACKTABLE_CORE_EXPORT string_type default_timestamp_input_format();


} // namespace tracktable


// ----------------------------------------------------------------------

namespace tracktable { namespace algorithms {

/*! @brief Interpolate between two timestamps.
 *
 * Standard linear interpolation. At `t <= 0` you get back the first
 * value. At `t >= 1` you get the second value. Anywhere in between,
 * you get `(1-t) * first + t * second`.
 *
 * This specializes the template in tracktable/Core/detail/algorithm_signatures/Interpolate.h.
 */

template<>
struct interpolate<Timestamp>
{
  static inline Timestamp
  apply(Timestamp const& first, Timestamp const& second, double t)
    {
      if (t <= 0)
        {
        return first;
        }
      else if (t >= 1)
        {
        return second;
        }
      else
        {
        // A 64-bit integer is enough to track timestamps at microsecond precision
        // for a little less than 600,000 years. It provides enough precision
        // for us here.
		int64_t usec = static_cast<int64_t>(t * (second-first).total_microseconds());
        boost::posix_time::time_duration delta_t = boost::posix_time::microseconds(usec);
        return( first + delta_t );
        }
    }
};

template<>
struct extrapolate<Timestamp>
{
    static inline Timestamp
        apply(Timestamp const& first, Timestamp const& second, double t)
    {
        // A 64-bit integer is enough to track timestamps at microsecond precision
        // for a little less than 600,000 years. It provides enough precision
        // for us here.
        int64_t usec = static_cast<int64_t>(t * (second - first).total_microseconds());
        boost::posix_time::time_duration delta_t = boost::posix_time::microseconds(usec);
        return(first + delta_t);
    }
};

} } // exit namespace tracktable::algorithms

// ----------------------------------------------------------------------
//
// Boost serialization support
//
// Timestamps don't have serialization by default. Here we include
// support just for boost::date_time::posix_time.
//
// ----------------------------------------------------------------------


#endif
