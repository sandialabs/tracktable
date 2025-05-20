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
 * Cartesian3D Domain - objects in a flat 3D space
 *
 * The Cartesian domain measures distances in dimensionless units and
 * speeds in units per second.
 */

#ifndef __tracktable_domain_Cartesian3D_h
#define __tracktable_domain_Cartesian3D_h

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

namespace tracktable { namespace domain { namespace cartesian3d {

/** Bare point in flat 3D space
 *
 * This class defines a point in 3D Euclidean space. Units have no
 * real-world interpretation and (unlike the surface of the globe)
 * space is isotropic.
 *
 * Use this class instead of instantiating the `PointCartesian` template
 * yourself.
 */

class CartesianPoint3D : public PointCartesian<3>
{
public:
  typedef PointCartesian<3> Superclass;

  /** Create an uninitialized point
   *
   * Assume that the coordinates will be initialized to garbage values
   * when you use this constructor.
   */
  CartesianPoint3D() { }

  /** Initialize a point with x, y, z coordinates
   *
   * The coordinates will be initialized to whatever values you specify.
   *
   * @param [in] x X value to use for the point
   * @param [in] y Y value to use for the point
   * @param [in] z Z value to use for the point
   */
  CartesianPoint3D(double x, double y, double z)
    {
      this->set<0>(x);
      this->set<1>(y);
      this->set<2>(z);
    }

  /** Copy constructor: make this point like another
   *
   * @param [in] other Point to make a copy of
   */
  CartesianPoint3D(CartesianPoint3D const& other)
    : Superclass(other)
    { }

  /** Initialize this point from its superclass
   *
   * If you happen to have `PointCartesian<3>` instances sitting around,
   * this is where you use them. This is more for the compiler's
   * benefit than the user's.
   *
   * @param [in] other Superclass to use as if it were a CartesianPoint3D
   */
  CartesianPoint3D(Superclass const& other)
    : Superclass(other)
    { }

  /** Empty destructor
   *
   * All of our resources are on the stack. We don't have any real
   * work to do here.
   */
  virtual ~CartesianPoint3D() { }

  /** Assignment operator
   *
   * We delegate this explicitly to the superclass so that the
   * compiler won't try to do anything clever like copying pointers.
   */
  CartesianPoint3D& operator=(CartesianPoint3D const& other)
    {
      this->Superclass::operator=(other);
      return *this;
    }

public:
  template<class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
  {
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
  }

  // Everything else -- operator==, operator!=, operator<< --
  // delegated implicitly to the superclass
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

/** Trajectory point in flat 3D space
 *
 * This class defines a point in 3D Euclidean space along with an
 * object ID, timestamp and named properties. Units have no
 * real-world interpretation and (unlike the surface of the globe)
 * space is isotropic.
 *
 * Use this class instead of instantiating the `TrajectoryPoint` template
 * yourself.
 */

class CartesianTrajectoryPoint3D : public TrajectoryPoint< CartesianPoint3D >
{
public:
  typedef TrajectoryPoint< CartesianPoint3D > Superclass;

  /** Create an uninitialized point
   *
   * Assume that the coordinates will be initialized to garbage values
   * when you use this constructor. The object ID, timestamp and
   * properties will all be empty.
   */
  CartesianTrajectoryPoint3D() { }

  /** Initialize a point with x, y, z coordinates
   *
   * The coordinates will be initialized to whatever values you specify.
   *
   * @param [in] x X value to use for the point
   * @param [in] y Y value to use for the point
   * @param [in] z Z value to use for the point
   */
  CartesianTrajectoryPoint3D(double x, double y, double z)
    {
    (*this)[0] = x;
    (*this)[1] = y;
    (*this)[2] = z;
    }

  /** Copy constructor: make this point like another
   *
   * @param [in] other Point to make a copy of
   */
  CartesianTrajectoryPoint3D(CartesianTrajectoryPoint3D const& other)
    : Superclass(other)
    { }

  /** Initialize this point from its superclass
   *
   * If you happen to have `TrajectoryPoint<PointCartesian<3>>`
   * instances sitting around, this is where you use them. This is
   * more for the compiler's benefit than the user's.
   *
   * @param [in] other Superclass to use as if it were a CartesianTrajectoryPoint3D
   */
  CartesianTrajectoryPoint3D(Superclass const& other)
    : Superclass(other)
    { }

