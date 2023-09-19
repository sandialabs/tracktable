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

#ifndef __tracktable_TrajectoryPoint_h
#define __tracktable_TrajectoryPoint_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/PointBase.h>

#include <tracktable/Core/detail/trait_signatures/HasObjectId.h>
#include <tracktable/Core/detail/trait_signatures/HasProperties.h>
#include <tracktable/Core/detail/trait_signatures/HasTimestamp.h>
#include <tracktable/Core/detail/trait_signatures/ObjectId.h>
#include <tracktable/Core/detail/trait_signatures/Tag.h>
#include <tracktable/Core/detail/trait_signatures/Timestamp.h>
#include <tracktable/Core/detail/trait_signatures/PointDomainName.h>

#include <tracktable/Core/detail/algorithm_signatures/Bearing.h>
#include <tracktable/Core/detail/algorithm_signatures/Distance.h>
#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>
#include <tracktable/Core/detail/algorithm_signatures/Extrapolate.h>
#include <tracktable/Core/detail/algorithm_signatures/SimplifyLinestring.h>
#include <tracktable/Core/detail/algorithm_signatures/SpeedBetween.h>
#include <tracktable/Core/detail/algorithm_signatures/SphericalCoordinateAccess.h>
#include <tracktable/Core/detail/algorithm_signatures/TurnAngle.h>

#include <ostream>
#include <cassert>

#include <boost/mpl/bool.hpp>
#include <boost/geometry/strategies/strategies.hpp>
#include <boost/serialization/map.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/variant.hpp>

namespace tracktable {

/**
 * @class TrajectoryPoint
 * @brief Add object ID, timestamp, property map
 *
 * This class will add trajectory properties (a timestamp, an object
 * ID and storage for named properties) to any point class.
 *
 * Timestamp is a `tracktable::Timestamp` which (under the hood) is a
 * `boost::posix_time::ptime`. Object ID is stored as a string.

 * We also include an interface to set, get and enumerate arbitrary
 * named properties. The only restriction is that the types of these
 * properties are limited to timestamps, floating-point numbers and
 * strings. If you need something more flexible than that please
 * consider creating your own alternative point class either by
 * subclassing TrajectoryPoint or by composition.
 *
 * @note Named property support is implemented using `boost::variant`.
 *       You can either use `boost::get<>` to cast it to your desired
 *       data type or call one of the `(type)_property_value`
 *       functions to retrieve it with no casting necessary. Take a
 *       look at tracktable/Core/Tests/test_trajectory_point_lonlat.cpp (XXX CHECK
 *       THIS) for a demonstration.
 */

#if defined(WIN32)
# pragma warning( push )
# pragma warning( disable : 4251 )
#endif

template<class BasePointT>
class TrajectoryPoint : public BasePointT
{
public:
  typedef BasePointT Superclass;
  friend class boost::serialization::access;

  /// Instantiate an uninitialized point
  TrajectoryPoint()
    : Superclass()
    ,CurrentLength(-1)
    ,ObjectId("")
    ,UpdateTime(tracktable::BeginningOfTime)
    {
    }

  /// Destructor for a trajectory point
  virtual ~TrajectoryPoint()
    {
    }

  /** Copy contructor, create a TrajectoryPoint with a copy of another
   *
   * @param [in] other TrajectoryPoint to copy from
   */
  TrajectoryPoint(TrajectoryPoint const& other)
    : Superclass(other)
    ,CurrentLength(other.CurrentLength)
    ,ObjectId(other.ObjectId)
    ,Properties(other.Properties)
    ,UpdateTime(other.UpdateTime)
    {
    }

  /** Instantiate a TrajectoryPoint with a base point
   *
   * @param [in] other Basepoint
   */
  TrajectoryPoint(Superclass const& other)
    : Superclass(other)
    {
    }

  /** Instantiate TrajectoryPoint using specified coordniates
   *
   * @param [in] coords Coordinates to set in point
   */
  TrajectoryPoint(const double* coords)
    : Superclass(coords)
    { }

