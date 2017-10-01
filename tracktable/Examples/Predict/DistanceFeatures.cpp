/*
 * Copyright (c) 2015-2017 National Technology and Engineering
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
#include "DistanceFeatures.h"
#include "Interpolate.h"

void DistanceFeatures(Trajectories &my_trajectories, Features& features)
{
  std::vector<std::pair<double,double> > control_points;
  for (int i = 1; i <= 4; ++i)
    for (int j = 0; j < i; ++j) {
      double start = static_cast<double>(j)/static_cast<double>(i);
      double stop = static_cast<double>(j+1)/static_cast<double>(i);
      control_points.push_back(std::make_pair(start,stop));
    }

  for (unsigned int i = 0; i < my_trajectories.size(); ++i) {
    std::vector<double>dists;
    for (unsigned int j = 0; j < control_points.size(); ++j) {
      dists.push_back(boost::geometry::distance(
       GetInterpolatedPoint(my_trajectories[i],control_points[j].first),
       GetInterpolatedPoint(my_trajectories[i],control_points[j].second)));
    }
    double length = boost::geometry::length(my_trajectories[i]);
    std::transform(dists.begin(),dists.end(),dists.begin(),
     boost::bind(std::divides<double>(),_1,length));

    Feature temp;
    for (unsigned int j = 0; j < 10; ++j)
      temp[j] = dists[j];

    features.push_back(temp);
  }

  return;
}
