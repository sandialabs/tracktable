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
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>

namespace tracktable {

typedef TrajectoryPoint<PointLonLat> TrajectoryPointLonLat;
typedef Trajectory<TrajectoryPointLonLat> TrajectoryLonLat;

}

int test_trajectory_uuid()
{
  typedef ::tracktable::TrajectoryLonLat trajectory_type;
  int error_count = 0;

  trajectory_type path1;

  ::tracktable::uuid_type null_uuid = tracktable::uuid_type();

  if (path1.uuid() == null_uuid) {
    std::cerr << "ERROR: Expected non-null trajectory UUID\n";
    ++error_count;
  }

  trajectory_type path2(path1);

  if (path1.uuid() != path2.uuid()) {
    std::cerr << "ERROR: Expected copy constructor to create equivalent UUIDs for trajectories\n";
    ++error_count;
  }

  path2.set_uuid();

  if (path1.uuid() == path2.uuid()) {
    std::cerr << "ERROR: Expected path2 to contain a new random UUID different from path1\n";
    ++error_count;
  }

  trajectory_type path3;
  path3 = path1;

  if (path1.uuid() != path3.uuid()) {
    std::cerr << "ERROR: Expected assignment operator to create equivalent UUIDs for trajectories\n";
    ++error_count;
  }

  ::tracktable::uuid_type new_random_uuid = tracktable::automatic_uuid_generator()->generate_uuid();
  path3.set_uuid(new_random_uuid);

  if (path1.uuid() == path3.uuid()) {
    std::cerr << "ERROR: Expected path3 to contain a new random UUID different from path1\n";
    ++error_count;
  }

  trajectory_type path4(false);

  if (path4.uuid() != null_uuid) {
    std::cerr << "ERROR: Expected null trajectory UUID with automatic generation disabled\n";
    ++error_count;
  }

  trajectory_type path5;

  if (path5.uuid() == null_uuid) {
    std::cerr << "ERROR: Expected non-null trajectory UUID with automatic generation re-enabled\n";
    ++error_count;
  }

  ::tracktable::set_automatic_uuid_generator(::tracktable::BoostRandomUUIDGeneratorPure::create());
  ::tracktable::uuid_type new_random_uuid2 = tracktable::automatic_uuid_generator()->generate_uuid();

  if (path5.uuid() == new_random_uuid2) {
    std::cerr << "ERROR: Expected different uuids with the new generator\n";
    ++error_count;
  }

  ::tracktable::uuid_type new_random_uuid3 = tracktable::automatic_uuid_generator()->generate_uuid();

  if (new_random_uuid3 == new_random_uuid2) {
    std::cerr << "ERROR: Expected different uuids with the new generator\n";
    ++error_count;
  }


  return error_count;
}

int main(int /*argc*/, char* /*argv*/[])
{
  int error_count = test_trajectory_uuid();
  return error_count;
}
