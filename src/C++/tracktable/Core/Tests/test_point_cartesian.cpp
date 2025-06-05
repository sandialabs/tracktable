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

#include <tracktable/Core/FloatingPointComparison.h>
#include <tracktable/Core/PointBase.h>
#include <tracktable/Core/PointCartesian.h>

#include <boost/geometry/arithmetic/arithmetic.hpp>
#include <boost/geometry/algorithms/distance.hpp>

#include <iostream>
#include <sstream>

template<class thing>
std::string to_string(thing const& t)
{
  return t.to_string();
}

// ----------------------------------------------------------------------

template<class point_type>
int test_boost_point_arithmetic(point_type const& left, point_type const& right)
{
  int error_count = 0;
  std::size_t dimension = boost::geometry::traits::dimension<point_type>::value;

  point_type a(left);
  point_type b = right;

  point_type sum(a);
  boost::geometry::add_point(sum, b);
  std::cout << "Point addition: a + b = "
            << to_string(sum) << "\n";

  for (std::size_t i = 0; i < dimension; ++i)
    {
    if (!tracktable::almost_equal(sum[i],  left[i] + right[i]))
      {
      std::cerr << "ERROR: Coordinate " << i << " of sum should be "
                << left[i] + right[i] << " but is " << sum[i] << "\n";
      ++error_count;
      }
    }

  point_type difference(a);
  boost::geometry::subtract_point(difference, b);
  std::cout << "Point subtraction: a - b = "
            << to_string(difference) << "\n";

  for (std::size_t i = 0; i < dimension; ++i)
    {
    if (!tracktable::almost_equal(difference[i], left[i] - right[i]))
      {
      std::cerr << "ERROR: Coordinate " << i << " of difference should be "
                << left[i] - right[i] << " but is " << difference[i] << "\n";
      ++error_count;
      }
    }

  point_type pointwise_product(a);
  boost::geometry::multiply_point(pointwise_product, b);
  std::cout << "Pointwise product: "
            << to_string(pointwise_product) << "\n";

  for (std::size_t i = 0; i < dimension; ++i)
    {
    if (!tracktable::almost_equal(pointwise_product[i], left[i] * right[i]))
      {
      std::cerr << "ERROR: Coordinate " << i << " of pointwise product should be "
                << left[i] * right[i] << " but is " << pointwise_product[i] << "\n";
      ++error_count;
      }
    }

  point_type pointwise_quotient(a);
  boost::geometry::divide_point(pointwise_quotient, b);
  std::cout << "Pointwise quotient: "
            << to_string(pointwise_quotient) << "\n";

  for (std::size_t i = 0; i < dimension; ++i)
    {
    if (!tracktable::almost_equal(pointwise_quotient[i], left[i] / right[i]))
      {
      std::cerr << "ERROR: Coordinate " << i << " of pointwise quotient should be "
                << left[i] / right[i] << " but is " << pointwise_quotient[i] << "\n";
      ++error_count;
      }
    }

  point_type scalar_product(a);
  boost::geometry::multiply_value(scalar_product, 2);
  std::cout << "Scalar product: "
            << to_string(scalar_product) << "\n";

  for (std::size_t i = 0; i < dimension; ++i)
    {
    if (!tracktable::almost_equal(scalar_product[i], left[i] * 2))
      {
      std::cerr << "ERROR: Coordinate " << i << " of scalar product should be "
                << left[i] * 2 << " but is " << scalar_product[i] << "\n";
      ++error_count;
      }
    }

  point_type scalar_quotient(a);
  boost::geometry::divide_value(scalar_quotient, 2);
  std::cout << "Scalar quotient: "
            << to_string(scalar_quotient) << "\n";


  for (std::size_t i = 0; i < dimension; ++i)
    {
    if (!tracktable::almost_equal(scalar_quotient[i],  (left[i] / 2)))
      {
      std::cerr << "ERROR: Coordinate " << i << " of scalar quotient should be "
                << left[i] / 2 << " but is " << scalar_quotient[i] << "\n";
      std::cerr << "    Difference is "
                << (left[i]/2) - scalar_quotient[i] << "\n";

      ++error_count;
      }
    }

  return error_count;
}

// ----------------------------------------------------------------------

bool test_point_cartesian()
{
  typedef tracktable::PointCartesian<2> point2_cartesian;
  typedef tracktable::PointCartesian<9> point9_cartesian;

  point2_cartesian a, b;
  a[0] = 1;
  a[1] = 2;
  b.set<0>(4);
  b.set<1>(6);

  point9_cartesian foo, bar;
  for (std::size_t i = 0; i < 9; ++i)
    {
    foo[i] = 3;
    bar[i] = 9;
    }

  std::cout << "Testing arithmetic on "
            << boost::geometry::traits::dimension<point2_cartesian>::value
            << "-D Cartesian points\n";
  int error_count1 = test_boost_point_arithmetic(a, b);

  std::cout << "\nTesting arithmetic on "
            << boost::geometry::traits::dimension<point9_cartesian>::value
            << "-D Cartesian points\n";
  int error_count2 = test_boost_point_arithmetic(foo, bar);

  double ab_distance = boost::geometry::distance(a, b);

  int error_count3 = 0;
  if (!tracktable::almost_equal(ab_distance, 5.0))
    {
    std::cerr << "ERROR: Distance between 2D points (1, 2) and (4, 6) should be 5 but is "
              << ab_distance << "\n";
    ++error_count3;
    }

  double foobar_distance = boost::geometry::distance(foo, bar);
  if (!tracktable::almost_equal(foobar_distance, 18.0))
    {
    std::cerr << "ERROR: Distance between 9D points [3]^9, [9]^9 should be 18 but is "
              << foobar_distance << "\n";
    ++error_count3;
    }

  return ( (error_count1 + error_count2 + error_count3) == 0 );
}

int main(int /*argc*/, char* /*argv*/[])
{
  bool result = test_point_cartesian();
  return (result == false);
}

