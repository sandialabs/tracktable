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

Traj_Point GetInterpolatedPoint(const BasicTrajectory &trajectory, double frac);

boost::posix_time::ptime GetInterpolatedTime( const BasicTrajectory &trajectory, double frac);
#endif
