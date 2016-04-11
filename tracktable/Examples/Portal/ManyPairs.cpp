//
//   ManyPairs
//   
// First example of finding two portals in the flight data
//
// Created by Danny Rintoul
// Copyright (c) 2014 Sandia Corporation.  All rights reserved.
//

#include "ManyPairs.h"
#include <string>

void FindMultiplePortals(my_pq<Portal_pair> &pairs, PP &US, const unsigned int level, const unsigned int interval_x, const unsigned int interval_y);

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

  readAirDataFile(data_file,sep_char,flights);
  

  // Clean up the data

  cleanFlights(flights);
  std::for_each(flights.begin(),flights.end(),
   boost::bind(&Flight::calculateFlightValues,_1));

  {
  std::cout << "Starting with " << flights.size() << " flights" << std::endl;
  boost::timer::auto_cpu_timer t;
  my_pq<Portal_pair> pairs;
  PP US(new Portal);
  MakeInitialPairs(flights,US,pairs);
  FindMultiplePortals(pairs,US,depth,interval,interval);
  }

  return 0;
}

void FindMultiplePortals(my_pq<Portal_pair> &pairs, PP &US, const unsigned int level, const unsigned int interval_x, const unsigned int interval_y)
{
  srand(time(0));

  for (unsigned int i = 1; i <= 100; ++i) {
    while (RefinePairs(pairs,10.0,level,interval_x,interval_y));
    std::vector<PP> out;
    out.push_back(pairs.top().p1);
    out.push_back(pairs.top().p2);
    std::string s1 = "output2/portals" + boost::lexical_cast<std::string>(i) + ".kml";
    std::string s2 = "output2/flights" + boost::lexical_cast<std::string>(i) + ".kml";
    writeKmlPortals(out,s1);
    writeKmlPortalPair(pairs.top(),s2);
    RemoveTopPair(pairs,US);
  }

  return;  
}
