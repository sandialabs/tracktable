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

//
//  Common.h
//
#ifndef _Common_h
#define _Common_h

#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Domain/Cartesian2D.h>

#include <boost/geometry/geometries/register/point.hpp>

typedef boost::array<double,10> Feature;
typedef std::vector<Feature> Features;
typedef tracktable::domain::terrestrial::trajectory_point_type trajectory_point_type;
typedef tracktable::domain::terrestrial::trajectory_type trajectory_type;
typedef std::vector<trajectory_type> Trajectories;
typedef Trajectories::iterator Ts_itr;
typedef trajectory_type::iterator T_itr;
typedef std::map<std::string,
 std::vector<tracktable::TrajectoryPoint<tracktable::PointLonLat> > > Trajectory_map;
typedef trajectory_point_type point_ll;
typedef tracktable::domain::cartesian2d::trajectory_point_type point_xy;
typedef std::vector<point_ll> TrackLonLat;
typedef tracktable::domain::cartesian2d::trajectory_type TrackCartesian;

class my_data {
public:
  Feature Point;
  unsigned int Id;
  trajectory_type *index;

  my_data(): Id(0), index(0) {}
  my_data(Feature const& p): Point(p), Id(0), index(0) {}
  my_data(Feature const& p, unsigned int id, trajectory_type *idx): Point(p), Id(id), index(idx) {}
  ~my_data() {}

  my_data(my_data const& p2) {
    Point = p2.Point;
    Id = p2.Id;
    index = p2.index;
  }

  my_data& operator=(my_data const& p2) {
    Point = p2.Point;
    Id = p2.Id;
    index = p2.index;
    return *this;
  }
  void set_Id(const unsigned int &id) {Id = id; return;}
  unsigned int get_Id() {return Id;}
};

#endif
