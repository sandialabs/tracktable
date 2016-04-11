/*
 * Copyright (c) 2014, Sandia Corporation.  All rights
 * reserved.
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
// PythonWrapping/PickleTrajectoryPoints.h
//
// Pickle support for TrajectoryPoint.
//

#ifndef __tracktable_PickleTrajectoryPoints_h
#define __tracktable_PickleTrajectoryPoints_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/PythonWrapping/PickleSuites.h>

namespace tracktable { namespace traits {

namespace bp = boost::python;

/// Provide a pickler and unpickler for TrajectoryPoint
template<>
struct pickle_suite< ::tracktable::TrajectoryPoint > : public bp::pickle_suite
{
  /// Convenience alias
  //
  // This makes it clearer what we're extracting and why.
  typedef ::tracktable::TrajectoryPoint native_object_t;

  /// Save the object's __dict__
  //
  // Python objects all have a __dict__ attribute that holds any
  // properties the user wants to set.  These can be entirely separate
  // from the properties we know about here in C++-land.  In order to
  // preserve those across pickling, we need to tell the pickler that
  // we are aware of and choose to handle __dict__ ourselves.
  static boost::python::tuple
  getstate(boost::python::object py_obj)
    {
      const native_object_t& native_obj = boost::python::extract<native_object_t>(py_obj)();
      return boost::python::make_tuple( pickle_suite<native_object_t>::getnativestate(native_obj),
                                        py_obj.attr("__dict__") );
    }

  /// Restore the object's __dict__
  //
  // Python objects all have a __dict__ attribute that holds any
  // properties the user wants to set.  These can be entirely separate
  // from the properties we know about here in C++-land.  In order to
  // preserve those across pickling, we need to tell the pickler that
  // we are aware of and choose to handle __dict__ ourselves.
  static void
  setstate(boost::python::object py_obj, boost::python::tuple state)
    {
      native_object_t& native_obj = boost::python::extract<native_object_t&>(py_obj)();
      pickle_suite<native_object_t>::setnativestate(native_obj,
                                                    boost::python::extract<boost::python::tuple>(state[0])());
      boost::python::dict d = boost::python::extract<boost::python::dict>(py_obj.attr("__dict__"));
      d.update(state[1]);
    }

  /// Pickle the state of the point
  //
  // This method does the actual work of pickling.  In this case, all
  // we have to do is provide Python (via Boost.Python) with a tuple
  // containing everything we need to restore the state of a
  // trajectory point.
  //
  // We trust that pickle support already exists for all the types we
  // stuff into this tuple.  The only one to really be concerned about
  // is PropertyMap but that's what the file PicklePropertyMap.h is
  // for.
  static bp::tuple
  getnativestate(native_object_t const& point)
    {
      bp::tuple point_info = bp::make_tuple(point.object_id(),
                                            point.longitude(),
                                            point.latitude(),
                                            point.altitude(),
                                            point.heading(),
                                            point.speed(),
                                            point.timestamp(),
                                            point.__properties());

      return point_info;
    }

  /// Restore a point from pickling
  //
  // This method does the actual work of unpickling.  Just like
  // getnativestate(), we assume (and trust) that support already
  // exists for unpickling all of the different values we're reading
  // from the tuple.
  static void setnativestate(native_object_t& point, bp::tuple state)
    {
#if 0
      std::cerr << "setnativestate on TrajectoryPoint: length of state vector is "
                << bp::len(state) << ", "
                << "longitude is " << bp::extract<double>(state[0])() << ", "
                << "latitude is " << bp::extract<double>(state[1])() << ", "
                << "object_id is " << bp::extract<std::string>(state[2])() << ", "
                << "timestamp is " << bp::extract<tracktable::Timestamp>(state[3])() << ", "
                << "heading is " << bp::extract<double>(state[4])() << ", "
                << "speed is " << bp::extract<double>(state[5])() << "\n";
#endif

      point.set_object_id(bp::extract<std::string>(state[0])());
      point.set_longitude(bp::extract<double>(state[1])());
      point.set_latitude(bp::extract<double>(state[2])());
      point.set_altitude(bp::extract<double>(state[3])());
      point.set_heading(bp::extract<double>(state[4])());
      point.set_speed(bp::extract<double>(state[5])());
      point.set_timestamp(bp::extract<tracktable::Timestamp>(state[6])());
      point.__set_properties(bp::extract<tracktable::PropertyMap>(state[7])());
    }

  /// Tell Boost that we manage __dict__ ourselves
  static bool getstate_manages_dict() { return true; }

};

} } // exit namespace tracktable::traits

#endif