  /** Assign a TrajectoryPoint to the value of another.
   *
   * @param [in] other TrajectoryPoint to assign value of
   * @return TrajectoryPoint with the new assigned value
   */
  TrajectoryPoint operator=(TrajectoryPoint const& other)
    {
      this->Superclass::operator=(other);
      this->CurrentLength = other.CurrentLength;
      this->ObjectId = other.ObjectId;
      this->Properties = other.Properties;
      this->UpdateTime = other.UpdateTime;
      return *this;
    }


  /** Check two points for equality
   *
   * Two TrajectoryPoints are equal if and only if they have:
   *    * the same coordinates (base point)
   *    * the same object ID
   *    * the same timestamp
   *    * the same user-defined properties
   *
   * @param [in] other TrajectoryPoint to assign value of
   */
  bool operator==(TrajectoryPoint const& other) const
    {
      return ( this->Superclass::operator==(other)
               // && this->CurrentLength == other.CurrentLength
               && this->ObjectId == other.ObjectId
               && this->Properties == other.Properties
               && this->UpdateTime == other.UpdateTime
        );
    }

  /** Check whether two TrajectoryPoint are unequal.
   *
   * @param [in] other TrajectoryPoint for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(TrajectoryPoint const& other) const
    {
      return ( (*this == other) == false );
    }

  /**
   * @return This point's object ID
   */
  std::string object_id() const { return this->ObjectId; }

  /**
   * @return This point's timestamp
   */
  Timestamp timestamp() const { return this->UpdateTime; }

  /** Set this point's object ID
   *
   * @param [in] new_id  ID to assign to object
   */
  void set_object_id(std::string const& new_id) { this->ObjectId = new_id; }

  /** Set this point's timestamp
   *
   * @param [in] ts  timestamp to assign to object
   */
  void set_timestamp(Timestamp const& ts) { this->UpdateTime = ts; }

  /** Set a named property with a variant value (let the caller handle the type)
   *
   * @param [in] name  Name of property
   * @param [in] name  Value to assign to property
   */
  void set_property(std::string const& name, PropertyValueT const& value)
    {
      ::tracktable::set_property(this->Properties, name, value);
    }

  /** Retrieve a named property with checking
   *
   * @param [in] name Name of property to retrieve
   * @param [in] ok If specified, this will be set to true or false as the property is found/not found
   * @return Property as a `boost::variant`
   */
  PropertyValueT property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::property(this->Properties, name, ok);
    }

  /** Retrieve a named property or a default value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] default_value Value to return if property is not present
   * @return Property as a `boost::variant`
   */
  PropertyValueT property(std::string const& name, PropertyValueT const& default_value) const
    {
      return ::tracktable::property_with_default(this->Properties, name, default_value);
    }

  /** Retrieve a named property without safety checking
   *
   * It is the caller's responsibility to know whether the requested
   * property actually exists when using this function.
   *
   * @param [in] name Name of property to retrieve
   * @return Property as a `boost::variant`
   */
  PropertyValueT property_without_checking(std::string const& name) const
    {
      bool ok;
      return ::tracktable::property(this->Properties, name, &ok);
    }

