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

#include <fstream>
#include <iostream>
#include <string>

#include <tracktable/RW/PointReader.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Domain/Terrestrial.h>



int read_air_data_file(int expected_num_points, std::string const& filename)
{
  typedef tracktable::TrajectoryPoint<tracktable::PointLonLat> my_trajectory_point_type;
  typedef tracktable::PointReader<my_trajectory_point_type> reader_type;

  std::ifstream infile(filename.c_str());
  if (!infile.is_open())
    {
    std::cout << "ERROR: read_air_data_file: Couldn't open '"
              << filename << "'\n";
    return 1;
    }

  reader_type reader(infile);
  reader.set_field_delimiter(",");

//  reader.set_string_field_column("test",0);
  reader.set_object_id_column(0);
  reader.set_timestamp_column(1);
  reader.set_coordinate_column(0, 2);
  reader.set_coordinate_column(1, 3);
  reader.set_real_field_column("speed", 4);
  reader.set_real_field_column("heading", 5);

  reader_type::iterator point_iter = reader.begin();
  int point_index = 0;
  for (; point_iter != reader.end(); ++point_iter)
    {
    std::cout << "Point index "
              << point_index++ << ": "
              << *point_iter << "\n";
    }

  std::cout << "test_point_fields: Read "
    << point_index
    << " points from file "
    << filename << "\n";

  if (point_index != expected_num_points)
  {
    std::cout << "ERROR: We expected to see "
      << expected_num_points << " points"
      << " but actually saw "
      << point_index << ".\n";
    return 1;
  }
  else
  {
    std::cout << "SUCCESS: We found the expected number of points ("
      << point_index << ")" << std::endl;
  }


  return 0;
}

int main(int argc, char* argv[])
{
  int expected_num_points = 0;
  std::string infilename;

  if (argc >= 2)
    {
    expected_num_points = atoi(argv[1]);
    infilename = argv[2];
    }
  else
    {
    infilename = "/Users/atwilso/test_air_data.tsv";
    }

  return read_air_data_file(expected_num_points, infilename);
}
