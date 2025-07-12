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

#include <tracktable/Domain/Terrestrial.h>

#include <iostream>
#include <sstream>

// ----------------------------------------------------------------------

template<class T>
std::string to_string(T const& thing)
{
  return thing.to_string();
}


// ----------------------------------------------------------------------

template<int coord, class point_type>
int test_expected_value(point_type const& value, double expected_result)
{
  if (tracktable::almost_equal(value.template get<coord>(),  expected_result))
    {
    return 0;
    }
  else
    {
    std::cout << "ERROR: Component " << coord << " of value "
              << to_string(value) << " should have been " << expected_result << "\n";
    return 1;
    }
}

// ----------------------------------------------------------------------

template<class point_type>
int test_boost_point_arithmetic(point_type const& left, point_type const& right)
{
  int error_count = 0;

  point_type a(left);
  point_type b = right;

  point_type sum(a);
  boost::geometry::add_point(sum, b);
  std::cout << "Point addition: a + b = "
            << to_string(sum) << "\n";

  error_count += test_expected_value<0>(sum, left.template get<0>() + right.template get<0>());
  error_count += test_expected_value<1>(sum, left.template get<1>() + right.template get<1>());

  point_type difference(a);
  boost::geometry::subtract_point(difference, b);
  std::cout << "Point subtraction: a - b = "
            << to_string(difference) << "\n";

  error_count += test_expected_value<0>(difference, left.template get<0>() - right.template get<0>());
  error_count += test_expected_value<1>(difference, left.template get<1>() - right.template get<1>());

  point_type pointwise_product(a);
  boost::geometry::multiply_point(pointwise_product, b);
  std::cout << "Pointwise product: "
            << to_string(pointwise_product) << "\n";

  error_count += test_expected_value<0>(pointwise_product, left.template get<0>() * right.template get<0>());
  error_count += test_expected_value<1>(pointwise_product, left.template get<1>() * right.template get<1>());

  point_type pointwise_quotient(a);
  boost::geometry::divide_point(pointwise_quotient, b);
  std::cout << "Pointwise quotient: "
            << to_string(pointwise_quotient) << "\n";

  error_count += test_expected_value<0>(pointwise_quotient, left.template get<0>() / right.template get<0>());
  error_count += test_expected_value<1>(pointwise_quotient, left.template get<1>() / right.template get<1>());

  point_type scalar_product(a);
  boost::geometry::multiply_value(scalar_product, 2);
  std::cout << "Scalar product: "
            << to_string(scalar_product) << "\n";

  error_count += test_expected_value<0>(scalar_product, left.template get<0>() * 2);
  error_count += test_expected_value<1>(scalar_product, left.template get<1>() * 2);

  point_type scalar_quotient(a);
  boost::geometry::divide_value(scalar_quotient, 2);
  std::cout << "Scalar quotient: "
            << to_string(scalar_quotient) << "\n";

  error_count += test_expected_value<0>(scalar_quotient, left.template get<0>() / 2);
  error_count += test_expected_value<1>(scalar_quotient, left.template get<1>() / 2);

  double how_far = distance(left, right);
//  double other_distance = left.distance_to(right);
  std::cout << "Geographic distance between points: " << how_far << "\n";

  return error_count;
}

int test_point_lonlat()
{
  typedef tracktable::domain::terrestrial::base_point_type point2_lonlat;
  int error_count = 0;

  point2_lonlat albuquerque, wellington, new_york, north_pole, south_pole, roswell, santa_fe;
  point2_lonlat access_test;

  tracktable::set_latitude_from_degrees(access_test, 40.0);
  tracktable::set_longitude_from_degrees(access_test, -120.0);

  if (!tracktable::almost_equal(tracktable::latitude_as_degrees(access_test),
				40.0))
    {
      error_count += 1;
      std::cout << "ERROR: latitude_as_degrees: Expected 40.0, got "
		<< tracktable::latitude_as_degrees(access_test)
		<< "\n";
    }

  if (!tracktable::almost_equal(tracktable::longitude_as_degrees(access_test),
				-120.0))
    {
      error_count += 1;
      std::cout << "ERROR: longitude_as_degrees: Expected -120.0, got "
		<< tracktable::longitude_as_degrees(access_test)
		<< "\n";
    }

  tracktable::set_latitude_from_radians(access_test, 1.57);
  tracktable::set_longitude_from_radians(access_test, -1.57);

  if (!tracktable::almost_equal(tracktable::latitude_as_radians(access_test),
				1.57))
    {
      error_count += 1;
      std::cout << "ERROR: latitude_as_radians: Expected 1.57, got "
		<< tracktable::latitude_as_degrees(access_test)
		<< "\n";
    }

  if (!tracktable::almost_equal(tracktable::longitude_as_radians(access_test),
				-1.57))
    {
      error_count += 1;
      std::cout << "ERROR: longitude_as_radians: Expected -1.57, got "
		<< tracktable::longitude_as_degrees(access_test)
		<< "\n";
    }

  santa_fe.set_latitude(35.6672);
  santa_fe.set_longitude(-105.9644);

  roswell.set_latitude(33.3872);
  roswell.set_longitude(-104.5281);

  std::cout << "Turn angle from ABQ to Santa Fe to Roswell: "
            << signed_turn_angle(albuquerque, santa_fe, roswell)
            << "\n";

  albuquerque.set_latitude(35.1107);
  albuquerque.set_longitude(-106.6100);

  new_york.set_latitude(40.7127);
  new_york.set_longitude(-74.0059);

  wellington.set_latitude(-41.2889);
  wellington.set_longitude(174.7772);

  north_pole.set_longitude(0);
  north_pole.set_latitude(90);
  south_pole.set_longitude(0);
  south_pole.set_latitude(-90);

  std::cout << "Distance between north and south poles: "
            << distance(north_pole, south_pole)
            << "\n";

  std::cout << "\nTesting arithmetic on "
            << boost::geometry::traits::dimension<point2_lonlat>::value
            << "-D lon/lat points\n";

  std::cout << "Distance from Albuquerque to New York: "
            << distance(albuquerque, new_york) << "\n";

  // If the radius of the Earth is 3959 miles then this comes out to
  // be 1808.099 miles
  double abq_ny_distance = distance(albuquerque, new_york);

  if (floor(abq_ny_distance) != 2909)
    {
    std::cout << "ERROR: Calculated distance between Albuquerque and New York should be about 2909 miles but is instead "
              << abq_ny_distance << "\n";
    ++error_count;
    }
  error_count += test_boost_point_arithmetic(albuquerque, wellington);
  std::cout << "test_point_lonlat: Error count is " << error_count << "\n";
  return error_count;
}

int main(int /*argc*/, char* /*argv*/[])
{
  return test_point_lonlat();
}

