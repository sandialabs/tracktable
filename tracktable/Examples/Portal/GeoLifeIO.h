/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// 
// AirDataRoutines
//
// This routine simply reads in the data from flight records that are stored
// in the original format that was obtained by us.  It reads a whole file and
// puts everything in one vector.
//
// Created by Danny Rintoul.
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.

#ifndef __GeoLifeIO
#define __GeoLifeIO
#include "AirDataRoutines.h"
int readGeoLifeFile(std::string &input_file, std::string& sep_char,
 Flights& flights);
void separateGeoLife(Flight_map& flight_map, Flights& flights);
#endif
