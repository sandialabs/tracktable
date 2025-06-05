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

#include "GreatCircleFit.h"

#include <tracktable/Domain/Terrestrial.h>

// TODO: template/sfinae for double/float
double constexpr sqrt_recursion(double _x, double _curr, double _prev) {
  return _curr == _prev ? _curr : sqrt_recursion(_x, 0.5 * (_curr + _x / _curr), _curr);
}

/** @brief constexpr sqrt because sqrt are the spot to optimize and standard library lacks
 * it for some reason
 * @note Ternary(?)  used because c++14 does not have constexpr_if
 * @param x The number to take the square root of
 * @return double constexpr
 */
double constexpr constsqrt(double _x) {
  return _x >= 0 && _x < std::numeric_limits<double>::infinity() ? sqrt_recursion(_x, _x, 0)
                                                                 : std::numeric_limits<double>::quiet_NaN();
}

/* optimization function */
double opt_fun(const tracktable::domain::cartesian3d::base_point_type &_p,
               const tracktable::domain::terrestrial::trajectory_type &_trajectory,
               std::string _altitude_string, tracktable::domain::terrestrial::AltitudeUnits _unit);
tracktable::domain::cartesian3d::base_point_type add_scaled_vector(
    const tracktable::domain::cartesian3d::base_point_type &_v0,
    const tracktable::domain::cartesian3d::base_point_type &_v1, double _fac);
void project_point_onto_plane_in_place(tracktable::domain::terrestrial::trajectory_point_type &_t_point,
                                       const tracktable::domain::cartesian3d::base_point_type &_normal,
                                       std::string _altitude_string,
                                       tracktable::domain::terrestrial::AltitudeUnits _unit);

namespace tracktable {

void great_circle_fit_and_project_in_place(tracktable::domain::terrestrial::trajectory_type &_trajectory,
                                           std::string _altitude_string,
                                           tracktable::domain::terrestrial::AltitudeUnits _unit) {
  tracktable::domain::cartesian3d::base_point_type normal = find_best_fit_plane(_trajectory);
  project_trajectory_onto_plane(_trajectory, normal, _altitude_string, _unit);
}

tracktable::domain::terrestrial::trajectory_type great_circle_fit_and_project(
    tracktable::domain::terrestrial::trajectory_type const &_trajectory, std::string _altitude_string,
    tracktable::domain::terrestrial::AltitudeUnits _unit) {
  tracktable::domain::terrestrial::trajectory_type result(_trajectory);
  great_circle_fit_and_project_in_place(result, _altitude_string, _unit);
  return result;
}

// TODO: Does not work well with trajectories with poor aspect ratio, should work direction of travel into it
tracktable::domain::cartesian3d::base_point_type find_best_fit_plane(
    const tracktable::domain::terrestrial::trajectory_type &_trajectory, std::string _altitude_string,
    tracktable::domain::terrestrial::AltitudeUnits _unit) {
  if (_trajectory.size() < 2) {
    throw TooFewPoints();
  }
  // First guess at the perpendicular to the plane!  There are a couple of
  // ways to do this, but this is the easiest.
  // First, we need to ensure we have two different points
  auto p = _trajectory.begin();
  auto v2 = _trajectory.back().ECEF(_altitude_string, _unit);
  auto v1 = (*p).ECEF(_altitude_string, _unit);
  while (std::next(p) != _trajectory.end() && v1 == v2) {
    v1 = (*(++p)).ECEF(_altitude_string, _unit);
  }
  if (v1 == v2) {
    throw IdenticalPositions();
  }

  // Then we can use them to make a first guess
  auto normal = tracktable::arithmetic::normalize(tracktable::arithmetic::cross_product(v1, v2));

  // Using our initial guess, see our optimization value.  We are trying
  // to minimize this.
  double minSum = opt_fun(normal, _trajectory, _altitude_string, _unit);

  // Tools for our optimization routine.  The first two give us a way to
  // find a neighborhood of points, the second is or control over how
  // much we want to optimize

  constexpr auto sqrt2 = constsqrt(2.0);
  constexpr auto numDirections = 8u;
  constexpr std::array<double, 8> cyc = {0.0, sqrt2, 1.0, sqrt2, 0.0, -sqrt2, -1.0, -sqrt2};
  constexpr double eps = 5.0e-8;
  // TODO: implement acceleration/deceleration of epsilon

  auto changed = false;
  do {
    changed = false;
    tracktable::domain::cartesian3d::base_point_type curPoint = normal;

    // Get some perpendiculars to our point on the sphere so we can walk
    // around it in a systematic way.
    v2 = tracktable::arithmetic::cross_product(normal,
                                               v1);  // TODO: maybe point this at the point of greatest error
    v1 = tracktable::arithmetic::cross_product(normal, v2);

    // Find the value of the optimization function in points around us.
    // We are done we all of the values are larger.
    for (auto i = 0u; i < numDirections; ++i) {
      auto temp = curPoint;
      temp = add_scaled_vector(temp, v1, eps * cyc.at(i));
      temp = add_scaled_vector(temp, v2, eps * cyc.at((i + 2u) % numDirections));
      tracktable::arithmetic::normalize_in_place(temp);
      auto sum = opt_fun(temp, _trajectory, _altitude_string, _unit);
      if (sum < minSum) {
        normal = temp;
        minSum = sum;
        changed = true;
      }
    }
  } while (changed);
  return normal;
}

void project_trajectory_onto_plane(tracktable::domain::terrestrial::trajectory_type &_trajectory,
                                   const tracktable::domain::cartesian3d::base_point_type &_normal,
                                   std::string _altitude_string,
                                   tracktable::domain::terrestrial::AltitudeUnits _unit) {
  if (_trajectory.empty()) {
    throw TooFewPoints();
  }
  if (0.0 == tracktable::arithmetic::norm_squared(_normal)) {
    throw ZeroNorm();
  }
  for (auto &p : _trajectory) {
    project_point_onto_plane_in_place(p, _normal, _altitude_string, _unit);
  }
}

}  // namespace tracktable

