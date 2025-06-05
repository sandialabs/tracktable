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

// How to compute turn angles in different coordinate systems.

#include <tracktable/Core/Conversions.h>
#include <boost/geometry/arithmetic/arithmetic.hpp>
#include <boost/geometry/core/cs.hpp>
#include <cmath>

#include <boost/mpl/assert.hpp>

namespace {

template<class PointT>
inline double bearing_to(
  PointT const& start,
  PointT const& finish
  )
{
  using tracktable::conversions::degrees;
  using tracktable::conversions::radians;

  double lon1(radians(start.longitude()));
  double lat1(radians(start.latitude()));
  double lon2(radians(finish.longitude()));
  double lat2(radians(finish.latitude()));

  double bearing = atan2( sin(lon2-lon1) * cos(lat2),
                          cos(lat1) * sin(lat2) -
                          sin(lat1) * cos(lat2) * cos(lon2 - lon1) );

  bearing = degrees(bearing) + 360.0;
  return fmod(bearing, 360.0);
}


inline double dot(const double ab[3], const double bc[3])
{
  return (ab[0] * bc[0] + ab[1] * bc[1] + ab[2] * bc[2]);
}

inline double magnitude(const double p[3])
{
  return sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]);
}

#if 0
void normalize(double p[3])
{
}
#endif


}

namespace tracktable { namespace algorithms { namespace implementations {

// ----------------------------------------------------------------------

// NOTE: This is *not* the same as the struct signed_turn_angle in
// tracktable::traits.  This is specialized on coordinate system (type
// and dimension) so that different point classes can call it as long
// as the coordinate systems match.

template<typename cs_type, int dimension>
struct signed_turn_angle
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(cs_type)==0,
    TURN_ANGLES_NOT_DEFINED_IN_THIS_COORDINATE_SYSTEM,
    (types<cs_type>)
    );
};

// ----------------------------------------------------------------------

template<>
struct signed_turn_angle<
  boost::geometry::cs::spherical_equatorial<
    boost::geometry::degree
    >,
  2
  >
{
  template<class PointT>
  inline static double apply(PointT const& a, PointT const& b, PointT const& c)
    {
      double ab_bearing = ::bearing_to(a, b);
      double bc_bearing = ::bearing_to(b, c);

      // Both of those values are between 0 and 360.  Bare subtraction
      // will get us a value between -360 and 360.
      double turn = bc_bearing - ab_bearing;
      if (turn > 180)
        {
        turn -= 360;
        }
      else if (turn < -180)
        {
        turn += 360;
        }
      return turn;
    }
};

// ----------------------------------------------------------------------

template<>
struct signed_turn_angle<boost::geometry::cs::cartesian, 2>
{
  static inline void normalize(double p[3])
    {
      double mag = ::magnitude(p);
      if (std::abs(mag) < 1e-5) return;
      p[0] /= mag;
      p[1] /= mag;
      p[2] /= mag;
    }

  template<class PointT>
  double operator()(PointT const& a, PointT const& b, PointT const& c)
    {
      double ab[3], bc[3];

      ab[0] = b.template get<0>() - a.template get<0>();
      ab[1] = b.template get<1>() - a.template get<1>();
      ab[2] = 0;

      bc[0] = c.template get<0>() - a.template get<0>();
      bc[1] = c.template get<1>() - a.template get<1>();
      bc[2] = 0;

      normalize(ab);
      normalize(bc);
      double angle_in_radians = acos(::dot(ab, bc));
      double cross_z_component = ab[1] * bc[2] - ab[2] * bc[1];
      if (cross_z_component < 0)
        {
        return -angle_in_radians;
        }
      else if (cross_z_component > 0)
        {
        return angle_in_radians;
        }
      else
        {
        return 0;
        }
    }
};


template<class CoordSystemT>
struct bearing
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(CoordSystemT)==0,
    BEARING_NOT_DEFINED_IN_THIS_COORDINATE_SYSTEM,
    (types<CoordSystemT>)
    );
};

template<>
struct bearing<
  boost::geometry::cs::spherical_equatorial<
  boost::geometry::degree
    >
  >
{
  template<class PointT>
  inline static double apply(PointT const& start, PointT const& finish)
    {
      using tracktable::conversions::degrees;
      using tracktable::conversions::radians;

      double lon1(radians(start.longitude()));
      double lat1(radians(start.latitude()));
      double lon2(radians(finish.longitude()));
      double lat2(radians(finish.latitude()));

      double bearing = atan2( sin(lon2-lon1) * cos(lat2),
                              cos(lat1) * sin(lat2) -
                              sin(lat1) * cos(lat2) * cos(lon2 - lon1) );


      bearing += 2.0 * ::tracktable::conversions::constants::PI;
      bearing = degrees(bearing) + 360.0;
      return fmod(bearing, 360.0);
    }
};


template<>
struct bearing<
  boost::geometry::cs::cartesian
  >
{
  template<class PointT>
  inline static double apply(PointT const& start, PointT const& finish)
    {
      double dx, dy;
      dx = finish.template get<0>() - start.template get<0>();
      dy = finish.template get<1>() - start.template get<1>();

      return atan2( dy, dx );
    }
};

} } } // namespace tracktable::algorithms::implementations
