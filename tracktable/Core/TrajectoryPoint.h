/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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

namespace tracktable {

/**
 * \class TrajectoryPoint
 * \brief Add object ID, timestamp, property map
 *
 * This class will add trajectory properties (a timestamp, an object
 * ID and storage for named properties) to any point class.
 *
 * Timestamp is a tracktable::Timestamp which (under the hood) is a
 * boost::posix_time::ptime.  Object ID is stored as a string.

 * We also include an interface to set, get and enumerate arbitrary
 * named properties.  The only restriction is that the types of these
 * properties are limited to timestamps, floating-point numbers and
 * strings.  If you need something more flexible than that please
 * consider creating your own alternative point class either by
 * subclassing TrajectoryPoint or by composition.
 *
 * \note Named property support is implemented using boost::variant.
 *       You can either use boost::get<> to cast it to your desired
 *       data type or call one of the (type)_property_value
 *       functions to retrieve it with no casting necessary.  Take a
 *       look at C++/Core/Tests/test_trajectory_point.cpp (XXX CHECK
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
  typedef BasePointT base_point_type;

  /// Instantiate an uninitialized point
  TrajectoryPoint()
    : base_point_type()
    ,CurrentLength(-1)
    ,ObjectId("")
    ,UpdateTime(tracktable::BeginningOfTime)
    {
    }

  virtual ~TrajectoryPoint()
    {
    }

  /// Initialize a TrajectoryPoint as a copy of an existing point
  TrajectoryPoint(TrajectoryPoint const& other)
    : base_point_type(other)
    ,CurrentLength(other.CurrentLength)
    ,ObjectId(other.ObjectId)
    ,Properties(other.Properties)
    ,UpdateTime(other.UpdateTime)
    {
    }

  /// Initialize with coordinates from a base point
  TrajectoryPoint(base_point_type const& other)
    : base_point_type(other)
    {
    }

  TrajectoryPoint(const double* coords)
    : base_point_type(coords)
    { }

  /// Make this TrajectoryPoint a copy of an existing point
  TrajectoryPoint operator=(TrajectoryPoint const& other)
    {
      this->base_point_type::operator=(other);
      this->CurrentLength = other.CurrentLength;
      this->ObjectId = other.ObjectId;
      this->Properties = other.Properties;
      this->UpdateTime = other.UpdateTime;
      return *this;
    }


  /// Check two points for equality
  //
  // Two TrajectoryPoints are equal if and only if they have:
  // * the same coordinates (base point)
  // * the same object ID
  // * the same timestamp
  // * the same user-defined properties
  bool operator==(TrajectoryPoint const& other) const
    {
      return ( this->base_point_type::operator==(other)
//               && this->CurrentLength == other.CurrentLength
               && this->ObjectId == other.ObjectId
               && this->Properties == other.Properties
               && this->UpdateTime == other.UpdateTime
        );
    }

  /// Check two points for inequality
  bool operator!=(TrajectoryPoint const& other) const
    {
      return ( (*this == other) == false );
    }

  /// Return this point's object ID
  std::string object_id() const { return this->ObjectId; }

  /// Return this point's timestamp
  Timestamp timestamp() const { return this->UpdateTime; }

  /// Set this point's object ID
  void set_object_id(std::string const& new_id) { this->ObjectId = new_id; }

  /// Set this point's timestamp
  void set_timestamp(Timestamp const& ts) { this->UpdateTime = ts; }

  /// Set a named property with a variant value (let the caller handle the type)
  void set_property(std::string const& name, PropertyValueT const& value)
    {
      ::tracktable::set_property(this->Properties, name, value);
    }

  /// Retrieve a named property with checking
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a boost::variant
  PropertyValueT property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::property(this->Properties, name, ok);
    }

  /// Retrieve a named property or a default value
  //
  // \param name Name of property to retrieve
  // \param default_value Value to return if property is not present
  // \return Property as a boost::variant
  PropertyValueT property(std::string const& name, PropertyValueT const& default_value) const
    {
      return ::tracktable::property_with_default(this->Properties, name, default_value);
    }

  /// Retrieve a named property without safety checking
  //
  // It is the caller's responsibility to know whether the requested
  // property actually exists when using this function.
  //
  // \param name Name of property to retrieve
  // \return Property as a boost::variant
  PropertyValueT property_without_checking(std::string const& name) const
    {
      bool ok;
      return ::tracktable::property(this->Properties, name, &ok);
    }

  /// Safely retrieve a named property with a string value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a std::string
  std::string string_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::string_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with a floating-point value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a double
  double real_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::real_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with an integer value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as an int64_t
  int64_t integer_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::integer_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with a timestamp value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a timestamp
  Timestamp timestamp_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::timestamp_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with a string value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a std::string
  std::string string_property_with_default(std::string const& name, std::string const& default_value) const
    {
      return ::tracktable::string_property_with_default(this->Properties, name, default_value);
    }

  /// Safely retrieve a named property with a floating-point value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a double
  double real_property_with_default(std::string const& name, double default_value) const
    {
      return ::tracktable::real_property_with_default(this->Properties, name, default_value);
    }

  /// Safely retrieve a named property with an integer value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as an int64_t
  int64_t integer_property_with_default(std::string const& name, int64_t default_value) const
    {
      return ::tracktable::integer_property_with_default(this->Properties, name, default_value);
    }

  /// Safely retrieve a named property with a timestamp value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a timestamp
  Timestamp timestamp_property_with_default(std::string const& name, Timestamp const& default_value) const
    {
      return ::tracktable::timestamp_property_with_default(this->Properties, name, default_value);
    }

  /// Check whether a property is present
  //
  // \param name Name of desired property
  // \return True if present, false if not
  bool has_property(std::string const& name) const
    {
      return ::tracktable::has_property(this->Properties, name);
    }

  /// Convert point to a human-readable string form
  std::string to_string() const
    {
      std::ostringstream outbuf;
      imbue_stream_with_timestamp_output_format(outbuf, default_timestamp_output_format());

      outbuf << "[";
      outbuf << this->object_id() << "@ ";
      outbuf << this->timestamp() << ": ";
      outbuf << this->base_point_type::to_string();
      outbuf << " ";
      outbuf << property_map_to_string(this->Properties);
      outbuf << "]";
      return outbuf.str();
    }

  /// Get length of trajectory up to this point
  //
  // When we build a trajectory this property will be set to the total
  // length of the trajectory up to this point.  This will be 0 at the
  // very first point and some non-negative value thereafter.
  //
  // The initial value of current_length is -1 to indicate that it is
  // not yet set.
  //
  // \return Trajectory length so far
  double current_length() const
    {
      return this->CurrentLength;
    }

  /// Set length of trajectory up to this point
  //
  // You will almost certainly not need to call this method yourself.
  // It is the responsibility of the Trajectory class to compute and
  // set the lengths.
  //
  // \param length Length up to this point
  void set_current_length(double length)
    {
      this->CurrentLength = length;
    }

  /// INTERNAL METHOD
  //
  // This method is for use by the Python wrappers that can provide
  // their own access to the property map.
  PropertyMap& __non_const_properties() { return this->Properties; }
  PropertyMap const& __properties() const { return this->Properties; }
  /// INTERNAL METHOD
  //
  // This method is for use by the Python wrappers that can provide
  // their own access to the property map.
  void __set_properties(PropertyMap const& props) { this->Properties = props; }

  friend std::ostream& operator<<(std::ostream& out, TrajectoryPoint const& point)
    {
      out << point.to_string();
      return out;
    }

protected:
  /// Length of trajectory up to this point
  double CurrentLength;
  /// Storage for a point's object ID
  std::string ObjectId;
  /// Storage for a point's named properties
  PropertyMap Properties;
  /// Storage for a point's timestamp
  Timestamp UpdateTime;
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


/** \brief Interpolate between two points.
 *
 * Interpolate between two different points in a trajectory.  At t <=
 * 0 you'll get the first point back.  At t >= 1 you'll get the second
 * point.  At any value in between you'll get a combination of the
 * two.  Coordinates and timestamp will be interpolated linearly.
 * Numeric properties will be interpolated linearly.  String
 * properties will be taken from the first point if t <= 0.5 and the
 * second point otherwise.
 */

template<class BasePointT>
struct interpolate< TrajectoryPoint<BasePointT> >
{
  typedef BasePointT base_point_type;

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
        interpolate<base_point_type>::apply(
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
    typedef BasePointT base_point_type;

    template<class trajectory_point_type>
    static inline trajectory_point_type
        apply(trajectory_point_type const& left,
            trajectory_point_type const& right,
            double t)
    {
        // Start off by extrapolating the coordinates with whatever
        // scheme the base point class provides
        trajectory_point_type result(
            extrapolate<base_point_type>::apply(
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
// specializations.  Still, this gets the job done.

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