  /** Safely retrieve a named property with a string value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] ok If specified, this will be set to true or false as the property is found/not found
   * @return Property as a `std::string`
   */
  std::string string_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::string_property(this->Properties, name, ok);
    }

  /** Safely retrieve a named property with a floating-point value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] ok If specified, this will be set to true or false as the property is found/not found
   * @return Property as a `double`
   */
  double real_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::real_property(this->Properties, name, ok);
    }

  /** Safely retrieve a named property with a timestamp value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] ok If specified, this will be set to true or false as the property is found/not found
   * @return Property as a `Timestamp`
   */
  Timestamp timestamp_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::timestamp_property(this->Properties, name, ok);
    }

  /** Safely retrieve a named property with a string value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] default_value String value to return if property is not present
   * @return Property as a `std::string`
   */
  std::string string_property_with_default(std::string const& name, std::string const& default_value) const
    {
      return ::tracktable::string_property_with_default(this->Properties, name, default_value);
    }

  /** Safely retrieve a named property with a floating-point value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] default_value Double value to return if property is not present
   * @return Property as a `double`
   */
  double real_property_with_default(std::string const& name, double default_value) const
    {
      return ::tracktable::real_property_with_default(this->Properties, name, default_value);
    }


  /** Safely retrieve a named property with a timestamp value
   *
   * @param [in] name Name of property to retrieve
   * @param [in] default_value Timestamp value to return if property is not present
   * @return Property as a `Timestamp`
   */
  Timestamp timestamp_property_with_default(std::string const& name, Timestamp const& default_value) const
    {
      return ::tracktable::timestamp_property_with_default(this->Properties, name, default_value);
    }

  /** Check whether a property is present
   *
   * @param [in] name Name of desired property
   * @return `True` if present, `False` if not
   */
  bool has_property(std::string const& name) const
    {
      return ::tracktable::has_property(this->Properties, name);
    }

  /** Convert point to a human-readable string form
   *
   * @return The string representation of the point
   */
  std::string to_string() const
    {
      std::ostringstream outbuf;
      imbue_stream_with_timestamp_output_format(outbuf, default_timestamp_output_format());

      outbuf << "[";
      outbuf << this->object_id() << "@ ";
      outbuf << this->timestamp() << ": ";
      outbuf << this->Superclass::to_string();
      outbuf << " ";
      outbuf << property_map_to_string(this->Properties);
      outbuf << "]";
      return outbuf.str();
    }

  /** Get length of trajectory up to this point
   *
   * When we build a trajectory this property will be set to the total
   * length of the trajectory up to this point. This will be 0 at the
   * very first point and some non-negative value thereafter.
   *
   * The initial value of current_length is -1 to indicate that it is
   * not yet set.
   *
   * @return Trajectory length so far
   */
  double current_length() const
    {
      return this->CurrentLength;
    }

  /** Set length of trajectory up to this point
   *
   * You will almost certainly not need to call this method yourself.
   * It is the responsibility of the Trajectory class to compute and
   * set the lengths.
   *
   * @param length Length up to this point
   */
  void set_current_length(double length)
    {
      this->CurrentLength = length;
    }

  /** Get fraction of total length of trajectory up to this point
   *
   * When we build a trajectory this property will be set to the
   * fraction of length of the trajectory up to this point. This
   * will be 0.0 at the very first point and range up to 1.0
   * thereafter.
   *
   * The initial value of `current_length_fraction` is -1.0 to indicate that it is
   * not yet set.
   *
   * @return fraction of Trajectory length so far
   */
  double current_length_fraction() const
    {
      return this->CurrentLengthFraction;
    }

  /** Set fraction of total length of trajectory up to this point
   *
   * You will almost certainly not need to call this method yourself.
   * It is the responsibility of the Trajectory class to compute and
   * set the lengths.
   *
   * @param fraction Fraction of Trajectory Length up to this point
   */
  void set_current_length_fraction(double fraction)
    {
      this->CurrentLengthFraction = fraction;
    }

  /** Get fraction of total duration of trajectory up to this point
   *
   * When we build a trajectory this property will be set to the
   * fraction of duration of the trajectory up to this point. This
   * will be 0.0 at the very first point and range up to 1.0
   * thereafter.
   *
   * The initial value of `current_time_fraction` is -1.0 to indicate that it is
   * not yet set.
   *
   * @return fraction of Trajectory duration so far
   */
  double current_time_fraction() const
    {
      return this->CurrentTimeFraction;
    }

  /** Set fraction of total duration of trajectory up to this point
   *
   * You will almost certainly not need to call this method yourself.
   * It is the responsibility of the Trajectory class to compute and
   * set the fractions.
   *
   * @param fraction Fraction of Trajectory Duration up to this point
   */
  void set_current_time_fraction(double fraction)
    {
      this->CurrentTimeFraction = fraction;
    }


  /** @internal
   *
   * This method is for use by the Python wrappers that can provide
   * their own access to the non-const property map.
   */
  PropertyMap& __non_const_properties() { return this->Properties; }

  /** @internal
   *
   * This method is for use by the Python wrappers that can provide
   * their own access to the property map.
   */
  PropertyMap const& __properties() const { return this->Properties; }

  /** @internal
   *
   * This method is for use by the Python wrappers that can provide
   * their own access to the property map.
   */
  void __set_properties(PropertyMap const& props) { this->Properties = props; }

  friend std::ostream& operator<<(std::ostream& out, TrajectoryPoint const& point)
    {
      out << point.to_string();
      return out;
    }

