/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// ConvexHull
//
// This routine calculates the convex hull of a set of lat-lon points
//
// Created by Danny Rintoul.
//

#ifndef __get_convex_hull
#define __get_convex_hull

#include "Common.h"

void GetConvexHull(trajectory_type &trajectory, TrackLonLat &hull);

double GetHullEccentricity(trajectory_type &trajectory);
double GetHullAspectRatio(trajectory_type &trajectory);
double GetHullArea(trajectory_type &trajectory);

point_ll GetLatLonCentroid(TrackLonLat &data);
point_ll GetLatLonCentroid(const trajectory_type &trajectory);

void RotatePoints(TrackLonLat &data, point_ll center);

void NorthPoleHull(TrackLonLat &data, TrackLonLat &hull);

void ReturnPoints(TrackLonLat &data, point_ll center);

double findMaxDistance(TrackLonLat &data, point_ll center);

double GetRadiusGyration(trajectory_type &trajectory);
#endif
