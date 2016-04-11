/*
 * Copyright (c) 2015, Sandia Corporation.  All rights
 * reserved.
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

#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Analysis/DBSCAN.h>

#include "AssignLengths.h"
#include "Common.h"
#include "Correlation.h"
#include "BuildTrajectories.h"
#include "CommandLineOptions.h"
#include "Interpolate.h"
#include "KmlOut.h"
#include "ParseCommandLine.h"

double ControlPointDistance(trajectory_type trajectory, 
 std::pair<double,double> control_point) {
  return boost::geometry::distance(
    GetLengthInterpolatedPoint(trajectory,control_point.first),
    GetLengthInterpolatedPoint(trajectory,control_point.second));
}

int main(int argc, char* argv[])
{

  CommandLineOptions options = ParseCommandLine(argc, argv);

  // Example: read in trajectories
  std::vector<trajectory_type> trajectories;
  BuildTrajectories<trajectory_type>(options,trajectories);

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
//   boost::bind(&boost::geometry::length<trajectory_type>,_1) <= 0.0),
   boost::bind(&tracktable::length<trajectory_type>,_1) <= 100.0),
   trajectories.end());

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(std::divides<double>(),
   boost::bind(&tracktable::end_to_end_distance<trajectory_type>,_1),
   boost::bind(&tracktable::length<trajectory_type>,_1)) > 0.5),
   trajectories.end());

  AssignTrajectoriesLengths(trajectories);
  // Example: create some feature vectors
  std::vector<feature_vector> features;

  std::vector<std::pair<double,double> > control_points;
  for (unsigned int i = 1; i <= 5; ++i)
    for (unsigned int j = 0; j < i; ++j) {
      double start = static_cast<double>(j)/static_cast<double>(i);
      double stop = static_cast<double>(j+1)/static_cast<double>(i);
      control_points.push_back(std::make_pair(start,stop));
    }

  for (unsigned int i = 0; i < trajectories.size(); ++i) {
    feature_vector dists;
    double length = boost::geometry::length(trajectories[i]);

    for (unsigned int j = 0; j < control_points.size(); ++j)
      dists[j] = ControlPointDistance(trajectories[i],control_points[j]);


    unsigned int cur = 0;
    for (unsigned int j = 1; j <= 5; ++j)
      for (unsigned int k = 0; k < j; ++k)
        dists[cur++] /= length/static_cast<double>(j);

    features.push_back(dists);
  }

  tracktable::DBSCAN<feature_vector> dbscan;
  feature_vector search_box;
  for (unsigned int i = 0; i < 15; ++i)
    search_box[i] = 0.1;

  dbscan.learn_clusters(features.begin(),features.end(),search_box,3);

  std::vector<std::vector<int> > membership;
  dbscan.cluster_membership_lists(membership);
  for (unsigned int i = 0; i < membership.size(); ++i) {
    std::cout << i << "(" << membership[i].size() << "):";
    feature_vector avg;
    avg = tracktable::arithmetic::zero<feature_vector>();
    for (unsigned int j = 0; j < membership[i].size(); ++j) {
      std::cout << trajectories[membership[i][j]].object_id() << " ";
      tracktable::arithmetic::add_in_place(avg,features[membership[i][j]]);
    }
    tracktable::arithmetic::divide_scalar_in_place(
     avg,static_cast<double>(membership[i].size()));
    std::cout << avg;
    std::cout << std::endl;
  }

  Correlation(features);

  for (unsigned int clus_num = 1; 
   clus_num <= 50 && clus_num < membership.size(); ++clus_num) {
    for (unsigned int i = 0; i < membership[clus_num].size(); ++i) {
      std::string s = "output" + 
       boost::lexical_cast<std::string>(clus_num) + "/" 
       + trajectories[membership[clus_num][i]].object_id() + "-" +
       boost::gregorian::to_simple_string(trajectories[membership[clus_num][i]].start_time().date()) + ".kml";
      std::ofstream outfile(s.c_str());
      writeKmlTrajectory(trajectories[membership[clus_num][i]],
       outfile,"FFFFFFFF",2.0);
      outfile.clear();
      outfile.close();
    }
  }

  return 0;
}
