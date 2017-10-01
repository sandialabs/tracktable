/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// AirDataRoutines
//
// Just reads in a file full of the air data records.  Doesn't do a 
// lot of error checking.  So far, the files have all had 17 columns
// as advertised. The problem is that some of the columns are empty.
//
// Created by Danny Rintoul.


#include "AirDataRoutines.h"
#include "Separate.h"
#include <iostream>
#include <numeric>
#include <string>
#include <tracktable/IO/PointReader.h>
#include <boost/bind.hpp>

int readAirDataFile(std::string &input_file, std::string& sep_char, 
 Trajectories& trajectories)
{
  Trajectory_map traj_map;

  std::ifstream in(input_file.c_str());
  if (!in.is_open()) return 1;

  tracktable::PointReader<Traj_Point> reader(in);

  reader.set_field_delimiter(sep_char.c_str());

  reader.set_object_id_column(0);
  reader.set_timestamp_column(1);
  reader.set_coordinate_column(0, 2);
  reader.set_coordinate_column(1, 3);
//  reader.set_numeric_field_column("speed", 4);
//  reader.set_numeric_field_column("heading", 5);
  reader.set_numeric_field_column("altitude", 6);
  reader.set_string_field_column("dep",25);
  reader.set_string_field_column("arr",30);

  tracktable::PointReader<Traj_Point>::iterator in_itr = reader.begin();

  for (; in_itr != reader.end(); ++in_itr) {
    Traj_Point tp(*in_itr);
    traj_map[tp.object_id()].push_back(tp);
  }

  // Turn the map into the flights format (vector of flights)
  separateMapFlights(traj_map,trajectories);

  return 0;
}

bool IsTailNumber(Trajectory &trajectory)
{
  std::string s = trajectory.object_id();
  if ((s[0] != 'N') || (s[1] < '0') || (s[1] > '9'))
    return false;

  return true;
}

double TotalLength(Trajectories &trajectories)
{
  return std::accumulate(trajectories.begin(),trajectories.end(),0.0,
   boost::bind(std::plus<double>(),_1,
   boost::bind(boost::geometry::length<Trajectory>,_2)));
}

bool IsStraight(Trajectory &trajectory)
{
  return boost::geometry::length(trajectory)/boost::geometry::distance(trajectory.front(),trajectory.back()) < 1.05;
}

void GetMajorAirports(std::vector<std::string> &airports)
{
  std::ifstream in("airports.txt");
  if (!in.is_open()) return;

  std::string line;

  while (std::getline(in,line))
    airports.push_back(line);

  std::sort(airports.begin(),airports.end());

  return;
}

bool HasMajorAirports(Trajectory &trajectory, 
 std::vector<std::string> &airports)
{
  return std::binary_search(airports.begin(),airports.end(),
   trajectory.front().string_property("arr")) &&
   std::binary_search(airports.begin(),airports.end(),
   trajectory.front().string_property("dep"));
}
