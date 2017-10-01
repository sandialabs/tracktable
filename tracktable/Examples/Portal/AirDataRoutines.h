/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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
#include "Common.h"

int readAirDataFile(std::string &input_file, std::string& sep_char,
 Trajectories& trajectories);

bool IsTailNumber(Trajectory &trajectory);
double TotalLength(Trajectories &trajectories);
bool IsStraight(Trajectory &trajectory);
void GetMajorAirports(std::vector<std::string> &airports);
bool HasMajorAirports(Trajectory &trajectory, 
 std::vector<std::string> &airports);


#endif
