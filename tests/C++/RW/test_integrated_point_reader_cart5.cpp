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

#include <tracktable/RW/PointReader.h>

#include <tracktable/Core/PointCartesian.h>
#include <iostream>
#include <fstream>

typedef tracktable::PointCartesian<5> point_type;

int test_point_reader(int expected_num_points, const char* filename)
{
  std::ifstream infile;
  infile.open(filename);
  int num_points = 0;
  int error_count = 0;

  typedef tracktable::PointReader<point_type> point_reader_type;

  point_reader_type::iterator blank_iterator;
  point_reader_type read_points(infile);

  read_points.set_field_delimiter(",");

  read_points.set_coordinate_column(0, 2);
  read_points.set_coordinate_column(1, 3);
  read_points.set_coordinate_column(2, 4);
  read_points.set_coordinate_column(3, 5);
  read_points.set_coordinate_column(4, 6);

#if 0
  read_points.set_column_for_field(0, "object_id");
  read_points.set_column_for_field(1, "timestamp");
#endif

  for (point_reader_type::iterator iter = read_points.begin();
       iter != read_points.end();
       ++iter)
    {
    // make sure the iterator assignment operator works
    blank_iterator = iter;

    point_type next_point(*iter);
    std::cout << "next point: " << next_point.to_string() << "\n";
    ++num_points;
    }

  std::cout << "test_integrated_point_reader_cart5: Read "
            << num_points
            << " points from file "
            << filename << "\n";

  if (num_points != expected_num_points)
    {
    std::cout << "ERROR: We expected to see "
              << expected_num_points << " points"
              << " but actually saw "
              << num_points << ".\n";
    ++error_count;
    }
  else
    {
    std::cout << "SUCCESS: We found the expected number of points ("
              << num_points << ")\n";
    }
  return error_count;
}

int main(int argc, char* argv[])
{
  int error_count = 0;

  if (argc != 3)
    {
    std::cerr << "usage: "
              << argv[0] << " expected_num_points file_to_read.txt\n";
    return 1;
    }

  int expected_num_points = atoi(argv[1]);
  char* filename = argv[2];

  error_count += test_point_reader(expected_num_points, filename);

  std::cout << "Returning exit code " << error_count << "\n";
  return error_count;
}
