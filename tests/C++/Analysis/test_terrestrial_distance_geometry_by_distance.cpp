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
#include <tracktable/Domain/Terrestrial.h>

#include <iostream>


typedef tracktable::domain::terrestrial::trajectory_point_type TerrestrialTrajectoryPoint;
typedef tracktable::domain::terrestrial::trajectory_type TerrestrialTrajectory;


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

TerrestrialTrajectoryPoint
create_terrestrial_trajectory_point(double longitude,
                                    double latitude,
                                    std::string const& id=std::string())
{
    TerrestrialTrajectoryPoint point;
    point.set_object_id(id);
    point.set_longitude(longitude);
    point.set_latitude(latitude);

    return point;
}

// --------------------------------------------------------------------

int test_terrestrial_dg_by_distance()
{
  int error_count = 0;

  double terrestrial_coordinates[][2] = {
    {0, 80},
    {90, 80},
    {180, 80},
    {-90, 80},
    {0, 80},
    {-1000, -1000}
  };

  TerrestrialTrajectory trajectory;
  int i = 0;
  while (terrestrial_coordinates[i][0] > -1000)
  {
    trajectory.push_back(
      create_terrestrial_trajectory_point(
        terrestrial_coordinates[i][0],
        terrestrial_coordinates[i][1],
        "terrestrial_dg_test"
        ));
    ++i;
  }

  std::vector<double> terrestrial_dg = tracktable::distance_geometry_by_distance(trajectory, 4);

  // As counterintuitive as it may appear, these values are actually correct.
  // The sample trajectory is a circle around the North Pole at latitude 80N.
  // When we compute distances on the sphere, we do so with great-circle arcs.
  // At that high latitude, the great circle is significantly different from
  // the "horizontal" (constant-latitude) segments that humans will naturally
  // draw for the trajectory.
  std::vector<double> expected_dg_values = {
    0.0,
    0.708916,
    0.708916,
    0.793393,
    0.710916,
    0.793393,
    0.999999,
    0.999999,
    0.999999,
    0.999999};

  error_count += compare_vectors(
    expected_dg_values,
    terrestrial_dg,
    1e-4,
    "terrestrial distance geometry"
    );

  return error_count;
}

// --------------------------------------------------------------------
int
main(int , char**)
{
  int error_count = 0;

  error_count += test_terrestrial_dg_by_distance();

  return error_count;
}
