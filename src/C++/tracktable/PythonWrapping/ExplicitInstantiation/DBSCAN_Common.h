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

#ifndef __tracktable_PythonWrapping_DBSCAN_h
#define __tracktable_PythonWrapping_DBSCAN_h

#include <tracktable/Core/TracktableCommon.h>

// Fix regression in Boost 1.74 with missing header file
#include <boost/geometry/geometry.hpp>

#include <tracktable/Analysis/ComputeDBSCANClustering.h>
#include <tracktable/Domain/FeatureVectors.h>


#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

#define xstr(s) str(s)
#define str(s) #s

#define DBSCAN_FUNCTION_NAME(dim) "dbscan_learn_cluster_ids_" xstr(dim)

using namespace tracktable::domain::feature_vectors;
using namespace boost::python;

#define WRAP_DBSCAN(dim) \
  def( DBSCAN_FUNCTION_NAME(dim), dbscan_learn_cluster_ids< FeatureVector<dim> > )


/*
 * Note: This binding only supports unlabeled points that are given
 * integer cluster IDs.  If the user supplies anything else we will
 * handle it in Python-land.
 */

template<typename point_type>
boost::python::object
dbscan_learn_cluster_ids(boost::python::object points,
                         boost::python::object _search_box_half_span,
                         int min_cluster_size)
{
  namespace bp = boost::python;

  point_type search_box_half_span = boost::python::extract<point_type>(_search_box_half_span);

  typedef std::pair<int, int> cluster_label_type;
  std::vector<cluster_label_type> result_cluster_labels;

  tracktable::cluster_with_dbscan(bp::stl_input_iterator<point_type>(points),
                                  bp::stl_input_iterator<point_type>(),
                                  search_box_half_span,
                                  min_cluster_size,
                                  std::back_inserter(result_cluster_labels));

  bp::list result;
  for (typename std::vector<cluster_label_type>::const_iterator iter = result_cluster_labels.begin();
       iter != result_cluster_labels.end();
       ++iter)
    {
    result.append(*iter);
    }
  return std::move(result);
}


void install_dbscan_wrappers_1_3();
void install_dbscan_wrappers_4_6();
void install_dbscan_wrappers_7_9();
void install_dbscan_wrappers_10_12();
void install_dbscan_wrappers_13_15();
void install_dbscan_wrappers_16_18();
void install_dbscan_wrappers_19_21();
void install_dbscan_wrappers_22_24();
void install_dbscan_wrappers_25_27();
void install_dbscan_wrappers_28_30();
void install_extra_dbscan_wrappers();
#endif
