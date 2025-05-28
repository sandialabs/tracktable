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
// Boost.Python wrappers for feature vector point types
//
// This module ONLY includes the classes (points)
// reader) exposed by the 2D cartesian domain.  All of the algorithm
// overloads are exposed in AlgorithmOverloadsModule so that
// Boost.Python can sort out the C++ overloading by itself.

#include <tracktable/Domain/FeatureVectors.h>

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>
#include <tracktable/PythonWrapping/DomainWrapperTemplates.h>
#include <tracktable/PythonWrapping/PythonAwarePointReader.h>
#include <tracktable/PythonWrapping/ExplicitInstantiation/FeatureVectorWrapperCommon.h>

// ----------------------------------------------------------------------

void install_feature_vector_point_wrappers()
{
  install_feature_vector_wrappers_1_5();
  install_feature_vector_wrappers_6_10();
  install_feature_vector_wrappers_11_15();
  install_feature_vector_wrappers_16_20();
  install_feature_vector_wrappers_21_25();
  install_feature_vector_wrappers_26_30();
  install_extra_feature_vector_wrappers();
}

// ----------------------------------------------------------------------


BOOST_PYTHON_MODULE(_feature_vector_points)
{
  install_feature_vector_point_wrappers();
}
