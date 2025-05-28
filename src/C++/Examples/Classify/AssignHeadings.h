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

#ifndef AssignHeadings_h
#define AssignHeadings_h

#include <tracktable/Core/detail/algorithm_signatures/Bearing.h>
#include <tracktable/Core/detail/algorithm_signatures/TurnAngle.h>

#include <algorithm>
#include <vector>

template <typename TrajectoryT>
void AssignTrajectoryHeadings(TrajectoryT &trajectory) {
    if (trajectory.size() == 0) return;
    if (trajectory.size() == 1) {
        trajectory[0].set_property("heading", 0.0);
        return;
    }
    for (unsigned int i = 0; i < trajectory.size() - 1; ++i) {
        trajectory[i].set_property("heading", tracktable::bearing(trajectory[i], trajectory[i + 1]));
    }
    trajectory[trajectory.size() - 1].set_property(
        "heading", trajectory[trajectory.size() - 2].real_property("heading"));
}
// overload for vector type
template <typename TrajectoryT>
void AssignTrajectoryHeadings(std::vector<TrajectoryT> &trajectories) {
    // use static cast to specify which overload
    std::for_each(trajectories.begin(), trajectories.end(),
                  static_cast<void (*)(TrajectoryT &)>(AssignTrajectoryHeadings<TrajectoryT>));
}

template <typename TrajectoryT>
double TotalCurvature(TrajectoryT const &trajectory) {
    if (trajectory.size() < 3) {
        return 0.0;
    }
    auto curvature = 0.0;
    for (auto i = 1u; i < trajectory.size() - 1; ++i)
        curvature += signed_turn_angle(trajectory[i - 1], trajectory[i], trajectory[i + 1]);
    return curvature;
}

#endif
