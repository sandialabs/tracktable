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

/*
 * NOTE: We use PointCartesian and PointLonLat here as lowest common
 * denominators.  You are cordially discouraged from using PointLonLat
 * and PointCartesian in your own code: we recommend
 * tracktable::domain::terrestrial and tracktable::domain::cartesian2d
 * instead.
 */


#include <tracktable/Analysis/ComputeDBSCANClustering.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>

#include <boost/geometry/arithmetic/arithmetic.hpp>

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_real_distribution.hpp>

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>

boost::random::mt19937 random_generator;
boost::random::uniform_real_distribution<> random_die(0, 1);

double random_float()
{
  double randomness(random_die(random_generator));
  return randomness;
}

// ----------------------------------------------------------------------

double random_gaussian(double mean=0, double stddev=1)
{
  double u1 = random_float();
  double u2 = random_float();

  return mean + stddev*(sqrt(-2 * log(u1)) * sin(2*M_PI*u2));
}

// ----------------------------------------------------------------------

template<int dim>
tracktable::PointCartesian<dim> random_point_in_sphere(double sphere_radius=1)
{
  typedef tracktable::PointCartesian<dim> point_t;

  point_t result(tracktable::arithmetic::zero<point_t>());
  double squared_magnitude = 0;
  for (int i = 0; i < dim; ++i)
    {
    // YOU ARE HERE
    double rg = random_gaussian();
    squared_magnitude += rg*rg;
    result[i] = rg;
    }

  boost::geometry::divide_value(result, sqrt(squared_magnitude));

  // now scale it down to somewhere within the sphere
  boost::geometry::multiply_value(result, sphere_radius * pow(random_float(), 1.0 / dim));
  return result;
}

// ----------------------------------------------------------------------

template<int dim>
void point_cloud_at_hypercube_vertices(int points_per_cloud,
                                       double cloud_radius,
                                       std::vector< tracktable::PointCartesian<dim> >& out_points,
                                       std::vector<int>& out_labels)
{
  // To generate all the edges of a hypercube we use the following
  // procedure:
  //
  // Take a d-dimensional integer and count from 0 to 2^d - 1 (all
  // ones).  Each of these numbers specifies one vertex of the
  // hypercube: if a given bit is 0, the coordinate for that dimension
  // is -1.  If a given bit is 1, the coordinate is 1.
  //
  // We can visit each edge once by watching for the bits that are
  // zero.  Whenever we see one, sample from -1 to 1 along that axis.

  typedef tracktable::PointCartesian<dim> point_t;

  std::cout << "TEST: Iterating over " << (1 << dim) << " hypercube vertices.\n";
  for (int vertex_id = 0; vertex_id < (1 << dim); ++vertex_id)
    {
    point_t corner_vertex;
    for (int d = 0; d < dim; ++d)
      {
      if ((vertex_id & (1 << d)) == 0)
        {
        corner_vertex[d] = -1;
        }
      else
        {
        corner_vertex[d] = 1;
        }
      }

    out_points.push_back(corner_vertex);
    out_labels.push_back(vertex_id);

    for (int i = 0; i < points_per_cloud; ++i)
      {
      point_t offset(random_point_in_sphere<dim>(cloud_radius));
//      std::cout << "random point in sphere: " << offset << "\n";
      point_t new_point(corner_vertex);
      boost::geometry::add_point(new_point, offset);

      out_points.push_back(new_point);
      out_labels.push_back(vertex_id);
      }
    }
}

// ----------------------------------------------------------------------

int test_dbscan_cs_test()
{
  typedef tracktable::PointCartesian<2> point_type;
  std::vector<point_type> hd_points;
  std::vector<int> labels;
  int dimension = 2;

  std::cout << "test_dbscan: Generating point clouds at vertices of "
            << dimension << "-dimensional hypercube\n";
  point_cloud_at_hypercube_vertices<2>(100, 0.25, hd_points, labels);

  point_type epsilon_halfspan;

  for (int d = 0; d < dimension; ++d)
    {
    epsilon_halfspan[d] = 0.2;
    }


  std::vector<int> cluster_labels;

  int num_clusters = tracktable::cluster_with_dbscan<point_type>(
    hd_points.begin(),
    hd_points.end(),
    epsilon_halfspan,
    10,
    cluster_labels
    );

  std::cout << "cluster_with_dbscan: "
            << num_clusters
            << " detected\n";

  std::cout << "cluster labels:";
  for (std::vector<int>::iterator iter = cluster_labels.begin();
       iter != cluster_labels.end();
       ++iter)
    {
    std::cout << " " << *iter;
    }
  std::cout << "\n";
  return num_clusters;
}

// ----------------------------------------------------------------------

int
main(int argc, char* argv[])
{
  int num_clusters_found = test_dbscan_cs_test();
  if (num_clusters_found != 5)
    {
    std::cerr << "ERROR: Expected 4 non-noise clusters but found "
              << num_clusters_found << "\n";
    return 1;
    }
  else
    {
    std::cerr << "SUCCESS: Found the expected 4 non-noise clusters\n";
    return 0;
    }
}
