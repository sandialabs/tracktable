// 
// Separate
//
// Separates a list of points into actual trajectories
//
// Created by Danny Rintoul.
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.

#ifndef __Separate_h
#define __Separate_h
#include <map>
#include <vector>
#include "Common.h"

#define MIN_FLIGHT_SIZE 20
#define MAX_TIME_GAP 10

void separateMapFlights(Trajectory_map& traj_map, Trajectories &trajectories,
 const int min_flight_size = MIN_FLIGHT_SIZE,
 const int max_time_gap = MAX_TIME_GAP);

void separateFlights(std::vector<Traj_Point> &fps, 
 Trajectories &trajectories, const int min_flight_size = MIN_FLIGHT_SIZE,
 const int max_time_gap = MAX_TIME_GAP);

bool apartInTime(const Traj_Point& tp1, const Traj_Point &tp2, 
 const int max_time_gap = MAX_TIME_GAP);

void cleanFlights(Trajectories &trajectories, 
 const int min_flight_size = MIN_FLIGHT_SIZE);

void cleanFlight(Trajectory &trajectory);

bool badPoint(const Traj_Point &fp1, const Traj_Point &fp2);
#endif
