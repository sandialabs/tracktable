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
 * Cartesian2D Domain - objects on a flat plane
 *
 * The Cartesian domain measures distances in dimensionless units and
 * speeds in units per second.
 */

#ifndef __tracktable_domain_Cartesian2D_h
#define __tracktable_domain_Cartesian2D_h

#include <tracktable/Core/TracktableCommon.h>

#include <tracktable/Core/Box.h>
#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Domain/DomainMacros.h>
#include <tracktable/Domain/TracktableDomainWindowsHeader.h>
#include <tracktable/RW/PointReader.h>
#include <tracktable/RW/TrajectoryReader.h>

#include <boost/geometry/algorithms/length.hpp>

#include <vector>
#include <string>

namespace tracktable { namespace domain { namespace cartesian2d {

/** Bare point in flat 2D space
 *
 * This class defines a point in 2D Euclidean space using Cartesian
 * coordinates. Units have no real-world interpretation and (unlike
 * the surface of the globe) space is isotropic.
 *
 * Use this class instead of instantiating the `PointCartesian` template
 * yourself.
 */

class CartesianPoint2D : public PointCartesian<2>
{
public:
  typedef PointCartesian<2> Superclass;

  /** Create an uninitialized point
   *
   * Assume that the coordinates will be initialized to garbage values
   * when you use this constructor.
   */
  CartesianPoint2D() { }


  /** Initialize a point with x, y coordinates
   *
   * The coordinates will be initialized to whatever values you specify.
   *
   * @param [in] x Lon value to use for the point
   * @param [in] y Lat value to use for the point
   */
  CartesianPoint2D(double x, double y)
    {
      (*this)[0] = x;
      (*this)[1] = y;
    }

  /** Copy constructor: make this point like another
   *
   * @param [in] other Point to make a copy of
   */
  CartesianPoint2D(CartesianPoint2D const& other)
    : Superclass(other)
    { }

  /** Initialize this point from its superclass
   *
   * If you happen to have `PointCartesian<2>` instances sitting around,
   * this lets you use them as if they were `CartesianPoint2D`
   * instances. This is more for the compiler's benefit than the
   * user's.
   *
   * @param [in] other Superclass to use as if it were a CartesianPoint2D
   */
  CartesianPoint2D(Superclass const& other)
    : Superclass(other)
    { }

  /** Empty destructor
   *
   * All of our resources are on the stack. We don't have any real
   * work to do here.
   */
  virtual ~CartesianPoint2D() { }

  /** Assignment operator
   *
   * We delegate this explicitly to the superclass so that the
   * compiler won't try to do anything clever like copying pointers.
   */
  CartesianPoint2D& operator=(CartesianPoint2D const& other)
    {
      this->Superclass::operator=(other);
      return *this;
    }


public:
  /** Serialize the point to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
  {
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
  }

  // Everything else -- operator==, operator!=, operator<< --
  // delegated to the superclass
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

/** Trajectory point in flat 2D space
 *
 * This class defines a point in 2D Euclidean space along with an
 * object ID, timestamp and named properties. Units have no
 * real-world interpretation and (unlike the surface of the globe)
 * space is isotropic.
 *
 * Use this class instead of instantiating the `TrajectoryPoint`
 * template yourself. That way the library can present you with a
 * consistent set of units. Also remember that you inherit all the
 * methods of `TrajectoryPoint`.
 */

class CartesianTrajectoryPoint2D : public TrajectoryPoint< CartesianPoint2D >
{
public:
  typedef TrajectoryPoint< CartesianPoint2D > Superclass;

  /** Create an uninitialized point
   *
   * Assume that the coordinates will be initialized to garbage values
   * when you use this constructor. The object ID, timestamp and
   * properties will all be empty.
   */
  CartesianTrajectoryPoint2D() { }

  /** Initialize a point with x, y coordinates
   *
   * The coordinates will be initialized to whatever values you specify.
   *
   * @param [in] x Lon value to use for the point
   * @param [in] y Lat value to use for the point
   */
  CartesianTrajectoryPoint2D(double x, double y)
    {
      (*this)[0] = x;
      (*this)[1] = y;
    }

  /** Copy constructor: make this point like another
   *
   * @param [in] other Point to make a copy of
   */
  CartesianTrajectoryPoint2D(CartesianTrajectoryPoint2D const& other)
    : Superclass(other)
    { }

  /** Initialize this point from its superclass
   *
   * If you happen to have `TrajectoryPoint<PointCartesian<2>>`
   * instances sitting around, this lets you use them as if they were
   * `CartesianTrajectoryPoint2D` objects. This is more for the compiler's
   * benefit than the user's.
   *
   * @param [in] other Superclass to use as if it were a CartesianTrajectoryPoint2D
   */
  CartesianTrajectoryPoint2D(Superclass const& other)
    : Superclass(other)
    { }

  /** Empty destructor
   *
   * All of our resources are on the stack. We don't have any real
   * work to do here.
   */
  virtual ~CartesianTrajectoryPoint2D() { }

