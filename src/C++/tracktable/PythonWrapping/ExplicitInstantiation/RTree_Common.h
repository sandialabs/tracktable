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

#ifndef __tracktable_PythonWrapping_RTree_Common_h
#define __tracktable_PythonWrapping_RTree_Common_h

#include <tracktable/Core/TracktableCommon.h>

// Fix regression in Boost 1.74 with missing header file
#include <boost/geometry/geometry.hpp>

#include <tracktable/Analysis/RTree.h>
#include <tracktable/Domain/FeatureVectors.h>

#include <tracktable/PythonWrapping/RTreePythonWrapper.h>
#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>
#include <sstream>

#define WRAP_RTREE(dimension) wrap_rtree<dimension>()

template<std::size_t dim>
void wrap_rtree()
{
  std::ostringstream namebuf;
  namebuf << "rtree_" << dim;

  using namespace boost::python;
  typedef tracktable::domain::feature_vectors::FeatureVector<dim> point_type;
  typedef RTreePythonWrapper<point_type> rtree_type;

  class_< rtree_type >(namebuf.str().c_str())
    .def(init<>())
    .def("insert_point", &rtree_type::insert_point)
    .def("insert_points", &rtree_type::insert_points)
    .def("find_points_in_box", &rtree_type::find_points_in_box)
    .def("find_nearest_neighbors", &rtree_type::find_nearest_neighbors)
    .def("__len__", &rtree_type::size)
    ;
}

void install_rtree_wrappers_1_3();
void install_rtree_wrappers_4_6();
void install_rtree_wrappers_7_9();
void install_rtree_wrappers_10_12();
void install_rtree_wrappers_13_15();
void install_rtree_wrappers_16_18();
void install_rtree_wrappers_19_21();
void install_rtree_wrappers_22_24();
void install_rtree_wrappers_25_27();
void install_rtree_wrappers_28_30();
void install_extra_rtree_wrappers();

#endif
