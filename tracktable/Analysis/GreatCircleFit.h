/* Copyright (c) 2014-2020 National Technology and Engineering
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

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using TrajectoryPointT = typename TrajectoryT::point_type;

using Point3dT = tracktable::domain::cartesian3d::base_point_type;

class TooFewPoints : public std::runtime_error {
 public:
  TooFewPoints() : std::runtime_error("Trajectory contains too few points") {}
};

class IdenticalPositions : public std::runtime_error {
 public:
  IdenticalPositions() : std::runtime_error("Cannot cross a vector with itself") {}
};

class ZeroNorm : public std::runtime_error {
 public:
  ZeroNorm() : std::runtime_error("Cannot define a plane with a normal of 0") {}
};

namespace tracktable {
namespace domain {
namespace terrestrial {

/** @brief Find the best fit plane and project onto it
 *   The purpose is to do a linear fit on a globe.
 * @note in place version is a destructive the process, the trajectory is modified.
 * @param _trajectory The trajectory to be 'linearized'
 * @param _altitudeString Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT
void great_circle_fit_and_project_in_place(TrajectoryT &_trajectory, std::string _altitudeString = "altitude",
                                           AltitudeUnits _unit = AltitudeUnits::FEET);

/** @brief Find the best fit plane and project onto it
 *   The purpose is to do a linear fit on a globe.
 * @note non destructive version.
 * @param _trajectory The trajectory to be 'linearized'
 * @param _altitudeString Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT TrajectoryT
great_circle_fit_and_project(TrajectoryT const &_trajectory, std::string _altitudeString = "altitude",
                             AltitudeUnits _unit = AltitudeUnits::FEET);

/** @brief We find the vector representing the normal to the plane where the
 * total squared distance of points in the trajectory to that plane is minimized.
 * @param _trajectory The trajectory to fit
 * @return The normal (in ECEF space) representing the best fit plane.
 * @param _altitudeString Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT
Point3dT find_best_fit_plane(const TrajectoryT &_trajectory, std::string _altitudeString = "altitude",
                             AltitudeUnits _unit = AltitudeUnits::FEET);

/** @brief Project a trajectory onto a plane defined by it's normal in ECEF space
 *
 * @param _trajectory the trajectory to project
 * @param _normal The normal that defines the plane to project on to
 * @param _altitudeString Label of point property that contains altitude
 * @param _unit Units of the altitude property
 */
TRACKTABLE_ANALYSIS_EXPORT
void project_trajectory_onto_plane(TrajectoryT &_trajectory, const Point3dT &_normal,
                                   std::string _altitudeString = "altitude",
                                   AltitudeUnits _unit = AltitudeUnits::FEET);

}  // namespace terrestrial
}  // namespace domain
}  // namespace tracktable

#endif
