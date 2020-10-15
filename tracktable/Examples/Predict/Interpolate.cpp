/*
 * Copyright (c) 2013-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//   Interpolate
//
// Do Interpolations
//
// Created by Danny Rintoul
//

#include "Common.h"
#include "Interpolate.h"
#include <numeric>
#include <boost/bind.hpp>

trajectory_point_type GetInterpolatedPoint(
 const trajectory_type &trajectory, double frac)
{
  if (frac == 0.0)
    return trajectory.front();

  if (frac == 1.0)
    return trajectory.back();

  boost::posix_time::ptime t = GetInterpolatedTime(trajectory,frac);

  if (t <= trajectory.front().timestamp())
    return trajectory.front();
  if (t >= trajectory.back().timestamp())
    return trajectory.back();

  trajectory_point_type fp;
  fp.set_timestamp(t);
  std::pair<trajectory_type::const_iterator,
   trajectory_type::const_iterator> itrs;

  itrs = std::equal_range(trajectory.begin(),trajectory.end(),
   fp,boost::bind(&trajectory_point_type::timestamp,_1) <
   boost::bind(&trajectory_point_type::timestamp,_2));

  trajectory_type::const_iterator lower = itrs.first;
  trajectory_type::const_iterator upper = itrs.second;

  if (lower != upper) {
    return *lower;  // We got lucky and hit an exact match
  } else {         // We have to do an interpolation
    do {
      --lower;
    } while (lower->timestamp() >= t);

    boost::posix_time::time_duration interval_t, interval_frac_t;

    interval_t = upper->timestamp() - lower->timestamp();
    interval_frac_t = t - lower->timestamp();

    double interval_frac = static_cast<double>(interval_frac_t.total_seconds())
     / static_cast<double>(interval_t.total_seconds());

    fp = tracktable::interpolate(*lower,*upper,interval_frac);

    return fp;
  }
}

boost::posix_time::ptime GetInterpolatedTime(
 const trajectory_type &trajectory, double frac)
{
  if (frac == 0.0)
    return trajectory.front().timestamp();

  if (frac == 1.0)
    return trajectory.back().timestamp();

  boost::posix_time::time_duration total_time =
   trajectory.back().timestamp() - trajectory.front().timestamp();

  long delta_sec = static_cast<long>(frac*total_time.total_seconds());

  return trajectory.front().timestamp() +
   boost::posix_time::time_duration(boost::posix_time::seconds(delta_sec));
}
