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
 * NOTE: We use PointCartesian here as a lowest common denominator.
 * You are cordially discouraged from using PointLonLat and
 * PointCartesian in your own code: we recommend
 * tracktable::domain::terrestrial and tracktable::domain::cartesian2d
 * instead.
 */

#include <tracktable/Analysis/ComputeDBSCANClustering.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>

#define BOOST_ALLOW_DEPRECATED_HEADERS
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_real_distribution.hpp>
#undef BOOST_ALLOW_DEPRECATED_HEADERS


#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>

namespace {
  static const double PI = 3.141592653589793238462643383;
}

// ----------------------------------------------------------------------

boost::random::mt19937 random_generator;
boost::random::uniform_real_distribution<> random_die(0);

inline double random_float(double min=0, double max=1)
{
  double span = max - min;
  return (random_die(random_generator) * span) + min;
}

// ----------------------------------------------------------------------

double random_gaussian(double mean=0, double stddev=1)
{
  double u = random_float();
  double v = random_float();

  // This is the Box-Muller transform.  Given two random numbers u, v
  // distributed uniformly on [0, 1],
  //
  // y1 = sqrt(-2 log u) * cos(2 \pi v)
  // y2 = sqrt(-2 log u) * sin(2 \pi v)
  //
  // y1 and y2 will be independent and normally distributed.

  return mean + stddev * (sqrt(-2 * log(u)) * sin(2*PI*v));
}

// ----------------------------------------------------------------------

template<int dim>
tracktable::PointCartesian<dim> random_point_in_sphere(double sphere_radius=1)
{
  typedef tracktable::PointCartesian<dim> point_t;

  point_t result((tracktable::arithmetic::zero<point_t>()));

  double squared_magnitude = 0;
  for (int i = 0; i < dim; ++i)
    {
    // YOU ARE HERE
    double rg = random_gaussian();
    squared_magnitude += rg*rg;
    result[i] = rg;
    }

//  std::cout << "raw point: " << result << " mag2: " << squared_magnitude << "\n";
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

      std::cout << "corner vertex: " << corner_vertex << " offset: " << offset << "\n";
      out_points.push_back(new_point);
      out_labels.push_back(vertex_id);
      }
    }
}

// ----------------------------------------------------------------------

template<int dimension>
void test_dbscan()
{
  typedef tracktable::PointCartesian<dimension> point_type;
  typedef std::pair<int, int> cluster_label_type;
  std::vector<point_type> hd_points;
  std::vector<int> labels;
  std::vector<cluster_label_type> dbscan_results;

  std::cout << "test_dbscan: Generating point clouds at vertices of "
            << dimension << "-dimensional hypercube\n";
  point_cloud_at_hypercube_vertices<dimension>(100, 0.1, hd_points, labels);

  for (typename std::vector<point_type>::iterator iter = hd_points.begin();
       iter != hd_points.end();
       ++iter)
    {
    std::cout << "point: " << *iter << "\n";
    }

  point_type epsilon_halfspan;

  for (int d = 0; d < dimension; ++d)
    {
    epsilon_halfspan[d] = 0.1;
    }


  std::cout << "test_dbscan: Learning cluster assignments\n";
  tracktable::cluster_with_dbscan(
    hd_points.begin(),
    hd_points.end(),
    epsilon_halfspan,
    10,
    std::back_inserter(dbscan_results));


  std::cout << "Vertex labels of points in each cluster:\n";
  for (std::size_t i = 0; i < dbscan_results.size(); ++i)
    {
    std::cout << "Vertex " << dbscan_results[i].first << ": cluster "
              << dbscan_results[i].second << "\n";
    }

  std::cout << "Done testing DBSCAN in "
            << dimension << " dimensions.\n";

}

// ----------------------------------------------------------------------

int
main(int , char**)
{
  test_dbscan<2>();
}
