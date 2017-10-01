/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
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

#include<vector>
#include <iostream>
#include <tracktable/Domain/FeatureVectors.h>

typedef tracktable::domain::feature_vectors::FeatureVector<15> feature_vector;

void Correlation(std::vector<feature_vector>& features)
{
  double mean[15];
  double sq_mean[15];
  double cov[15][15];

  for (unsigned int i = 0; i < 15; ++i) {
    for (unsigned int j = 0; j < 15; ++j)
      cov[i][j] = 0.0;
    mean[i] = 0.0;
    sq_mean[i] = 0.0;
  }

  double N = static_cast<double>(features.size());

  for (unsigned int i = 0; i < features.size(); ++i) 
    for (unsigned int j = 0; j < 15; ++j) {
      mean[j] += features[i][j]/N;
    }

  for (unsigned int i = 0; i < features.size(); ++i) 
    for (unsigned int j = 0; j < 15; ++j) {
      sq_mean[j] += (features[i][j] - mean[j]) * (features[i][j] - mean[j]);
    }

  for (unsigned int i = 0; i < 15; ++i)
    for (unsigned int j = 0; j <= i; ++j)
      for (unsigned int k = 0; k < features.size(); ++k)
        cov[i][j] += ((features[k][i]-mean[i]) * (features[k][j]-mean[j]))
         /(sqrt(sq_mean[i]*sq_mean[j]));

  
  for (unsigned int i = 0; i < 15; ++i) {
    for (unsigned int j = 0; j <= i; ++j)
      std::cout << cov[i][j] << "\t";
    std::cout << std::endl;
  }

  return;
}
