// 
// BuildFeatures
//
// Created by Danny Rintoul.
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.

#ifndef __BuildFeatures_h
#define __BuildFeatures_h
#include "Common.h"

void BuildFeatures(Trajectories &trajectories, std::vector<my_data> &features,
 double flight_frac);
void BuildManyEvenFeatures(Trajectories &trajectories, 
 std::vector<my_data> &features);
void BuildManyRandomFeatures(Trajectories &trajectories, 
 std::vector<my_data> &features);
void BuildRandomFeatures(Trajectories &trajectories,
 std::vector<my_data> &features, double lower, double upper);
my_data BuildFeature(trajectory_type &trajectory, double flight_frac);

#endif
