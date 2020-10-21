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


// Tracktable Trajectory Library
//
// Boost.Python wrappers for the Terrestrial domain types
//
// This module ONLY includes the classes (points, trajectory and
// reader) exposed by the terrestrial domain.  All of the algorithm
// overloads are exposed in AlgorithmOverloadsModule so that
// Boost.Python can sort out the C++ overloading by itself.

#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Core/Box.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/IO/PointWriter.h>
#include <tracktable/IO/TrajectoryWriter.h>

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>
#include <tracktable/PythonWrapping/BasePointToString.h>
#include <tracktable/PythonWrapping/PythonFileLikeObjectStreams.h>
#include <tracktable/PythonWrapping/DomainWrapperTemplates.h>
#include <tracktable/PythonWrapping/PythonAwarePointReader.h>
#include <tracktable/PythonWrapping/PythonAwareTrajectoryReader.h>
#include <tracktable/PythonWrapping/PythonTypedObjectWriter.h>
#include <tracktable/PythonWrapping/TrajectoryIndexingSuite.h>

#include <tracktable/PythonWrapping/DocStrings/GenericBasePointDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericBasePointReaderDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericBasePointWriterDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericBoundingBoxDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericTrajectoryDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericTrajectoryPointDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericTrajectoryPointReaderDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericTrajectoryPointWriterDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericTrajectoryReaderDocs.h>
#include <tracktable/PythonWrapping/DocStrings/GenericTrajectoryWriterDocs.h>

using tracktable::domain::terrestrial::base_point_type;
using tracktable::domain::terrestrial::trajectory_point_type;
using tracktable::domain::terrestrial::trajectory_type;
using tracktable::domain::terrestrial::base_point_reader_type;
using tracktable::domain::terrestrial::trajectory_point_reader_type;
using tracktable::domain::terrestrial::trajectory_reader_type;
using tracktable::domain::terrestrial::box_type;

namespace {

// ----------------------------------------------------------------------
#if 0
box_type make_box(base_point_type const& Min, base_point_type const& Max)
{
  return box_type(Min, Max);
}
#endif

void set_min_corner(box_type& box, base_point_type const& corner)
{
  box.min_corner() = corner;
}

void set_max_corner(box_type& box, base_point_type const& corner)
{
  box.max_corner() = corner;
}

base_point_type min_corner(box_type const& box)
{
  return box.min_corner();
}

base_point_type max_corner(box_type const& box)
{
  return box.max_corner();
}

}

std::ostream&
operator<<(std::ostream& out, box_type const& box)
{
  std::ostringstream outbuf;
  outbuf << "<BoundingBox: ";
  outbuf << box.min_corner();
  outbuf << " - ";
  outbuf << box.max_corner();
  outbuf << ">";
  out << outbuf.str();
  return out;
}

// ----------------------------------------------------------------------

void install_terrestrial_box_wrappers()
{
  using namespace boost::python;
  using namespace tracktable::python_wrapping;

  class_<box_type>("BoundingBoxTerrestrial", tracktable::python_wrapping::docstrings::GenericBoundingBoxDocString)
    .def("__init__", make_constructor(make_box<base_point_type, box_type>))
    .def("__init__", make_constructor(make_box<trajectory_point_type, box_type>))
    .def("__init__", make_constructor(make_box_2d_from_objects<box_type>))
    .def(tracktable::python_wrapping::bounding_box_methods())
    ;
}

// ----------------------------------------------------------------------

void install_terrestrial_base_point_wrappers()
{
  using namespace boost::python;
  using tracktable::python_wrapping::make_point_2d;
  using tracktable::python_wrapping::base_point_to_string_methods;

  class_<base_point_type>("BasePointTerrestrial", tracktable::python_wrapping::docstrings::GenericBasePointDocString)
    .def(tracktable::python_wrapping::basic_point_methods())
    .def(tracktable::python_wrapping::base_point_to_string_methods("tracktable.domain.terrestrial.BasePoint"))
    .def("__init__", make_constructor(make_point_2d<base_point_type>))
    ;
}

// ----------------------------------------------------------------------

void install_terrestrial_trajectory_point_wrappers()
{
  using namespace boost::python;
  using tracktable::python_wrapping::make_point_2d;

  //deal with overloaded ECEF function
  CartesianPoint3D(trajectory_point_type::*ECEF)
      (const double ratio, const std::string&) const = &trajectory_point_type::ECEF;
  class_< trajectory_point_type >("TrajectoryPointTerrestrial", tracktable::python_wrapping::docstrings::GenericTrajectoryPointDocString)
    .def(tracktable::python_wrapping::basic_point_methods())
    .def(tracktable::python_wrapping::point_to_string_methods())
    .def(tracktable::python_wrapping::property_access_suite())
    .def(tracktable::python_wrapping::trajectory_point_methods())
    .def("__init__", make_constructor(make_point_2d<trajectory_point_type>))
    .def("ECEF", ECEF)
    .def("ECEF_from_feet", &trajectory_point_type::ECEF_from_feet)
    .def("ECEF_from_meters", &trajectory_point_type::ECEF_from_meters)
    ;
 }

