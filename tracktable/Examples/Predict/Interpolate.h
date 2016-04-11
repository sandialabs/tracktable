// 
// Interpolate
//
// Do Interpolations
//
//
// Created by Danny Rintoul
// Copyright (c) 2015 Sandia Corporation.  All rights reserved.
//

#ifndef __FindSimilar
#define __FindSimilar
#include "Common.h"

trajectory_point_type GetInterpolatedPoint(const trajectory_type &trajectory, double frac);

boost::posix_time::ptime GetInterpolatedTime( const trajectory_type &trajectory, double frac);
#endif
