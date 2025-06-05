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

#ifndef __tracktable_conversions_h
#define __tracktable_conversions_h

namespace tracktable { namespace conversions {


namespace constants {
constexpr double PI = 3.141592653589793238462643383;
constexpr double EARTH_RADIUS_IN_KM = 6371;
constexpr double EARTH_RADIUS_IN_MI = 3959;
constexpr double EARTH_RADIUS_IN_NM = 3440;
constexpr double DEGREES_PER_RADIAN = 57.29577951308232087679;
constexpr double RADIANS_PER_DEGREE = .01745329251994329576;
constexpr double SECONDS_PER_HOUR = 3600.0;
constexpr double HOURS_PER_SECOND = 0.0027777777777777;
constexpr double METERS_PER_FOOT = 0.3048; //exact
}

/** Convert radians to degrees.
 *
 * @param [in] _rad Angle to convert
 * @return Angle measured in degrees
 */

inline double degrees(double _rad)
{
  return _rad * constants::DEGREES_PER_RADIAN;
}

/** Convert degrees to radians.
 *
 * @param [in] _deg Angle to convert
 * @return Angle measured in radians
 */

inline double radians(double _deg)
{
  return _deg * constants::RADIANS_PER_DEGREE;
}

/** Convert hours to seconds.
 *
 * @param [in] _hrs Hours to convert
 * @return Time measured in seconds
 */

inline double hours_to_seconds(double _hrs)
{
  return _hrs * constants::SECONDS_PER_HOUR;
}

/** Convert seconds to hours.
 *
 * @param [in] _secs Seconds to convert
 * @return Time measured in hours
 */

inline double seconds_to_hours(double _secs)
{
  return _secs * constants::HOURS_PER_SECOND;
}

/** Convert steradians to kilometers squared.
 *
 * @param [in] _sr Steradians to convert
 * @return Distance measured in kilometers squared
 */

inline double steradians_to_km2(double _sr)
{
  return _sr * constants::EARTH_RADIUS_IN_KM * constants::EARTH_RADIUS_IN_KM;
}

/** Convert kilometers squared to steradians.
 *
 * @param [in] _km2 kilometers squared to convert
 * @return Distance measured in steradians squared
 */

inline double km2_to_steradians(double _km2)
{
  return _km2 / (constants::EARTH_RADIUS_IN_KM * constants::EARTH_RADIUS_IN_KM);
}

/** Convert radians to kilometer.
 *
 * @param [in] _rad Angle to convert
 * @return Angle measured in kilometers
 */

inline double radians_to_km(double _rad)
{
  return _rad * constants::EARTH_RADIUS_IN_KM;
}

/** Convert kilometers to radians.
 *
 * @param [in] _km Angle to convert
 * @return Angle measured in radians
 */

inline double km_to_radians(double _km)
{
  return _km / constants::EARTH_RADIUS_IN_KM;
}

/** Convert feet to meters.
 *
 * @param [in] _feet Feet to convert
 * @return Distance measured in meters
 */

inline double feet_to_meters(double _feet)
{
  return _feet * constants::METERS_PER_FOOT;
}

} } // exit tracktable::conversions

#endif
