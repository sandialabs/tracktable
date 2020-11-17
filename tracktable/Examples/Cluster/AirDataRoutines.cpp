/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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
#include <string>
#include <sstream>
#include <boost/foreach.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <tracktable/RW/PointReader.h>

int readAirDataFile(std::string &input_file, std::string& sep_char,
 Trajectories& trajectories)
{
  Trajectory_map traj_map;

  std::vector<std::string> mappers;
//  GetMappers(mappers);

  std::ifstream in(input_file.c_str());
  if (!in.is_open()) return 1;

  tracktable::PointReader<tracktable::TrajectoryPoint<
   tracktable::PointLonLat> > reader(in);

  reader.set_delimiters(sep_char.c_str());

  reader.set_object_id_column(0);
  reader.set_timestamp_column(1);
  reader.set_coordinate_column(0, 2);
  reader.set_coordinate_column(1, 3);
  reader.set_numeric_field_column("speed", 4);
  reader.set_numeric_field_column("heading", 5);
  reader.set_numeric_field_column("altitude", 6);
  reader.set_string_field_column("dest", 30);

  tracktable::PointReader<tracktable::TrajectoryPoint<tracktable::PointLonLat>
>::iterator in_itr = reader.begin();

  for (; in_itr != reader.end(); ++in_itr) {
    tracktable::TrajectoryPoint<tracktable::PointLonLat> tp(*in_itr);
//    if (!binary_search(mappers.begin(),mappers.end(),in_itr->object_id()))
//      continue;
    traj_map[tp.object_id()].push_back(tp);
  }

  // Turn the map into the flights format (vector of flights)
  separateMapFlights(traj_map,trajectories);

  return 0;
}

int readTrajectoryFile(std::string &input_file, std::string &sep_char,
 BasicTrajectory &trajectory)
{
  std::ifstream in(input_file.c_str());
  if (!in.is_open()) return 1;

  tracktable::PointReader<tracktable::TrajectoryPoint<tracktable::PointLonLat> > reader(in);

  reader.set_delimiters(sep_char.c_str());

  reader.set_object_id_column(0);
  reader.set_timestamp_column(1);
  reader.set_coordinate_column(0, 2);
  reader.set_coordinate_column(1, 3);

  tracktable::PointReader<tracktable::TrajectoryPoint<tracktable::PointLonLat>
>::iterator in_itr = reader.begin();

  for (; in_itr != reader.end(); ++in_itr) {
    tracktable::TrajectoryPoint<tracktable::PointLonLat> tp(*in_itr);
    trajectory.push_back(tp);
  }

  return 0;
}

void readJSONData(BasicTrajectory &trajectory, std::string &output_file)
{
  boost::property_tree::ptree pt;

  boost::posix_time::ptime t =
   boost::posix_time::time_from_string("2013-01-01 00:00:00");

  std::string line;
  if (!std::getline(std::cin,line))
    exit(0);
  std::stringstream s;
  s << line;

  read_json(s,pt);

  output_file = pt.get<std::string>("parameters.result-kml");

  BOOST_FOREACH(boost::property_tree::ptree::value_type &v,
   pt.get_child("path.latlong")) {

    boost::property_tree::ptree::iterator itr = v.second.begin();
    tracktable::TrajectoryPoint<tracktable::PointLonLat> tp;

    tp.set_object_id("EX100");
//    double lat = boost::lexical_cast<double>(itr->second.data());
//    tp.set_latitude(lat); ++itr;
//    double lon = boost::lexical_cast<double>(itr->second.data());
//    tp.set_longitude(lon);

    tp.set_timestamp(t);
    t = t + boost::posix_time::minutes(1);

    trajectory.push_back(tp);
  }

  return;
}

double HeadingDifference(const double h2, const double h1)
{
  return (h2 - h1) - 360.0 * int((h2-h1)/180.0);
}

double TrajHeadingDifference(const Traj_Point &t2, const Traj_Point &t1)
{
  double h2 = t2.numeric_property("heading");
  double h1 = t1.numeric_property("heading");

  return HeadingDifference(h2,h1);
}

void GetMappers(std::vector<std::string> &mappers)
{
  std::ifstream in("map_list.txt");
  if (!in.is_open()) return;

  std::string line;

  while (std::getline(in,line))
    mappers.push_back(line);

  std::sort(mappers.begin(),mappers.end());

  return;
}

bool IsTailNumber(BasicTrajectory &trajectory)
{
  std::string s = trajectory.object_id();
  if ((s[0] != 'N') || (s[1] < '0') || (s[1] > '9'))
    return false;

  return true;
}

bool HasConsistentDestination(BasicTrajectory &trajectory)
{
  return !trajectory.front().string_property("dest").empty() &&
   !trajectory.back().string_property("dest").empty() &&
   (trajectory.front().string_property("dest") ==
   trajectory.back().string_property("dest"));
}
