/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

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

trajectory_point_type GetInterpolatedPoint(const trajectory_type &trajectory, double frac);

boost::posix_time::ptime GetInterpolatedTime( const trajectory_type &trajectory, double frac);
#endif
