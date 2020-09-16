/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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


#ifndef __tracktable_BasicPointMath_h
#define __tracktable_BasicPointMath_h

#include <tracktable/Core/TracktableCommon.h>
#include <boost/geometry/arithmetic/arithmetic.hpp>
#include <boost/geometry/arithmetic/dot_product.hpp>
#include <boost/type_traits/is_base_of.hpp>
#include <cmath>

namespace tracktable {

/** Basic arithmetic operations for all point types.
 *
 * These operations are wrappers around boost::geometry's point
 * arithmetic operations.  You can (obviously) call boost::geometry
 * directly if you want but this will also let you use more natural
 * arithmetic operations on points.
 */
namespace arithmetic {

// original code follows
template<class PointT>
PointT add(PointT const& left, PointT const& right)
{
  PointT result(left);
  boost::geometry::add_point(result, right);
  return result;
}

template<class PointT>
PointT add_in_place(PointT& left, PointT const& right)
{
  boost::geometry::add_point(left, right);
  return left;
}

template<class PointT>
PointT subtract(PointT const& left, PointT const& right)
{
  PointT result(left);
  boost::geometry::subtract_point(result, right);
  return result;
}

template<class PointT>
PointT subtract_in_place(PointT left, PointT const& right)
{
  boost::geometry::subtract_point(left, right);
  return left;
}

template<class PointT>
PointT multiply(PointT const& left, PointT const& right)
{
  PointT result(left);
  boost::geometry::multiply_point(result, right);
  return result;
}

template<class PointT>
PointT multiply_in_place(PointT& left, PointT const& right)
{
  boost::geometry::multiply_point(left, right);
  return left;
}

template<class PointT, typename ScalarT>
PointT multiply_scalar(PointT const& left, ScalarT const& value)
{
  PointT result(left);
  boost::geometry::multiply_value(result, value);
  return result;
}

template<class PointT, typename ScalarT>
PointT multiply_scalar_in_place(PointT& left, ScalarT const& value)
{
  boost::geometry::multiply_value(left, value);
  return left;
}

template<class PointT>
PointT divide(PointT const& left, PointT const& right)
{
  PointT result(left);
  boost::geometry::divide_point(result, right);
  return result;
}

template<class PointT>
PointT divide_in_place(PointT& left, PointT const& right)
{
  boost::geometry::divide_point(left, right);
  return left;
}

template<class PointT, typename ScalarT>
PointT divide_scalar(PointT const& left, ScalarT const& value)
{
  PointT result(left);
  boost::geometry::divide_value(result, value);
  return result;
}

template<class PointT, typename ScalarT>
PointT divide_scalar_in_place(PointT& left, ScalarT const& value)
{
  boost::geometry::divide_value(left, value);
  return left;
}

template<class PointT>
double dot(PointT const& left, PointT const& right)
{
  return boost::geometry::dot_product(left, right);
}

template<class PointT>
double norm_squared(PointT const& left)
{
  return boost::geometry::dot_product(left, left);
}

template<class PointT>
double norm(PointT const& left)
{
  return sqrt(norm_squared(left));
}

template<class PointT>
PointT zero()
{
  PointT result;
  for (std::size_t i = 0; i < result.size(); ++i)
  {
    result[i] = 0;
  }
  return result;
}

} }

#endif
