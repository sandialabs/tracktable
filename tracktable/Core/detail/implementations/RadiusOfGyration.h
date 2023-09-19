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

#ifndef __tracktable_detail_implementations_RadiusOfGyration_h
#define __tracktable_detail_implementations_RadiusOfGyration_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/Trajectory.h>

#include <tracktable/Core/detail/algorithm_signatures/RadiusOfGyration.h>
#include <tracktable/Core/detail/algorithm_signatures/ConvexHull.h>

#include <cassert>
#include <typeinfo>

#include <iostream>


namespace tracktable { namespace algorithms {


    /** Return radius of gyration for a collection of points
     *
     * Returns the radius of gyration for a set of points in
     * radians. If the set is empty, return 0.
     * The units of the result depend on the trajectory type
     * used as this is the basis of the distance function.
     *
     * @param a trajectory or container of points.
     *
     * @return double - the radius of gyration.
     */

    template<typename point_type>
    struct radius_of_gyration<tracktable::Trajectory<point_type> >
    {
      typedef tracktable::Trajectory<point_type> TrajectoryT;

      static inline double apply(TrajectoryT const& path)
      {
        // Sanity check: if a trajectory has fewer than 3 points its
        // radius of gyration is by definition zero
        if (path.size() < 2) return 0;

        point_type centroid = tracktable::convex_hull_centroid(path);

        double sum = 0.0;
        double size = 0.0;
        for (typename TrajectoryT::const_iterator itr = path.begin(); itr != path.end(); itr++)
          {
          double dist = tracktable::distance(*itr, centroid);
          sum += (dist * dist);
          size += 1.0;
          }
        if (size < 1) return 0;
        return sqrt(sum / size);
      }
    };

} } // exit namespace tracktable::algorithms

#endif
