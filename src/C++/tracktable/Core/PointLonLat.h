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


#ifndef __tracktable_PointLonLat_h
#define __tracktable_PointLonLat_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/TracktableCoreWindowsHeader.h>

#include <tracktable/Core/PointBase.h>
#include <tracktable/Core/PointCartesian.h>

#include <tracktable/Core/detail/algorithm_signatures/Distance.h>
#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>
#include <tracktable/Core/detail/algorithm_signatures/Bearing.h>
#include <tracktable/Core/detail/algorithm_signatures/Extrapolate.h>
#include <tracktable/Core/detail/algorithm_signatures/SimplifyLinestring.h>
#include <tracktable/Core/detail/algorithm_signatures/SphericalCoordinateAccess.h>
#include <tracktable/Core/detail/algorithm_signatures/TurnAngle.h>


#include <tracktable/Core/detail/implementations/GenericDistance.h>
#include <tracktable/Core/detail/implementations/TurnAngle.h>
#include <tracktable/Core/detail/implementations/GreatCircleInterpolation.h>

#include <sstream>
#include <ostream>
#include <cmath>

#include <boost/geometry/geometries/register/point.hpp>
#include <boost/geometry/strategies/strategies.hpp>


namespace tracktable {

// @ingroup C++
// @{

/**
 * @class PointLonLat
 * @brief 2D point on a sphere
 *
 * This class specializes PointBase to use `boost::geometry` in a
 * spherical-equatorial coordinate system -- the familiar
 * longitude/latitude mapping onto a sphere.
 *
 */

class TRACKTABLE_CORE_EXPORT PointLonLat : public PointBase<2>
{
public:
  friend class boost::serialization::access;

  /// Convenient alias for superclass
  typedef PointBase<2> Superclass;
  typedef Superclass::coordinate_type coord_type;

  /// Create an uninitialized point
  PointLonLat() { }

  /** Create a 2D point on a sphere (convenience constructor)
   *
   * Since this class is explicitly about a point in a 2-dimensional
   * domain we provide a convenience constructor to let you
   * instantiate and populate one with one line.
   */
  PointLonLat(coord_type const& a, coord_type const& b)
    {
      this->set<0>(a);
      this->set<1>(b);
    }

  /** Create a 2D point on a sphere (convenience constructor)
   *
   * Populate the point from an array of coordinates. The caller is
   * responsible for ensuring that the array is large enough to
   * contain the right number of coordinates.
   */
  PointLonLat(const double* coordinates)
    {
      this->set<0>(coordinates[0]);
      this->set<1>(coordinates[1]);
    }

  /// Destructor for a point
  ~PointLonLat() { }

  /// Make this point a copy of a generic 2D point
  PointLonLat(Superclass const& other)
    {
      detail::assign_coordinates<2>::apply(*this, other);
    }

  /// Make this point a copy of another
  PointLonLat(PointLonLat const& other)
    {
      this->set_latitude(other.latitude());
      this->set_longitude(other.longitude());
    }

  /** Return this point's longitude.
   *
   * @return Longitude in degrees
   */
  coord_type longitude() const { return this->get<0>(); }

  /** Set this point's longitude.
   *
   * @param [in] new_longitude   New value for longitude
   */
  void set_longitude(coord_type const& new_longitude)
    {
      this->set<0>(new_longitude);
    }

  /** Return this point's latitude.
   *
   * @return Latitude in degrees
   */
  coord_type latitude() const { return this->get<1>(); }

  /** Set this point's latitude.
   *
   * @param [in] new_latitude   New value for latitude
   */
  void set_latitude(coord_type const& new_latitude)
    {
      this->set<1>(new_latitude);
    }

