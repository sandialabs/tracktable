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

#include <tracktable/IO/LineReader.h>
#include <tracktable/IO/SkipCommentsReader.h>
#include <tracktable/IO/StringTokenizingReader.h>
#include <tracktable/IO/TrajectoryPointReader.h>

#include <iostream>
#include <fstream>

int test_point_reader(int expected_num_points, const char* filename)
{
  std::ifstream infile;
  infile.open(filename);
  int num_points = 0;
  int error_count = 0;

  typedef tracktable::LineReader<> line_reader_type;
  typedef tracktable::SkipCommentsReader<line_reader_type::iterator> skip_comments_reader_type;
  typedef tracktable::StringTokenizingReader<skip_comments_reader_type::iterator> string_tokenizer_type;
  typedef tracktable::TrajectoryPointReader<string_tokenizer_type::iterator> point_reader_type;


  point_reader_type::iterator blank_iterator;

  line_reader_type line_reader(infile);
  skip_comments_reader_type skip_comments(
    tracktable::make_skip_comments_reader(line_reader.begin(),
                                          line_reader.end()));
  string_tokenizer_type tokenize_strings(skip_comments.begin(),
                                         skip_comments.end());
  tokenize_strings.set_field_delimiter(",");
  point_reader_type read_points(tokenize_strings.begin(),
                                tokenize_strings.end());

  read_points.set_column_for_field("heading", 5);
  read_points.set_column_for_field("string_test", 0);
  read_points.set_column_for_field("timestamp_test", 1);
  read_points.set_column_for_field("numeric_test", 2);

  for (point_reader_type::iterator iter = read_points.begin();
       iter != read_points.end();
       ++iter)
    {
    // make sure the iterator assignment operator works
    blank_iterator = iter;

    tracktable::TrajectoryPoint next_point(*iter);
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

    if (next_point.longitude() != next_point.numeric_property("numeric_test"))
      {
      std::cout << "ERROR: Expected longitude ("
                << next_point.longitude()
                << ") and numeric property ("
                << next_point.numeric_property("numeric_test")
                << ") to match on point "
                << num_points << "\n";
      ++error_count;
      }

#if 0
    std::cout << "next point: object_id "
              << next_point.object_id()
              << ", timestamp "
              << next_point.timestamp()
              << ", position ("
              << next_point.longitude()
              << ", "
              << next_point.latitude()
              << "), "
              << "heading "
              << next_point.heading()
              << ", string test "
              << next_point.property("string_test")
              << ", timestamp test "
              << next_point.property("timestamp_test")
              << ", numeric test "
              << next_point.property("numeric_test")
              << "\n";
#endif
    ++num_points;
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
