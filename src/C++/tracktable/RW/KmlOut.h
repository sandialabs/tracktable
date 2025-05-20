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

#ifndef KmlOut_h
#define KmlOut_h

#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/RW/TracktableRWWindowsHeader.h>

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

/** Handles writing tracks as kml
 * Has lots of internal structure to make the following use cases work:
 *
 * @code
 *
 * std::cout << kml::header;
 * std::cout << kml(t);
 * std::cout << kml::footer;
 *
 * out = ofstream;
 * out << kml(t);
 *
 * @endcode
 *
 * For both of the above a default style will be used (green, width = 3) in the case
 * of a single trajectory and a random color will be used with the same default
 * width = 3 for a vector of trajectories.
 * -----------------------------------------------------------------------------
 * To control color and width:
 *
 * @code
 *
 * std::cout << kml::header;
 * kml::write(std::cout, t, "AABBGGRR", 4)
 * std::cout << kml::footer;
 *
 * kml::write("filname", t, "AABBGGRR", 5)
 *
 * @endcode
 *
 * These are the limits of style control at this time.
 *
 * TODO: Simplify use of multipoint and linepoint methods (requires placemark)
 * TODO: Implement placemark manipulation
 * TODO: Implement style manipulation
 */
class TRACKTABLE_RW_EXPORT kml {
   public:
    using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
    using TrajectoryVectorT = std::vector<TrajectoryT>;
    using PointerT = std::shared_ptr<TrajectoryT>;
    using PointerVectorT = std::vector<PointerT>;
    using VectorT = std::vector<TrajectoryT>;
    using PointT = TrajectoryT::point_type;

    /** Helper struct that allows for
     *
     * @code
     *
     * out << linestring(t)
     *
     * @endcode
     *
     * which will render as a line.
     * This will be missing some header/footer information neccesary for full kml rendering.
     */
    struct linestring {
        linestring() = delete;
        linestring(const TrajectoryT &_t) : trajectory(&_t) {}
        TrajectoryT const *const trajectory;
    };

    /** Helper struct that allows for for
     *
     * @code
     *
     * out << multipoint(t)
     *
     * @endcode
     *
     * which will render as set of points.
     * This will be missing some header/footer information neccesary for full kml rendering.
     */
    struct multipoint {
        multipoint() = delete;
        multipoint(const TrajectoryT &_t) : trajectory(&_t) {}
        TrajectoryT const *const trajectory;
    };

    /** Helper struct that allows for for
     *
     * @code
     *
     * out << linepoints(t)
     *
     * @endcode
     *
     * which will render as lines with points
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct linepoints {
        linepoints() = delete;
        linepoints(const TrajectoryT &_t) : trajectory(&_t) {}
        TrajectoryT const *const trajectory;
    };

    /** Helper struct that allows for for
     *
     * @code
     *
     * out << point(t)
     *
     * @endcode
     *
     * which will render as a single point
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct point {
        point() = delete;
        point(const PointT &_t) : trajectory(&_t) {}
        PointT const *const trajectory;
    };

   public:
    /** @{ @name Overloaded KML Methods
     * These methods generate kml objects for output for a given tracjectory or point.
     * If a file is specified, the header and footer are automatically written.
     * If a stream is specified, the header and footer are NOT automatically written.
     * Write can be called with either a single trajectory or a vector.
     */
    kml(const TrajectoryT &_t) : trajectoryPtr(&_t) {}
    kml(const TrajectoryVectorT &_v) : trajectoryListPtr(&_v) {}
    kml(const PointerT &_p) : trajectoryPtr(_p.get()) {}
    kml(const PointerVectorT &_vp) : trajectorySmartListPtr(&_vp) {}
    /// @}

