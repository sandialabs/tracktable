/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// 
// Portal
//
// A simple definition of a portal
//
//
// Created by Danny Rintoul
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.
//

#ifndef __Portal
#define __Portal

#include <set>
#include <string>
#include <list>
#include <boost/shared_ptr.hpp>
#include <boost/geometry/geometries/box.hpp>
#include <boost/geometry/geometries/register/box.hpp>
#include "Common.h"
#include "my_pq.h"

class Portal : public boost::geometry::model::box<trajectory_point_type>
{
public:
  Portal() {};
  Portal(const boost::geometry::model::box<trajectory_point_type>& b) : 
   boost::geometry::model::box<trajectory_point_type>(b) {};

  unsigned int level;
  std::set<trajectory_type*> trajectories;
  std::list<boost::shared_ptr<Portal> > children;
  bool operator < (const Portal &p) 
   const {return (trajectories.size() < p.trajectories.size());}
};

BOOST_GEOMETRY_REGISTER_BOX(Portal, trajectory_point_type, min_corner(), max_corner());

typedef std::set<trajectory_type*>::iterator fp_itr;
typedef boost::shared_ptr<Portal> PP;
typedef std::list<PP>::iterator pp_itr;

struct PPCompare {
  bool operator() (const PP& p1, const PP& p2) const {
   return p1->trajectories.size() < p2->trajectories.size();}
};

std::ostream& operator<< (std::ostream &out, Portal &p);

double PortalDist(const PP &p1, const PP &p2);

class Portal_pair
{
public:
  PP p1;
  PP p2;
  unsigned int val;
  double sep;
//  bool operator < (const Portal_pair &p) const {return (val < p.val);}
//  bool operator < (const Portal_pair &p) const {return (sep < p.sep);}
  bool operator < (const Portal_pair &p) const {return (val*sep < p.val*p.sep);}
};

class Pair_heap : public my_pq<Portal_pair>
{
public:
  double min_sep;
  unsigned int min_val;
};

void SubDividePortal(PP &parent, unsigned int interval_x = 2, 
 unsigned int inverval_y = 2);
int RefinePairs(Pair_heap &pairs,
 const unsigned int depth, const unsigned int interval_x = 2, 
 const unsigned int interval_y = 2);
void RefineTopPair(Pair_heap &pairs,
 const unsigned int depth, const unsigned int interval_x = 2, 
 const unsigned int interval_y = 2);
void MakeNewPair(Pair_heap &pairs, PP &p1, PP &p2);
void RemoveTopPair(Pair_heap &pairs, PP &US);
void RemoveTopPair(Pair_heap &pairs, 
 Trajectories &trajectories, PP &US);
void RemoveTrajectories(PP &US, Trajectories &trajectories, 
 std::vector<trajectory_type*> &to_remove);
void RemoveClippedTrajectories(PP &portal, Trajectories &trajectories,
 std::vector<trajectory_type*> &to_remove, const Portal_pair &pp);
void UpdatePairVal(Portal_pair &pp);
void UpdatePairSep(Portal_pair &pp);
int RefineSingles(my_pq<PP,std::vector<PP>,PPCompare> &portals, 
 const unsigned int depth, const unsigned int interval_x = 2, 
 const unsigned int interval_y = 2);
void RefineTopSingle(my_pq<PP,std::vector<PP>,PPCompare> &portals, 
 const unsigned int depth, const unsigned int interval_x = 2, 
 const unsigned int interval_y = 2);
void RemoveTopPortal(my_pq<PP,std::vector<PP>,PPCompare> &portals, PP &US);
bool FPIntersects(const trajectory_type* fp, const PP &pp);
std::vector<trajectory_point_type> FPIntersection(const trajectory_type* fp, const PP &pp);
//void GetTwoBoxLS(const Portal_pair &pp, trajectory_type *trajectory,
// Ls &trajectory_portion);
bool WithinPortalEllipse(const Portal_pair &pp, trajectory_type *trajectory,
 const double &ecc);
void RemoveTopPairClipped(Pair_heap &pairs,
 Trajectories &trajectories, PP &US);
void ClipTrajectory(PP &portal, Trajectories &trajectories, 
 trajectory_type *trajectory, T_itr &first_pt, T_itr &last_pt);
void AddTrajectory(PP &portal, trajectory_type *to_add);
void GetTwoPortalSegment(const Portal_pair &pp, trajectory_type *trajectory,
T_itr &first_pt, T_itr &last_pt);
void PortalRemoveTrajectory(PP &portal, trajectory_type *to_remove);
void ListRemoveTrajectory(Trajectories &trajectories, trajectory_type *t);
#endif
