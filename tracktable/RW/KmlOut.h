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

#include <tracktable/RW/TracktableRWWindowsHeader.h>

#include <tracktable/Domain/Terrestrial.h>

#include <fstream>
#include <ostream>
#include <string>
#include <vector>

namespace tracktable {
class kml;
}

TRACKTABLE_RW_EXPORT std::ofstream &operator<<(std::ofstream &_o, const tracktable::kml &_k);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml &_k);

namespace tracktable {

class TRACKTABLE_RW_EXPORT kml {
/** Handles writing tracks as kml
 * Has lots of internal structure to make the following use cases work:
 *
 * std::cout << kml::header;
 * std::cout << kml(t);
 * std::cout << kml::footer;
 *
 * out = ofstream;
 * out << kml(t);
 *
 * For both the above a default style will be used (green, width =3) in the case
 * of a single trajectory and a random color will be used with the same default
 * width=3 for a vector of trajectories.
 * -----------------------------------------------------------------------------
 * To control color and width:
 *
 * std::cout << kml::header;
 * kml::write(std::cout, t, "AABBGGRR", 4)
 * std::cout << kml::footer;
 *
 * kml::write("filname", t, "AABBGGRR", 5)
 *
 * These are the limits of style control at this time.
 *
 * TODO: Simplify use of multipoint and linepoint methods (requires placemark)
 * TODO: Implement placemark manipulation
 * TODO: Implement style manipulation
 */

 public:
  using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
  using VectorT = std::vector<TrajectoryT>;
  using PointT = TrajectoryT::point_type;
  /** Helper struct that allows for for
    * out << linestring(t)
    * which will render as a line
    * This will be missing some header/footer neccesary for full kml rendering */
  struct linestring {
    linestring(const TrajectoryT &_t) : trajectory(&_t) {}
    TrajectoryT const *const trajectory;
  };
  /** Helper struct that allows for for
   * out << multipoint(t)
   * which will render as set of points
   * This will be missing some header/footer neccesary for full kml rendering */
  struct multipoint {
    multipoint(const TrajectoryT &_t) : trajectory(&_t) {}
    TrajectoryT const *const trajectory;
  };
  /** Helper struct that allows for for
   * out << linepoints(t)
   * which will render as lines with points
   * This will be missing some header/footer neccesary for full kml rendering */
  struct linepoints {
    linepoints(const TrajectoryT &_t) : trajectory(&_t) {}
    TrajectoryT const *const trajectory;
  };
  /** Helper struct that allows for for
   * out << point(t)
   * which will render as a single point
   * This will be missing some header/footer neccesary for full kml rendering */
  struct point {
    point(const PointT &_t) : trajectory(&_t) {}
    PointT const *const trajectory;
  };

 public:
  kml(const TrajectoryT &_t) : trajectoryPtr(&_t) {}
  kml(const VectorT &_v) : trajectoryListPtr(&_v) {}
  /** This will start a kml file off */
  static constexpr char header[] =
      "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
      "<kml xmlns=\"http://www.opengis.net/kml/2.2\" "
      "xmlns:gx=\"http://www.google.com/kml/ext/2.2\" "
      "xmlns:kml=\"http://www.opengis.net/kml/2.2\">\n"
      "<Document>\n";
  /** This is how to close a kml file */
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

  /** @{ @name write
   * These methods output kml
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
  /// @}
  /** Writes a style
   * @param _o Where to write
   * @param _id The id to use for the style, referenced by placemarks later
   * @param _color ABGR hex value for color
   * @param _width pixel width to use */
  static void writeStyle(std::ostream &_o, const std::string &_id, const std::string &_color, double _width);
  /** Writes a placemark that renders as lines
   * @param _o where to write
   * @param _trajectory what to write */
  static void writeLinestring(std::ostream &_o, const TrajectoryT &_trajectory);
  /** Writes a placemark that renders as points
   * @param _o where to write
   * @param _trajectory what to write */
  static void writeMultipoint(std::ostream &_o, const TrajectoryT &_trajectory);
  /** Writes a placemark that renders as a single point
   * @param _o where to write
   * @param _point what to write */
  static void writePoint(std::ostream &_o, const PointT &_point);
  /** Writes a placemark that uses multigeomtry to render a line with points
   * @param _o where to write
   * @param _trajectory what to write */
  static void writeLineAndPoints(std::ostream &_o, const TrajectoryT &_trajectory);
  /** Utility to minimize maintenance on writing points as coordinates
   * @param _o where to write
   * @param _point what to write */
  static void writeCoords(std::ostream &_o, const PointT &_point);
  /** This simplifies writing individual files for a set of trajectories
   * The directory to write the files is specified instead of a filename */
  static void writeToSeparateKmls(const VectorT &_trajectories, const std::string &_output_dir);
};

}  // namespace tracktable

TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::linestring &_l);
TRACKTABLE_RW_EXPORT std::ostream& operator<<(std::ostream &_o, const tracktable::kml::multipoint &_mp);
TRACKTABLE_RW_EXPORT std::ostream& operator<<(std::ostream &_o, const tracktable::kml::point &_p);
TRACKTABLE_RW_EXPORT std::ostream& operator<<(std::ostream &_o, const tracktable::kml::linepoints &_lp);

#endif
