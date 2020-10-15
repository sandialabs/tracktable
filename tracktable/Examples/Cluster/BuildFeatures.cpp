/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//  Building "features" representing spaced points on a trajectory
//
//  Created by Danny Rintoul
//
#include <boost/bind.hpp>
#include <functional>
#include "BuildFeatures.h"
#include "Interpolate.h"

void BuildFeatures(Trajectories &trajectories, std::vector<my_data> &features,
 double flight_frac)
{

  std::transform(trajectories.begin(),trajectories.end(),
   std::back_inserter(features),boost::bind(BuildFeature,_1,flight_frac));

  return;
}

void BuildManyEvenFeatures(Trajectories &trajectories,
 std::vector<my_data> &features)
{
  for (int i = 2; i <= 8; ++i) {
    BuildFeatures(trajectories,features,i/10.0);
  }

  return;
}

void BuildManyRandomFeatures(Trajectories &trajectories,
 std::vector<my_data> &features)
{
  srand48(time(0));  // use a different long int for other numbers;
  for (int i = 2; i <= 8; ++i) {
    BuildFeatures(trajectories,features,0.2+drand48()*0.6);
  }

  return;
}

void BuildRandomFeatures(Trajectories &trajectories,
 std::vector<my_data> &features, double lower, double upper)
{

  // Somewhat unfortunate syntax to generate random numbers between lower
  // and upper for random feature selection.  It would be cleaner to write
  // a quick routine to a tiny function to return the random number, but
  // it's nicer to use existing routines.  One of many things that would
  // be done differently in C++11 in many ways.

  srand48(time(0));  // use a different long int for other numbers;
  double diff = upper - lower;
  std::transform(trajectories.begin(),trajectories.end(),
   std::back_inserter(features),
   boost::bind(BuildFeature,_1,boost::bind(std::plus<double>(),lower,
    boost::bind(std::multiplies<double>(),diff,boost::bind(drand48)))));

  return;
}

my_data BuildFeature(BasicTrajectory &trajectory, double flight_frac)
{
  // Nothing complicated here.  Basically, divide the trajectory up into
  // some even-sized pieces, and take the early way-points and build a
  // feature vector out of them. The only tricky part is that when you
  // divide a trajectory into n pieces, you essentially have n+1 points
  // to choose from.

  const unsigned int sample_pts = 4; // Must be >= 2

  Feature temp;
  for (unsigned int i = 0; i < sample_pts; ++i) {
    double frac = flight_frac *
     static_cast<double>(i)/static_cast<double>(sample_pts-1);
    Traj_Point pt = GetInterpolatedPoint(trajectory,frac);
    temp[2*i] = pt.longitude();
    temp[2*i + 1] = pt.latitude();
//    temp[3*i + 2 ] = (pt.timestamp() -
//     trajectory.front().timestamp()).seconds()/1200;
  }
  Traj_Point pt = GetInterpolatedPoint(trajectory,flight_frac);
  temp[2*sample_pts] = (pt.timestamp() -
   trajectory.front().timestamp()).seconds()/1200.;

  return my_data(temp,0,&(trajectory));
}
