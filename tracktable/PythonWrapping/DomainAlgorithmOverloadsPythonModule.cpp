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

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

#include <tracktable/Core/Geometry.h>
#include <tracktable/Core/GeometricMean.h>
#include <tracktable/Core/GeometricMedian.h>
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Cartesian3D.h>

#include <vector>
#include <typeinfo>

// Here's the problem: Boost.Python can't look inside the list of
// points to find out what each point's actual type is.  We're going
// to have to tell it somehow.  That's what the first argument is.
// We're going to pass in the first point from Python so that
// Boost.Python can use it to resolve overloads.

template<
    typename point_type
>
point_type wrap_geometric_median(point_type const& /*first_point*/, boost::python::object points)
{
    // Since a Python iterable might be a one-time-only sequence we have
    // to make a temporary copy of the points.

    boost::python::stl_input_iterator<point_type> begin(points), end;

    std::vector<point_type> my_points(begin, end);

    return tracktable::arithmetic::geometric_median(
        my_points.begin(), my_points.end()
    );
}

template<
    typename point_type
>
point_type wrap_geometric_mean(point_type const& /*first_point*/, boost::python::object points)
{
    boost::python::stl_input_iterator<point_type> begin(points), end;

    return tracktable::arithmetic::geometric_mean(
        begin, end
    );
}

template<
    typename base_point_type,
    typename trajectory_point_type
>
void register_point_point_distance_functions()
{
    using boost::python::def;
    using tracktable::distance;

    def("distance", distance<base_point_type, base_point_type>);
    def("distance", distance<base_point_type, trajectory_point_type>);
    def("distance", distance<trajectory_point_type, base_point_type>);
    def("distance", distance<trajectory_point_type, trajectory_point_type>);
}

template<
    typename point_type,
    typename polyline_type
>
void register_point_polyline_distance_functions()
{
    using boost::python::def;
    using tracktable::distance;

    def("distance", distance<point_type, polyline_type>);
    def("distance", distance<polyline_type, point_type>);
}

template<
    typename linestring_type,
    typename trajectory_type
>
void register_polyline_polyline_distance_functions()
{
    using boost::python::def;
    using tracktable::distance;

    def("distance", distance<linestring_type, linestring_type>);
    def("distance", distance<linestring_type, trajectory_type>);
    def("distance", distance<trajectory_type, linestring_type>);
    def("distance", distance<trajectory_type, trajectory_type>);
}

template<
    typename base_point_type,
    typename trajectory_point_type,
    typename linestring_type,
    typename trajectory_type
>
void register_distance_functions()
{
    register_point_point_distance_functions<base_point_type, trajectory_point_type>();
    register_point_polyline_distance_functions<base_point_type, linestring_type>();
    register_point_polyline_distance_functions<base_point_type, trajectory_type>();
    register_point_polyline_distance_functions<trajectory_point_type, linestring_type>();
    register_point_polyline_distance_functions<trajectory_point_type, trajectory_type>();
    register_polyline_polyline_distance_functions<linestring_type, trajectory_type>();
}

template<
    typename base_point_type,
    typename trajectory_point_type,
    typename linestring_type,
    typename trajectory_type,
    typename box_type
>
void register_intersection_functions()
{
    using namespace boost::python;

    // type intersects itself
    def("intersects", &(tracktable::intersects<box_type, box_type>));
    def("intersects", &(tracktable::intersects<linestring_type, linestring_type>));
    def("intersects", &(tracktable::intersects<trajectory_type, trajectory_type>));

    // type intersects other type
    // These are commented out because they cause a template ambiguity down
    // in boost::geometry.  It can't decide what type to use for the
    // intersection.  I suppose that's fair.
    //  def("intersects", &(tracktable::intersects<linestring_type, trajectory_type>));
    //  def("intersects", &(tracktable::intersects<trajectory_type, linestring_type>));

    def("intersects", &(tracktable::intersects<box_type, linestring_type>));
    def("intersects", &(tracktable::intersects<linestring_type, box_type>));

    def("intersects", &(tracktable::intersects<box_type, trajectory_type>));
    def("intersects", &(tracktable::intersects<trajectory_type, box_type>));

    def("intersects", &(tracktable::intersects<box_type, base_point_type>));
    def("intersects", &(tracktable::intersects<base_point_type, box_type>));

    def("intersects", &(tracktable::intersects<box_type, trajectory_point_type>));
    def("intersects", &(tracktable::intersects<trajectory_point_type, box_type>));
}


