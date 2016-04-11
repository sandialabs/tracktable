// 
// Mapping
//
// Find Mapping Flights
//
//
// Created by Danny Rintoul
// Copyright (c) 2014 Sandia Corporation.  All rights reserved.
//

#ifndef _Mapping_h_
#define _Mapping_h_
#include "Common.h"

unsigned int TurnArounds(trajectory_type &trajectory);
double StraightFraction(trajectory_type &trajectory);
double HeadingDifference(const double h2, const double h1);
double TrajHeadingDifference(const trajectory_point_type &t2,
 const trajectory_point_type &t1);


#endif
