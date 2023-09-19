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

#ifndef __tracktable_FeatureVectorWrapperCommon_h
#define __tracktable_FeatureVectorWrapperCommon_h


#include <tracktable/Domain/FeatureVectors.h>

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>
#include <tracktable/PythonWrapping/BasePointToString.h>
#include <tracktable/PythonWrapping/DomainWrapperTemplates.h>
#include <tracktable/PythonWrapping/PythonAwarePointReader.h>

#include <sstream>


namespace tracktable { namespace python_wrapping {

template<std::size_t dim>
void wrap_feature_vector_point()
{
	std::ostringstream short_name_buf;
	string_type short_name;

	short_name_buf << "FeatureVector" << dim;
	short_name = short_name_buf.str();

	std::ostringstream full_name_buf;
	string_type full_name;
	full_name_buf << "tracktable.domain.feature_vectors." << short_name;
    full_name = full_name_buf.str();

	using tracktable::domain::feature_vectors::FeatureVector;
	boost::python::class_< FeatureVector<dim> >(short_name.c_str())
	   .def(tracktable::python_wrapping::basic_point_methods())
	   .def(tracktable::python_wrapping::base_point_to_string_methods(full_name))
	   ;
}

} } // close namespace tracktable::python_wrapping

void install_feature_vector_wrappers_1_5();
void install_feature_vector_wrappers_6_10();
void install_feature_vector_wrappers_11_15();
void install_feature_vector_wrappers_16_20();
void install_feature_vector_wrappers_21_25();
void install_feature_vector_wrappers_26_30();
void install_extra_feature_vector_wrappers();
#endif

