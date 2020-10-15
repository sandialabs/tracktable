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

#include <algorithm>
#include <boost/bind.hpp>


#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/ShadowedDeclaration.h>
#include <boost/date_time/gregorian/gregorian.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

#include "Common.h"
#include "AssignHeadings.h"
#include "BuildTrajectories.h"
#include "CommandLineOptions.h"
#include "KmlOut.h"
#include "ParseCommandLine.h"
#include "GetMappers.h"
#include "Mapping.h"
#include "ConvexHull.h"

template<typename trajectory_t>
float absolute_curvature(trajectory_t const& trajectory)
{
  return fabs(TotalCurvature(trajectory));
}

int main(int argc, char* argv[])
{

  CommandLineOptions options = ParseCommandLine(argc, argv);

  // Example: read in trajectories
  std::vector<trajectory_type> trajectories;
  BuildTrajectories<trajectory_type>(options,trajectories);

  // Example: assign headings to all of the points
  AssignTrajectoriesHeadings(trajectories);

  // Example: get rid of short (< 50km) trajectories
  trajectories.erase(
   std::remove_if(trajectories.begin(), trajectories.end(),
                  boost::bind(&tracktable::length<trajectory_type>,_1) < 50.0),
   trajectories.end());

  // trajectories.erase(
  //     std::remove_if(
  //         trajectories.begin(),
  //         trajectories.end(),
  //         boost::bind(fabs,
  //                     (boost::bind(TotalCurvature,_1))) < 3600),
  //     trajectories.end());


  trajectories.erase(
                     std::remove_if(
                                    trajectories.begin(),
                                    trajectories.end(),
                                    (boost::bind(absolute_curvature<trajectory_type>, _1) < 3600)),
                     trajectories.end());

  /*
  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(std::divides<double>(),
   boost::bind(&GetHullArea,_1),
   boost::bind(&GetRadiusGyration,_1)) < 300.0),
   trajectories.end());

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(std::divides<double>(),
   boost::bind(&tracktable::end_to_end_distance<trajectory_type>,_1),
   boost::bind(&tracktable::length<trajectory_type>,_1)) > 0.2),
   trajectories.end());

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(&GetHullAspectRatio,_1) < 0.05),trajectories.end());

  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(&StraightFraction,_1) < 0.03),trajectories.end());
*/
  trajectories.erase(std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(&TurnArounds,_1) < 5U),trajectories.end());

  // Example: read in a list of object_id's of known (sort of) mappers
/*
  std::vector<std::string> mappers;
  GetMappers(mappers);

  std::vector<int> labels;
  std::ifstream in("/tmp/output");
  int temp;
  while (in >> temp)
    labels.push_back(temp);
*/

  // Example: separate the trajectories based on whether they are on the
  // mapping list.  Uglier than it needs to be for C++03 reasons.
/*  std::vector<trajectory_type> map_trajectories;
  typedef bool(*binary_search_signature)(std::vector<std::string>::iterator,
    std::vector<std::string>::iterator, const std::string &);

  std::remove_copy_if(trajectories.begin(),trajectories.end(),
   std::back_inserter(map_trajectories),
   !boost::bind(static_cast<binary_search_signature>
   (std::binary_search),mappers.begin(),mappers.end(),
   boost::bind(&trajectory_type::object_id,_1)));

  trajectories.erase(
   std::remove_if(trajectories.begin(),trajectories.end(),
   boost::bind(static_cast<binary_search_signature>
   (std::binary_search),mappers.begin(),mappers.end(),
   boost::bind(&trajectory_type::object_id,_1))),trajectories.end());

  std::cout << "trajectories.size() = " << trajectories.size() << std::endl;
  std::cout << "map_trajectories.size() = " << map_trajectories.size() << std::endl; */


/*
  for (unsigned int i = 0; i < trajectories.size(); ++i) {
    if (GetHullArea(trajectories[i])/GetRadiusGyration(trajectories[i]) > 300.0)
      std::cout << " 1";
    else
      std::cout << "-1";
    std::cout << " 1:" << TurnArounds(trajectories[i]);
    std::cout << " 2:" << StraightFraction(trajectories[i]);
    std::cout << " 3:" << GetHullAspectRatio(trajectories[i]);
    std::cout << " 4:" << tracktable::end_to_end_distance(trajectories[i])/tracktable::length(trajectories[i]);
    std::cout << " 5:" << GetHullArea(trajectories[i])/GetRadiusGyration(trajectories[i]);
    std::cout << std::endl;
  }
*/

  for (unsigned int i = 0; i < trajectories.size(); ++i) {
    std::string s = "output/" + trajectories[i].object_id();
    s += "-";
    s += boost::gregorian::to_simple_string(trajectories[i].start_time().date());
    s += ".kml";
    std::ofstream outfile(s.c_str());
    writeKmlTrajectory(trajectories[i],
     outfile,"FFFFFFFF",2.0);
    outfile.clear();
    outfile.close();
  }


  return 0;
}