  /** Assignment operator
   *
   * We delegate this explicitly to the superclass so that the
   * compiler won't try to do anything clever like copying pointers.
   */
  CartesianTrajectoryPoint2D& operator=(CartesianTrajectoryPoint2D const& other)
    {
      this->Superclass::operator=(other);
      return *this;
    }

public:
  /** Serialize the points to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
  {
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
  }

  // Everything else -- operator==, operator!=, operator<< --
  // delegated to the superclass
};

#if defined(WIN32)
# pragma warning( pop )
#endif


typedef CartesianPoint2D base_point_type;
typedef std::vector<base_point_type> linestring_type;
typedef CartesianTrajectoryPoint2D trajectory_point_type;
typedef Trajectory<trajectory_point_type> trajectory_type;
typedef PointReader<base_point_type> base_point_reader_type;
typedef PointReader<trajectory_point_type> trajectory_point_reader_type;
typedef TrajectoryReader<trajectory_type> trajectory_reader_type;
typedef boost::geometry::model::box<base_point_type> box_type;


TRACKTABLE_DOMAIN_EXPORT std::ostream& operator<<(std::ostream& out, base_point_type const& pt);

TRACKTABLE_DOMAIN_EXPORT std::ostream& operator<<(std::ostream& out, trajectory_point_type const& pt);

} } } // exit namespace tracktable::domain::cartesian2d

#ifndef DOXYGEN_SHOULD_SKIP_THIS

// ----------------------------------------------------------------------
//
// TRAIT DELEGATION
//
// ----------------------------------------------------------------------

namespace tracktable { namespace traits {

namespace domains {
  struct cartesian2d { };
}

template<>
struct point_domain_name<tracktable::domain::cartesian2d::CartesianPoint2D>
{
  static inline string_type apply() { return "cartesian2d"; }
};

} } // close namespace tracktable:traits

TRACKTABLE_DELEGATE_DOMAIN_TRAIT(tracktable::domain::cartesian2d,
                                 tracktable::traits::domains::cartesian2d)

TRACKTABLE_DELEGATE_POINT_DOMAIN_NAME_TRAIT(tracktable::domain::cartesian2d)

TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS(tracktable::domain::cartesian2d::CartesianPoint2D,
                                       tracktable::PointCartesian<2>)

TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS(tracktable::domain::cartesian2d::CartesianTrajectoryPoint2D,
                                       tracktable::TrajectoryPoint< tracktable::domain::cartesian2d::CartesianPoint2D >)

TRACKTABLE_DELEGATE_BASE_POINT_TRAITS(tracktable::domain::cartesian2d::CartesianPoint2D,
                                      tracktable::PointCartesian<2>)

TRACKTABLE_DELEGATE_TRAJECTORY_POINT_TRAITS(tracktable::domain::cartesian2d::CartesianTrajectoryPoint2D,
                                            tracktable::TrajectoryPoint< tracktable::domain::cartesian2d::CartesianPoint2D >)

// ----------------------------------------------------------------------
//
// ALGORITHM DELEGATION
//
// ----------------------------------------------------------------------

#undef TT_DELEGATE_BASE_POINT_ALGORITHM
#undef TT_DELEGATE_TP_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_ALGORITHM
#undef TT_DOMAIN

#define TT_DOMAIN tracktable::domain::cartesian2d

#define TT_DELEGATE_BASE_POINT_ALGORITHM(ALGORITHM) \
  TRACKTABLE_DELEGATE( \
    TT_DOMAIN::base_point_type, \
    PointCartesian<2>, \
    ALGORITHM \
    )

#define TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(ALGORITHM) \
  TRACKTABLE_DELEGATE( \
    TT_DOMAIN::trajectory_point_type, \
    tracktable::TrajectoryPoint<TT_DOMAIN::base_point_type>,       \
    ALGORITHM \
    )

#define TT_DELEGATE_TRAJECTORY_ALGORITHM(ALGORITHM) \
  TRACKTABLE_DELEGATE( \
    TT_DOMAIN::trajectory_type, \
    tracktable::Trajectory<TT_DOMAIN::trajectory_point_type>, \
    ALGORITHM \
    )

namespace tracktable { namespace algorithms {

template<>
struct distance<traits::domains::cartesian2d>
{
  template<typename Geom1, typename Geom2>
  static inline double apply(Geom1 const& from, Geom2 const& to)
  {
    return boost::geometry::distance(from, to);
  }
};


template<>
struct bearing<domain::cartesian2d::base_point_type>
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

template<>
struct signed_turn_angle<domain::cartesian2d::base_point_type>
{
  inline static double dot(const double ab[3], const double bc[3])
    {
      return (ab[0] * bc[0] + ab[1] * bc[1] + ab[2] * bc[2]);
    }

  inline static double magnitude(const double p[3])
    {
      return sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]);
    }

  inline static void normalize(double p[3])
    {
      double mag = magnitude(p);
      if (!tracktable::almost_zero(mag)) return;
      p[0] /= mag;
      p[1] /= mag;
      p[2] /= mag;
    }

  template<class PointT>
  static inline double apply(PointT const& a, PointT const& b, PointT const& c)
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
      double angle_in_radians = acos(dot(ab, bc));
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

template<>
struct unsigned_turn_angle<TT_DOMAIN::base_point_type>
{
  template<typename P>
  static inline double apply(P const& a, P const& b, P const& c)
    {
      return fabs(signed_turn_angle<P>::apply(a, b, c));
    }
};


TT_DELEGATE_BASE_POINT_ALGORITHM(interpolate)
TT_DELEGATE_BASE_POINT_ALGORITHM(extrapolate)
// TT_DELEGATE_BASE_POINT_ALGORITHM(distance)

// spherical coordinate access is not appropriate for this point type

TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(interpolate)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(extrapolate)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(bearing)
// TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(distance)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(signed_turn_angle)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(speed_between)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(unsigned_turn_angle)


template<>
struct length<TT_DOMAIN::trajectory_type>
{
  typedef TT_DOMAIN::trajectory_type trajectory_type;

  inline static double apply(trajectory_type const& trajectory)
    {
      return boost::geometry::length(trajectory);
    }
};

} } // exit namespace tracktable::algorithms


#undef TT_DOMAIN
#undef TT_DELEGATE_BASE_POINT_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_POINT_TRAIT

#endif // DOXYGEN_SHOULD_SKIP_THIS

#endif
