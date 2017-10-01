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

//
//   test
//
//

#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/BasicTrajectory.h>

#include <boost/geometry/arithmetic/arithmetic.hpp>
#include <boost/geometry/algorithms/distance.hpp>

int main()
{

  // First, some point examples

  tracktable::TrajectoryPoint tp1(100.0,40);
  tracktable::TrajectoryPoint tp2(105.0,45);

  // This works, but...
  boost::geometry::distance<
     tracktable::PointBaseLonLat<double>,
     tracktable::PointBaseLonLat<double> >(tp1,tp2);

  // This doesn't.  Probably a boost geometry registration issue...
  boost::geometry::distance(tp1,tp2);


  // Now some point/track distance examples

  tracktable::TrajectoryPoint tp3(110.0,30);
  tracktable::TrajectoryPoint tp4(115.0,35);
  tracktable::TrajectoryPoint tp5(120.0,40);
  tracktable::TrajectoryPoint tp6(125.0,45);

  tracktable::PointBaseLonLat<double> ll3(110.0,30);
  tracktable::PointBaseLonLat<double> ll4(115.0,35);
  tracktable::PointBaseLonLat<double> ll5(120.0,40);
  tracktable::PointBaseLonLat<double> ll6(125.0,45);

  tracktable::Trajectory<tracktable::TrajectoryPoint> tp_traj;
  tracktable::Trajectory<tracktable::PointBaseLonLat<double> > ll_traj;

  tp_traj.add_point(tp3);
  tp_traj.add_point(tp4);
  tp_traj.add_point(tp5);
  tp_traj.add_point(tp6);

  ll_traj.add_point(ll3);
  ll_traj.add_point(ll4);
  ll_traj.add_point(ll5);
  ll_traj.add_point(ll6);

  // This doesn't work, but probably would if the linestring was registered
  boost::geometry::distance(ll_traj,ll3);

  // This doesn't work and needs to linestring and point registered
  boost::geometry::distance(tp_traj,tp3);

  // Now some math examples

  // This doesn't work...
  boost::geometry::multiply_value(tp3,0.5);

  // ...but this does.  Again, probably a registration issue
  boost::geometry::multiply_value(ll3,0.5);

  return 0;
}
