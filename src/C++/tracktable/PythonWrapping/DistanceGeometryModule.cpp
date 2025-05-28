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


// Tracktable Trajectory Library
//
// DistanceGeometryModule - Python bindings for C++ distance geometry
// functions
//

#include <tracktable/Analysis/DistanceGeometry.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Domain/Cartesian2D.h>
#include <tracktable/Domain/Cartesian3D.h>

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/module.hpp>
#include <Python.h>


BOOST_PYTHON_MODULE(_distance_geometry) {
  typedef tracktable::domain::terrestrial::trajectory_type terrestrial_trajectory_type;
  typedef tracktable::domain::cartesian2d::trajectory_type cartesian2d_trajectory_type;
  typedef tracktable::domain::cartesian3d::trajectory_type cartesian3d_trajectory_type;

  using boost::python::def;

  def("_distance_geometry_by_distance",
      &tracktable::distance_geometry_by_distance<terrestrial_trajectory_type>);

  def("_distance_geometry_by_distance",
      &tracktable::distance_geometry_by_distance<cartesian2d_trajectory_type>);

  def("_distance_geometry_by_distance",
      &tracktable::distance_geometry_by_distance<cartesian3d_trajectory_type>);

  def("_distance_geometry_by_time",
      &tracktable::distance_geometry_by_time<terrestrial_trajectory_type>);

  def("_distance_geometry_by_time",
      &tracktable::distance_geometry_by_time<cartesian2d_trajectory_type>);

  def("_distance_geometry_by_time",
      &tracktable::distance_geometry_by_time<cartesian3d_trajectory_type>);
}


