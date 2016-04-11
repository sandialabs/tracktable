//  
// KmlOut.h
//
// Created by Danny Rintoul.
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.

#ifndef __KmlOut
#define __KmlOut
#include <iostream>
#include "Common.h"

void writeKmlHeader(std::ostream &outfile);

void writeKmlTrailer(std::ostream &outfile);

void writeKmlSepTrajectories(Trajectories &trajectories, 
 const std::string &output_dir);

void writeKmlTrajectory(trajectory_type &trajectory,
 std::ostream &outfile, const std::string &ColorString, const double &width);

void writeKmlTrajectories(Trajectories &trajectories,
 const std::string &file_name);

std::string getColorString(void);

#endif
