/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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


// Tracktable Trajectory Library
//
// Python wrapping for point types
//
// Created by Danny Rintoul and Andy Wilson.

#include <boost/python.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/to_python_converter.hpp>
#include <boost/shared_ptr.hpp>
#include <Python.h>

#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/PointBaseCartesian.h>
#include <tracktable/Core/PointBaseLonLat.h>

#include <tracktable/PythonWrapping/PickleTrajectoryPoints.h>


void install_point_type_wrappers();


template<size_t dim>
void point_setitem(tracktable::PointBaseCartesian<dim>& pt, int index, double value)
{
  if (index < 0) index += dim;
  if (index >= 0 && index < dim)
    {
    pt[index] = value;
    }
  else
    {
    PyErr_SetString(PyExc_IndexError, "index out of range");
    boost::python::throw_error_already_set();
    }
}

template <size_t dim>
double point_getitem(tracktable::PointBaseCartesian<dim> const& pt, int index)
{
  if (index < 0) index += dim;
  if (index >= 0 && index < dim)
    {
    return pt[index];
    }
  else
    {
    PyErr_SetString(PyExc_IndexError, "index out of range");
    boost::python::throw_error_already_set();
    return -1; // it's OK, compiler, I know what I'm doing
    }
}

boost::shared_ptr<
  tracktable::PointBaseCartesian<2>
  >
make_point2d(double x=0, double y=0)
{
  boost::shared_ptr<
    tracktable::PointBaseCartesian<2>
    > point(new tracktable::PointBaseCartesian<2>);

  (*point)[0] = x;
  (*point)[1] = y;
  return point;
}

boost::shared_ptr<
  tracktable::PointBaseCartesian<3>
  >
make_point3d(double x=0, double y=0, double z=0)
{
  boost::shared_ptr<
    tracktable::PointBaseCartesian<3>
    > point(new tracktable::PointBaseCartesian<3>);

  (*point)[0] = x;
  (*point)[1] = y;
  (*point)[2] = z;
  return point;
}



// ----------------------------------------------------------------------


// Thanks to http://bfroehle.com/2011/07/boost-python-submodules/ for
// the demonstration of how to do submodules with Boost.Python.

namespace bp = boost::python;

void install_point_type_wrappers()
{
  using namespace boost::python;
  using tracktable::TrajectoryPoint;
  using tracktable::PointBaseCartesian;
  using tracktable::PointBaseLonLat;

  // We do this so that we can tell Python about the different
  // overloads available for this function.
  void (TrajectoryPoint::*set_property_double)(std::string const&, double) = &TrajectoryPoint::set_property;
  void (TrajectoryPoint::*set_property_string)(std::string const&, std::string const&) = &TrajectoryPoint::set_property;
  void (TrajectoryPoint::*set_property_timestamp)(std::string const&, tracktable::Timestamp const&) = &TrajectoryPoint::set_property;


  // Now we export everything in the points namespace.
  //
  // Note that this used to include bases<PointBaseLonLat2> in its
  // declaration.  We used to have a separate boost python declaration
  // for PointBaseLonLat2.  Then we tripped over something weird where
  // calling base class methods on points after we called
  // Trajectory.from_position_list would cause a segfault.
  class_<TrajectoryPoint>("TrajectoryPoint")
    .def(init<double, double, optional<double> >())
    .add_property("object_id", &TrajectoryPoint::object_id, &TrajectoryPoint::set_object_id)
    .add_property("altitude", &TrajectoryPoint::altitude, &TrajectoryPoint::set_altitude)
    .add_property("heading", &TrajectoryPoint::heading, &TrajectoryPoint::set_heading)
    .add_property("speed", &TrajectoryPoint::speed, &TrajectoryPoint::set_speed)
    .add_property("timestamp", &TrajectoryPoint::timestamp, &TrajectoryPoint::set_timestamp)
    .add_property("latitude", &TrajectoryPoint::latitude, &TrajectoryPoint::set_latitude)
    .add_property("longitude", &TrajectoryPoint::longitude, &TrajectoryPoint::set_longitude)
    .add_property("x", &TrajectoryPoint::longitude, &TrajectoryPoint::set_longitude)
    .add_property("y", &TrajectoryPoint::latitude, &TrajectoryPoint::set_latitude)
    .def("bearing_to", &TrajectoryPoint::bearing_to)
    .def("distance_to", &TrajectoryPoint::distance_to)
    .def("inside_box", &TrajectoryPoint::inside_box)
    .def("has_property", &TrajectoryPoint::has_property)
    .def("set_property", set_property_double)
    .def("set_property", set_property_string)
    .def("set_property", set_property_timestamp)
    .def("property", &TrajectoryPoint::property_without_checking)
    .add_property("properties", make_function( &TrajectoryPoint::__properties, return_internal_reference<>() ))
    .def(self == self)
    .def(self < self)
    .def("__str__", &TrajectoryPoint::to_string)
    .def(self != self)
    .def_pickle(tracktable::traits::pickle_suite<TrajectoryPoint>())
    ;

  typedef PointBaseCartesian<2> point_2d;
  typedef PointBaseCartesian<3> point_3d;

  class_<point_2d>("BarePointCartesian2D")
    .def(init<>())
    .def("__init__", make_constructor(make_point2d))
    .def("__getitem__", & point_getitem<2> )
    .def("__setitem__", & point_setitem<2> )
    .def("distance_to", & point_2d::distance_to )
    ;

  class_<point_2d>("BarePointCartesian3D")
    .def(init<>())
    .def("__init__", make_constructor(make_point3d))
    .def("__getitem__", & point_getitem<3> )
    .def("__setitem__", & point_setitem<3> )
    .def("distance_to", & point_3d::distance_to )
    ;

}
