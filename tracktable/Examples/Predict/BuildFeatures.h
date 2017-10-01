/*
 * Copyright (c) 2015-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// 
// BuildFeatures
//
// Created by Danny Rintoul.

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
