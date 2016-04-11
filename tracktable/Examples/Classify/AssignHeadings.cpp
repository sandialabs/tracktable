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

#include <algorithm>
#include "AssignHeadings.h"

void AssignTrajectoriesHeadings(std::vector<trajectory_type> &trajectories)
{
  std::for_each(trajectories.begin(),trajectories.end(),
   AssignTrajectoryHeadings);

  return;
}

void AssignTrajectoryHeadings(trajectory_type &trajectory)
{
  if (trajectory.size() == 0)
    return;
  if (trajectory.size() == 1) {
    trajectory[0].set_property("heading",0.0);
    return;
  }
    
  for (unsigned int i = 0; i < trajectory.size()-1; ++i)
    trajectory[i].set_property("heading", 
     tracktable::bearing(trajectory[i],trajectory[i+1]));
  trajectory[trajectory.size()-1] = trajectory[trajectory.size()-2];

  return;
}

double TotalCurvature(trajectory_type &trajectory)
{
  if (trajectory.size() < 3)
    return 0.0;

  double curvature = 0.0;

  for (unsigned int i = 1; i < trajectory.size()-1; ++i)
    curvature += signed_turn_angle(trajectory[i-1],trajectory[i],trajectory[i+1]);

//  trajectory.set_property("curvature",curvature);

//  std::cout << trajectory.size() << "\t" << curvature << std::endl;
  return curvature;
}
