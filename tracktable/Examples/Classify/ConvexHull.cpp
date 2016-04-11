/*
 * Copyright (c) 2015, Sandia Corporation.  All rights
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

//
// ConvexHull
//
// Here is the convex hull calculation as done by default in boost.
// It seems to work fine with lat-lon, but there are clearly some issues
// related to problems if it is more than 2 Pi Steradians.
//

#include "ConvexHull.h"
#include <boost/geometry/geometries/register/linestring.hpp>
#include <boost/geometry/geometries/polygon.hpp>
#include <boost/geometry/algorithms/convex_hull.hpp>
#include <boost/geometry/geometries/polygon.hpp>
#include <boost/geometry/geometries/linestring.hpp>

BOOST_GEOMETRY_REGISTER_LINESTRING(TrackLonLat)

void GetConvexHull(trajectory_type &trajectory, TrackLonLat &hull)
{
  TrackLonLat test_data;

  // Grab the lat_lon from the flight record

  std::copy(trajectory.begin(),trajectory.end(),std::back_inserter(test_data));

  // Find the center

  point_ll center = GetLatLonCentroid(test_data);

  // Rotate the points to the "top of the world" such that the center point
  // is at the North Pole.  This is to ensure a good transformation

  RotatePoints(test_data,center);

  // Do a flat downward to 2-d projection, get the hull

  NorthPoleHull(test_data,hull);

  // Re-rotate the points to the original coordinate system

  ReturnPoints(hull,center);

  return;
}

double GetHullEccentricity(trajectory_type &trajectory)
{
  // The way this works is that it finds a crude measure of the eccentricity
  // of the convex hull of the flight by taking the min distance of the
  // center to the hull, the maximum distance from the center to the hull,
  // and using those as the semi-minor and semi-major axes, respectively.

  TrackLonLat hull;

  GetConvexHull(trajectory,hull);

  point_ll center = GetLatLonCentroid(hull);
//  double min_dist = distFromTrack(center,hull);
  double min_dist = tracktable::conversions::radians_to_km(
   boost::geometry::distance(hull,center));
  double max_dist = findMaxDistance(hull,center);

  // This is the true "eccentricity".  In practice, this number is always
  // too close to one to be useful.  I prefer the aspect ratio.

  return sqrt(1.0 - pow(min_dist/max_dist,2.0));
}
  
double GetHullAspectRatio(trajectory_type &trajectory)
{
  // The way this works is that it finds a crude measure of the eccentricity
  // of the convex hull of the flight by taking the min distance of the
  // center to the hull, the maximum distance from the center to the hull,
  // and using that ratio (strictly less than 1) as the aspect ratio.

  TrackLonLat hull;

  GetConvexHull(trajectory,hull);

  point_ll center = GetLatLonCentroid(hull);

  double min_dist = tracktable::conversions::radians_to_km(
   boost::geometry::distance(center,hull));
//  double min_dist = 0.0;
  double max_dist = findMaxDistance(hull,center);

  return (max_dist == 0.0) ? 0 : min_dist/max_dist;
}

double GetHullArea(trajectory_type &trajectory)
{
  // Convex hull area in steradians

  TrackLonLat hull;

  GetConvexHull(trajectory,hull);

  boost::geometry::model::polygon<point_ll> poly_hull;
  boost::geometry::assign_points(poly_hull,hull);

  return tracktable::conversions::steradians_to_km2(boost::geometry::area(poly_hull));
}

point_ll GetLatLonCentroid(TrackLonLat &data)
{

  // This calculation is strictly a 3-D centroid of the points which is then
  // projected onto the sphere.  This only screws up if you have two antinodal
  // points.

  double x = 0.0, y = 0.0, z = 0.0;

  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr) {
    double lat_rad = itr->get<1>()*M_PI/180.0;
    double lon_rad = itr->get<0>()*M_PI/180.0;
    x += cos(lat_rad)*cos(lon_rad);
    y += cos(lat_rad)*sin(lon_rad);
    z += sin(lat_rad);
  }

  x /= static_cast<double>(data.size());
  y /= static_cast<double>(data.size());
  z /= static_cast<double>(data.size());
  double center_lon = atan2(y,x)*180.0/M_PI;
  double center_lat = atan2(z,sqrt(x*x + y*y))*180.0/M_PI;
  return point_ll(center_lon,center_lat);
}

point_ll GetLatLonCentroid(const trajectory_type &trajectory)
{

  // The LatLonCentroid for the flight.  You have to extract the points first
  // and then just use the linestring routine.  This will probably be
  // simpler with a better data structure.

  TrackLonLat temp;
  std::copy(trajectory.begin(),trajectory.end(),std::back_inserter(temp));
  return GetLatLonCentroid(temp);
}

void RotatePoints(TrackLonLat &data, point_ll center)
{
  // The points are in lat-lon, and so is the center.  First, we rotate
  // the points so that the center is at longitude 0.0.  No trig here.

  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr) {
    double new_lon = fmod((itr->get<0>() - center.get<0>()),360.0);
    itr->set<0>(new_lon);
  }


  // Now we rotate points so that the center is at latitude 90 degrees
  // (North Pole).  There is trig here.  It is a little work to do this
  // right, but it's just trig.  I have a hardcopy of the pen & paper
  // calculation, but you can also just back it out of any Euler angle
  // discussion.

  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr) {
    double old_lon = itr->get<0>()*M_PI/180.0;
    double old_lat = itr->get<1>()*M_PI/180.0;
    double theta = center.get<1>()*M_PI/180.0;
    double new_lon = atan2(sin(old_lon)*cos(old_lat),
     cos(old_lon)*cos(old_lat)*sin(theta) - sin(old_lat)*cos(theta));
    double new_lat = asin(sin(old_lat)*sin(theta) +
     cos(old_lon)*cos(old_lat)*cos(theta));
    itr->set<0>(180.0*new_lon/M_PI);
    itr->set<1>(180.0*new_lat/M_PI);
  }

  return;
}

void NorthPoleHull(TrackLonLat &data, TrackLonLat &hull)
{

  // We don't do much on 2-D flat planes, so I don't have a typedef here,
  // as if to say, "This is unusual".  

  boost::geometry::model::polygon<point_xy> projection;
  boost::geometry::model::linestring<point_xy> flat_hull;

  // First fill project the points down to a plane through the equator

  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr) {
    double r = cos(itr->get<1>()*M_PI/180.0);
    point_xy temp;
    temp.set<0>(r*cos(itr->get<0>()*M_PI/180.0));
    temp.set<1>(r*sin(itr->get<0>()*M_PI/180.0));
    boost::geometry::append(projection,temp);
  }

  // Then calculate the convex hull via boost

  boost::geometry::convex_hull(projection,flat_hull);

  // And then re-project back to the North Pole centered system.

  for (boost::geometry::model::linestring<point_xy>::iterator itr = flat_hull.begin(); itr != flat_hull.end(); ++itr) {
    double x = itr->get<0>();
    double y = itr->get<1>();
    point_ll temp;
    temp.set<0>(atan2(y,x)*180.0/M_PI);
    temp.set<1>(acos(sqrt(x*x + y*y))*180.0/M_PI);
    hull.push_back(temp);
//    boost::geometry::append(hull,temp);
//     point_ll(atan2(y,x)*180.0/M_PI,acos(sqrt(x*x + y*y))*180.0/M_PI));
  }

  // Note we don't return the points from the North Pole centered system.
  // That is done in "ReturnPoints".

  return;
}
    
void ReturnPoints(TrackLonLat &data, point_ll center)
{
  // Just invert the previous rotation.

  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr) {
    double old_lon = itr->get<0>()*M_PI/180.0;
    double old_lat = itr->get<1>()*M_PI/180.0;
    double theta = center.get<1>()*M_PI/180.0;
    double new_lon = atan2(sin(old_lon)*cos(old_lat),
     cos(old_lon)*cos(old_lat)*sin(theta) + sin(old_lat)*cos(theta));
    double new_lat = asin(sin(old_lat)*sin(theta) -
     cos(old_lon)*cos(old_lat)*cos(theta));
    itr->set<0>(180.0*new_lon/M_PI);
    itr->set<1>(180.0*new_lat/M_PI);
  }

  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr) {
    double new_lon = fmod((itr->get<0>() + center.get<0>()),360.0);
    itr->set<0>(new_lon);
  }

  return;
}

double findMaxDistance(TrackLonLat &data, point_ll center)
{
  double max_dist = 0.0;
  for (TrackLonLat::iterator itr = data.begin(); itr != data.end(); ++itr)
    max_dist = std::max(max_dist,tracktable::distance(center,*itr));

  return max_dist;
}

double GetRadiusGyration(trajectory_type &trajectory)
{
  TrackLonLat test_data;

  // Grab the lat_lon from the flight record

  std::copy(trajectory.begin(),trajectory.end(),std::back_inserter(test_data));

  point_ll center = GetLatLonCentroid(test_data);
  double sum = 0.0;
  for (trajectory_type::iterator itr = trajectory.begin(); itr != trajectory.end(); ++itr) {
//    double dist = boost::geometry::distance<point_ll,point_ll>(*itr,center);
    double dist = tracktable::distance(*itr,center);
    sum += dist*dist;
  }

  return sqrt(sum/(static_cast<double>(trajectory.size() - 1)));
}
