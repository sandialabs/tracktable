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
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/TimestampConverter.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>

#include <iterator>
#include <iostream>
#include <fstream>

tracktable::Timestamp 
read_and_get_timestamp(const std::string filename, const std::string format)
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
    string_tokenizer_type tokenize_strings(skip_comments.begin(),
        skip_comments.end());
    tokenize_strings.set_field_delimiter(",");
    point_reader_type read_points(tokenize_strings.begin(),
        tokenize_strings.end());

    read_points.set_coordinate_column(0, 2);
    read_points.set_coordinate_column(1, 3);

    read_points.set_object_id_column(0);
    read_points.set_timestamp_column(1);
    read_points.set_timestamp_format(format);
    read_points.set_real_field_column("heading", 5);
    read_points.set_string_field_column("string_test", 0);
    read_points.set_time_field_column("timestamp_test", 1);
    read_points.set_real_field_column("numeric_test", 2);

    point_reader_type::iterator iter = read_points.begin();
    std::advance(iter, 3);
    point_type next_point(*iter);
   
    return next_point.timestamp();
}

int test_timestamp_formats(const std::string file_location)
{
    TRACKTABLE_LOG(tracktable::log::info) << 
        "Attempting to read timestamps from files in " << file_location;
    int error_count = 0;
    tracktable::TimestampConverter converter;
    converter.set_input_format("%Y-%m-%d %H:%M:%S");
    
    tracktable::Timestamp expected_timestamp = 
        converter.timestamp_from_string(std::string("2004-12-07 11:43:18"));
    
    tracktable::Timestamp actual_timestamp =
        read_and_get_timestamp(file_location + "PointsWithTimestamps1.csv", "%Y-%m-%d %H:%M:%S");

    if (actual_timestamp != expected_timestamp)
    {
        TRACKTABLE_LOG(tracktable::log::error) << "Actual timestamp " <<
            actual_timestamp << " does not match expected timestamp " <<
            expected_timestamp << ".";
        error_count += 1;
    }
            
    actual_timestamp = 
        read_and_get_timestamp(file_location + "PointsWithTimestamps2.csv", "%Y:%m:%d::%H:%M:%S");
    
    if(actual_timestamp != expected_timestamp)
    {
        TRACKTABLE_LOG(tracktable::log::error) << "Actual timestamp " <<
            actual_timestamp << " does not match expected timestamp " <<
            expected_timestamp << ".";
        error_count += 1;
    }

    actual_timestamp = 
        read_and_get_timestamp(file_location + "PointsWithTimestamps3.csv", "%b %d %Y %H:%M:%S");

    if (actual_timestamp != expected_timestamp)
    {
        TRACKTABLE_LOG(tracktable::log::error) << "Actual timestamp " <<
            actual_timestamp << " does not match expected timestamp " <<
            expected_timestamp << ".";
        error_count += 1;
    }

  return error_count;
}

int main(int argc, char* argv[])
{
  int error_count = 0;

  if (argc != 2)
    {
    std::cerr << "usage: "
              << argv[0] << " folder_to_read\n";
    return 1;
    }

  char* file_location = argv[1];

  error_count += test_timestamp_formats(file_location);

  std::cout << "Returning exit code " << error_count << "\n";
  return error_count;
}
