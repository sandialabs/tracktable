/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// Predict
//
// Created by Danny Rintoul.


#ifndef __Predict_h
#define __Predict_h
#include "Common.h"

void Predict(Trajectories &trajectories, std::vector<my_data> &features,
 std::vector<my_data> &to_be_predicted, unsigned int sample_size);
void LLPredict(Trajectories &trajectories, std::vector<my_data> &features,
 std::vector<my_data> &to_be_predicted, unsigned int sample_size);

#endif
