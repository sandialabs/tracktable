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
 * Terrestrial Domain - objects on the surface of the Earth
 *
 * When we reason about objects on the surface of the Earth we use
 * human-scale measurements such as kilometers for distance, square
 * kilometers for area, and km per hour for speed. Point and
 * trajectory types in the Terrestrial domain adhere to these
 * standards.
 *
 * TODO: The following statement implies that altitude is included whiich not accurate?
 * We also provide the 'altitude' trait for terrestrial trajectory
 * points. We recommend that you use altitude values measured in
 * meters wherever possible. However, we acknowledge that the
 * international standard of describing aircraft altitudes in feet (or
 * hundreds of feet) may make that a more convenient scale.
 */

#ifndef tracktable_domain_Terrestrial_h
#define tracktable_domain_Terrestrial_h

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Conversions.h>
#include <tracktable/Core/Box.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>

#include <tracktable/Domain/DomainMacros.h>
#include <tracktable/Domain/Cartesian3D.h>

#include <tracktable/RW/PointReader.h>
#include <tracktable/RW/TrajectoryReader.h>

#include <boost/geometry/algorithms/length.hpp>

#include <vector>
#include <iostream>
#include <string>

#include <tracktable/Domain/TracktableDomainWindowsHeader.h>

typedef tracktable::domain::cartesian3d::CartesianPoint3D CartesianPoint3D;

// ----------------------------------------------------------------------
//
// Part 1: Instantiate the classes for this domain.
//
// These are TerrestrialPoint, TerrestrialTrajectoryPoint and
// TerrestrialTrajectory. These classes are almost entirely
// boilerplate.
//
// Once we've defined them we alias them to base_point_type,
// trajectory_point_type and trajectory_type respectively.
//
// ----------------------------------------------------------------------

namespace tracktable { namespace domain { namespace terrestrial {

enum class AltitudeUnits {
  FEET,
  METERS,
  KILOMETERS,
};

/** An exception to be used when a property cannot be found */
class PropertyDoesNotExist : public std::runtime_error {
 public:
  PropertyDoesNotExist(std::string _property) : std::runtime_error(_property) {}
};

/**
 * @class TerrestrialPoint
 * @brief 2D point on a sphere
 *
 * This class represents a point on a sphere. Its coordinates are
 * measured in degrees of longitude and latitude.
 *
 * Distances between `TerrestrialPoints` are measured in kilometers.
 * Speeds between two `TerrestrialTrajectoryPoints` will be measured in
 * kilometers per hour.
 */

class TerrestrialPoint : public PointLonLat
{
public:
  friend class boost::serialization::access;
  using Superclass = PointLonLat;

  /// Create an uninitialized point
  TerrestrialPoint() = default;

  /** Copy constructor: make this point like another
   *
   * @param [in] other Const point to make a copy of
   */
  TerrestrialPoint(TerrestrialPoint const& other) = default;

  /** Copy constructor: make this point like another
   *
   * @param [in] other Const point to make a copy of
   */
  TerrestrialPoint(TerrestrialPoint&& other) = default;

  /** Copy constructor: use PointLonLat instances as if they were TerrestrialPoint instances
   *
   * @param [in] other Const point to make a copy of
   */
  TerrestrialPoint(Superclass const& other) : PointLonLat(other) {}

  /// Empty destructor - nothing to do here
  ~TerrestrialPoint() override = default;

  /// Explicitly delegate assignment to prevent compiler hijinks
  TerrestrialPoint& operator=(TerrestrialPoint const& other) {
    this->Superclass::operator=(other);
    return *this;
  }
  TerrestrialPoint& operator=(TerrestrialPoint&& other) = default;

  /** Convenience constructor.
   *
   * @param [in] _longitude Longitude in degrees
   * @param [in] _latitude  Latitude in degrees
   */
  TerrestrialPoint(double _longitude, double _latitude) {
    this->set_longitude(_longitude);
    this->set_latitude(_latitude);
  }

