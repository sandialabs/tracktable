/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// Interpolate
//
// Do Interpolations
//
//
// Created by Danny Rintoul
//

#ifndef __FindSimilar
#define __FindSimilar
#include "Common.h"

Traj_Point GetInterpolatedPoint(const BasicTrajectory &trajectory, double frac);

boost::posix_time::ptime GetInterpolatedTime( const BasicTrajectory &trajectory, double frac);
#endif
