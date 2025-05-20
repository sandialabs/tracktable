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

#include "KmlOut.h"

#include <random>
#include <stdexcept>
double tracktable::kml::_width = 3;
std::string tracktable::kml::_color = "FFFFFFFF";
std::string tracktable::kml::_name = "UNIDFENTIFIED";
tracktable::Timestamp tracktable::kml::_start;
tracktable::Timestamp tracktable::kml::_stop;
std::string tracktable::kml::_styleid = "tracktable_style";
bool tracktable::kml::_isInsidePlacemark = false;
bool tracktable::kml::_isInsideMultiGeometry = false;

constexpr char tracktable::kml::header[];
constexpr char tracktable::kml::footer[];

namespace tracktable {

using ::operator<<;

using TrajectoryT = kml::TrajectoryT;
using TrajectoryVectorT = kml::TrajectoryVectorT;
using PointT = kml::PointT;

std::string kml::generateColorString() {
    static std::random_device rd;   // Will be used to obtain a seed for the random number engine
    static std::mt19937 gen(rd());  // Standard mersenne_twister_engine seeded with rd()
    static std::uniform_int_distribution<> distrib(0, 255);
    std::stringstream ss;
    ss << std::hex << std::setfill('0') << std::uppercase;
    ss << "FF" << std::setw(2) << distrib(gen) << std::setw(2) << distrib(gen) << std::setw(2)
       << distrib(gen);
    return ss.str();
}

void kml::write(const std::string &_filename, const TrajectoryVectorT &_trajectories) {
    std::ofstream out(_filename);
    if (!out.is_open()) {
        throw std::runtime_error("Could not open output file:" + _filename);
    }
    out << header;
    write(out, _trajectories);
    out << footer;
    out.close();
}

void kml::write(std::ostream &_o, const TrajectoryVectorT &_trajectories) {
    constexpr auto width = 3.0;
    for (auto &t : _trajectories) {
        write(_o, t, generateColorString(), width);
    }
}

void kml::write(std::ostream &_o, const PointerVectorT &_trajectories) {
    constexpr auto width = 3.0;
    for (auto &t : _trajectories) {
        write(_o, *t, generateColorString(), width);
    }
}

void kml::writeToSeparateKmls(const TrajectoryVectorT &_trajectories, const std::string &_output_dir) {
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

void write_name(std::ostream &_o, const std::string &_name) { _o << "  <name>" << _name << "</name>\n"; }
void write_name(std::ostream &_o) { write_name(_o,kml::_name); }

void write_timespan(std::ostream &_o, const tracktable::Timestamp &_start, const tracktable::Timestamp &_end) {
    _o << "  <TimeSpan> <begin>" << boost::posix_time::to_iso_extended_string(_start) << "</begin>\n";
    _o << "             <end>" << boost::posix_time::to_iso_extended_string(_end) << "</end> </TimeSpan>\n";
}
void write_timespan(std::ostream &_o) { write_timespan(_o, kml::_start, kml::_stop); }

void write_styleid(std::ostream &_o, const std::string &_id) {
    _o << "  <styleUrl>#" << _id << "</styleUrl>\n";
}

void write_styleid(std::ostream &_o) {
    write_styleid(_o,kml::_styleid);
}

void writeStyle(std::ostream &_o) {
    static size_t seed = 1u;
    std::string id = "generated" + std::to_string(seed);
    kml::writeStyle(_o, id, kml::_color, kml::_width);
    _o << kml::style_id(id);
}

void kml::writePlacemarkHeader(std::ostream &_o) {
    _o << "<Placemark>\n";
    write_name(_o);
    write_timespan(_o);
    write_styleid(_o);
}

void kml::writePlacemarkFooter(std::ostream &_o) { _o << "</Placemark>" << std::endl; }

void kml::writeMultiGeometryHeader(std::ostream &_o) {
    _o << "<MultiGeometry>\n";
}

void kml::writeMultiGeometryFooter(std::ostream &_o) { _o << "</MultiGeometry>" << std::endl; }

void kml::write(std::ostream &_o, const TrajectoryT &_trajectory, const std::string &_color,
                const double &_width) {
    const auto id = _trajectory.object_id();
    const auto date_string = boost::gregorian::to_simple_string(_trajectory.start_time().date());

    _o << name(id + "-" + date_string);
    _o << time_span(_trajectory.start_time(), _trajectory.end_time());

    writeStyle(_o, id, _color, _width);
    _o << style_id(id);

    writePlacemarkHeader(_o);

    writeLinestring(_o, _trajectory);

    writePlacemarkFooter(_o);
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
    writeMultiGeometryHeader(_o);
    for (auto &p : _trajectory) {
        _o << point(p);
    }
    writeMultiGeometryFooter(_o);
}

void kml::writePoint(std::ostream &_o, const PointT &_point) {
    _o << "    <Point>\n";
    _o << "      <coordinates>\n";
    writeCoords(_o, _point);
    _o << "      </coordinates>\n";
    _o << "    </Point>\n";
}

void kml::writeLineAndPoints(std::ostream &_o, const TrajectoryT &_trajectory) {
    writeMultiGeometryHeader(_o);
    _o << linestring(_trajectory);
    _o << multipoint(_trajectory);
    writeMultiGeometryFooter(_o);
}

void kml::writeBox(std::ostream &_o, const box &_box) {
    TrajectoryT box;
    box.push_back(*_box.corner1);
    box.push_back(PointT(_box.corner1->longitude(), _box.corner2->longitude()));
    box.push_back(*_box.corner2);
    box.push_back(PointT(_box.corner2->longitude(), _box.corner1->latitude()));
    box.push_back(*_box.corner1);
    writeLinestring(_o, box);
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
    constexpr auto GREEN = "FF00FF00";  // KML uses ABGR for some silly reason
    constexpr auto WIDTH = 3.0;
    if (nullptr != _k.trajectoryPtr) {
        tracktable::kml::write(_o, *_k.trajectoryPtr, GREEN, WIDTH);
    } else if (nullptr != _k.trajectoryListPtr) {
        tracktable::kml::write(_o, *_k.trajectoryListPtr);
    } else {
        tracktable::kml::write(_o, *_k.trajectorySmartListPtr);
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

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::box &_b) {
    tracktable::kml::writeBox(_o, _b);
    return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::style &_s) {
    tracktable::kml::writeStyle(_o, _s.id,_s.color,_s.width);
    return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::width & /*_w*/) { return _o; }
std::ostream &operator<<(std::ostream &_o, const tracktable::kml::color & /*_c*/) { return _o; }
std::ostream &operator<<(std::ostream &_o, const tracktable::kml::name & /*_n*/) { return _o; }
std::ostream &operator<<(std::ostream &_o, const tracktable::kml::style_id & /*_s*/) { return _o; }
std::ostream &operator<<(std::ostream &_o, const tracktable::kml::time_span & /*_t*/) { return _o; }

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::startpm & /*_s*/) {
  tracktable::kml::writePlacemarkHeader(_o);
  return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::stoppm & /*_s*/) {
    tracktable::kml::writePlacemarkFooter(_o);
    return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::startmulti & /*_s*/) {
    tracktable::kml::writeMultiGeometryHeader(_o);
    return _o;
}

std::ostream &operator<<(std::ostream &_o, const tracktable::kml::stopmulti & /*_s*/) {
    tracktable::kml::writeMultiGeometryFooter(_o);
    return _o;
}