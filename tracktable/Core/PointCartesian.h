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


#ifndef __tracktable_PointCartesian_h
#define __tracktable_PointCartesian_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PointBase.h>

#include <tracktable/Core/detail/algorithm_signatures/Distance.h>
#include <tracktable/Core/detail/algorithm_signatures/Interpolate.h>
#include <tracktable/Core/detail/algorithm_signatures/Extrapolate.h>
#include <tracktable/Core/detail/algorithm_signatures/TurnAngle.h>

#include <tracktable/Core/detail/points/AssignCoordinates.h>
#include <tracktable/Core/detail/points/InterpolateCoordinates.h>
#include <tracktable/Core/detail/points/CheckCoordinateEquality.h>

#include <tracktable/Core/detail/trait_signatures/PointDomainName.h>
#include <tracktable/Core/detail/trait_signatures/Tag.h>


#include <sstream> // for ostringstream in to_string


#include <tracktable/Core/GuardedBoostGeometryHeaders.h>
#include <boost/geometry/core/cs.hpp>
#include <boost/geometry/geometries/register/point.hpp>

namespace tracktable {

/**
 * @class PointCartesian
 *
 * @brief N-dimensional point in Cartesian space
 *
 * This specializes PointBase to exist in a Cartesian coordinate
 * system and be usable with `boost::geometry`. You must still
 * instantiate it explicitly with the number of dimensions.
 */

template<std::size_t Dimension>
class PointCartesian : public PointBase<Dimension>
{
public:
  friend class boost::serialization::access;

  /// Convenient alias for the parent class
  typedef PointBase<Dimension> Superclass;

  /// Create an uninitialized point
  PointCartesian() { }

  /// Destructor for a point
  ~PointCartesian() { }

  /** Make this point into a copy of another
  *
  * @param [in] other Point we want to copy
  */
  PointCartesian(Superclass const& other)
    {
      detail::assign_coordinates<Dimension>::apply(*this, other);
    }

  /** Create a point with user-supplied coordinates
  *
  * Populate the point from an array of coordinates. The caller is
  * responsible for ensuring that the array is large enough to
  * contain the right number of coordinates.
  *
  * @param [in] coordinates Coordinates to use when creating a point
  */
  PointCartesian(const double* coordinates)
    {
      for (std::size_t i = 0; i < Dimension; ++i)
        {
        (*this)[i] = coordinates[i];
        }
    }

  /** Convert point coordinates to a string
   *
   * @return Coordinates string
   */
  std::string to_string() const
    {
      std::ostringstream outbuf;
      outbuf << "(";
      for (std::size_t i = 0; i < Dimension; ++i)
        {
        if (i > 0) outbuf << ", ";
        outbuf << this->Coordinates[i];
        }
      outbuf << ")";
      return outbuf.str();
    }

public:
  /** Serialize the coordinates to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
  {
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
  }

};

} // exit namespace tracktable

/** Write a point to a stream as a string
 *
 * @param [in] os Stream to write to
 * @param [in] pt Point to write to string
 */
template<std::size_t dim>
std::ostream& operator<<(std::ostream& out, tracktable::PointCartesian<dim> const& pt)
{
  out << pt.to_string();
  return out;
}

// ----------------------------------------------------------------------
//
// TRACKTABLE POINT ALGORITHMS
//
// ----------------------------------------------------------------------

namespace tracktable { namespace algorithms {

/** Interpolate between two PointCartesian objects
 *
 * This is a standard Tracktable algorithm that must be implemented
 * for any two things that you might want to interpolate, generally
 * points. In this case we default to linear interpolation between
 * coordinates.
 *
 */
template<std::size_t Dimension>
struct interpolate< PointCartesian<Dimension> >
{
  template<typename point_type>
  static inline point_type
  apply(point_type const& left, point_type const& right, double t)
    {
      point_type result;
      detail::interpolate_coordinates<Dimension>::apply(left, right, t, result);
      return result;
    }
};

template<std::size_t Dimension>
struct extrapolate< PointCartesian<Dimension> >
{
    template<typename point_type>
    static inline point_type
        apply(point_type const& left, point_type const& right, double t)
    {
        point_type result;
        detail::interpolate_coordinates<Dimension>::apply(left, right, t, result);
        return result;
    }
};

} } // exit namespace tracktable::algorithms

#ifndef DOXYGEN_SHOULD_SKIP_THIS

// ----------------------------------------------------------------------
//
// TRACKTABLE POINT TRAITS
//
// ----------------------------------------------------------------------

namespace tracktable { namespace traits {

template<std::size_t Dimension>
struct tag< PointCartesian<Dimension> >
{
  typedef base_point_tag type;
};

template<std::size_t Dimension>
struct dimension< PointCartesian<Dimension> > : dimension< typename PointCartesian<Dimension>::Superclass > {};

template<std::size_t Dimension>
struct point_domain_name< PointCartesian<Dimension> >
{
  static inline string_type apply()
    {
      return "generic_cartesian";
    }
};

template<std::size_t Dimension>
struct undecorated_point< PointCartesian<Dimension> >
{
  typedef PointCartesian<Dimension> type;
};

template<std::size_t Dimension>
struct domain<PointCartesian<Dimension> >
{
  typedef domains::generic type;
};


} } // exit namespace tracktable::traits

// ----------------------------------------------------------------------
//
// BOOST GEOMETRY POINT TRAITS
//
// Below this point are the templates that register PointCartesian
// with boost::geometry. If we do this right (using partial
// specialization) then you can declare a PointCartesian<D> and have
// it work automatically. *If* we do it right... and if the compiler
// obliges.
//
// ----------------------------------------------------------------------

namespace boost { namespace geometry { namespace traits {

/// PointCartesian is a model of the Point concept
template<std::size_t Dimension>
struct tag< tracktable::PointCartesian<Dimension> >
{
  typedef point_tag type;
};

/// Publish the coordinate data type
template<std::size_t Dimension>
struct coordinate_type< tracktable::PointCartesian<Dimension> >
{
  typedef tracktable::settings::point_coordinate_type type;
};

/// Publish the number of dimensions
template<std::size_t Dimension>
struct dimension< tracktable::PointCartesian<Dimension> > : boost::mpl::int_<Dimension> {};


/// PointCartesian exists in a Cartesian coordinate system
template<std::size_t Dimension>
struct coordinate_system< tracktable::PointCartesian<Dimension> >
{
  typedef cs::cartesian type;
};


/// Access to coordinates

template<std::size_t Dimension, std::size_t dim>
  struct access< tracktable::PointCartesian<Dimension>, dim>
{
  typedef tracktable::PointCartesian<Dimension> point_type;
  typedef typename point_type::coordinate_type coordinate_type;

  static coordinate_type get(point_type const& p)
  {
    return p.template get<dim>();
  }

  static void set(point_type& p, coordinate_type value)
  {
    p.template set<dim>(value);
  }
};

} } } // exit namespace boost::geometry::traits

#endif // DOXYGEN_SHOULD_SKIP_THIS

#endif
