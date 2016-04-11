// 
// ConvexHull
//
// This routine calculates the convex hull of a set of lat-lon points
//
// Created by Danny Rintoul.
// Copyright 2013 Sandia Corporation.  All rights reserved. 
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
point_ll GetWeightedLatLonCentroid(std::vector<std::pair<point_ll,double> >&data);
point_ll GetWeightedLatLonSlerp(std::vector<std::pair<point_ll,double> >&data);

void RotatePoints(TrackLonLat &data, point_ll center);

void NorthPoleHull(TrackLonLat &data, TrackLonLat &hull);

void ReturnPoints(TrackLonLat &data, point_ll center);

double findMaxDistance(TrackLonLat &data, point_ll center);

double GetRadiusGyration(trajectory_type &trajectory);
#endif
