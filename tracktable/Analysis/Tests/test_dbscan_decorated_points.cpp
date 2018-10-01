/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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

#include <tracktable/Analysis/DBSCAN.h>
#include <tracktable/Domain/FeatureVectors.h>


#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_real_distribution.hpp>


#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <cstdlib>
#include <iostream>
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
tracktable::FeatureVector<dim> random_point_in_sphere(double sphere_radius=1)
{
  typedef tracktable::FeatureVector<dim> point_t;

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

template<
  int dim,
  typename PointOutputIteratorT,
  typename LabelOutputIteratorT
  >
void point_cloud_at_hypercube_vertices(int points_per_cloud,
                                       double cloud_radius,
                                       PointOutputIteratorT point_sink,
                                       LabelOutputIteratorT label_sink)
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

  typedef tracktable::FeatureVector<dim> point_t;

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

    *point_sink = corner_vertex;
    ++point_sink;
    *label_sink = vertex_id;
    ++label_sink;

    for (int i = 0; i < points_per_cloud; ++i)
      {
      point_t offset(random_point_in_sphere<dim>(cloud_radius));
      point_t new_point(corner_vertex);
      boost::geometry::add_point(new_point, offset);

      *out_points++ = new_point;
      *out_labels++ = vertex_id;
      }
    }
}

// ----------------------------------------------------------------------

template<int dimension>
void test_dbscan()
{
  typedef tracktable::FeatureVector<dimension> point_type;
  typedef std::pair<int, point_type> labeled_point_type;
  typedef std::pair<int, int> cluster_result_type;
  typedef std::vector<point_type> point_vector_type;
  typedef std::vector<int> label_vector_type;
  
  typedef std::vector<labeled_point_type> labeled_point_vector_type;
  typedef std::vector<cluster_result_type> cluster_result_vector_type;


  std::cout << "test_dbscan_decorated_points: "
            << "Generating point clouds at vertices of "
            << dimension << "-dimensional hypercube\n";
  point_vector_type hd_points;
  label_vector_type vertex_ids;
  point_cloud_at_hypercube_vertices<dimension>(100, 0.25, hd_points, vertex_ids);

  tracktable::DBSCAN<point_type> dbscan;
  point_type epsilon_halfspan;
  for (int d = 0; d < dimension; ++d)
    {
    epsilon_halfspan[d] = 0.2;
    }


  labeled_point_vector_type labeled_points;
  point_vector_type::iterator point_iter = hd_points.begin();
  label_vector_type::iterator vertex_id_iter = vertex_ids.begin();

  std::vector<cluster_result_type> dbscan_results;
  
  for (; point_iter != hd_points.end(); ++point_iter, ++vertex_id_iter)
    {
    labeled_points.push_back(labeled_point_type(100 * (*vertex_id_iter),  *point_iter));
    }

  int num_clusters = tracktable::cluster_with_dbscan(
    labeled_points.begin(),
    labeled_points.end(),
    epsilon_halfspan,
    10,
    std::insert_iterator<std::vector<cluster_result_type> >(dbscan_results,
                                                            dbscan_results.begin()));

  std::cout << "Vertex ID and cluster label for each point:\n";

  for (cluster_result_vector_type::iterator iter = dbscan_results.begin();
       iter != dbscan_results.end();
       ++iter)
    {
    std::cout << "Vertex ID " << iter->first << " belongs to cluster "
              << iter->second << "\n";
    }
  std::cout << "Done testing DBSCAN with labeled points.";

}

// ----------------------------------------------------------------------

int
main(int argc, char* argv[])
{
  test_dbscan<3>();
}
