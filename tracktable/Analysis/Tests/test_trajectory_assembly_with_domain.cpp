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
 * 2. Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following
 * disclaimer in the documentation and/or other materials provided
 * with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Analysis/AssembleTrajectories.h>

#include <iostream>
#include <fstream>

int read_asdi_trajectories(
  std::string const& filename,
  int expected_trajectory_count,
  int expected_reject_count,
  int expected_point_count
  )
{
  namespace tt_domain = tracktable::domain::terrestrial;
  typedef tt_domain::trajectory_point_reader_type reader_type;
  typedef tt_domain::trajectory_type              trajectory_type;
  typedef tracktable::AssembleTrajectories<trajectory_type, reader_type::iterator> assembler_type;


  reader_type point_reader;
  assembler_type trajectory_builder;

  int valid_trajectory_count = 0;
  int invalid_trajectory_count = 0;
  int point_count = 0;

  trajectory_builder.set_separation_time(tracktable::minutes(20));
  trajectory_builder.set_separation_distance(100);
  trajectory_builder.set_minimum_trajectory_length(500);

  std::ifstream infile(filename.c_str());

  if (!infile)
    {
    std::cerr << "ERROR: Could not open file '"
              << filename << "'\n";
    return -1;
    }

  point_reader.set_input(infile);
  point_reader.set_object_id_column(0);
  point_reader.set_timestamp_column(1);
  point_reader.set_longitude_column(2);
  point_reader.set_latitude_column(3);

  trajectory_builder.set_input(point_reader.begin(), point_reader.end());

  std::cout << "Reading trajectories...\n";
  int num_trajectories = 0;
  for (assembler_type::iterator iter = trajectory_builder.begin();
       iter != trajectory_builder.end();
       ++iter)
    {
    ++num_trajectories;
    trajectory_type next_trajectory(*iter);
    std::cout << "Trajectory " << num_trajectories << ": "
              << next_trajectory.size() << " points, object_id "
              << next_trajectory.object_id() << "\n";
    std::cout << "Iterator has processed "
              << iter.point_count() << " points, published "
              << iter.valid_trajectory_count() << " trajectories and rejected "
              << iter.invalid_trajectory_count() << "\n";
    valid_trajectory_count = iter.valid_trajectory_count();
    invalid_trajectory_count = iter.invalid_trajectory_count();
    point_count = iter.point_count();
    }

  int error_count = 0;
  if (valid_trajectory_count != expected_trajectory_count)
    {
    std::cout << "ERROR: Expected to receive "
              << expected_trajectory_count
              << " trajectories but instead got "
              << valid_trajectory_count << ".\n";
    ++error_count;
    }

  if (invalid_trajectory_count != expected_reject_count)
    {
    std::cout << "ERROR: Expected to see "
              << expected_reject_count
              << " rejected trajectories but instead got "
              << invalid_trajectory_count << ".\n";
    ++error_count;
    }

  if (point_count != expected_point_count)
    {
    std::cout << "ERROR: Expected to see "
              << expected_point_count
              << " points processed but instead got "
              << point_count << ".\n";
    ++error_count;
    }

  return (error_count != 0);
}

// ----------------------------------------------------------------------

int
main(int argc, char* argv[])
{
  if (argc != 5)
    {
    std::cerr << "usage: "
              << argv[0] << " filename.tsv expected_trajectories expected_rejects expected_points\n";
    return 1;
    }

  std::string filename(argv[1]);
  int expected_trajectory_count = atoi(argv[2]);
  int expected_reject_count = atoi(argv[3]);
  int expected_point_count = atoi(argv[4]);

  return read_asdi_trajectories(filename,
                                expected_trajectory_count,
                                expected_reject_count,
                                expected_point_count);

}
