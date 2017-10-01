/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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
#include "AirDataRoutines.h"

void GetConvexHull(BasicTrajectory &trajectory, TrackLonLat &hull);

double GetHullEccentricity(BasicTrajectory &trajectory);
double GetHullAspectRatio(BasicTrajectory &trajectory);
double GetHullArea(BasicTrajectory &trajectory);

point_ll GetLatLonCentroid(TrackLonLat &data);
point_ll GetLatLonCentroid(const BasicTrajectory &trajectory);
point_ll GetWeightedLatLonCentroid(std::vector<std::pair<point_ll,double> >&data);
point_ll GetWeightedLatLonSlerp(std::vector<std::pair<point_ll,double> >&data);

void RotatePoints(TrackLonLat &data, point_ll center);

void NorthPoleHull(TrackLonLat &data, TrackLonLat &hull);

void ReturnPoints(TrackLonLat &data, point_ll center);

double findMaxDistance(TrackLonLat &data, point_ll center);

double GetRadiusGyration(BasicTrajectory &trajectory);
#endif
