/*
 * Copyright (c) 2013-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//   SimilarShape
//
// A simple example how one can find similar flights using control points
//
// Created by Danny Rintoul
//

#include "Nearby.h"
#include <boost/bind.hpp>
#include <tracktable/Core/TrajectoryPoint.h>

void Nearby(Trajectories &trajectories,
 Trajectories& results)
{

  point_ll point1 = point_ll(-106.67,35.05);
  point_ll point2 = point_ll(-106.67,37.69);
  point_ll point3 = point_ll(-106.67,33.76);

  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr) {
    // Get the L_2 distance between the two vectors (the square actually)

    double tot_dist = boost::geometry::distance(point1,*itr) +
                      boost::geometry::distance(point2,*itr) +
                      boost::geometry::distance(point3,*itr);

    itr->set_property("dist",tot_dist);
    results.push_back(*itr);
  }

  std::sort(results.begin(),results.end(),
   boost::bind(&trajectory_type::property_without_checking,_1,"dist") <
   boost::bind(&trajectory_type::property_without_checking,_2,"dist"));

  if (results.size() > 10)
    results.erase(results.begin()+10,results.end());

  return;
}
