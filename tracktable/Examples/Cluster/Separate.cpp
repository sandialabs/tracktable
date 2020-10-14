/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// Separate
//
// Separates a list of points into actual trajectories
//
// Created by Danny Rintoul.


#include "Separate.h"
#include <boost/bind.hpp>

void separateMapFlights(Trajectory_map &traj_map, Trajectories &trajectories,
 const int min_flight_size, const int max_flight_gap)
{

  // Take the vectors from the traj_map, separate them, and put them into
  // the fector of flights.

  Trajectory_map::iterator map_itr;

  for (map_itr = traj_map.begin(); map_itr != traj_map.end(); ++map_itr) {
  // Can technically remove next line if points start out time sorted...
    std::sort(map_itr->second.begin(),map_itr->second.end(),
     boost::bind(&Traj_Point::timestamp,_1) <
     boost::bind(&Traj_Point::timestamp,_2));
    separateFlights(map_itr->second,trajectories);
  }

  return;
}
void separateFlights(std::vector<Traj_Point> &tps,
 Trajectories &trajectories, const int min_flight_size,
 const int max_flight_gap)
{
  // Simple for loop to separate the individual flights.  There is an
  // awkwardness to doing this with a for loop that has to do with how
  // std::adjacent_find works.  Basically, when you hit the end, you still
  // have one more record to do, so a do-while is better.  The constant
  // in the pointer comparison is the minimum data points we need to define
  // a flight.

  std::vector<Traj_Point>::iterator ptr1 = tps.begin();
  std::vector<Traj_Point>::iterator ptr2;
  do {
    ptr2 = std::adjacent_find(ptr1,tps.end(),
     boost::bind(apartInTime,_1,_2,max_flight_gap));
    if (ptr2 != tps.end()) ++ptr2;
    if ((ptr2 - ptr1) >= min_flight_size)
      trajectories.push_back(BasicTrajectory(ptr1,ptr2));
    ptr1 = ptr2;
  } while (ptr2 != tps.end());

  return;
}

bool apartInTime(const Traj_Point& tp1, const Traj_Point &tp2,
 const int max_time_gap)
{ return (tp2.timestamp() - tp1.timestamp()) >=
   boost::posix_time::time_duration(boost::posix_time::minutes(max_time_gap));
}

