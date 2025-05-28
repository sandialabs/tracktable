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
 *
 * Mapping: A simple example for finding mapping flights with lots of
 * back-and-forth motion.
 *
 * Created by Danny Rintoul.
 */

#include "Mapping.h"

#include <algorithm>

// TODO: Move this into tracktable, if there isn't already an equivalent
double HeadingDifference(const double h2, const double h1) {
    return (h2 - h1) - 360.0 * int((h2 - h1) / 180.0);
}

double HeadingDifference(const PointT& t2, const PointT& t1) {
    auto h2 = t2.real_property("heading");
    auto h1 = t1.real_property("heading");
    return HeadingDifference(h2, h1);
}

// TODO: investigate whether this is prudent without assigning headings.
// TODO: Move into tracktable.
unsigned int TurnArounds(TrajectoryT const& trajectory) {
    constexpr size_t window = 5;
    unsigned int ctr = 0;

    if (trajectory.size() <= window) return 0;

    auto itr1 = trajectory.begin();
    auto itr2 = itr1 + window;
    double diff = 0;
    bool found = false;

    do {
        diff = std::abs(itr1->real_property("heading") - itr2->real_property("heading"));

        if (std::abs(diff - 180.0) < 2.0) {  // 2.0 is the fudge factor for comparing against 180 degrees
            if (!found) {
                ++ctr;
            }
            found = true;
        } else {
            found = false;
        }

        if (found) {
            int leap = std::min(static_cast<int>(std::distance(itr2, trajectory.end())), 5);
            // The 5 above is related to how far away you want to go before you
            // define another turnaround
            itr1 += leap;
            itr2 += leap;
        } else {
            ++itr1;
            ++itr2;
        }
    } while (itr2 != trajectory.end());

    return ctr;
}

// ----------------------------------------------------------------------
// TODO: possible to do this without assigning headings using unsigned_angle
double StraightFraction(TrajectoryT const& trajectory) {
    int sum = 0;
    constexpr size_t min_straight_size = 5;

    auto itr1 = trajectory.begin();
    auto itr2 = trajectory.end();

    do {
        // The 2.0 below is related to how different the straightness can be from 180
        itr2 = std::adjacent_find(itr1, trajectory.end(), [](const PointT& _lhs, const PointT& _rhs) {
            return std::abs(HeadingDifference(_lhs, _rhs)) < 2.0;
        });
        if (itr2 != trajectory.end()) {
            ++itr2;
        }

        if (size_t(itr2 - itr1) >= min_straight_size) {
            sum += (itr2 - itr1);
        }

        itr1 = itr2;
    } while (itr2 != trajectory.end());

    return static_cast<double>(sum) / static_cast<double>(trajectory.size());
}
