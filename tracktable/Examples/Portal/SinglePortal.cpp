/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//   SinglePortal
//
// First example of covering flights with single portals
//
// Created by Danny Rintoul
//

#include "SinglePortal.h"
#include <string>

void FindTopPortals(my_pq<PP,std::vector<PP>,PPCompare> &portals, PP &Full, const unsigned int level, const unsigned int interval_x, const unsigned int interval_y);

int main(int argc, char *argv[])
{

  ProgramOptions opts;
  opts.addOption<std::string>("input_file,i","input file");
  opts.addOption<std::string>("output_dir,o","output directory","output");
  opts.addOption<std::string>("sep_char,s","separation character","\t,");
  opts.addOption<unsigned int>("depth,d","depth of search",5);
  opts.addOption<unsigned int>("bin_size,b","portal chopping factor",2);
  opts.parseOptions(argc,argv);
  std::string data_file = opts.getValue<std::string>("input_file");
  std::string output_dir = opts.getValue<std::string>("output_dir");
  std::string sep_char = opts.getValue<std::string>("sep_char");
  unsigned int depth = opts.getValue<unsigned int>("depth");
  unsigned int interval = opts.getValue<unsigned int>("bin_size");
  output_dir += "/";

  Flights flights;

  readGeoLifeFile(data_file,sep_char,flights);

  // Clean up the data

/*
  cleanFlights(flights);
  std::for_each(flights.begin(),flights.end(),
   boost::bind(&Flight::calculateFlightValues,_1));
*/
  {
  std::cout << "Starting with " << flights.size() << " flights" << std::endl;
  boost::timer::auto_cpu_timer t;
  my_pq<PP,std::vector<PP>,PPCompare> portals;

  // Make the whole simulation
  point_2d ll = point_2d(-125.0,25.0);
  point_2d ur = point_2d(-65.0,50.0);
//  point_2d ll = point_2d(116.2,39.8);
//  point_2d ur = point_2d(116.6,40.1);
  PP Full(new Portal(boost::geometry::model::box<point_2d>(ll,ur)));
  Full->level = 0;
  MakeInitialSingles(flights,Full,portals,12,5);
  std::cout << "Starting with " << Full->flights.size() << " flights" << std::endl;
  FindTopPortals(portals,Full,depth,interval,interval);
  }

  return 0;
}

void FindTopPortals(my_pq<PP,std::vector<PP>,PPCompare> &portals, PP &Full, const unsigned int level, const unsigned int interval_x, const unsigned int interval_y)
{
  srand(time(0));

  double total = 0.0;
  double Full_total = Full->flights.size();
  std::list<PP> out;
  for (unsigned int i = 1; i <= 5; ++i) {
    while(RefineSingles(portals,level,interval_x,interval_y));
    out.push_back(portals.top());
//    std::string s1 = "output2/portals" + boost::lexical_cast<std::string>(i) + ".kml";
    std::string s2 = "output2/flights" + boost::lexical_cast<std::string>(i) + ".kml";
    Flights flights;
    for (fp_itr itr = portals.top()->flights.begin(); itr != portals.top()->flights.end(); ++itr)
      flights.push_back(**itr);
    writeKmlFlights(flights,s2);
    RemoveTopPortal(portals,Full);
    total += flights.size();
    std::cout << i << "\t" << flights.size() << "\t" << total/Full_total << std::endl;
  }
  writeKmlPortals(out,"output2/portals.kml");
}
