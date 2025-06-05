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
 * 2. Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following
 * disclaimer in the documentation and/or other materials provided
 * with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// test_distance_geometry_by_distance -- exercise distance_geometry
// with control points selected by distance traveled

#include <tracktable/Analysis/DistanceGeometry.h>
#include <tracktable/Domain/Cartesian2D.h>

#include <iostream>

typedef tracktable::domain::cartesian2d::trajectory_point_type Cartesian2dTrajectoryPoint;
typedef tracktable::domain::cartesian2d::trajectory_type Cartesian2dTrajectory;

template<typename value_type>
int
compare_vectors(
  std::vector<value_type> const& expected,
  std::vector<value_type> const& actual,
  double equality_tolerance=1e-5,
  std::string const& description="unnamed vector"
  )
{
  int error_count = 0;
  if (expected.size() != actual.size())
  {
    std::cout << "ERROR: compare_vectors ("
              << description
              << "): Vectors differ in size.  Expected "
              << expected.size()
              << " but got "
              << actual.size()
              << ".\n";
    return 1;
  }

  for (std::size_t i = 0; i < expected.size(); ++i)
  {
    if (!tracktable::almost_equal(
          expected[i], actual[i], equality_tolerance
          ))
    {
      ++error_count;
      std::cout << "ERROR: compare_vectors ("
                << description
                << "): Element "
                << i
                << " does not match expected value. "
                << "Expected " << expected[i]
                << ", got " << actual[i]
                << ".\n";
    }
  }
  return error_count;
}

//----------------------------------------------------

Cartesian2dTrajectoryPoint
create_cartesian2d_trajectory_point(double x, double y, std::string const& id=std::string())
{
    Cartesian2dTrajectoryPoint point;
    point[0] = x;
    point[1] = y;
    point.set_object_id(id);
    return point;
}

// --------------------------------------------------------------------

int test_cartesian2d_dg_by_distance()
{
  int error_count = 0;

  double cartesian_coordinates[][2] = {
    {0, 0},
    {100, 0},
    {100, 100},
    {0, 100},
    {0, 0},
    {-1000, -1000}
  };

  Cartesian2dTrajectory trajectory;
  int i = 0;
  while (cartesian_coordinates[i][0] > -1000)
  {
    trajectory.push_back(
      create_cartesian2d_trajectory_point(
        cartesian_coordinates[i][0],
        cartesian_coordinates[i][1],
        "cartesian2d_dg_test"
        ));
    ++i;
  }

  std::vector<double> cartesian2d_dg = tracktable::distance_geometry_by_distance(trajectory, 4);

  std::vector<double> expected_dg_values = {
    0.0,
    0.707107,
    0.707107,
    0.790569,
    0.707107,
    0.790569,
    1.0,
    1.0,
    1.0,
    1.0};

  error_count += compare_vectors(
    expected_dg_values,
    cartesian2d_dg,
    1e-4,
    "Cartesian distance geometry"
    );

  return error_count;
}

// --------------------------------------------------------------------
int
main(int , char**)
{
  int error_count = 0;

  error_count += test_cartesian2d_dg_by_distance();

  return error_count;
}
