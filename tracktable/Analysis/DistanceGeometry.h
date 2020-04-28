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

#ifndef _DG_h
#define _DG_h

#include <vector>
#include <utility> // for std::pair
#include <tracktable/Core/Trajectory.h>


template<typename TrajectoryT>
double ControlPointDistance(TrajectoryT trajectory,
 std::pair<double,double> control_point) {
  return tracktable::distance(
    tracktable::point_at_length_fraction(trajectory,control_point.first),
    tracktable::point_at_length_fraction(trajectory,control_point.second));
}

// This routine returns a vector of distance geometries of length 
// depth * (depth+1)/2 for each trajectory.  The are all normalized to be 
// between 0 and 1.
template<typename TrajectoryT>
void GetDistanceGeometries(std::vector<TrajectoryT> &trajectories, 
 std::vector<std::vector<double> > &dgs, unsigned int depth)
{

  if (depth < 1)
    return;

  // This builds the different fractional intervals
  std::vector<std::pair<double,double> > control_points;
  for (unsigned int i = 1; i <= depth; ++i)
    for (unsigned int j = 0; j < i; ++j) {
      double start = static_cast<double>(j)/static_cast<double>(i);
      double stop = static_cast<double>(j+1)/static_cast<double>(i);
      control_points.push_back(std::make_pair(start,stop));
    }

  for (unsigned int i = 0; i < trajectories.size(); ++i) {
    std::vector<double> dists;
    double length = tracktable::length(trajectories[i]);

    // Build the distances for all of the control points
    for (unsigned int j = 0; j < control_points.size(); ++j)
      dists.push_back(ControlPointDistance(trajectories[i],control_points[j]));

    // Normalize them all with respect to fraction of total length
    // If it is a zero length trajectory, in theory we could just ignore it
    // but this could cause some misalignment with the trajectory vector that
    // the user may want.  So, so just give it a default value.  Really, the
    // user should be filtering for zero length trajectories
    unsigned int cur = 0;
    for (unsigned int j = 1; j <= depth; ++j)
      for (unsigned int k = 0; k < j; ++k)
        if (length == 0.0)
          dists[cur++] = 1.0;  // Need a default behavior, either this or 0.0
        else
          dists[cur++] /= length/static_cast<double>(j);

    dgs.push_back(dists);
  }
  
  return;
}
#endif
