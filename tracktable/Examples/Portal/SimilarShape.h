// 
// Support
//
// Some supporting stuff
//
//
// Created by Danny Rintoul
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.
//

#ifndef __Support
#define __Support

#include "AirDataRecord.h"
#endif
FlightPoint GetInterpolatedPoint(const Flight &flight, double frac);
boost::posix_time::ptime GetInterpolatedTime(const Flight &flight, double frac);