// ----------------------------------------------------------------------

void install_point_reader_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonAwarePointReader<base_point_reader_type> python_base_point_reader_type;
  typedef tracktable::PythonAwarePointReader<trajectory_point_reader_type> python_trajectory_point_reader_type;

  class_<python_base_point_reader_type>("BasePointReaderTerrestrial", tracktable::python_wrapping::docstrings::GenericBasePointReaderDocString)
    .def(tracktable::python_wrapping::basic_point_reader_methods())
    .def(tracktable::python_wrapping::terrestrial_point_reader_methods())
    ;

  class_<python_trajectory_point_reader_type>("TrajectoryPointReaderTerrestrial", tracktable::python_wrapping::docstrings::GenericTrajectoryPointReaderDocString)
    .def(tracktable::python_wrapping::basic_point_reader_methods())
    .def(tracktable::python_wrapping::terrestrial_point_reader_methods())
    .def(tracktable::python_wrapping::trajectory_point_reader_methods())
    ;

}

// ----------------------------------------------------------------------

void install_trajectory_reader_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonAwareTrajectoryReader<trajectory_reader_type> python_trajectory_reader_type;

  class_<python_trajectory_reader_type>("TrajectoryReaderTerrestrial", tracktable::python_wrapping::docstrings::GenericTrajectoryReaderDocString)
    .def(tracktable::python_wrapping::trajectory_reader_methods())
    ;
}

// ----------------------------------------------------------------------

void install_terrestrial_trajectory_wrappers()
{
  using namespace boost::python;

  class_< trajectory_type >("TrajectoryTerrestrial", tracktable::python_wrapping::docstrings::GenericTrajectoryDocString)
    .def(tracktable::python_wrapping::property_access_suite())
    .def("from_position_list", &tracktable::python_wrapping::trajectory_from_position_list<trajectory_type>, return_value_policy<manage_new_object>())
    .staticmethod("from_position_list")
    .def("__iter__", iterator<trajectory_type>())
    .def(tracktable::python_wrapping::trajectory_methods())
    .def(self==self)
    .def(self!=self)
    .def(tracktable::python_wrapping::trajectory_indexing_suite<trajectory_type>())
    ;
}

// ----------------------------------------------------------------------

void install_point_writer_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonTypedObjectWriter<
    tracktable::PointWriter,
    tracktable::domain::terrestrial::base_point_type
    > base_point_writer_t;

  typedef tracktable::PythonTypedObjectWriter<
    tracktable::PointWriter,
    tracktable::domain::terrestrial::trajectory_point_type
    > trajectory_point_writer_t;

  class_< base_point_writer_t >("BasePointWriterTerrestrial", tracktable::python_wrapping::docstrings::GenericBasePointWriterDocString)
    .def(tracktable::python_wrapping::common_writer_methods())
    .add_property("write_header",
                  &base_point_writer_t::write_header,
                  &base_point_writer_t::set_write_header)
    ;


  class_< trajectory_point_writer_t >("TrajectoryPointWriterTerrestrial", tracktable::python_wrapping::docstrings::GenericTrajectoryPointWriterDocString)
    .def(tracktable::python_wrapping::common_writer_methods())
    .add_property("write_header",
                  &trajectory_point_writer_t::write_header,
                  &trajectory_point_writer_t::set_write_header)
    ;

}

// ----------------------------------------------------------------------

void install_trajectory_writer_wrappers()
{
  using namespace boost::python;

  typedef tracktable::PythonTypedObjectWriter<
    tracktable::TrajectoryWriter,
    tracktable::domain::terrestrial::trajectory_type
    > trajectory_writer_t;

  class_< trajectory_writer_t >("TrajectoryWriterTerrestrial", tracktable::python_wrapping::docstrings::GenericTrajectoryWriterDocString)
    .def(tracktable::python_wrapping::common_writer_methods())
    ;
}

// ----------------------------------------------------------------------

void install_terrestrial_domain_wrappers()
{
  using namespace boost::python;

  tracktable::domain::terrestrial::base_point_type base_point;
  tracktable::domain::terrestrial::trajectory_point_type trajectory_point;

  install_terrestrial_base_point_wrappers();
  install_terrestrial_trajectory_point_wrappers();
  install_terrestrial_trajectory_wrappers();
  install_point_reader_wrappers();
  install_point_writer_wrappers();
  install_trajectory_reader_wrappers();
  install_trajectory_writer_wrappers();
  install_terrestrial_box_wrappers();
}

BOOST_PYTHON_MODULE(_terrestrial)
{
  // Set docstrings to display user-defined only
  boost::python::docstring_options doc_options(true, false, false);

  using namespace boost::python;
  install_terrestrial_domain_wrappers();
#if 0
  def("print_int_int_map", print_map_contents<tracktable::IntIntMap>);
  def("print_string_map", print_map_contents<tracktable::StringIntMap>);
#endif
}
