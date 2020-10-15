/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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

#include "Interpolate.h"
#include <numeric>
#include <boost/bind.hpp>

bool len_compare(const trajectory_point_type &p1,
 const trajectory_point_type &p2) {
  return p1.real_property("length") < p2.real_property("length");
}

trajectory_point_type GetLengthInterpolatedPoint(
 const trajectory_type &trajectory, double frac)
{
  if ((frac < 0.0) || (frac > 1.0)) {
    std::cerr << "Bad fraction " << frac << std::endl;
    exit(1);
  }

  if (frac == 0.0)
    return trajectory.front();

  if (frac == 1.0)
    return trajectory.back();

  double len = frac * trajectory.back().real_property("length");

  trajectory_point_type fp;
  fp.set_property("length", len);
  std::pair<trajectory_type::const_iterator,
   trajectory_type::const_iterator> itrs;

  itrs = std::equal_range(trajectory.begin(),trajectory.end(),
   fp,&len_compare);

  trajectory_type::const_iterator lower = itrs.first;
  trajectory_type::const_iterator upper = itrs.second;

  if (lower != upper) {
    return *lower;  // We got lucky and hit an exact match
  } else {         // We have to do an interpolation
    do {
      --lower;
    } while (lower->real_property("length") >= len);

    double interval_len, interval_frac_len;

    interval_len = upper->real_property("length") -
     lower->real_property("length");
    interval_frac_len = len - lower->real_property("length");

    double interval_frac = interval_frac_len
     / interval_len;

    fp = tracktable::interpolate(*lower,*upper,interval_frac);
    fp.set_property("length", len);

    return fp;
  }
}
