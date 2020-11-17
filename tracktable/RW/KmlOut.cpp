/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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

#include "KmlOut.h"

#include <random>
#include <stdexcept>


constexpr char tracktable::kml::header[];
constexpr char tracktable::kml::footer[];

namespace tracktable {

using ::operator<<;

using TrajectoryT = kml::TrajectoryT;
using VectorT = kml::VectorT;
using PointT = kml::PointT;

std::string kml::generateColorString() {
  static std::random_device rd;   // Will be used to obtain a seed for the random number engine
  static std::mt19937 gen(rd());  // Standard mersenne_twister_engine seeded with rd()
  static std::uniform_int_distribution<> distrib(0, 255);
  std::stringstream ss;
  ss << std::hex << std::setfill('0') << std::uppercase;
  ss << "FF" << std::setw(2) << distrib(gen) << std::setw(2) << distrib(gen) << std::setw(2) << distrib(gen);
  return ss.str();
}

void kml::write(const std::string &_filename, const VectorT &_trajectories) {
  std::ofstream out(_filename);
  if (!out.is_open()) {
    throw std::runtime_error("Could not open output file:" + _filename);
  }
  out << header;
  write(out, _trajectories);
  out << footer;
  out.close();
}

void kml::write(std::ostream &_o, const VectorT &_trajectories) {
  constexpr auto width = 3.0;
  for (auto &t : _trajectories) {
    write(_o, t, generateColorString(), width);
  }
}

void kml::writeToSeparateKmls(const VectorT &_trajectories, const std::string &_output_dir) {
  for (auto &t : _trajectories) {
    // Assumes one track per day with some id
    auto filename = _output_dir + t.object_id() + "-" +
                    boost::gregorian::to_simple_string(t.start_time().date()) + ".kml";
    std::ofstream out(filename);
    out << kml(t);
  }
}

void kml::write(const std::string &_filename, const TrajectoryT &_trajectory) {
  constexpr auto width = 3.0;
  write(_filename, _trajectory, generateColorString(), width);
}

void kml::write(const std::string &_filename, const TrajectoryT &_trajectory, const std::string &_color,
                const double &_width) {
  std::ofstream out(_filename);
  if (!out.is_open()) {
    throw std::runtime_error("Could not open output file:" + _filename);
  }
  out << header;
  write(out, _trajectory, _color, _width);
  out << footer;
  out.close();
}

void kml::write(std::ostream &_o, const TrajectoryT &_trajectory, const std::string &_color,
                const double &_width) {
  const auto id = _trajectory.object_id();
  const auto start_time = boost::posix_time::to_iso_extended_string(_trajectory.start_time());
  const auto end_time = boost::posix_time::to_iso_extended_string(_trajectory.end_time());
  const auto date_string = boost::gregorian::to_simple_string(_trajectory.start_time().date());
  writeStyle(_o, id, _color, _width);
  _o << "<Placemark>\n";
  _o << "  <name>" << id + "-" + date_string << "</name>\n";
  _o << "  <TimeSpan> <begin>" << start_time << "</begin>\n";
  _o << "             <end>" << end_time << "</end> </TimeSpan>\n";
  _o << "  <styleUrl>#" << id << "</styleUrl>\n";
  writeLinestring(_o, _trajectory);
  _o << "</Placemark>" << std::endl;  // Flush at the end.
}

void kml::writeStyle(std::ostream &_o, const std::string &_id, const std::string &_color, double _width) {
  _o << "<Style id=\"" << _id << "\">\n";
  _o << "  <LineStyle>\n";
  _o << "    <gx:labelVisibility>1</gx:labelVisibility>\n";
  _o << "    <width>" << _width << "</width>\n";
  _o << "    <color>" << _color << "</color>\n";
  _o << "  </LineStyle>\n";
  _o << "</Style>\n";
}
void kml::writeLinestring(std::ostream &_o, const TrajectoryT &_trajectory) {
  _o << "  <LineString>\n";
  _o << "    <coordinates>\n";
  for (auto &p : _trajectory) {
    writeCoords(_o, p);
  }
  _o << "    </coordinates>\n";
  _o << "  </LineString>\n";
}
void kml::writeMultipoint(std::ostream &_o, const TrajectoryT &_trajectory) {
  _o << "  <MultiGeometry>\n";
  for (auto &p : _trajectory) {
    _o << point(p);
  }
  _o << "  </MultiGeometry>";
}
void kml::writePoint(std::ostream &_o, const PointT &_point) {
  _o << "    <Point>\n";
  _o << "      <coordinates>\n";
  writeCoords(_o, _point);
  _o << "      </coordinates>\n";
  _o << "    </Point>\n";
}

void kml::writeLineAndPoints(std::ostream &_o, const TrajectoryT &_trajectory) {
  _o << "  <MultiGeometry>\n";
  _o << linestring(_trajectory);
  _o << multipoint(_trajectory);
  _o << "  </MultiGeometry>";
}

void kml::writeCoords(std::ostream &_o, const PointT &_point) {
  // TODO: address issue of ft vs m
  _o << "        " << _point.longitude() << "," << _point.latitude() << ","
     << _point.real_property("Altitude") << "\n";
  // TODO: address real_property_with_default not working here.
}

}  // namespace tracktable

std::ofstream &operator<<(std::ofstream &_o, const tracktable::kml &_k) {
  _o << tracktable::kml::header;
  static_cast<std::ostream &>(_o) << _k;
  _o << tracktable::kml::footer;
  return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml &_k) {
  constexpr auto GREEN = "FF00FF00"; //KML uses ABGR for some silly reason
  constexpr auto WIDTH = 3.0;
  if (nullptr != _k.trajectoryPtr) {
    tracktable::kml::write(_o, *_k.trajectoryPtr, GREEN, WIDTH);
  } else {
    tracktable::kml::write(_o, *_k.trajectoryListPtr);
  }
  return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::linestring &_l) {
  tracktable::kml::writeLinestring(_o, *_l.trajectory);
  return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::multipoint &_mp) {
  tracktable::kml::writeMultipoint(_o, *_mp.trajectory);
  return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::point &_p) {
  tracktable::kml::writePoint(_o, *_p.trajectory);
  return _o;
}
std::ostream &operator<<(std::ostream &_o, const tracktable::kml::linepoints &_lp) {
  tracktable::kml::writeLineAndPoints(_o, *_lp.trajectory);
  return _o;
}
