/* Copyright (c) 2014-2023 National Technology and Engineering
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

#ifndef GreatCircleFit_h
#define GreatCircleFit_h

#include <tracktable/Analysis/TracktableAnalysisWindowsHeader.h>
#include <tracktable/Domain/Cartesian3D.h>
#include <tracktable/Domain/Terrestrial.h>

/**
 * @brief An exception thrown when a trajectory has too few points
 */
class TooFewPoints : public std::runtime_error {
 public:
  TooFewPoints() : std::runtime_error("Trajectory contains too few points") {}
};

/**
 * @brief An exception thrown when two trying to take a cross product of a point with itself
 */
class IdenticalPositions : public std::runtime_error {
 public:
  IdenticalPositions() : std::runtime_error("Cannot cross a vector with itself") {}
};

/**
 * @brief An exceptions thrown when trying to pass a zero point for plane normal
 */
class ZeroNorm : public std::runtime_error {
 public:
  ZeroNorm() : std::runtime_error("Cannot define a plane with a normal of 0") {}
};

namespace tracktable {

/** @brief Find the best fit plane and project onto it
 *   The purpose is to do a linear fit on a globe. Thus it only works with terrestrial trajectories
 * @note in place version is a destructive the process, the trajectory is modified.
 * @param _trajectory The trajectory to be 'linearized'
 * @param _altitude_string Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT
void great_circle_fit_and_project_in_place(tracktable::domain::terrestrial::trajectory_type &_trajectory,
                                           std::string _altitude_string = "altitude",
                                           tracktable::domain::terrestrial::AltitudeUnits _unit =
                                               tracktable::domain::terrestrial::AltitudeUnits::FEET);

/** @brief Find the best fit plane and project onto it
 *   The purpose is to do a linear fit on a globe. Thus it only works with terrestrial trajectories
 * @note non destructive version.
 * @param _trajectory The trajectory to be 'linearized'
 * @param _altitude_string Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT tracktable::domain::terrestrial::trajectory_type great_circle_fit_and_project(
    tracktable::domain::terrestrial::trajectory_type const &_trajectory,
    std::string _altitude_string = "altitude",
    tracktable::domain::terrestrial::AltitudeUnits _unit =
        tracktable::domain::terrestrial::AltitudeUnits::FEET);

/** @brief We find the vector representing the normal to the plane where the
 * total squared distance of points in the trajectory to that plane is minimized.
 * @param _trajectory The trajectory to fit
 * @return The normal (in ECEF space) representing the best fit plane.
 * @param _altitude_string Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT
tracktable::domain::cartesian3d::base_point_type find_best_fit_plane(
    const tracktable::domain::terrestrial::trajectory_type &_trajectory,
    std::string _altitude_string = "altitude",
    tracktable::domain::terrestrial::AltitudeUnits _unit =
        tracktable::domain::terrestrial::AltitudeUnits::FEET);

/** @brief Project a trajectory onto a plane defined by it's normal in ECEF space
 *
 * @param _trajectory the trajectory to project
 * @param _normal The normal that defines the plane to project on to
 * @param _altitude_string Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT
void project_trajectory_onto_plane(tracktable::domain::terrestrial::trajectory_type &_trajectory,
                                   const tracktable::domain::cartesian3d::base_point_type &_normal,
                                   std::string _altitude_string = "altitude",
                                   tracktable::domain::terrestrial::AltitudeUnits _unit =
                                       tracktable::domain::terrestrial::AltitudeUnits::FEET);

}  // namespace tracktable

#endif
