/*
 * Copyright (c) 2015, Sandia Corporation.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// Panther Trajectory Library
//
// CleanTrajectories
//
// This is a routines that takes a vector of Trajectories and cleans bad points

#ifndef _CleanTrajectories_h
#define _CleanTrajectories_h

#include "Common.h"

#define MIN_FLIGHT_SIZE 20 // Minimum number of points for a flight
#define MAX_DIST_SEP 60.0 // Maximum allowed distance between point in nm
#define MAX_ALT_CHANGE 75000 // Maximum altitude change between points 
#define MIN_TIME_SEP 30 // Minimum time separation between points in seconds
#define MIN_ALT 0 // Minimum altitude for valid points

void CleanTrajectories(Trajectories& trajectories, 
 int min_flight_size=MIN_FLIGHT_SIZE, 
 int min_time_between_points=MIN_TIME_SEP, 
 double max_distance_between_points=MAX_DIST_SEP, 
 int max_altitude_change=MAX_ALT_CHANGE, int min_altitude=MIN_ALT);

void CleanTrajectory(BasicTrajectory& trajectory, 
 int min_flight_size=MIN_FLIGHT_SIZE, 
 int min_time_between_points=MIN_TIME_SEP, 
 double max_distance_between_points=MAX_DIST_SEP, 
 int max_altitude_change=MAX_ALT_CHANGE, int min_altitude=MIN_ALT);

bool badPoint(const tracktable::TrajectoryPoint<tracktable::PointLonLat>& fp1, 
 const tracktable::TrajectoryPoint<tracktable::PointLonLat>& fp2, 
 int min_time_between_points, double max_distance_between_points, 
 int max_altitude_change, int min_altitude);

#endif
