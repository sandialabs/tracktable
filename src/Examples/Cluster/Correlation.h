/*
 * Copyright (c) 2014-2023 National Technology and Engineering
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

#ifndef Correlation_h
#define Correlation_h

#include <tracktable/Domain/FeatureVectors.h>

#include <sstream>
#include <string>
#include <vector>

/** Calculates and prints the covariance matrix for a set of features.
 * @Tparam N size of individual feature vector
 * @param feature Vector of feature vectors to display covariance matrix of
 */
template <size_t N>
std::string Correlation(std::vector<tracktable::domain::feature_vectors::FeatureVector<N>>& features) {
    double mean[N] = {0.0};
    double sq_mean[N] = {0.0};
    double cov[N][N] = {{0.0}};

    for (auto i = 0u; i < features.size(); ++i) {
        for (auto j = 0u; j < N; ++j) {
            mean[j] += features[i][j] / static_cast<double>(N);
        }
    }

    for (auto i = 0u; i < features.size(); ++i) {
        for (auto j = 0u; j < N; ++j) {
            auto e = features[i][j] - mean[j];
            sq_mean[j] += e * e;
        }
    }
    for (auto k = 0u; k < features.size(); ++k) {
        auto& feature = features[k];
        for (auto i = 0u; i < N; ++i) {
            for (auto j = 0u; j <= i; ++j) {
                cov[i][j] +=
                    ((feature[i] - mean[i]) * (feature[j] - mean[j])) / (sqrt(sq_mean[i] * sq_mean[j]));
            }
        }
    }

    std::stringstream result;
    for (auto& row : cov) {
        for (auto& col : row) {
            result << std::setw(8) << col << "\t";
        }
        result << "\b\n";
    }
    return result.str();
}

#endif