  /** Empty destructor
   *
   * All of our resources are on the stack. We don't have any real
   * work to do here.
   */
  virtual ~CartesianTrajectoryPoint3D() { }

  /** Assignment operator
   *
   * We delegate this explicitly to the superclass so that the
   * compiler won't try to do anything clever like copying pointers.
   */
  CartesianTrajectoryPoint3D& operator=(CartesianTrajectoryPoint3D const& other)
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


typedef CartesianPoint3D base_point_type;
typedef std::vector<base_point_type> linestring_type;
typedef CartesianTrajectoryPoint3D trajectory_point_type;
typedef Trajectory<trajectory_point_type> trajectory_type;
typedef PointReader<base_point_type> base_point_reader_type;
typedef PointReader<trajectory_point_type> trajectory_point_reader_type;
typedef TrajectoryReader<trajectory_type> trajectory_reader_type;
typedef boost::geometry::model::box<base_point_type> box_type;


TRACKTABLE_DOMAIN_EXPORT std::ostream& operator<<(std::ostream& out, base_point_type const& pt);

TRACKTABLE_DOMAIN_EXPORT std::ostream& operator<<(std::ostream& out, trajectory_point_type const& pt);

} } } // exit namespace tracktable::domain::cartesian3d

#ifndef DOXYGEN_SHOULD_SKIP_THIS

// ----------------------------------------------------------------------
//
// TRAIT DELEGATION
//
// ----------------------------------------------------------------------

namespace tracktable { namespace traits {

namespace domains {
  struct cartesian3d { };
}

template<>
struct point_domain_name<tracktable::domain::cartesian3d::CartesianPoint3D>
{
  static inline string_type apply() { return "cartesian3d"; }
};

} }

TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS(tracktable::domain::cartesian3d::CartesianPoint3D,
                                       tracktable::PointCartesian<3>)

TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS(tracktable::domain::cartesian3d::CartesianTrajectoryPoint3D,
                                       tracktable::TrajectoryPoint< tracktable::domain::cartesian3d::CartesianPoint3D >)

TRACKTABLE_DELEGATE_BASE_POINT_TRAITS(tracktable::domain::cartesian3d::CartesianPoint3D,
                                      tracktable::PointCartesian<3>)

TRACKTABLE_DELEGATE_TRAJECTORY_POINT_TRAITS(tracktable::domain::cartesian3d::CartesianTrajectoryPoint3D,
                                            tracktable::TrajectoryPoint< tracktable::domain::cartesian3d::CartesianPoint3D >)

TRACKTABLE_DELEGATE_DOMAIN_TRAIT(tracktable::domain::cartesian3d,
                                 tracktable::traits::domains::cartesian3d)

TRACKTABLE_DELEGATE_POINT_DOMAIN_NAME_TRAIT(tracktable::domain::cartesian3d)

// ----------------------------------------------------------------------
//
// ALGORITHM DELEGATION
//
// ----------------------------------------------------------------------

#undef TT_DELEGATE_BASE_POINT_ALGORITHM
#undef TT_DELEGATE_TP_ALGORITHM
#undef TT_DELEGATE_TRAJECTORY_ALGORITHM
#undef TT_DOMAIN

#define TT_DOMAIN tracktable::domain::cartesian3d

#define TT_DELEGATE_BASE_POINT_ALGORITHM(ALGORITHM) \
  TRACKTABLE_DELEGATE( \
    TT_DOMAIN::base_point_type, \
    tracktable::PointCartesian<3>, \
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
struct distance<traits::domains::cartesian3d>
{
  template<typename Geom1, typename Geom2>
  static inline double apply(Geom1 const& from, Geom2 const& to)
  {
    return boost::geometry::distance(from, to);
  }
};


template<>
struct unsigned_turn_angle<domain::cartesian3d::base_point_type>
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
      return angle_in_radians;
    }
};

TT_DELEGATE_BASE_POINT_ALGORITHM(interpolate)
TT_DELEGATE_BASE_POINT_ALGORITHM(extrapolate)

TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(interpolate)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(extrapolate)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(speed_between)
TT_DELEGATE_TRAJECTORY_POINT_ALGORITHM(unsigned_turn_angle)

template<>
struct length<TT_DOMAIN::trajectory_type>
{
  static inline double apply(TT_DOMAIN::trajectory_type const& path)
    {
      return boost::geometry::length(path);
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
