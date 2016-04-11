//
//   Supporting tools
//   
// A simple example how one can find similar trajectorys using control points
//
// Created by Danny Rintoul
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.
//

#include <numeric>

Traj_Point GetInterpolatedPoint(const Trajectory &trajectory, double frac)
{
  if (frac == 0.0)
    return trajectory.front();

  if (frac == 1.0)
    return trajectory.back();

  boost::posix_time::ptime t = GetInterpolatedTime(trajectory,frac);

  Traj_Point fp;
  fp.set_time(t);
  std::pair<Trajectory::const_iterator,Trajectory::const_iterator> itrs; 

  itrs = std::equal_range(trajectory.begin(),trajectory.end(),
   fp,boost::bind(&Traj_Point::get_time,_1) < 
   boost::bind(&Traj_Point::get_time,_2));

  if (itrs.first == itrs.second) {
    return *itrs.first;
  } else {
    boost::posix_time::time_duration interval_t, interval_frac_t;

    interval_t = (itrs.second)->get_time() - itrs.first->get_time();
    interval_frac_t = t - itrs.first->get_time();

    double interval_frac =static_cast<double>(interval_frac_t.total_seconds()) /
    static_cast<double>(interval_t.total_seconds());

    point_ll temp1 = *(itrs.first);
    point_ll temp2 = *(itrs.second);

    boost::geometry::subtract_point(temp2,temp1);
    boost::geometry::multiply_value(temp2,interval_frac);
    boost::geometry::add_point(temp1,temp2);
    fp = temp1;

    return fp;
  }
}

boost::posix_time::ptime GetInterpolatedTime(const Trajectory &trajectory, 
 double frac)
{
  if (frac == 0.0)
    return trajectory.front().get_time();

  if (frac == 1.0)
    return trajectory.back().get_time();

  boost::posix_time::time_duration total_time = 
   trajectory.back().get_time() - trajectory.front().get_time();

  long delta_sec = static_cast<long>(frac*total_time.total_seconds());

  return trajectory.front().get_time() +
   boost::posix_time::time_duration(boost::posix_time::seconds(delta_sec));
}