protected:
  /// Length of trajectory up to this point
  double CurrentLength;
  /// Length fraction of trajectory up to this point
  double CurrentLengthFraction;
  /// Duration fraction of trajectory up to this point
  double CurrentTimeFraction;
  /// Storage for a point's object ID
  std::string ObjectId;
  /// Storage for a point's named properties
  PropertyMap Properties;
  /// Storage for a point's timestamp
  Timestamp UpdateTime;

private:
  /** Serialize the points and properties to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<typename archive_t>
  void serialize(archive_t& archive, const unsigned int /*version*/)
  {
/*
    archive & boost::serialization::make_nvp("Superclass",
                                             static_cast<Superclass*>(*this));
*/
    archive & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
    archive & BOOST_SERIALIZATION_NVP(CurrentLength);
    archive & BOOST_SERIALIZATION_NVP(ObjectId);
    archive & BOOST_SERIALIZATION_NVP(UpdateTime);
    archive & BOOST_SERIALIZATION_NVP(Properties);
  }

};

} // namespace tracktable

#if defined(WIN32)
# pragma warning( pop )
#endif

// ----------------------------------------------------------------------
//
// ALGORITHM TRAITS
//
// Except for things that involve timestamps or property maps, we
// delegate algorithms to the implementations for the base point type.
//
// ----------------------------------------------------------------------

namespace tracktable { namespace algorithms {


/** @brief Interpolate between two points.
 *
 * Interpolate between two different points in a trajectory. At t <=
 * 0 you'll get the first point back. At t >= 1 you'll get the second
 * point. At any value in between you'll get a combination of the
 * two. Coordinates and timestamp will be interpolated linearly.
 * Numeric properties will be interpolated linearly. String
 * properties will be taken from the first point if t <= 0.5 and the
 * second point otherwise.
 */

template<class BasePointT>
struct interpolate< TrajectoryPoint<BasePointT> >
{
  typedef BasePointT Superclass;

  template<class trajectory_point_type>
  static inline trajectory_point_type
  apply(trajectory_point_type const& left,
        trajectory_point_type const& right,
        double t)
    {
      if (t <= 0) return left;
      if (t >= 1) return right;

      // Start off by interpolating the coordinates with whatever
      // scheme the base point class provides
      trajectory_point_type result(
        interpolate<Superclass>::apply(
          left, right, t
          )
        );

      // Now interpolate the things specific to TrajectoryPoint
      result.set_timestamp(
        interpolate<Timestamp>::apply(left.timestamp(), right.timestamp(), t)
        );

      result.set_object_id(
        interpolate<std::string>::apply(left.object_id(), right.object_id(), t)
        );

      result.__set_properties(
        interpolate<PropertyMap>::apply(left.__properties(), right.__properties(), t)
        );
      return result;
    }
};

template<class BasePointT>
struct extrapolate< TrajectoryPoint<BasePointT> >
{
    typedef BasePointT Superclass;

