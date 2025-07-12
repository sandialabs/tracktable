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

#include <tracktable/Domain/FeatureVectors.h>
#include <iostream>


// This function should match what's in operator<<(ostream, FeatureVector).
template<std::size_t dim>
std::string
expected_string_representation(
  tracktable::domain::feature_vectors::FeatureVector<dim> const& my_feature_vector
  )
{
  std::ostringstream outbuf;
  outbuf << "(";
  for (std::size_t i = 0; i < dim; ++i)
  {
    if (i > 0)
    {
      outbuf << ", ";
    }
    outbuf << my_feature_vector[i];
  }
  outbuf << ")";
  return outbuf.str();
}


template<std::size_t num_components>
int test_feature_vector_to_string()
{
  tracktable::domain::feature_vectors::FeatureVector<num_components> my_feature_vector;
  for (std::size_t i = 0; i < num_components; ++i)
  {
    my_feature_vector[i] = i + 0.5;
  }

  std::ostringstream outbuf;
  outbuf << my_feature_vector;
  if (outbuf.str() != expected_string_representation(my_feature_vector))
  {
    std::cerr << "ERROR: Expected FeatureVector operator<< to return '"
              << expected_string_representation(my_feature_vector)
              << "' but instead got '"
              << outbuf.str() << "'\n";
    return 1;
  }
  return 0;
}


int
main(int , char**)
{
  int error_count = 0;
  error_count += test_feature_vector_to_string<1>();
  error_count += test_feature_vector_to_string<2>();
  error_count += test_feature_vector_to_string<10>();
  return error_count;
}
