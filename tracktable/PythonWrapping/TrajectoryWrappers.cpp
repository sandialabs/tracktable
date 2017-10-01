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
// Python wrapping for trajectory types
//
// Created by Danny Rintoul and Andy Wilson.

#include <boost/python.hpp>
#include <boost/python/class.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/def_visitor.hpp>
#include <boost/python/list.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/return_internal_reference.hpp>
#include <Python.h>

#include <iostream>
#include <sstream>

#include <tracktable/Core/BasicTrajectory.h>
#include <tracktable/PythonWrapping/PickleTrajectories.h>

void do_nothing() { }

void install_trajectory_wrappers();

using tracktable::BasicTrajectory;

// ----------------------------------------------------------------------

BasicTrajectory*
trajectory_from_position_list(const boost::python::list& position_list)
{
  using namespace boost::python;

  BasicTrajectory* trajectory = new BasicTrajectory;

  stl_input_iterator<object> iter(position_list), end;

  for ( ; iter != end; ++iter )
    {
    BasicTrajectory::point_type next_point((extract<BasicTrajectory::point_type>(*iter)));
    trajectory->push_back(next_point);
//    std::cout << "next_point as string: " << next_point.to_string() << "\n";
    }

  return trajectory;

}

// ----------------------------------------------------------------------

void install_trajectory_wrappers()
{
  using namespace boost::python;

  bool (BasicTrajectory::*intersects_box_raw_coords)(double, double, double, double) const = &BasicTrajectory::intersects_box;


  bool (BasicTrajectory::*intersects_box_points)(tracktable::TrajectoryPoint const&, tracktable::TrajectoryPoint const&) const = &BasicTrajectory::intersects_box;

  void (BasicTrajectory::*set_property_double)(std::string const&, double) = &BasicTrajectory::set_property;
  void (BasicTrajectory::*set_property_string)(std::string const&, std::string const&) = &BasicTrajectory::set_property;
  void (BasicTrajectory::*set_property_timestamp)(std::string const&, tracktable::Timestamp const&) = &BasicTrajectory::set_property;

  // While it's a little bit inefficient to have both trajectory
  // classes separate, it's the cleanest way to deal with the
  // impedance mismatch between C++ templates and Python duck typing.
  class_<BasicTrajectory>("Trajectory")
    .add_property("object_id", &BasicTrajectory::object_id)
    .add_property("trajectory_id", &BasicTrajectory::trajectory_id)
    .add_property("start_time", &BasicTrajectory::start_time)
    .add_property("end_time", &BasicTrajectory::end_time)
    .def("add_point", &BasicTrajectory::add_point)
    .def("subset_in_window", &BasicTrajectory::subset_in_window)
    .def("point_at_time", &BasicTrajectory::point_at_time)
    .def("recompute_speed", &BasicTrajectory::recompute_speed)
    .def("recompute_heading", &BasicTrajectory::recompute_heading)
    .def("intersects_box", intersects_box_raw_coords)
    .def("intersects_box", intersects_box_points)
    .def("from_position_list", &trajectory_from_position_list, return_value_policy<manage_new_object>())
    .def("has_property", &BasicTrajectory::has_property)
    .def("set_property", set_property_double)
    .def("set_property", set_property_string)
    .def("set_property", set_property_timestamp)
    .def("property", &BasicTrajectory::property_without_checking)
    .add_property("properties", make_function( &BasicTrajectory::__properties, return_internal_reference<>() ))

    .staticmethod("from_position_list")
    .def(self==self)
    .def(self!=self)
    .def(vector_indexing_suite<BasicTrajectory>())
    .def_pickle(tracktable::traits::pickle_suite<BasicTrajectory>())
    ;
}
