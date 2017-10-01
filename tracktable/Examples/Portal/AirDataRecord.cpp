/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// 
// AirDataRecord
//
// Supporting routines for AirDataRecord.h
//
// Created by Danny Rintoul.
//

#include "AirDataRecord.h"
#include <boost/geometry/algorithms/distance.hpp>

  // A little mini-function that determines if two flights are "equal".  There
  // are clearly a lot of ways to define this.  We could perhaps have lots of 
  // these sorts of functions.  Equality is defined by having the same 
  // object_id and being within 10 minutes of each other.  If you are clever, 
  // you actually don't really need these but can write things on the fly 
  // with boost::bind.

bool sameFlight(const Traj_Point &fp1, const Traj_Point &fp2)
{ return (fp1.get_id() == fp2.get_id()) && 
   ((fp2.get_time() - fp1.get_time()) < 
   boost::posix_time::time_duration(boost::posix_time::minutes(10)));
}


  // A little function to separate flights by time.  Note we don't assume
  // anything about ID's.

bool apartInTime(const Traj_Point &fp1, const Traj_Point &fp2)
{ return (fp2.get_time() - fp1.get_time()) >=
   boost::posix_time::time_duration(boost::posix_time::minutes(10));
}

  // Defines a less than operator for sorting purposes.  Lots of different
  // ways to do this.  Currently this sorts on the object_id as the primary
  // and then currently update_time as the secondary.  The hope is
  // that this is a simple and mostly effective way of identifying a single
  // flight.

bool Traj_Point::operator < (const Traj_Point &fp) const
  {return ((id < fp.get_id()) || 
   ((get_id() == fp.get_id()) && (get_time() < fp.get_time())));}

  // Also define a sort that goes strictly by time.

bool timeSort(const Traj_Point &fp1, const Traj_Point &fp2)
{ return (fp1.get_time() < fp2.get_time()); }

  // Describes all of the conditions for throwing away a data point as bad
  // compared to the previous one.  Some of the numbers are a bit arbitrary
  // but they'll vary from application to application.  

bool badPoint(const Traj_Point &fp1, const Traj_Point &fp2) {

  // Maximum distance we'll allow between two points, in nautical miles
  double max_dist = 1.0;
  double min_dist = 0.0;
  
  // Maximum altitude difference we'll allow, in feet
  int max_alt_change = 75000;

  return  // The logic follows..

  // If the points are less than 30 seconds apart, throw them out
   ((fp2.get_time() - fp1.get_time()) < 
   boost::posix_time::time_duration(boost::posix_time::seconds(10))) ||

  // Or, if the latlon are the same, throw them out.  This gets around the
  // problem of some latlon staying constant for different time periods and 
  // making some of the derived calculations nonsensical.  Sure, this 
  // could be valid for a helicopter, but for now, we lose it.

   (boost::geometry::distance<point_2d,point_2d>(fp1,fp2) == 0.0) ||

  // or, if the second point is way too far away from the first point, it's
  // probably bad.  There are lots of points like this in the data set that
  // very clearly don't belong.  The constant in there converts to nm.
   (boost::geometry::distance<point_2d,point_2d>(fp1,fp2) < min_dist) ||
   (boost::geometry::distance<point_2d,point_2d>(fp1,fp2) > max_dist) ||

  // Throw away the altitude 0 points.  These could be realistic but usually
  // correspond to bad data.

   (fp2.get_altitude() == 0) ||

  // There are some crazy altitude changes in the data.  But keeping it in
  // doesn't change much.
   (abs(fp2.get_altitude() - fp1.get_altitude()) > max_alt_change);
}
