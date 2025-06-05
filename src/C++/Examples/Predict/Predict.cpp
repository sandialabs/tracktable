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

#include "Predict.h"

#include "BuildFeatures.h"
#include "PredictData.h"

#include <tracktable/RW/KmlOut.h>

using tracktable::kml;

void Predict(const TrajectoryVectorT &_trajectories, const size_t _numSamples) {
    // This routine builds a feature database from specific intervals
    auto features = BuildManyEvenFeatures(_trajectories);
    // use random features as our 'test' set
    auto to_be_predicted = BuildRandomFeatures(_trajectories, 0.2, 0.8);

    // Create rtree for our predictions
    PredictRtreeT rtree;
    // std::vector<PredictRtreeT::value_type> data;

    // Build the feature vector/id number combo for the rtree.  There is an
    // unused value set to 0 that might be used in the future.

    for (auto i = 0u; i < features.size(); ++i) {
        rtree.insert(&(features[i]));
    }

    // Define the the number of trajectories that will be used to predict
    // the destination.  The bins vector will be used to hold the result of
    // how far down the potential list of predicted destinations you need to
    // go to find the right destination.  The bins vector is a little larger
    // to hold the count of getting it wrong.

    std::vector<size_t> bins(_numSamples + 1);

    // Okay.  Here is where the work is done.  Go through each flight and
    // find all of its neighbors to predict where it will land.

    for (auto &current : to_be_predicted) {
        std::vector<PredictRtreeT::value_type> result_n;

        // Note we are getting more results than _numSamples.  This is because
        // we will throw out the hit that corresponds to the trajectory itself.
        // It would be cheating to use that for prediction.

        auto it = rtree.qbegin(boost::geometry::index::nearest(current.feature, _numSamples + 10));
        for (; (it != rtree.qend()) && (result_n.size() < _numSamples); ++it) {
            if ((*it)->index != current.index) result_n.push_back(*it);
        }

        using WeightPairT = std::pair<std::string, double>;
        std::map<WeightPairT::first_type, WeightPairT::second_type> weights;

        TrajectoryVectorT results;

        auto dest = current.index->front().string_property("dest");
        std::cout << dest << std::endl;

        // Take the results from the rtree query, and then build a vector that
        // has the resulting flights.  In addition, build a table of weights for
        // each potential destination (via a map) using what is essentially a
        // 1/d^2 weight.  The d^2 term comes from the "comparable_distance"
        // function.

        auto total_weight = 0.0;
        for (auto &found : result_n) {
            double weight =
                1.0 / (0.01 + boost::geometry::comparable_distance(current.feature, found->feature));
            total_weight += weight;
            results.push_back(found->index);
            weights[found->index->front().string_property("dest")] += weight;
        }

        // An intermediate step.  Basically, the elements of the map are sorted
        // by key (destination) not by value (weight).  We put them in a vector
        // that will be sorted by value since that is how we will use them.

        std::vector<WeightPairT> sorted(weights.begin(), weights.end());

        // Do the actual sorting.  Have to specify using the second element since
        // sort will use the first element (destination) by default.

        std::sort(sorted.begin(), sorted.end(),
                  [](WeightPairT &_lhs, WeightPairT &_rhs) { return _lhs.second > _rhs.second; });

        // Here is where we fill the bin of whether they were ther first guess,
        // second guess, etc., or wrong. The wrong answers go in the 0 bin.
        // The number is done by iterator subtraction, which is a totally
        // valid way to do things in C++.  Note that if pos == sorted.size(),
        // then the find_if returned sorted.end() and the value was
        // not found.

        // size_t cast safe because gauranteed >= 0
        auto pos = size_t(std::find_if(sorted.begin(), sorted.end(),
                                       [&dest](WeightPairT &_wp) { return _wp.first == dest; }) -
                          sorted.begin());
        ++bins[pos == sorted.size() ? 0 : pos + 1];

        if ((pos != sorted.size()) && (pos == 3) && (total_weight > 400)) {
            std::string filename = "output/" + current.index->object_id() + "cand.kml";
            std::ofstream canidateOut(filename);
            if (!canidateOut.is_open()) {
                std::cerr << "Could not open" << filename << std::endl;
            } else {
                canidateOut << kml(results);
            }
            filename = "output/" + current.index->object_id() + ".kml";
            std::ofstream resultOut(filename);
            if (!resultOut.is_open()) {
                std::cerr << "Could not open" << filename << std::endl;
            } else {
                resultOut << kml(*(current.index));
            }
        }
    }

    int total = 0;
    for (unsigned int i = 1; i < bins.size(); ++i) {
        total += bins[i];
        std::cout << "bins[" << i << "] = " << bins[i] << ", total = " << total
                  << ", cumulative fraction  = " << double(total) / double(to_be_predicted.size())
                  << std::endl;
    }
    std::cout << "Got " << bins[0] << " (" << double(bins[0]) / double(to_be_predicted.size())
              << " fraction) wrong" << std::endl;
}
