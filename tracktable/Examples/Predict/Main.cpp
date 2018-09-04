/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//   Main
//   
// This code will do prediction!
//
// Created by Danny Rintoul
//

#include "Common.h"
#include "ProgramOptions.h"
#include "Nearby.h"
#include "ConvexHull.h"
#include "BuildFeatures.h"
#include "DistanceFeatures.h"
#include "Predict.h"
#include "KmlOut.h"
#include "BuildTrajectories.h"
#include "ParseCommandLine.h"
#include <tracktable/Analysis/DBSCAN.h>
#include <boost/bind.hpp>
#include <boost/array.hpp>
#include <boost/geometry/geometries/adapted/boost_array.hpp>
#include <string>
#include <vector>

BOOST_GEOMETRY_REGISTER_BOOST_ARRAY_CS(cs::cartesian)

bool IsTailNumber(trajectory_type &trajectory);
bool HasConsistentDestination(trajectory_type &trajectory);

int main(int argc, char *argv[])
{
  srand(time(0));
  CommandLineOptions options = ParseCommandLine(argc, argv);

  Trajectories trajectories;
  BuildTrajectories<trajectory_type>(options,trajectories);
  std::size_t num_samples = options.NumSamples;

  std::cout << "trajectories.size() = " << trajectories.size() << std::endl;

  // Remove "tail number" flights
  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(IsTailNumber,_1)),trajectories.end());
  std::cout << "trajectories.size() = " << trajectories.size() << std::endl;

  std::vector<my_data> features, to_be_predicted;

  // This routine builds a feature database from specific intervals
  BuildManyEvenFeatures(trajectories,features);

  // This routine builds a feature database from randome intervals
//  BuildManyRandomFeatures(trajectories,features);


  // It's confusing, but this routine takes intial fractions from the flights
  // as test flights.
  BuildRandomFeatures(trajectories,to_be_predicted,0.2,0.8);

  // This routine does a lat/lon predict.
//  LLPredict(trajectories,features,to_be_predicted,num_samples);

  // This routine does a prediction based on destination airport
  Predict(trajectories,features,to_be_predicted,boost::numeric_cast<int>(num_samples));

  return 0;
}

bool IsTailNumber(trajectory_type &trajectory)
{
  std::string s = trajectory.object_id();
  if ((s[0] != 'N') || (s[1] < '0') || (s[1] > '9'))
    return false;

  return true;
}

bool HasConsistentDestination(trajectory_type &trajectory)
{
  return !trajectory.front().string_property("dest").empty() &&
   !trajectory.back().string_property("dest").empty() &&
   (trajectory.front().string_property("dest") ==
   trajectory.back().string_property("dest"));
}