    template<class trajectory_point_type>
    static inline trajectory_point_type
        apply(trajectory_point_type const& left,
            trajectory_point_type const& right,
            double t)
    {
        // Start off by extrapolating the coordinates with whatever
        // scheme the base point class provides
        trajectory_point_type result(
            extrapolate<Superclass>::apply(
                left, right, t
            )
        );

        // Now extrapolate the things specific to TrajectoryPoint
        result.set_timestamp(
            extrapolate<Timestamp>::apply(left.timestamp(), right.timestamp(), t)
        );

        result.set_object_id(
            interpolate<std::string>::apply(left.object_id(), right.object_id(), t)
        );

        result.__set_properties(
            extrapolate<PropertyMap>::apply(left.__properties(), right.__properties(), t)
        );
        return result;
    }
};

/** Speed between two points in native units per second
 *
 */

template<class BasePointT>
struct speed_between< TrajectoryPoint<BasePointT> >
{
  typedef TrajectoryPoint<BasePointT> point_type;
  static inline double apply(point_type const& start, point_type const& finish)
    {
      double units_traveled = ::tracktable::distance(start, finish);
      double duration = (finish.timestamp() - start.timestamp()).total_seconds();
      if (std::abs(duration) < 0.001)
        {
        return 0;
        }
      else
        {
        return units_traveled / duration;
        }
    }
};

// We can't blithely delegate these because they're not full
// specializations. Still, this gets the job done.

template<class BasePointT>
struct bearing< TrajectoryPoint<BasePointT> > : bearing<BasePointT> { };

template<class BasePointT>
struct signed_turn_angle< TrajectoryPoint<BasePointT> > : signed_turn_angle<BasePointT> { };

template<class BasePointT>
struct unsigned_turn_angle< TrajectoryPoint<BasePointT> > : unsigned_turn_angle<BasePointT> { };

template<class BasePointT>
struct spherical_coordinate_access< TrajectoryPoint<BasePointT> > : spherical_coordinate_access<BasePointT> { };

template<class BasePointT>
struct simplify_linestring< TrajectoryPoint<BasePointT> > : simplify_linestring<BasePointT> {};

} } // exit namespace tracktable::algorithms

namespace tracktable { namespace traits {

template<class BasePointT>
struct dimension< tracktable::TrajectoryPoint<BasePointT> > : dimension< BasePointT > {};

template<class BasePointT>
struct domain< tracktable::TrajectoryPoint<BasePointT> > : domain<BasePointT> {};

template<class BasePointT>
struct tag< TrajectoryPoint<BasePointT> > : tag<BasePointT> { };

template<class BasePointT>
struct has_properties< TrajectoryPoint<BasePointT> > : boost::mpl::bool_<true> { };

template<class BasePointT>
struct has_object_id< TrajectoryPoint<BasePointT> > : boost::mpl::bool_<true> { };

template<class BasePointT>
struct has_timestamp< TrajectoryPoint<BasePointT> > : boost::mpl::bool_<true> { };

template<class BasePointT>
struct object_id< TrajectoryPoint<BasePointT> > : object_id_is_member< TrajectoryPoint<BasePointT> > { };

template<class BasePointT>
struct timestamp< TrajectoryPoint<BasePointT> > : timestamp_is_member< TrajectoryPoint<BasePointT> > { };

template<typename BasePointT>
struct point_domain_name< TrajectoryPoint<BasePointT> > : point_domain_name<BasePointT> { };

template<typename BasePointT>
struct undecorated_point< TrajectoryPoint<BasePointT> > : undecorated_point<BasePointT> { };

} }


// ----------------------------------------------------------------------
//
// BOOST GEOMETRY TRAITS
//
// As before, we delegate to the base point class where
// boost::geometry is concerned.
//
// ----------------------------------------------------------------------

namespace boost { namespace geometry { namespace traits {

template<class BasePointT>
struct tag< tracktable::TrajectoryPoint<BasePointT> > : tag<BasePointT> {};

template<class BasePointT>
struct coordinate_type< tracktable::TrajectoryPoint<BasePointT> > : coordinate_type<BasePointT> {};

template<class BasePointT>
struct coordinate_system< tracktable::TrajectoryPoint<BasePointT> > : coordinate_system<BasePointT> { };


template<class BasePointT>
struct dimension< tracktable::TrajectoryPoint<BasePointT> > : dimension<BasePointT> {};

template<class BasePointT, size_t dim >
struct access< tracktable::TrajectoryPoint<BasePointT>, dim > : access<BasePointT, dim> {};

} } } // exit boost::geometry::traits


#endif
