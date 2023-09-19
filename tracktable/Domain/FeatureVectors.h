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
 * FeatureVector Domain - many-D Cartesian space
 *
 * This domain contains points with anywhere from 2 to 30 dimensions.
 * It does not have trajectories or trajectory points (yet).
 */


#ifndef __tracktable_domain_FeatureVector_h
#define __tracktable_domain_FeatureVector_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Box.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Domain/DomainMacros.h>
#include <tracktable/Domain/TracktableDomainWindowsHeader.h>
#include <tracktable/RW/PointReader.h>

#include <vector>
#include <string>


// Basic definition of FeatureVector - you can use this in C++

namespace tracktable { namespace domain { namespace feature_vectors {

/** Point type for feature vectors
 *
 * A feature vector is a list of numbers that collectively describe
 * properties of some entity, generally a trajectory. We typically
 * treat feature vectors as a kind of fingerprint: we don't want to
 * modify them or do arithmetic with them, but instead look at the
 * structure of a larger collection of feature vectors.
 *
 * In Tracktable we use the `FeatureVector` template for such things.
 * You can specify any dimension you want from 1 on up. Algorithms
 * such as `DBSCAN` and the `R-tree` are templated on point type so that
 * you can use them with any kind of feature vector you want.
 */

template<std::size_t dim>
class FeatureVector : public PointCartesian<dim>
{
public:
  typedef PointCartesian<dim> Superclass;

  /// Create an uninitialized vector
  FeatureVector() { }

  /// Empty destructor - nothing to do here
  virtual ~FeatureVector() { }

  /** Instantiate coordinates from the given feature vector
   *
   * @param [in] other Feature vector to use for initialization
   */
  FeatureVector(FeatureVector const& other)
    {
      detail::assign_coordinates<dim>::apply(*this, other);
    }

  /** Instantiate coordinates from the given coordinate list
   *
   * @param [in] other Coordinates to use for initialization
   */
  FeatureVector(const double* coords)
    {
      tracktable::detail::assign_coordinates_from_array<dim>(*this, coords);
    }

  FeatureVector& operator=(FeatureVector const& other)
    {
      tracktable::detail::assign_coordinates<dim>::apply(*this, other);
      return *this;
    }

  /** Serialize the points to an archive
   *
   * @param [in] ar Archive to serialize to
   * @param [in] version Version of the archive
   */
  template<class Archive>
  void serialize(Archive& ar, const unsigned int /*version*/)
    {
    // ar & boost::serialization::base_object< PointCartesian<dim> >(*this);
    ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(Superclass);
    }

  /** Convert point coordinates to a string
   *
   * @return Coordinates string
   */
  string_type to_string() const
    {
    std::ostringstream outbuf;
    outbuf << *this;
    return outbuf.str();
    }
};


/** Write a feature vector to a stream as a string
 *
 * This supports the idiom "stream << my_point". This function
 * is also the implementation for `FeatureVector<dim>::to_string()`.
 *
 * Example:
 *
 * @code
 *
 * FeatureVector<3> my_vector;
 * my_vector[0] = 1;
 * my_vector[1] = 2;
 * my_vector[2] = 3;
 * std::cout << my_vector << std::endl;
 *
 * @endcode
 *
 * Output:
 *
 * "(1, 2, 3)"
 *
 * @param [in] out Stream to write to
 * @param [in] pt Point to write to string
 */

template<std::size_t dim>
std::ostream& operator<<(std::ostream& out, FeatureVector<dim> const& pt)
{
  out << "(";
  for (std::size_t i = 0; i < dim; ++i)
  {
    if (i > 0)
    {
      out << ", ";
    }
    out << pt[i];
  }
  out << ")";
  return out;
}

} } }

// ----------------------------------------------------------------------

// Tracktable trait delegation for FeatureVector


// Boost trait delegation for FeatureVector

namespace boost { namespace geometry { namespace traits {

template<std::size_t dim>
struct tag< tracktable::domain::feature_vectors::FeatureVector<dim> > : tag< tracktable::PointCartesian<dim> > {};

template<std::size_t dim>
struct dimension< tracktable::domain::feature_vectors::FeatureVector<dim> > : dimension< tracktable::PointCartesian<dim> > {};

template<std::size_t dim>
struct coordinate_type< tracktable::domain::feature_vectors::FeatureVector<dim> > : coordinate_type< tracktable::PointCartesian<dim> > {};

template<std::size_t dim>
struct coordinate_system< tracktable::domain::feature_vectors::FeatureVector<dim> > : coordinate_system< tracktable::PointCartesian<dim> > {};

template<std::size_t Dimension, std::size_t dim>
struct access< tracktable::domain::feature_vectors::FeatureVector<Dimension>, dim > :
    access< tracktable::PointCartesian<Dimension>, dim > {};


} } } // exit boost::geometry::traits

namespace tracktable { namespace traits {

template<std::size_t dim>
struct tag< tracktable::domain::feature_vectors::FeatureVector<dim> > : tag< tracktable::PointCartesian<dim> > {};

template<std::size_t dim>
struct dimension< tracktable::domain::feature_vectors::FeatureVector<dim> > : dimension< tracktable::PointCartesian<dim> > {};

template<std::size_t dim>
struct point_domain_name< tracktable::domain::feature_vectors::FeatureVector<dim> > : point_domain_name< tracktable::PointCartesian<dim> > {};

} } // exit tracktable::traits



#endif
