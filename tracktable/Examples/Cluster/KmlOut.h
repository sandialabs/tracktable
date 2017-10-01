/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// KmlOut.h
//
// Created by Danny Rintoul.


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