double opt_fun(const tracktable::domain::cartesian3d::base_point_type &_p,
               const tracktable::domain::terrestrial::trajectory_type &_trajectory,
               std::string _altitude_string, tracktable::domain::terrestrial::AltitudeUnits _unit) {
  auto sum = 0.0;
  for (const auto &p : _trajectory) {
    auto val =
        tracktable::arithmetic::dot(_p, tracktable::arithmetic::normalize(p.ECEF(_altitude_string, _unit)));
    // val += val * val * val / 6.0;  // TODO: Ask Rintoul to confirm the +=
    sum += std::abs(val);  // * val;
  }
  return sum;
}

tracktable::domain::cartesian3d::base_point_type add_scaled_vector(
    const tracktable::domain::cartesian3d::base_point_type &_v0,
    const tracktable::domain::cartesian3d::base_point_type &_v1, double _fac) {
  return tracktable::arithmetic::add(_v0, tracktable::arithmetic::multiply_scalar(_v1, _fac));
}

// TODO: create a fromECEF() function or Trajectory point constructor that does the conversion
void project_point_onto_plane_in_place(tracktable::domain::terrestrial::trajectory_point_type &_t_point,
                                       const tracktable::domain::cartesian3d::base_point_type &_normal,
                                       std::string _altitude_string,
                                       tracktable::domain::terrestrial::AltitudeUnits _unit) {
  // An elegant way to project points.  Basically, most of these points
  // are very close to the plane.  So if you find the dot product between
  // the trajectory points and the perpendicular, that will be a tiny
  // number that essentially represents the amount you have to move the
  // point to get it to the plane.  There are some small angle approximations
  // happening here, but to second order, it's all good, and to third order,
  // you are running out of digits on your double.
  constexpr double a = 6378.137;
  constexpr double e2 = 8.1819190842622e-2 * 8.1819190842622e-2;
  constexpr double a2 = a * a;
  constexpr double b2 = a2 * (1.0 - e2);
  constexpr double b = constsqrt(b2);
  constexpr double ep2 = (a2 - b2) / b2;

  auto pt = _t_point.ECEF(_altitude_string, _unit);
  pt = add_scaled_vector(pt, _normal, -1.0 * tracktable::arithmetic::dot(pt, _normal));

  auto p = std::sqrt(pt[0] * pt[0] + pt[1] * pt[1]);
  auto th = std::atan2(a * pt[2], b * p);
  auto sinTh = std::sin(th);
  auto cosTh = std::cos(th);

  auto lon = atan2(pt[1], pt[0]);
  auto lat = atan2(pt[2] + ep2 * b * sinTh * sinTh * sinTh, p - e2 * a * cosTh * cosTh * cosTh);

  _t_point.set_longitude(tracktable::conversions::degrees(lon));
  _t_point.set_latitude(tracktable::conversions::degrees(lat));

  // auto sin_lat = std::sin(lat);
  // auto N = a / std::sqrt(1.0 - e2 * sin_lat * sin_lat);
  // double alt = p / cos(lat) - N;
  //_tPoint.set_property(_altitudeString,alt);
}