  /** Serialize the points to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template <class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/) {
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
  }

  /** Returns ECEF values for lon, lat, and altitude. Uses a km convention.
   *
   * @note this expects an altitude in km (not ft or m).
   *
   * @param [in] _longitude Longitude in degrees
   * @param [in] _latitude Latitude in degrees
   * @param [in] _altitude Altitude in km
   *
   * @return 3D Earth Centered, Earth Fixed point in km
   */
  static CartesianPoint3D ECEF_from_km(const coord_type _longitude, const coord_type _latitude,
                                const double _altitude) {
    constexpr double a = 6378.137;
    constexpr double e2 = 8.1819190842622e-2 * 8.1819190842622e-2;
    const auto sinLatitude = sin(_latitude);
    const auto n = a / sqrt((1.0 - e2 * sinLatitude * sinLatitude));
    const auto NAC = (n + _altitude) * cos(_latitude);
    coord_type pt[3];
    pt[0] = NAC * cos(_longitude);
    pt[1] = NAC * sin(_longitude);
    pt[2] = (n * (1.0 - e2) + _altitude) * sinLatitude;
    return CartesianPoint3D(pt);
  }
};

// ----------------------------------------------------------------------

// If you write libraries for Microsoft platforms you will have to
// care about this warning sooner or later. Warning #4251 says
// "This type must have a DLL interface in order to be used by
// clients of <class>". After you dig through the layers, this
// ends up meaning "You cannot use STL classes in the interface of a
// method or function if you expect your library to work with any
// compiler other than the one you're using right now."
//
// This is a symptom of a bigger problem. Since the STL does not have
// a single standard implementation (for good reason) you cannot assume
// that my std::map is the same on the inside as your std::map. Idioms
// such as PIMPL are one approach to minimizing the impact.
//
// The bottom line is that yea, verily, you cannot use STL classes as
// arguments or return values in your library's interface unless it will
// only ever be used by the same compiler that built it. We are going to
// proclaim that this is the case for Tracktable and put great big warnings
// in the developer documentation to that effect.
//
// Meanwhile, we use #pragma warning(disable) to hush the compiler up
// so that people who just want to use the library don't have to care
// about the arcana of __declspec(dllimport) and friends.

#if defined(WIN32)
# pragma warning( push )
# pragma warning( disable : 4251 )
#endif

class TerrestrialTrajectoryPoint : public TrajectoryPoint<TerrestrialPoint>
{
public:
  friend class boost::serialization::access;

  using Superclass = TrajectoryPoint<TerrestrialPoint>;

  /// Create an uninitialized point
  TerrestrialTrajectoryPoint() = default;

    /** Copy constructor: make this point like another
   *
   * @param [in] other Const point to make a copy of
   */
  TerrestrialTrajectoryPoint(TerrestrialTrajectoryPoint const& other) = default;

    /** Copy constructor: make this point like another
   *
   * @param [in] other Point to make a copy of
   */
  TerrestrialTrajectoryPoint(TerrestrialTrajectoryPoint&& other) = default;

  /** Copy constructor: use PointLonLat instances as if they were TerrestrialTrajectoryPoint instances
   *
   * @param [in] other Const point to make a copy of
   */
  TerrestrialTrajectoryPoint(Superclass const& other)
    : Superclass(other)
    { }

  /// Empty destructor: nothing to do here.
  ~TerrestrialTrajectoryPoint() override = default;

  /// Explicitly delegate assignment to prevent compiler hijinks.
  TerrestrialTrajectoryPoint& operator=(TerrestrialTrajectoryPoint const& other) {
    this->Superclass::operator=(other);
    return *this;
  }
  TerrestrialTrajectoryPoint& operator=(TerrestrialTrajectoryPoint&& other) = default;

  /** Convenience constructor.
   *
   * @param [in] _longitude Longitude in degrees
   * @param [in] _latitude  Latitude in degrees
   */
  TerrestrialTrajectoryPoint(double _longitude, double _latitude) {
    this->set_longitude(_longitude);
    this->set_latitude(_latitude);
  }

  /** @name Earth Centered Earth Fixed
   * This group of functions is useful for converting longitude and latitude to a
   * cartesian point. A static method is provided to convert any arbitrary point.
   * `ECEF_from_feet` will be the most common use case. Multiple functions will throw
   * an exception if altitude is not present. To bypass exception throws, use `ECEF(ratio,altString)`
   * with the appropriate ratio to convert to km and the name of the property you
   * are expecting to find altitude in.
   * @sa TerrestrialPoint::ECEF
   * @{
   */

  /** Returns ECEF values for lon/lat points. Uses a km convention.
   *
   * @note this expects an altitude in km (not ft or m).
   *
   * @param _altitudeString The label of the property that contains altitude
   * @param _unit The units the altitude contains
   * @return 3D Earth Centered, Earth Fixed point in km
   */
  //TODO: redo python binding
  CartesianPoint3D ECEF(const std::string& _altitudeString = "",
                        const AltitudeUnits _unit = AltitudeUnits::KILOMETERS) const {
    if (AltitudeUnits::KILOMETERS == _unit) {
      return ECEF_from_kilometers(_altitudeString);
    }
    if (AltitudeUnits::METERS == _unit) {
      return ECEF_from_meters(_altitudeString);
    }
    return ECEF_from_feet(_altitudeString);
  }

