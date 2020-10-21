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

#ifndef KmlOut_h
#define KmlOut_h

#include <tracktable/IO/TracktableIOWindowsHeader.h>

#include <tracktable/Domain/Terrestrial.h>

#include <fstream>
#include <ostream>
#include <string>
#include <vector>

namespace tracktable {
class kml;
}

TRACKTABLE_IO_EXPORT std::ofstream &operator<<(std::ofstream &_o, const tracktable::kml &_k);
TRACKTABLE_IO_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml &_k);

namespace tracktable {

class TRACKTABLE_IO_EXPORT kml {
 public:
  using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
  using VectorT = std::vector<TrajectoryT>;
  using PointT = TrajectoryT::point_type;
  struct linestring {
    linestring(const TrajectoryT &_t) : trajectory(&_t) {}
    TrajectoryT const *const trajectory;
  };
  struct multipoint {
    multipoint(const TrajectoryT &_t) : trajectory(&_t) {}
    TrajectoryT const *const trajectory;
  };
  struct linepoints {
    linepoints(const TrajectoryT &_t) : trajectory(&_t) {}
    TrajectoryT const *const trajectory;
  };
  struct point {
    point(const PointT &_t) : trajectory(&_t) {}
    PointT const *const trajectory;
  };

 public:
  kml(const TrajectoryT &_t) : trajectoryPtr(&_t) {}
  kml(const VectorT &_v) : trajectoryListPtr(&_v) {}
  static constexpr char header[] =
      "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
      "<kml xmlns=\"http://www.opengis.net/kml/2.2\" "
      "xmlns:gx=\"http://www.google.com/kml/ext/2.2\" "
      "xmlns:kml=\"http://www.opengis.net/kml/2.2\">\n"
      "<Document>\n";
  static constexpr char footer[] =
      "</Document>\n"
      "</kml>";

 private:
  friend std::ostream &(::operator<<)(std::ostream &_o, const tracktable::kml &_kml);
  friend std::ofstream &(::operator<<)(std::ofstream &_o, const tracktable::kml &_kml);
  const TrajectoryT *trajectoryPtr = nullptr;
  const VectorT *trajectoryListPtr = nullptr;

 public:
  static std::string generateColorString();

  /** These classes output kml
   * if a file is specified, the header and footer are automatically written
   * if a stream is specified, the header and footer are NOT automatically written
   * write can be called with either a single trajectory or a vector */
  static void write(const std::string &_filename, const VectorT &_trajectories);
  static void write(std::ostream &_o, const VectorT &_trajectories);
  static void write(const std::string &_filename, const TrajectoryT &_trajectory);
  static void write(const std::string &_filename, const TrajectoryT &_trajectory, const std::string &_color,
                    const double &_width);
  static void write(std::ostream &_o, const TrajectoryT &_trajectory, const std::string &_color,
                    const double &_width);
  static void writeStyle(std::ostream &_o, const std::string &_id, const std::string &_color, double _width);
  static void writeLinestring(std::ostream &_o, const TrajectoryT &_trajectory);
  static void writeMultipoint(std::ostream &_o, const TrajectoryT &_trajectory);
  static void writePoint(std::ostream &_o, const PointT &_point);
  static void writeLineAndPoints(std::ostream &_o, const TrajectoryT &_trajectory);
  static void writeCoords(std::ostream &_o, const PointT &_point);
  /** This simplifies writing individual files for a vector
   * The directory to write the files is specified instead of a filename */
  static void writeToSeparateKmls(const VectorT &_trajectories, const std::string &_output_dir);
};

}  // namespace tracktable

TRACKTABLE_IO_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::linestring &_l);
TRACKTABLE_IO_EXPORT std::ostream& operator<<(std::ostream &_o, const tracktable::kml::multipoint &_mp);
TRACKTABLE_IO_EXPORT std::ostream& operator<<(std::ostream &_o, const tracktable::kml::point &_p);
TRACKTABLE_IO_EXPORT std::ostream& operator<<(std::ostream &_o, const tracktable::kml::linepoints &_lp);

#endif