BOOST_PYTHON_MODULE(_domain_algorithm_overloads) {

    using namespace boost::python;

    typedef tracktable::domain::cartesian3d::base_point_type BasePointCartesian3D;
    typedef tracktable::domain::cartesian3d::trajectory_point_type TrajectoryPointCartesian3D;
    typedef tracktable::domain::cartesian3d::trajectory_type TrajectoryCartesian3D;


    // Terrestrial domain
    typedef tracktable::domain::terrestrial::base_point_type BasePointTerrestrial;
    typedef tracktable::domain::terrestrial::trajectory_point_type TrajectoryPointTerrestrial;
    typedef tracktable::domain::terrestrial::trajectory_type TrajectoryTerrestrial;
    typedef tracktable::domain::terrestrial::box_type BoxTerrestrial;
    typedef tracktable::domain::terrestrial::linestring_type LineStringTerrestrial;

    def("interpolate", &(tracktable::interpolate<BasePointTerrestrial>));
    def("extrapolate", &(tracktable::extrapolate<BasePointTerrestrial>));
    def("signed_turn_angle", &(tracktable::signed_turn_angle<BasePointTerrestrial>));
    def("unsigned_turn_angle", &(tracktable::unsigned_turn_angle<BasePointTerrestrial>));
    def("bearing", &(tracktable::bearing<BasePointTerrestrial>));

    def("interpolate", &(tracktable::interpolate<TrajectoryPointTerrestrial>));
    def("extrapolate", &(tracktable::extrapolate<TrajectoryPointTerrestrial>));
    def("signed_turn_angle", &(tracktable::signed_turn_angle<TrajectoryPointTerrestrial>));
    def("unsigned_turn_angle", &(tracktable::unsigned_turn_angle<TrajectoryPointTerrestrial>));
    def("bearing", &(tracktable::bearing<TrajectoryPointTerrestrial>));
    def("speed_between", &(tracktable::speed_between<TrajectoryPointTerrestrial>));
    def("current_length", &(tracktable::current_length<TrajectoryPointTerrestrial>));
    def("current_length_fraction", &(tracktable::current_length_fraction<TrajectoryPointTerrestrial>));
    def("current_time_fraction", &(tracktable::current_time_fraction<TrajectoryPointTerrestrial>));

    def("simplify", &(tracktable::simplify<TrajectoryTerrestrial>));
    def("point_at_time_fraction", &(tracktable::point_at_time_fraction<TrajectoryTerrestrial>));
    def("point_at_length_fraction", &(tracktable::point_at_length_fraction<TrajectoryTerrestrial>));
    def("point_at_time", &(tracktable::point_at_time<TrajectoryTerrestrial>));
    def("time_at_fraction", &(tracktable::time_at_fraction<TrajectoryTerrestrial>));
    def("subset_during_interval", &(tracktable::subset_during_interval<TrajectoryTerrestrial>));
    def("length", &(tracktable::length<TrajectoryTerrestrial>));
    def("end_to_end_distance", &(tracktable::end_to_end_distance<TrajectoryTerrestrial>));

    def("geometric_mean", &(wrap_geometric_mean<BasePointTerrestrial>));
    def("geometric_mean", &(wrap_geometric_mean<TrajectoryPointTerrestrial>));

    def("geometric_median", &(wrap_geometric_median<BasePointTerrestrial>));
    def("geometric_median", &(wrap_geometric_median<TrajectoryPointTerrestrial>));

    def("convex_hull_area", &(tracktable::convex_hull_area<TrajectoryTerrestrial>));
    def("convex_hull_aspect_ratio", &(tracktable::convex_hull_aspect_ratio<TrajectoryTerrestrial>));
    def("convex_hull_perimeter", &(tracktable::convex_hull_perimeter<TrajectoryTerrestrial>));

    def("radius_of_gyration", &(tracktable::radius_of_gyration<TrajectoryTerrestrial>));
    def("convex_hull_centroid", &(tracktable::convex_hull_centroid<TrajectoryTerrestrial>));


    register_distance_functions<
        BasePointTerrestrial,
        LineStringTerrestrial,
        TrajectoryPointTerrestrial,
        TrajectoryTerrestrial
    >();

    register_intersection_functions<
        BasePointTerrestrial,
        TrajectoryPointTerrestrial,
        LineStringTerrestrial,
        TrajectoryTerrestrial,
        BoxTerrestrial
    >
        ();


    // 2D Cartesian domain

    typedef tracktable::domain::cartesian2d::base_point_type BasePointCartesian2D;
    typedef tracktable::domain::cartesian2d::trajectory_point_type TrajectoryPointCartesian2D;
    typedef tracktable::domain::cartesian2d::trajectory_type TrajectoryCartesian2D;
    typedef tracktable::domain::cartesian2d::linestring_type LineStringCartesian2D;
    typedef tracktable::domain::cartesian2d::box_type BoxCartesian2D;

    def("interpolate", &(tracktable::interpolate<BasePointCartesian2D>));
    def("extrapolate", &(tracktable::extrapolate<BasePointCartesian2D>));

    def("signed_turn_angle", &(tracktable::signed_turn_angle<BasePointCartesian2D>));
    def("unsigned_turn_angle", &(tracktable::unsigned_turn_angle<BasePointCartesian2D>));
    def("bearing", &(tracktable::bearing<BasePointCartesian2D>));

    def("interpolate", &(tracktable::interpolate<TrajectoryPointCartesian2D>));
    def("extrapolate", &(tracktable::extrapolate<TrajectoryPointCartesian2D>));
    def("signed_turn_angle", &(tracktable::signed_turn_angle<TrajectoryPointCartesian2D>));
    def("unsigned_turn_angle", &(tracktable::unsigned_turn_angle<TrajectoryPointCartesian2D>));
    def("bearing", &(tracktable::bearing<TrajectoryPointCartesian2D>));
    def("speed_between", &(tracktable::speed_between<TrajectoryPointCartesian2D>));
    def("current_length", &(tracktable::current_length<TrajectoryPointCartesian2D>));
    def("current_length_fraction", &(tracktable::current_length_fraction<TrajectoryPointCartesian2D>));
    def("current_time_fraction", &(tracktable::current_time_fraction<TrajectoryPointCartesian2D>));

    def("simplify", &(tracktable::simplify<TrajectoryCartesian2D>));
    def("point_at_time_fraction", &(tracktable::point_at_time_fraction<TrajectoryCartesian2D>));
    def("point_at_length_fraction", &(tracktable::point_at_length_fraction<TrajectoryCartesian2D>));
    def("point_at_time", &(tracktable::point_at_time<TrajectoryCartesian2D>));
    def("time_at_fraction", &(tracktable::time_at_fraction<TrajectoryCartesian2D>));
    def("subset_during_interval", &(tracktable::subset_during_interval<TrajectoryCartesian2D>));
    def("length", &(tracktable::length<TrajectoryCartesian2D>));
    def("end_to_end_distance", &(tracktable::end_to_end_distance<TrajectoryCartesian2D>));
    def("norm", &(tracktable::arithmetic::norm<BasePointCartesian2D>));
    def("norm", &(tracktable::arithmetic::norm<TrajectoryPointCartesian2D>));

    def("geometric_mean", &(wrap_geometric_mean<BasePointCartesian2D>));
    def("geometric_mean", &(wrap_geometric_mean<TrajectoryPointCartesian2D>));

    def("geometric_median", &(wrap_geometric_median<BasePointCartesian2D>));
    def("geometric_median", &(wrap_geometric_median<TrajectoryPointCartesian2D>));

    def("convex_hull_area", &(tracktable::convex_hull_area<TrajectoryCartesian2D>));
    def("convex_hull_aspect_ratio", &(tracktable::convex_hull_aspect_ratio<TrajectoryCartesian2D>));
    def("convex_hull_perimeter", &(tracktable::convex_hull_perimeter<TrajectoryCartesian2D>));

    def("radius_of_gyration", &(tracktable::radius_of_gyration<TrajectoryCartesian2D>));
    def("convex_hull_centroid", &(tracktable::convex_hull_centroid<TrajectoryCartesian2D>));

    register_distance_functions<
        BasePointCartesian2D,
        LineStringCartesian2D,
        TrajectoryPointCartesian2D,
        TrajectoryCartesian2D
    >();

    register_intersection_functions<
        BasePointCartesian2D,
        TrajectoryPointCartesian2D,
        LineStringCartesian2D,
        TrajectoryCartesian2D,
        BoxCartesian2D
    >
        ();


    // 3D Cartesian domain

    typedef tracktable::domain::cartesian3d::base_point_type BasePointCartesian3D;
    typedef tracktable::domain::cartesian3d::trajectory_point_type TrajectoryPointCartesian3D;
    typedef tracktable::domain::cartesian3d::trajectory_type TrajectoryCartesian3D;
    typedef tracktable::domain::cartesian3d::linestring_type LineStringCartesian3D;
    typedef tracktable::domain::cartesian3d::box_type BoxCartesian3D;

    def("interpolate", &(tracktable::interpolate<BasePointCartesian3D>));
    def("extrapolate", &(tracktable::extrapolate<BasePointCartesian3D>));
    def("unsigned_turn_angle", &(tracktable::unsigned_turn_angle<BasePointCartesian3D>));

    def("interpolate", &(tracktable::interpolate<TrajectoryPointCartesian3D>));
    def("extrapolate", &(tracktable::extrapolate<TrajectoryPointCartesian3D>));
    def("unsigned_turn_angle", &(tracktable::unsigned_turn_angle<TrajectoryPointCartesian3D>));
    def("speed_between", &(tracktable::speed_between<TrajectoryPointCartesian3D>));
    def("simplify", &(tracktable::simplify<TrajectoryCartesian3D>));
    def("point_at_time_fraction", &(tracktable::point_at_time_fraction<TrajectoryCartesian3D>));
    def("point_at_length_fraction", &(tracktable::point_at_length_fraction<TrajectoryCartesian3D>));
    def("point_at_time", &(tracktable::point_at_time<TrajectoryCartesian3D>));
    def("time_at_fraction", &(tracktable::time_at_fraction<TrajectoryCartesian3D>));
    def("subset_during_interval", &(tracktable::subset_during_interval<TrajectoryCartesian3D>));
    def("length", &(tracktable::length<TrajectoryCartesian3D>));
    def("end_to_end_distance", &(tracktable::end_to_end_distance<TrajectoryCartesian3D>));
    def("norm", &(tracktable::arithmetic::norm<BasePointCartesian3D>));
    def("norm", &(tracktable::arithmetic::norm<TrajectoryPointCartesian3D>));

    def("geometric_mean", &(wrap_geometric_mean<BasePointCartesian3D>));
    def("geometric_mean", &(wrap_geometric_mean<TrajectoryPointCartesian3D>));

    def("geometric_median", &(wrap_geometric_median<BasePointCartesian3D>));
    def("geometric_median", &(wrap_geometric_median<TrajectoryPointCartesian3D>));


    // We register these manually instead of calling
    // register_intersection_functions because line/line intersections
    // are not implemented in 3D or higher by boost::geometry.

    using tracktable::intersects;
    def("intersects", &(intersects<BoxCartesian3D, BoxCartesian3D>));

    def("intersects", &(intersects<BoxCartesian3D, LineStringCartesian3D>));
    def("intersects", &(intersects<LineStringCartesian3D, BoxCartesian3D>));

    def("intersects", &(intersects<BoxCartesian3D, TrajectoryCartesian3D>));
    def("intersects", &(intersects<TrajectoryCartesian3D, BoxCartesian3D>));

    def("intersects", &(intersects<BoxCartesian3D, BasePointCartesian3D>));
    def("intersects", &(intersects<BasePointCartesian3D, BoxCartesian3D>));

    def("intersects", &(intersects<BoxCartesian3D, TrajectoryCartesian3D>));
    def("intersects", &(intersects<TrajectoryCartesian3D, BoxCartesian3D>));

    using tracktable::distance;

    register_point_point_distance_functions<
        BasePointCartesian3D,
        TrajectoryPointCartesian3D
    >();

    register_point_polyline_distance_functions<
        BasePointCartesian3D,
        LineStringCartesian3D
    >();

    register_point_polyline_distance_functions<
        BasePointCartesian3D,
        TrajectoryCartesian3D
    >();

    register_point_polyline_distance_functions<
        TrajectoryPointCartesian3D,
        LineStringCartesian3D
    >();

    register_point_polyline_distance_functions<
        TrajectoryPointCartesian3D,
        TrajectoryCartesian3D
    >();
}
