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

// Panther Trajectory Library
//
// CleanTrajectories
//
// This is a routines that takes a vector of Trajectories and cleans bad points

#include <boost/bind.hpp>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include "CleanTrajectory.h"

void CleanTrajectories(Trajectories& trajectories, int min_flight_size, 
 int min_time_between_points, double max_distance_between_points, 
 int max_altitude_change, int min_altitude)
{
  for_each(trajectories.begin(),trajectories.end(),
   boost::bind(CleanTrajectory,_1,min_flight_size,min_time_between_points, 
   max_distance_between_points,max_altitude_change,min_altitude));

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(std::less<int>(),
   boost::bind(&BasicTrajectory::size,_1),min_flight_size)),
   trajectories.end());
}

// ----------------------------------------------------------------------

void CleanTrajectory(BasicTrajectory& traj, int min_flight_size, 
 int min_time_between_points, double max_distance_between_points, 
 int max_altitude_change, int min_altitude)
{
  traj.erase(std::unique(traj.begin(),traj.end(), 
   boost::bind(badPoint,_1,_2,min_time_between_points,
   max_distance_between_points,max_altitude_change,min_altitude)),traj.end());
}

// ----------------------------------------------------------------------

// Is this correct?  I can't find any way to reproduce this number.
#define EARTH_RADIUS_IN_NM 3343.89849

bool badPoint(const Traj_Point &p1, 
              const Traj_Point &p2,
              int min_time_between_points, // seconds
              double max_distance_between_points, // measured in nm 
              int max_altitude_change, // measured in feet
              int min_altitude) // measured in feet
{
  return  // The logic follows..

  // If the points are less than some seconds apart, throw them out
   ((p2.timestamp() - p1.timestamp()) <
   boost::posix_time::time_duration(boost::posix_time::seconds(min_time_between_points))) ||

  // Or, if the latlon are the same, throw them out.  This gets around the
  // problem of some latlon staying constant for different time periods and
  // making some of the derived calculations nonsensical.  Sure, this
  // could be valid for a helicopter, but for now, we lose it.
   ((boost::geometry::distance(p1,p2) == 0.0)) ||

  // or, if the second point is way too far away from the first point, it's
  // probably bad.  There are lots of points like this in the data set that
  // very clearly don't belong.  The constant in there converts to nm.
   (EARTH_RADIUS_IN_NM*boost::geometry::distance(p1,p2) > max_distance_between_points) ||

  // Throw away the altitude 0 points.  These could be realistic but usually
  // correspond to bad data.
   (p2.numeric_property("altitude") < min_altitude) ||

  // There are some crazy altitude changes in the data.  But keeping it in
  // doesn't change much.
   (fabs(p2.numeric_property("altitude") - p1.numeric_property("altitude")) > max_altitude_change);
}
