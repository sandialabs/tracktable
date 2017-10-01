/*
 * Copyright (c) 2015-2017 National Technology and Engineering
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

#include <boost/bind.hpp>
#include <boost/geometry/geometries/linestring.hpp>

#include "Common.h"
#include "BuildTrajectories.h"
#include "CommandLineOptions.h"
#include "KmlOut.h"
#include "ParseCommandLine.h"

int main(int argc, char* argv[])
{

  CommandLineOptions options = ParseCommandLine(argc, argv);

  // Example: read in trajectories
  std::vector<trajectory_type> trajectories;
  BuildTrajectories<trajectory_type>(options,trajectories);
  std::cout << "trajectories.size() = " << trajectories.size() << std::endl;

  // Example: remove trajectories < 500 km
  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(&tracktable::end_to_end_distance<trajectory_type>,_1) < 500.0),
   trajectories.end());
  std::cout << "trajectories.size() = " << trajectories.size() << std::endl;

  // Example: remove trajectories that have a ratio of end_to_end_distance
  // to total distance less than 0.5
  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(std::divides<double>(),
   boost::bind(&tracktable::end_to_end_distance<trajectory_type>,_1),
   boost::bind(&tracktable::length<trajectory_type>,_1)) < 0.5),
   trajectories.end());
  std::cout << "trajectories.size() = " << trajectories.size() << std::endl;

  // Example: get distance from point to trajectory (not built in)
  trajectory_point_type abq;
  abq.set_latitude(35.1107);
  abq.set_longitude(-106.6100);

  std::cout << tracktable::conversions::radians_to_km(
   boost::geometry::distance<trajectory_type,trajectory_point_type>(trajectories.front(),abq)) << std::endl;;

  // Example: get a point that is, time-wise, halfway between the start and
  // end time
  tracktable::point_at_time(trajectories.front(),
   tracktable::interpolate(
    trajectories.front().start_time(),
    trajectories.front().end_time(),0.5));

  return 0;
}
