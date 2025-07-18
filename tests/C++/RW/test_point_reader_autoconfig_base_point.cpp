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

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/RW/PointWriter.h>
#include <tracktable/RW/PointReader.h>

#include <cstdlib>
#include <iostream>
#include <iterator>
#include <sstream>
#include <vector>

template<typename point_type>
int test_point_reader()
{
  int error_count = 0;

  typedef std::vector<point_type> point_vector_type;

  point_vector_type points;

  for (std::size_t point_id = 0; point_id < 10; ++point_id)
    {
    point_type next_point;
    for (std::size_t i = 0; i < tracktable::traits::dimension<point_type>::value; ++i)
      {
      next_point[i] = static_cast<typename point_type::coordinate_type>(10*i + point_id);
      }
    points.push_back(next_point);
    }

  std::ostringstream outbuf;
  tracktable::PointWriter writer(outbuf);
  writer.write(points.begin(), points.end());

  std::cout << "Point writer output:\n" << outbuf.str() << "(end)\n";

  std::string writer_result(outbuf.str());
  std::istringstream inbuf(writer_result);

  tracktable::PointReader<point_type> reader(inbuf);

  point_vector_type reconstituted_points(reader.begin(), reader.end());

  if (points.size() != reconstituted_points.size())
    {
    std::cout << "ERROR: Original point array contains "
              << points.size() << " entries.  Reconstituted array contains "
              << reconstituted_points.size() << " entries.\n";
    ++error_count;
    }

  typename point_vector_type::const_iterator before_iter = points.begin();
  typename point_vector_type::const_iterator after_iter = reconstituted_points.begin();
  std::size_t point_id = 0;

  for (;
       before_iter != points.end() && after_iter != reconstituted_points.end();
       ++before_iter, ++after_iter
    )
    {
    if ((*before_iter) != (*after_iter))
      {
      std::cout << "ERROR: Point "
                << point_id
                << " does not match after writing and reading back in.  Before:\n"
                << *before_iter << "\nAfter: " << *after_iter << "\n";
      ++error_count;
      }
    }
  return error_count;
}

int main(int /*argc*/, char* /*argv*/[])
{
  int num_errors = 0;

  num_errors += test_point_reader<tracktable::PointLonLat>();
  num_errors += test_point_reader<tracktable::PointCartesian<2> >();

  return num_errors;
}
