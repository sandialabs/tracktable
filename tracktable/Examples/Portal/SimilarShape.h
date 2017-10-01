/*
 * Copyright (c) 2013-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// 
// Support
//
// Some supporting stuff
//
//
// Created by Danny Rintoul
//

#ifndef __Support
#define __Support

#include "AirDataRecord.h"
#endif
FlightPoint GetInterpolatedPoint(const Flight &flight, double frac);
boost::posix_time::ptime GetInterpolatedTime(const Flight &flight, double frac);