  /** Returns ECEF values for lon/lat points. Uses a km convention.
   *
   * @note this expects an altitude in km (not ft or m). Change ratio if the altitude is not km
   *
   * @param [in] ratio The value to multiply altitude by to get km
   * @param [in] _altitudeString The label of the property that contains altitude
   *
   * @return 3D Earth Centered, Earth Fixed point in km
   *
   * @throw PropertyDoesNotExist if we can't find altitude
   */
  CartesianPoint3D ECEF(const double ratio, const std::string& _altitudeString) const {
    double altitude;
    bool ok = false;
    if (_altitudeString.length() != 0)
    {
      altitude = ratio * this->real_property(_altitudeString, &ok);
      if (!ok) {
        throw PropertyDoesNotExist(_altitudeString);
      }
    } else {
      altitude = 0.0;
    }
    coord_type longitude = conversions::radians(this->get<0>());
    coord_type latitude = conversions::radians(this->get<1>());
    return TerrestrialPoint::ECEF_from_km(longitude, latitude, altitude);
  }

  /** Returns ECEF values for lon/lat points. Uses a km convention.
   *
   * @note  this expects an altitude in feet.
   *
   * @param [in] _altitudeString The label of the property that contains altitude
   *
   * @return 3D Earth Centered, Earth Fixed point in km
   *
   * @throw PropertyDoesNotExist if we can't find altitude
   */
  CartesianPoint3D ECEF_from_feet(const std::string& _altitudeString = "altitude") const {
    // NOTE: Potential for this number ratio to be slightly different between
    // machines of differing precisions.
    constexpr auto feetToKilometers = 1.0 / 3280.839895013123;
    return ECEF(feetToKilometers, _altitudeString);
  }

  /** Returns ECEF values for lon/lat points. Uses a km convention.
   *
   * @note this expects an altitude in meters.
   *
   * @param [in] _altitudeString The label of the property that contains altitude
   *
   * @return 3D Earth Centered, Earth Fixed point in km
   *
   * @throw PropertyDoesNotExist if we can't find altitude
   */
  CartesianPoint3D ECEF_from_meters(const std::string& _altitudeString = "altitude") const {
    constexpr auto metersToKilometers = 1.0 / 1000.0;
    return ECEF(metersToKilometers, _altitudeString);
  }

  /** Returns ECEF values for lon/lat points. Uses a km convention.
   *
   * @note this expects an altitude in kilometers.
   *
   * @param [in] _altitudeString The label of the property that contains altitude
   *
   * @return 3D Earth Centered, Earth Fixed point in km
   *
   * @throw PropertyDoesNotExist if we can't find altitude
   */
  //TODO: python binding
  CartesianPoint3D ECEF_from_kilometers(const std::string& _altitudeString = "altitude") const {
    return ECEF(1.0, _altitudeString);
  }
  /// @}

private:
  /** Serialize the points to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<class Archive>
  void serialize(Archive& ar, const unsigned int  /*version*/)
  {
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
  }

};

#if defined(WIN32)
# pragma warning( pop )
#endif

using base_point_type = TerrestrialPoint;
using linestring_type = std::vector<base_point_type>;
using trajectory_point_type = TerrestrialTrajectoryPoint;
using trajectory_type = Trajectory<trajectory_point_type>;
using base_point_reader_type = PointReader<base_point_type>;
using trajectory_point_reader_type = PointReader<trajectory_point_type>;
using trajectory_reader_type = TrajectoryReader<trajectory_type>;
using box_type = boost::geometry::model::box<base_point_type>;

TRACKTABLE_DOMAIN_EXPORT std::ostream& operator<<(std::ostream& out, base_point_type const& pt);

TRACKTABLE_DOMAIN_EXPORT std::ostream& operator<<(std::ostream& out, trajectory_point_type const& pt);

} } } // namespace tracktable::domain::terrestrial


#ifndef DOXYGEN_SHOULD_SKIP_THIS

// ----------------------------------------------------------------------
//
// TRAITS FOR TERRESTRIAL OBJECTS
//
// ----------------------------------------------------------------------


namespace tracktable { namespace traits {

namespace domains {
  struct terrestrial { };
}

template<>
struct point_domain_name<tracktable::domain::terrestrial::TerrestrialPoint>
{
  static inline string_type apply() { return "terrestrial"; }
};

} }

// ----------------------------------------------------------------------
// BOOST GEOMETRY REGISTRATION
// ----------------------------------------------------------------------

// boost::geometry

TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS(
  tracktable::domain::terrestrial::TerrestrialPoint,
  tracktable::PointLonLat
  )

TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS(
  tracktable::domain::terrestrial::TerrestrialTrajectoryPoint,
  tracktable::TrajectoryPoint< tracktable::domain::terrestrial::TerrestrialPoint >
  )

TRACKTABLE_DELEGATE_BASE_POINT_TRAITS(
  tracktable::domain::terrestrial::TerrestrialPoint,
  tracktable::PointLonLat
  )

TRACKTABLE_DELEGATE_TRAJECTORY_POINT_TRAITS(
  tracktable::domain::terrestrial::TerrestrialTrajectoryPoint,
  tracktable::TrajectoryPoint<tracktable::domain::terrestrial::TerrestrialPoint>
  )

// ----------------------------------------------------------------------
// TRACKTABLE POINT ALGORITHMS FOR BASE POINT
// ----------------------------------------------------------------------

namespace tracktable { namespace algorithms {

// Distance between points is measured in km, not radians
template<>
struct distance<
  ::tracktable::traits::domains::terrestrial
  >
{
  template<typename Geom1, typename Geom2>
  static inline double apply(Geom1 const& from, Geom2 const& to)
    {
      double distance_in_radians = boost::geometry::distance(from, to);
      return conversions::radians_to_km(distance_in_radians);
    }
};


// Speed between points is measured in km/hr, not radians/sec
template<>
struct speed_between<tracktable::domain::terrestrial::TerrestrialTrajectoryPoint>
{
  using base_point_type = tracktable::domain::terrestrial::TerrestrialPoint;
  using point_type = tracktable::domain::terrestrial::TerrestrialTrajectoryPoint;

  inline static double apply(point_type const& from, point_type const& to)
    {
      double distance_traveled = tracktable::distance(from, to);
      double seconds_elapsed = static_cast<double>((to.timestamp() - from.timestamp()).total_seconds());
      // Returns 0 if division by 0 could be a problem
      if (tracktable::almost_zero(seconds_elapsed))
        {
        return 0;
        }
      else
        {
        return 3600.0 * distance_traveled / seconds_elapsed;
        }
    }
};

// All of the other algorithms are the defaults. These macros
// make it cleaner to express that.


#define TT_DOMAIN tracktable::domain::terrestrial

#define TT_DELEGATE_BASE_POINT_ALGORITHM(ALGORITHM) \
TRACKTABLE_DELEGATE( \
  TT_DOMAIN::TerrestrialPoint, \
  PointLonLat, \
  ALGORITHM \
)

#define TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(ALGORITHM) \
TRACKTABLE_DELEGATE( \
TT_DOMAIN::TerrestrialTrajectoryPoint, \
TrajectoryPoint<TT_DOMAIN::TerrestrialPoint>, \
ALGORITHM \
)

#define TT_DELEGATE_TRAJECTORY_ALGORITHM(ALGORITHM) \
TRACKTABLE_DELEGATE( \
TT_DOMAIN::TerrestrialTrajectory, \
Trajectory<TT_DOMAIN::TerrestrialTrajectoryPoint>, \
ALGORITHM \
)

TT_DELEGATE_BASE_POINT_ALGORITHM(interpolate)
TT_DELEGATE_BASE_POINT_ALGORITHM(extrapolate)
TT_DELEGATE_BASE_POINT_ALGORITHM(bearing)
TT_DELEGATE_BASE_POINT_ALGORITHM(signed_turn_angle)
TT_DELEGATE_BASE_POINT_ALGORITHM(spherical_coordinate_access)
TT_DELEGATE_BASE_POINT_ALGORITHM(unsigned_turn_angle)

TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(interpolate)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(extrapolate)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(bearing)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(signed_turn_angle)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(spherical_coordinate_access)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(unsigned_turn_angle)

template<>
struct length<tracktable::domain::terrestrial::trajectory_type>
{
  using trajectory_type = tracktable::domain::terrestrial::trajectory_type;

  inline static double apply(trajectory_type const& trajectory)
    {
      return tracktable::conversions::radians_to_km(boost::geometry::length(trajectory));
    }
};


} } // exit namespace tracktable::algorithms

TRACKTABLE_DELEGATE_POINT_DOMAIN_NAME_TRAIT(tracktable::domain::terrestrial)
TRACKTABLE_DELEGATE_DOMAIN_TRAIT(tracktable::domain::terrestrial, tracktable::traits::domains::terrestrial)

#undef TT_DOMAIN
#undef TT_DELEGATE_BASE_POINT_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_POINT_TRAIT

#endif // DOXYGEN_SHOULD_SKIP_THIS

#endif
