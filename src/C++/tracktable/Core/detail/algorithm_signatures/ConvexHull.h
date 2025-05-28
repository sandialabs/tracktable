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

/*
 * ConvexHull - Signatures for algorithms that use the convex hull.
 * We do not yet provide a way to get the convex hull itself.
 */

#ifndef __tracktable_core_detail_algorithm_signatures_ConvexHull_h
#define __tracktable_core_detail_algorithm_signatures_ConvexHull_h

#include <boost/mpl/assert.hpp>

#include <tracktable/Core/detail/trait_signatures/Dimension.h>
#include <boost/geometry/core/cs.hpp>

namespace tracktable { namespace algorithms {

template<typename coord_sys, std::size_t dimension>
struct compute_convex_hull_aspect_ratio
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(coord_sys)==0,
    CONVEX_HULL_ASPECT_RATIO_NOT_IMPLEMENTED_FOR_THIS_COORDINATE_SYSTEM,
    (types<coord_sys>)
    );
};

template<typename coord_sys, std::size_t dimension>
struct compute_convex_hull_perimeter
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(coord_sys)==0,
    CONVEX_HULL_PERIMETER_NOT_IMPLEMENTED_FOR_THIS_COORDINATE_SYSTEM,
    (types<coord_sys>)
    );
};

template<typename coord_sys, std::size_t dimension>
struct compute_convex_hull_area
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(coord_sys)==0,
    CONVEX_HULL_AREA_NOT_IMPLEMENTED_FOR_THIS_COORDINATE_SYSTEM,
    (types<coord_sys>)
    );
};

template<typename coord_sys, std::size_t dimension>
struct compute_convex_hull_centroid
{
  BOOST_MPL_ASSERT_MSG(
    sizeof(coord_sys)==0,
    CONVEX_HULL_CENTROID_NOT_IMPLEMENTED_FOR_THIS_COORDINATE_SYSTEM,
    (types<coord_sys>)
    );
};

} } // exit namespace tracktable::algorithms

// Now we include the driver functions that let us use the
// implementations in functions instead of instantiating them manuall.

namespace tracktable {

template<typename TrajectoryT>
double convex_hull_aspect_ratio(TrajectoryT const& path)
{
  typedef typename TrajectoryT::value_type point_type;
  typedef typename boost::geometry::coordinate_system<point_type>::type coord_system_type;
  const std::size_t dimension(tracktable::traits::dimension<point_type>::value);

  return algorithms::compute_convex_hull_aspect_ratio<coord_system_type, dimension>::apply(path.begin(), path.end());
}

template<typename TrajectoryT>
double convex_hull_perimeter(TrajectoryT const& path)
{
  typedef typename TrajectoryT::value_type point_type;
  typedef typename boost::geometry::coordinate_system<point_type>::type coord_system_type;
  const std::size_t dimension(tracktable::traits::dimension<point_type>::value);

  return algorithms::compute_convex_hull_perimeter<coord_system_type, dimension>::apply(path.begin(), path.end());
}

template<typename TrajectoryT>
double convex_hull_area(TrajectoryT const& path)
{
  typedef typename TrajectoryT::value_type point_type;
  typedef typename boost::geometry::coordinate_system<point_type>::type coord_system_type;
  const std::size_t dimension(tracktable::traits::dimension<point_type>::value);

  return algorithms::compute_convex_hull_area<coord_system_type, dimension>::apply(path.begin(), path.end());
}

template<typename TrajectoryT>
typename TrajectoryT::value_type convex_hull_centroid(TrajectoryT const& path)
{
  typedef typename TrajectoryT::value_type point_type;
  typedef typename boost::geometry::coordinate_system<point_type>::type coord_system_type;
  const std::size_t dimension(tracktable::traits::dimension<point_type>::value);

  return algorithms::compute_convex_hull_centroid<coord_system_type, dimension>::apply(path.begin(), path.end());
}


} // exit namespace tracktable

#endif
