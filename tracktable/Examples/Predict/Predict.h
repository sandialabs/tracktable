// 
// Predict
//
// Created by Danny Rintoul.
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.

#ifndef __Predict_h
#define __Predict_h
#include "Common.h"

void Predict(Trajectories &trajectories, std::vector<my_data> &features, 
 std::vector<my_data> &to_be_predicted, unsigned int sample_size);
void LLPredict(Trajectories &trajectories, std::vector<my_data> &features,
 std::vector<my_data> &to_be_predicted, unsigned int sample_size);

#endif