    /** Helper struct that allows for for
     *
     * @code
     *
     * out << box(corner1, corner2)
     *
     * @endcode
     *
     * which will render a box
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct box {
        box() = delete;
        box(const PointT &_c1, const PointT &_c2) : corner1(&_c1), corner2(&_c2) {}
        PointT const *const corner1;
        PointT const *const corner2;
    };

    /** Helper struct that allows for for
     *
     * @code
     *
     * out << time_span(start, stop)
     *
     * @endcode
     *
     * which will render a timespan between two timestamps
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct time_span {
        time_span() = delete;
        time_span(const tracktable::Timestamp &_start, const tracktable::Timestamp &_stop) {
            kml::_start = _start;
            kml::_stop = _stop;
        }
    };

    /** Helper struct that sets the KML object's name
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct name {
        name(const std::string &_name) { kml::_name = _name; }
        operator std::string() { return kml::_name; }
    };

    /** Helper struct that sets the KML object's width
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct width {
        width(double _w) { kml::_width = _w; }
        operator double() { return kml::_width; }
    };

    /** Helper struct that sets the KML object's color
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct color {
        color(const std::string &_c) {
            if (_c.length() != 8) {
                throw std::runtime_error("Invalid Color String");
            }
            kml::_color = _c;
        }
        operator std::string() { return kml::_color; }
    };

    /** Helper struct that sets the KML object's style
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct style {
        style(const std::string &_id, const std::string &_c, const double &_w)
            : id(_id), color(_c), width(_w) {
            kml::_styleid = _id;
        }
        const std::string &id;
        const std::string &color;
        const double width;
    };

    /** Helper struct that sets the KML object's style id
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct style_id {
        style_id(const std::string &_id) { kml::_styleid = _id; }
        operator std::string() { return kml::_styleid; }
    };

    /** Helper struct that sets the KML object's starting Placemark
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct startpm {
        startpm() {
            if (kml::_isInsidePlacemark) {
                throw std::runtime_error("Cannot Start Placemark inside a Placemark");
            }
            kml::_isInsidePlacemark = true;
        }
    };

    /** Helper struct that sets the KML object's stopping Placemark
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct stoppm {
        stoppm() {
            if (!kml::_isInsidePlacemark) {
                throw std::runtime_error("not inside a placemark");
            }
            kml::_isInsidePlacemark = false;
        }
    };

    /** Helper struct that sets the KML object's starting Multigeometry
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct startmulti {
        startmulti() {
            if (!kml::_isInsidePlacemark) {
                throw std::runtime_error("Cannot start Multigeometry outside a Placemark");
            }
            if (kml::_isInsideMultiGeometry) {
                throw std::runtime_error("Cannot Start MultiGeometry inside a MultiGeometry");
            }
            kml::_isInsideMultiGeometry = true;
        }
    };

    /** Helper struct that sets the KML object's stopping Multigeometry
     * This will be missing some header/footer neccesary for full kml rendering
     */
    struct stopmulti {
        stopmulti() {
            if (!kml::_isInsideMultiGeometry) {
                throw std::runtime_error("not inside a MultiGeometry");
            }
            kml::_isInsideMultiGeometry = false;
        }
    };

    // Doxygen gets confused by the inline XML
#if !defined(DOXYGEN_SHOULD_SKIP_THIS)
    /** This will start a kml file off */
    static constexpr char header[] =
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<kml xmlns=\"http://www.opengis.net/kml/2.2\" "
        "xmlns:gx=\"http://www.google.com/kml/ext/2.2\" "
        "xmlns:kml=\"http://www.opengis.net/kml/2.2\">\n"
        "<Document>\n"
        "<Style id=\"tracktable_style\">\n"
        "  <LineStyle>\n"
        "    <gx:labelVisibility>1</gx:labelVisibility>\n"
        "    <width>3</width>\n"
        "    <color>\"FFFFFFFF\"</color>\n"
        "  </LineStyle>\n"
        "</Style>\n";

    /** This is how to close a kml file */
    static constexpr char footer[] =
        "</Document>\n"
        "</kml>";
#endif