  /** Convert point coordinates to a string
   *
   * @return Coordinates string
   */
  std::string to_string() const
    {
    std::ostringstream outbuf;
    outbuf << "(" << this->longitude() << ", " << this->latitude() << ")";
    return outbuf.str();
    }

private:
  /** Serialize the coordinates to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
  {
    ar & boost::serialization::make_nvp("Coordinates", this->Coordinates);
  }
};


} // namespace tracktable

/** Write a point to a stream as a string
 *
 * @param [in] os Stream to write to
 * @param [in] pt Point to write to string
 */
TRACKTABLE_CORE_EXPORT std::ostream&
operator<<(std::ostream& os, tracktable::PointLonLat const& pt);

// This macro call registers this point class for use with
// boost::geometry. We have to do this before we define any of our
// own traits.

BOOST_GEOMETRY_REGISTER_POINT_2D_GET_SET(
  tracktable::PointLonLat,
  tracktable::settings::point_coordinate_type,
  boost::geometry::cs::spherical_equatorial<boost::geometry::degree>,
  longitude, latitude,
  set_longitude, set_latitude
)


namespace tracktable { namespace traits {

template<>
struct tag<tracktable::PointLonLat>
{
  typedef base_point_tag type;
};

template<>
struct dimension<PointLonLat> : dimension<PointLonLat::Superclass> {};

template<>
struct point_domain_name<PointLonLat>
{
  static inline string_type apply()
    {
      return "generic_lonlat";
    }
};

template<>
struct undecorated_point<PointLonLat>
{
  typedef PointLonLat type;
};

template<>
struct domain<PointLonLat>
{
  typedef domains::generic type;
};



} } // close namespace tracktable::traits



// ----------------------------------------------------------------------
//
// ALGORITHMS
//
// Here are the implementations for the common algorithms we want to
// run on points. These are set up by the #includes at the top of the
// file that reach into detail/algorithm_signatures.
//
// ----------------------------------------------------------------------

namespace tracktable { namespace algorithms {

// Distance is not defined here because as a member of the generic
// point domain we inherit the definition in PointBase.h.

// The signed turn angle is defined so that a right turn is positive.

template<>
struct signed_turn_angle<PointLonLat>
{
  static inline double apply(
    PointLonLat const& a, PointLonLat const& b, PointLonLat const& c
    )
    {
      typedef boost::geometry::coordinate_system<PointLonLat>::type coordinate_system;
      return implementations::signed_turn_angle<coordinate_system, 2>::apply(a, b, c);
    }
};

// You may well ask why we've got a templated apply method here when
// we're talking about the PointLonLat class. The reason is that
// we're not just implementing this for PointLonLat but for subclasses
// that behave like PointLonLat. The template lets us construct and
// turn whatever point type we're asked for instead of just
// PointLonLat.

template<>
struct interpolate<PointLonLat> : implementations::great_circle_interpolate
{ };

template<>
struct extrapolate<PointLonLat> : implementations::great_circle_interpolate
{ };

// ----------------------------------------------------------------------

template<>
struct bearing<PointLonLat>
{
  inline static double apply(PointLonLat const& from, PointLonLat const& to)
    {
      typedef boost::geometry::traits::coordinate_system<PointLonLat>::type coord_system;
      return implementations::bearing<coord_system>::apply(from, to);
    }
};

template<>
struct simplify_linestring<PointLonLat>
{
  template<typename linestring_type>
  static inline void apply(linestring_type const& input,
                           linestring_type& result,
                           double tolerance)
    {
      // Since we measure distances for PointLonLat in kilometers, we
      // have to convert back to degrees before we call the real
      // simplify(). Note that here we use degrees and NOT radians
      // since the coordinate system is
      // boost::geometry::cs<spherical_equatorial<degree>>.
      double tolerance_in_radians = tolerance / tracktable::conversions::constants::EARTH_RADIUS_IN_KM;
      double tolerance_in_degrees = tolerance_in_radians * tracktable::conversions::constants::DEGREES_PER_RADIAN;
      boost::geometry::simplify(input, result, tolerance_in_degrees);
    }
};

// ----------------------------------------------------------------------

// ----------------------------------------------------------------------
//
// Coordinate access for spherical point
//
// PointLonLat stores its coordinates in degrees.
//
// ----------------------------------------------------------------------

template<>
struct spherical_coordinate_access<PointLonLat>
{
  typedef PointLonLat point_type;

  static inline double longitude_as_degrees(point_type const& p)
    {
      return p.longitude();
    }
  static inline double latitude_as_degrees(point_type const& p)
    {
      return p.latitude();
    }
  static inline double longitude_as_radians(point_type const& p)
    {
      return conversions::radians(p.longitude());
    }
  static inline double latitude_as_radians(point_type const& p)
    {
      return conversions::radians(p.latitude());
    }

  static inline void set_longitude_from_degrees(point_type & p, double value)
    {
      p.set_longitude(value);
    }

  static inline void set_latitude_from_degrees(point_type & p, double value)
    {
      p.set_latitude(value);
    }

  static inline void set_longitude_from_radians(point_type & p, double value)
    {
      p.set_longitude(conversions::degrees(value));
    }

  static inline void set_latitude_from_radians(point_type & p, double value)
    {
      p.set_latitude(conversions::degrees(value));
    }
};


} } // exit namespace tracktable::algorithms


#endif
