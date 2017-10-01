/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

#ifndef _Mapping_h_
#define _Mapping_h_
#include "Common.h"

unsigned int TurnArounds(trajectory_type &trajectory);
double StraightFraction(trajectory_type &trajectory);
double HeadingDifference(const double h2, const double h1);
double TrajHeadingDifference(const trajectory_point_type &t2,
 const trajectory_point_type &t1);


#endif
