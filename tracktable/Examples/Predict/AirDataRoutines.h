/*
 * Copyright (c) 2013-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */
// 
// AirDataRoutines
//
// This routine simply reads in the data from flight records that are stored
// in the original format that was obtained by us.  It reads a whole file and
// puts everything in one vector.
//
// Created by Danny Rintoul.

#ifndef __AirDataRoutines
#define __AirDataRoutines
#include <string>
#include <boost/geometry/geometries/linestring.hpp>
#include <boost/geometry/geometries/segment.hpp>

#include "Common.h"

int readAirDataFile(std::string &input_file, std::string& sep_char,
 Trajectories& trajectories);

int readTrajectoryFile(std::string &input_file, std::string &sep_char,
 BasicTrajectory &trajectory);

double distFromTrack(const point_ll &point, 
 const TrackLonLat &tps);

void readJSONData(BasicTrajectory &trajectory, 
 std::string &output_file);

double HeadingDifference(const double h2, const double h1);
double TrajHeadingDifference(const Traj_Point &h2, const Traj_Point &h1);
void GetMappers(std::vector<std::string> &mappers);
bool IsTailNumber(BasicTrajectory &trajectory);
bool HasConsistentDestination(BasicTrajectory &trajectory);
#endif
