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
 * SphericalCoordinateAccess - Every point type that lives on a sphere
 * must specialize this in order to provide us a way of setting and
 * getting coordinates regardless of input units.
 *
 * You need to implement eight functions:
 *
 * static inline double longitude_as_degrees(Point const& p)
 * static inline double longitude_as_radians(Point const& p)
 * static inline double latitude_as_degrees(Point const& p)
 * static inline double latitude_as_radians(Point const& p)
 *
 * static inline void set_longitude_from_degrees(Point const& p)
 * static inline void set_longitude_from_radians(Point const& p)
 * static inline void set_latitude_from_degrees(Point const& p)
 * static inline void set_latitude_from_radians(Point const& p)
 *
 * See tracktable/Core/PointLonLat.h for an example.
 */


#ifndef __tracktable_core_algorithms_detail_SphericalCoordinateAccess_h
#define __tracktable_core_algorithms_detail_SphericalCoordinateAccess_h

#include <boost/mpl/assert.hpp>

namespace tracktable { namespace algorithms {

template<typename T>
struct spherical_coordinate_access
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(T)==0,
    SPHERICAL_COORDINATE_ACCESS_NOT_DEFINED_FOR_THIS_POINT_TYPE,
    (types<T>)
    );
};

} } // namespace tracktable::algorithms

/*
 * Now we have functions that wrap the algorithms structs so that we can
 * call them easily instead of worrying about instantiation.
 */

namespace tracktable {

template<typename T>
double longitude_as_degrees(T const& point)
{
  return algorithms::spherical_coordinate_access<T>::longitude_as_degrees(point);
}

template<typename T>
double longitude_as_radians(T const& point)
{
  return algorithms::spherical_coordinate_access<T>::longitude_as_radians(point);
}

template<typename T>
double latitude_as_degrees(T const& point)
{
  return algorithms::spherical_coordinate_access<T>::latitude_as_degrees(point);
}

template<typename T>
double latitude_as_radians(T const& point)
{
  return algorithms::spherical_coordinate_access<T>::latitude_as_radians(point);
}

template<typename T>
void set_longitude_from_degrees(T& point, double value)
{
  algorithms::spherical_coordinate_access<T>::set_longitude_from_degrees(point, value);
}

template<typename T>
void set_longitude_from_radians(T& point, double value)
{
  algorithms::spherical_coordinate_access<T>::set_longitude_from_radians(point, value);
}

template<typename T>
void set_latitude_from_degrees(T& point, double value)
{
  algorithms::spherical_coordinate_access<T>::set_latitude_from_degrees(point, value);
}

template<typename T>
void set_latitude_from_radians(T& point, double value)
{
  algorithms::spherical_coordinate_access<T>::set_latitude_from_radians(point, value);
}


} // namespace tracktable

#endif
