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
 
#define _USE_MATH_DEFINES
#include <cmath>

#include <tracktable/Analysis/DBSCAN.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_real_distribution.hpp>

#include <cstdlib>
#include <limits>

// ----------------------------------------------------------------------

boost::random::mt19937 random_generator;
boost::random::uniform_real_distribution<> random_die(-1, 1);

double random_float()
{
  return random_die(random_generator) * std::numeric_limits<double>::max();
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

  point_t result((tracktable::arithmetic::zero<point_t>()));
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

template<int dimension>
void test_dbscan()
{
  typedef tracktable::PointCartesian<dimension> point_type;
  std::vector<point_type> hd_points;
  std::vector<int> labels;

  std::cout << "test_dbscan: Generating point clouds at vertices of "
            << dimension << "-dimensional hypercube\n";
  point_cloud_at_hypercube_vertices<dimension>(100, 0.25, hd_points, labels);

  tracktable::DBSCAN<point_type> dbscan;
  point_type epsilon_halfspan;

  for (int d = 0; d < dimension; ++d)
    {
    epsilon_halfspan[d] = 0.2;
    }

  std::cout << "test_dbscan: Learning cluster assignments\n";
  dbscan.learn_clusters(hd_points.begin(),
                        hd_points.end(),
                        epsilon_halfspan,
                        10);

  typedef std::vector<int> int_vector;
  typedef std::vector<int_vector> int_vector_vector;

  std::cout << "test_dbscan: Retrieving cluster membership lists\n";
  int_vector_vector clusters;
  dbscan.cluster_membership_lists(clusters);

  std::cout << "Vertex labels of points in each cluster:\n";

  for (unsigned int cluster_id = 0; cluster_id < clusters.size(); ++cluster_id)
    {
    std::cout << "cluster " << cluster_id << ": "
              << clusters[cluster_id].size() << " members: ";

    for (unsigned int i = 0; i < clusters[cluster_id].size(); ++i)
      {
      std::cout << labels[clusters[cluster_id][i]] << " ";
      }
    std::cout << "\n";
    }

  std::cout << "Done testing DBSCAN in "
            << dimension << " dimensions.\n";

}

// ----------------------------------------------------------------------

int
main(int argc, char* argv[])
{
  test_dbscan<2>();
}
