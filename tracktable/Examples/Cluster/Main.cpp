/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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

#include <boost/bind.hpp>
#include <boost/geometry/geometries/linestring.hpp>

#include <tracktable/Domain/FeatureVectors.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Analysis/ComputeDBSCANClustering.h>

#include "Common.h"
#include "BuildTrajectories.h"
#include "CommandLineOptions.h"
#include "KmlOut.h"
#include "ParseCommandLine.h"

typedef tracktable::domain::feature_vectors::FeatureVector<10> feature_vector;

trajectory_point_type GetInterpolatedPoint(trajectory_type trajectory,
 double frac) {
  return tracktable::point_at_time(trajectory,
   tracktable::interpolate(trajectory.start_time(),
   trajectory.end_time(),frac));
}

double ControlPointDistance(trajectory_type trajectory,
 std::pair<double,double> control_point) {
  return boost::geometry::distance(
    GetInterpolatedPoint(trajectory,control_point.first),
    GetInterpolatedPoint(trajectory,control_point.second));
}

void Correlation(std::vector<feature_vector>& features);

int main(int argc, char* argv[])
{

  CommandLineOptions options = ParseCommandLine(argc, argv);

  // Example: read in trajectories
  std::vector<trajectory_type> trajectories;
  BuildTrajectories<trajectory_type>(options,trajectories);

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(&boost::geometry::length<trajectory_type>,_1) <= 0.0),
   trajectories.end());
/*
  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(std::divides<double>(),
   boost::bind(&tracktable::end_to_end_distance<trajectory_type>,_1),
   boost::bind(&tracktable::length<trajectory_type>,_1)) > 0.5),
   trajectories.end());
*/
  // Example: create some feature vectors
  std::vector<feature_vector> features;

  std::vector<std::pair<double,double> > control_points;
  for (unsigned int i = 1; i <= 4; ++i)
    for (unsigned int j = 0; j < i; ++j) {
      double start = static_cast<double>(j)/static_cast<double>(i);
      double stop = static_cast<double>(j+1)/static_cast<double>(i);
      control_points.push_back(std::make_pair(start,stop));
    }

  for (unsigned int i = 0; i < trajectories.size(); ++i) {
    feature_vector dists;
    double length = boost::geometry::length(trajectories[i]);
    if (length == 0.0)
      continue;

    for (unsigned int j = 0; j < control_points.size(); ++j)
      dists[j] = ControlPointDistance(trajectories[i],control_points[j]);


    unsigned int cur = 0;
    for (unsigned int j = 1; j <= 4; ++j)
      for (unsigned int k = 0; k < j; ++k)
        dists[cur++] /= length/static_cast<double>(j);

    features.push_back(dists);
  }

  for (unsigned int i = 0; i < 10; ++i) {
    for (unsigned int j = 0; j < features.size(); ++j)
      std::cout << features[j][i] << " ";
    std::cout << std::endl;
  }
  exit(0);

  typedef std::pair<int, int> cluster_label_type;
  typedef std::vector<cluster_label_type> cluster_label_vector_type;
  typedef std::vector<int> vertex_id_vector_type;

  feature_vector search_box;
  for (unsigned int i = 0; i < 10; ++i)
    search_box[i] = 0.1;

  cluster_label_vector_type vertex_cluster_labels;
  tracktable::cluster_with_dbscan(
    features.begin(),
    features.end(),
    search_box,
    3,
    std::back_inserter(vertex_cluster_labels)
  );

  std::vector<vertex_id_vector_type> membership;
  tracktable::build_cluster_membership_lists(
    vertex_cluster_labels.begin(),
    vertex_cluster_labels.end(),
    std::back_inserter(membership)
  );

  for (unsigned int i = 0; i < membership.size(); ++i) {
    std::cout << i << "(" << membership[i].size() << "):";
    feature_vector avg;
    avg = tracktable::arithmetic::zero<feature_vector>();
    for (unsigned int j = 0; j < membership[i].size(); ++j) {
//      std::cout << trajectories[membership[i][j]].object_id() << " ";
      tracktable::arithmetic::add_in_place(avg,features[membership[i][j]]);
    }
    tracktable::arithmetic::divide_scalar_in_place(
     avg,static_cast<double>(membership[i].size()));
    std::cout << avg;
    std::cout << std::endl;
  }

  Correlation(features);
/*
  for (unsigned int clus_num = 2;
   clus_num <= 20 && clus_num < membership.size(); ++clus_num) {
    for (unsigned int i = 0; i < membership[clus_num].size(); ++i) {
      std::string s = "output" +
       boost::lexical_cast<std::string>(clus_num) + "/"
       + trajectories[membership[clus_num][i]].object_id() + ".kml";
      std::ofstream outfile(s.c_str());
      writeKmlTrajectory(trajectories[membership[clus_num][i]],
       outfile,"FFFFFFFF",2.0);
      outfile.clear();
      outfile.close();
    }
  }
*/
  return 0;
}
