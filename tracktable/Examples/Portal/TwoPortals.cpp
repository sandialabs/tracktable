/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//   TwoPortals
//   
// First example of finding two portals in the flight data
//
// Created by Danny Rintoul
//

#include "TwoPortals.h"
#include <boost/bind.hpp>
#include <string>
#include <numeric>

/*
void WriteAllFlights(Pair_heap &pairs,
 const unsigned int level, const unsigned int interval_x, 
 const unsigned int interval_y);
*/

void FindMultiplePortals(Trajectories &trajectories, Pair_heap &pairs,
 PP &US, const unsigned int level, 
 const unsigned int interval_x, const unsigned int interval_y);

int main(int argc, char *argv[])
{

  CommandLineOptions options = ParseCommandLine(argc, argv);

  Trajectories trajectories;
  BuildTrajectories<trajectory_type>(options,trajectories);

  Pair_heap pairs;
  pairs.min_sep = options.PortalSeparation;
  pairs.min_val = options.MinVal;

  trajectory_point_type ll;  // lower left of US (roughly)
  ll.set<0>(-125.0); ll.set<1>(25.0);

  trajectory_point_type ur; // upper right of US (roughly)
  ur.set<0>(-65.0); ur.set<1>(50.0);

  PP US(new Portal(boost::geometry::model::box<trajectory_point_type>(ll,ur)));
  US->level = 0;
  MakeInitialPairs(trajectories,US,pairs);
//  WriteAllFlights(pairs,depth,interval,interval);
  FindMultiplePortals(trajectories,pairs,US,options.Depth,
   options.BinSize,options.BinSize);

  return 0;
}
/*
void WriteAllFlights(Pair_heap &pairs,
 const unsigned int level, const unsigned int interval_x, 
 const unsigned int interval_y)
{
  double max_sep = 0.0;
  int i = 1;
  do 
  {
    while (RefinePairs(pairs,level,interval_x,interval_y));
//    if (pairs.top().sep < max_sep)
//      break;
    std::list<PP> out;
    out.push_back(pairs.top().p1);
    out.push_back(pairs.top().p2);
    std::string s2 = "flights" + boost::lexical_cast<std::string>(i) + ".kml";
    writeKmlPortalPairClipped(pairs.top(),s2);
    max_sep = pairs.top().sep;
    pairs.pop();
    ++i;
  } while (pairs.size() > 0);

  return;  
}
*/
void FindMultiplePortals(Trajectories &trajectories, Pair_heap &pairs, 
 PP &US, const unsigned int level, const unsigned int interval_x, 
 const unsigned int interval_y)
{
  static int i = 0;
  srand(time(0));

  while (pairs.size()) {
    while (RefinePairs(pairs,level,interval_x,interval_y));
    if (!pairs.empty()) {
      std::vector<PP> out;
      out.push_back(pairs.top().p1);
      out.push_back(pairs.top().p2);
      std::string s2 = "flights" + boost::lexical_cast<std::string>(i) + ".kml";
      writeKmlPortalPair(pairs.top(),s2);
//      writeKmlPortalPairClipped(pairs.top(),s2);
      RemoveTopPair(pairs,trajectories,US);
//      RemoveTopPairClipped(pairs,trajectories,US);
      ++i;
    }
  }

  return;
}

