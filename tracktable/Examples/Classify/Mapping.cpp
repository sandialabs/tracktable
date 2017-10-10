/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Mapping: A simple example for finding mapping flights with lots of
 * back-and-forth motion.
 *
 * Created by Danny Rintoul.
 */

#include "Mapping.h"
#include <algorithm>
#include <boost/bind.hpp>


double HeadingDifference(const double h2, const double h1)
{
  return (h2 - h1) - 360.0 * int((h2-h1)/180.0);
}

double TrajHeadingDifference(
                             const trajectory_point_type &t2, 
                             const trajectory_point_type &t1)
{
  double h2 = t2.real_property("heading");
  double h1 = t1.real_property("heading");

  return HeadingDifference(h2,h1);
}

double AbsTrajHeadingDifference(trajectory_point_type const& t1, trajectory_point_type const& t2)
{
  return fabs(TrajHeadingDifference(t1, t2));
}


unsigned int TurnArounds(trajectory_type const &trajectory)
{
  const unsigned int window = 5;
  unsigned int ctr = 0;

  if (trajectory.size() <= window)
    return 0;

  trajectory_type::const_iterator itr1 = trajectory.begin();
  trajectory_type::const_iterator itr2 = itr1 + window;
  double diff;
  bool found = false;

  do {
    diff = fabs(itr1->real_property("heading") - 
                itr2->real_property("heading"));

    if (fabs(diff - 180.0) < 2.0)
      {  // 2.0 is the fudge factor for comparing against 180 degrees
      if (!found)
        {
          ++ctr;
        }
      found = true;
      }
    else
      {
        found = false;
      }

    if (found)
      {
        int leap = 
          std::min(static_cast<int>(std::distance(itr2,trajectory.end())),5);
        // The 5 above is related to how far away you want to go before you
        // define another turnaround
        itr1 += leap; itr2 += leap;
      }
    else
      {
        ++itr1; ++itr2;
      }
  } while (itr2 != trajectory.end());

  return ctr;
}

// ----------------------------------------------------------------------

double StraightFraction(trajectory_type const& trajectory)
{
  int sum = 0;
  const int min_straight_size = 5;

  trajectory_type::const_iterator itr1 = trajectory.begin();
  trajectory_type::const_iterator itr2;

  do {
    itr2 = 
    // The 2.0 below is related to how different the straightness can be from 180
    itr2 = std::adjacent_find(itr1,
                              trajectory.end(),
                              !boost::bind(std::less<double>(),
                                           boost::bind(AbsTrajHeadingDifference,_1,_2), 2.0));
    
                                           // boost::bind(fabs,
                                           //             (boost::bind(TrajHeadingDifference,_1,_2))),2.0));

    if (itr2 != trajectory.end()) ++itr2;

    if ((itr2 - itr1) >= min_straight_size)
      sum += (itr2 - itr1);

    itr1 = itr2;
  } while (itr2 != trajectory.end());

  return static_cast<double>(sum)/static_cast<double>(trajectory.size());
}
