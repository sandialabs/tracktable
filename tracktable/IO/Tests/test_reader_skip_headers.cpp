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

#include <tracktable/IO/PointReader.h>

#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>

#include <iostream>
#include <fstream>


int test_point_reader(int skip_num_lines, int expected_num_points, const char* filename)
{
  std::ifstream infile;
  infile.open(filename);
  int num_points = 0;
  int error_count = 0;

  typedef tracktable::TrajectoryPoint< tracktable::PointLonLat > point_type;
  typedef tracktable::LineReader<> line_reader_type;
  typedef tracktable::SkipCommentsReader<line_reader_type::iterator> skip_comments_reader_type;
  typedef tracktable::StringTokenizingReader<skip_comments_reader_type::iterator> string_tokenizer_type;

  typedef tracktable::PointFromTokensReader<point_type, string_tokenizer_type::iterator> point_reader_type;


  point_reader_type::iterator blank_iterator;

  line_reader_type line_reader(infile);
  skip_comments_reader_type skip_comments(
    tracktable::make_skip_comments_reader(line_reader.begin(),
                                          line_reader.end()));
  skip_comments.set_skip_n_lines(skip_num_lines);
  string_tokenizer_type tokenize_strings(skip_comments.begin(),
                                         skip_comments.end());
  tokenize_strings.set_field_delimiter(",");
  point_reader_type read_points(tokenize_strings.begin(),
                                tokenize_strings.end());

  // Longitude is in column 2, latitude is in column 3
  //
  // BUG: These signatures are backward.  It's set_Y_for_X but the
  // arguments are in the order (X, Y).

  read_points.set_coordinate_column(0, 2);
  read_points.set_coordinate_column(1, 3);

  read_points.set_object_id_column(0);
  read_points.set_timestamp_column(1);

  read_points.set_real_field_column("heading", 5);
  read_points.set_string_field_column("string_test", 0);
  read_points.set_time_field_column("timestamp_test", 1);
  read_points.set_real_field_column("numeric_test", 2);

  for (point_reader_type::iterator iter = read_points.begin();
       iter != read_points.end();
       ++iter)
    {
    // make sure the iterator assignment operator works
    blank_iterator = iter;

    point_type next_point(*iter);

    if (next_point.object_id() != next_point.string_property("string_test"))
      {
      std::cout << "ERROR: Expected object ID ("
                << next_point.object_id()
                << ") and string property ("
                << next_point.string_property("string_test")
                << ") to match on point "
                << num_points << "\n";
      ++error_count;
      }

    if (next_point.timestamp() != next_point.timestamp_property("timestamp_test"))
      {
      std::cout << "ERROR: Expected timestamp ("
                << next_point.timestamp()
                << ") and timestamp property ("
                << next_point.timestamp_property("timestamp_test")
                << ") to match on point "
                << num_points << "\n";
      ++error_count;
      }

    if (next_point.longitude() != next_point.real_property("numeric_test"))
      {
      std::cout << "ERROR: Expected longitude ("
                << next_point.longitude()
                << ") and numeric property ("
                << next_point.real_property("numeric_test")
                << ") to match on point "
                << num_points << "\n";
      ++error_count;
      }

#if 1
    std::cout << "next point: " << next_point << "\n";
#endif

    ++num_points;
    if (num_points % 100000 == 0)
      {
      std::cout << "Read " << num_points << " points\n";
      }
    }

  std::cout << "test_trajectory_point_reader: Read "
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
              << num_points;
    }
  return error_count;
}

int main(int argc, char* argv[])
{
  int error_count = 0;

  if (argc != 4)
    {
    std::cerr << "usage: "
              << argv[0] << " skip_num_lines expected_num_points file_to_read.txt\n";
    return 1;
    }

  int skip_num_lines = atoi(argv[1]);
  int expected_num_points = atoi(argv[2]);
  char* filename = argv[3];

  error_count += test_point_reader(skip_num_lines, expected_num_points, filename);

  std::cout << "Returning exit code " << error_count << "\n";
  return error_count;
}
