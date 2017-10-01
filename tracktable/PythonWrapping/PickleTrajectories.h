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


//
// PythonWrapping/PickleTrajectories.h - Pickle support for trajectory classes
//
// This is much simpler than the pickle suites for PropertyMap and
// TrajectoryPoint because there's much less going on.  A Trajectory
// is just a container for points.  If we know how to pickle those
// points, all we have to do in the container is walk over them.
//

#ifndef __tracktable_PickleTrajectories_h
#define __tracktable_PickleTrajectories_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/PythonWrapping/PickleSuites.h>
#include <tracktable/PythonWrapping/PickleTrajectoryPoints.h>

namespace tracktable { namespace traits {

/// Pickle a vector of points
template<class point_type>
struct pickle_suite< ::tracktable::Trajectory<point_type> > : public boost::python::pickle_suite
{
public:
  /// Convenience alias
  //
  // This makes it clearer when and how we're crossing the boundaries
  // between Python and (native) C++.
  typedef ::tracktable::Trajectory<point_type> native_object_t;

  /// Pickle the object's __dict__ attribute
  //
  // Every Python object has a __dict__ attribute that stores
  // properties.  This is even true of extension objects that are
  // defined in C++.  We manage __dict__ ourselves so that we can
  // cleanly save and restore things the user sets behind our back.
  static boost::python::tuple
  getstate(boost::python::object py_obj)
    {
      const native_object_t& native_obj = boost::python::extract<native_object_t>(py_obj)();
      return boost::python::make_tuple( pickle_suite<native_object_t>::getnativestate(native_obj),
                                        py_obj.attr("__dict__") );
    }

  /// Unpickle the object's __dict__ attribute
  //
  // Every Python object has a __dict__ attribute that stores
  // properties.  This is even true of extension objects that are
  // defined in C++.  We manage __dict__ ourselves so that we can
  // cleanly save and restore things the user sets behind our back.
  static void
  setstate(boost::python::object py_obj, boost::python::tuple state)
    {
      native_object_t& native_obj = boost::python::extract<native_object_t&>(py_obj)();
      pickle_suite<native_object_t>::setnativestate(native_obj,
                                                    boost::python::extract<boost::python::tuple>(state[0])());
      boost::python::dict d = boost::python::extract<boost::python::dict>(py_obj.attr("__dict__"));
      d.update(state[1]);
    }

  /// Pickle the points one by one
  //
  // Since Boost tuples have arbitrary length it's quite reasonable to
  // store all the points as a single tuple. This could get awkward if
  // we had trajectories with tens or hundreds of millions of points
  // but we don't foresee that ever happening.
  static boost::python::tuple
  getnativestate(native_object_t const& trajectory)
    {
      boost::python::list pickled_points;

      for (typename native_object_t::size_type i = 0; i < trajectory.size(); ++i)
        {
        pickled_points.append(pickle_suite<point_type>::getnativestate(trajectory[i]));
        }

      return boost::python::make_tuple(pickled_points,
                                       trajectory.__properties());
    }

  /// Restore all points from pickledom
  //
  // We receive all the points for a trajectory as a single long
  // tuple.  Here we unpickle them one by one and append them to the
  // trajectory.
  static void
  setnativestate(native_object_t& trajectory, boost::python::tuple state)
    {
      namespace bp = boost::python;

      bp::list pickled_points = bp::extract<bp::list>(state[0])();

      for (int i = 0; i < bp::len(pickled_points); ++i)
        {
        point_type next_point;
        pickle_suite<point_type>::setnativestate(next_point,
                                                 bp::extract<bp::tuple>(pickled_points[i])());
        trajectory.push_back(next_point);
        }

      trajectory.__set_properties(bp::extract<tracktable::PropertyMap>(state[1]));
    }
};

} } // exit namespace tracktable::traits

#endif
