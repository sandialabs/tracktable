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

#include "BuildFeatures.h"

#include <algorithm>  // for transform
#include <iterator>   //for back_insterter
#include <random>

DataVectorT BuildFeatures(const TrajectoryVectorT &_trajectories, double _fraction) {
    DataVectorT features;
    // transform allows creating a vector of type b from a vector of type a
    std::transform(_trajectories.begin(), _trajectories.end(), std::back_inserter(features),
                   [&](std::shared_ptr<TrajectoryT> _t) { return BuildFeature(_t, _fraction); });
    return features;
}

DataVectorT BuildManyEvenFeatures(const TrajectoryVectorT &_trajectories) {
    DataVectorT features;
    for (auto i = 2u; i <= 8u; ++i) {
        auto f = BuildFeatures(_trajectories, i / 10.0);
        features.insert(features.end(), f.begin(), f.end());
    }
    return features;
}

DataVectorT BuildManyRandomFeatures(const TrajectoryVectorT &_trajectories) {
    DataVectorT features;
    for (auto i = 0u; i < 7u; ++i) {
        auto f = BuildRandomFeatures(_trajectories, 0.2, 0.8);
        features.insert(features.end(), f.begin(), f.end());
    }
    return features;
}

DataVectorT BuildRandomFeatures(const TrajectoryVectorT &_trajectories, double _lower, double _upper) {
    static std::mt19937 gen(0);
    DataVectorT features;
    std::uniform_real_distribution<double> dis(_lower, _upper);  // uniform distribution
    std::transform(_trajectories.begin(), _trajectories.end(), std::back_inserter(features),
                   [&](std::shared_ptr<TrajectoryT> _t) { return BuildFeature(_t, dis(gen)); });
    return features;
}

PredictData BuildFeature(std::shared_ptr<TrajectoryT> _trajectory, double _fraction) {
    // Nothing complicated here.  Basically, divide the trajectory up into
    // some even-sized pieces, and take the early way-points and build a
    // feature vector out of them. The only tricky part is that when you
    // divide a trajectory into n pieces, you essentially have n+1 points
    // to choose from.

    constexpr auto numSamples = 4u;  // Must be >= 2 and <= 4

    PredictData::FeatureT feature;
    static_assert(((numSamples - 1) * 2 + 1) < feature.size(), "Size Mismatch");
    for (auto i = 0u; i < numSamples; ++i) {
        auto frac = _fraction * double(i) / double(numSamples - 1.0);
        auto p = tracktable::point_at_length_fraction(*_trajectory, frac);
        feature[2 * i] = p.longitude();
        feature[2 * i + 1] = p.latitude();
    }
    auto p = tracktable::point_at_length_fraction(*_trajectory, _fraction);
    feature[2 * numSamples] = (p.timestamp() - _trajectory->front().timestamp()).seconds() / 1200.;

    return PredictData(feature, 0, _trajectory);
}