   private:
    friend std::ostream &(::operator<<)(std::ostream &_o, const tracktable::kml &_kml);
    friend std::ofstream &(::operator<<)(std::ofstream &_o, const tracktable::kml &_kml);
    const TrajectoryT *trajectoryPtr = nullptr;
    const TrajectoryVectorT *trajectoryListPtr = nullptr;
    const PointerVectorT *trajectorySmartListPtr = nullptr;

   public:
    static std::string generateColorString();

    /** @{ @name Overloaded Write Methods
     * These methods output kml.
     * If a file is specified, the header and footer are automatically written.
     * If a stream is specified, the header and footer are NOT automatically written.
     * Write can be called with either a single trajectory or a vector.
     */
    static void write(const std::string &_filename, const TrajectoryVectorT &_trajectories);
    static void write(std::ostream &_o, const TrajectoryVectorT &_trajectories);
    static void write(std::ostream &_o, const PointerVectorT &_trajectories);
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
     * @param _width pixel width to use
     */
    static void writeStyle(std::ostream &_o, const std::string &_id, const std::string &_color,
                           double _width);

    /** Writes a placemark that renders as lines
     * @param _o where to write
     * @param _trajectory what to write
     */
    static void writeLinestring(std::ostream &_o, const TrajectoryT &_trajectory);

    /** Writes a placemark that renders as points
     * @param _o where to write
     * @param _trajectory what to write
     */
    static void writeMultipoint(std::ostream &_o, const TrajectoryT &_trajectory);

    /** Writes a placemark that renders as a single point
     * @param _o where to write
     * @param _point what to write
     */
    static void writePoint(std::ostream &_o, const PointT &_point);

    /** Writes a placemark that uses multigeomtry to render a line with points
     * @param _o where to write
     * @param _trajectory what to write
     */
    static void writeLineAndPoints(std::ostream &_o, const TrajectoryT &_trajectory);

    /** Writes a placemark that uses multigeomtry to render a line with points
     * @param _o where to write
     * @param _trajectory what to write
     */
    static void writeBox(std::ostream &_o, const box &_box);

    /** Utility to minimize maintenance on writing points as coordinates
     * @param _o where to write
     * @param _point what to write
     */
    static void writeCoords(std::ostream &_o, const PointT &_point);

    /** This simplifies writing individual files for a set of trajectories
     * The directory to write the files is specified instead of a filename
     * @param _trajectories trajectories to write
     * @param _output_dir directory to write to
     */
    static void writeToSeparateKmls(const TrajectoryVectorT &_trajectories, const std::string &_output_dir);

    /** Writes a default Placemark header tag
     * @param _o where to write
     */
    static void writePlacemarkHeader(std::ostream &_o);

    /** Writes a default Placemark footer tag
     * @param _o where to write
     */
    static void writePlacemarkFooter(std::ostream &_o);

    /** Writes a default MultiGeometry header tag
     * @param _o where to write
     */
    static void writeMultiGeometryHeader(std::ostream &_o);

    /** Writes a default MultiGeometry footer tag
     * @param _o where to write
     */
    static void writeMultiGeometryFooter(std::ostream &_o);

   public:
    static double _width;
    static std::string _color;
    static std::string _name;
    static std::string _styleid;
    static bool _isInsidePlacemark;
    static bool _isInsideMultiGeometry;
    static tracktable::Timestamp _start;
    static tracktable::Timestamp _stop;
};

}  // namespace tracktable

TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::linestring &_l);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::multipoint &_mp);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::point &_p);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::linepoints &_lp);

TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::box &_b);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::style &_s);

TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::width & /*_w*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::color & /*_c*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::name & /*_n*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::style_id & /*_s*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::time_span & /*_t*/);

TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::startpm & /*_s*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::stoppm & /*_s*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::startmulti & /*_s*/);
TRACKTABLE_RW_EXPORT std::ostream &operator<<(std::ostream &_o, const tracktable::kml::stopmulti & /*_s*/);

#endif
