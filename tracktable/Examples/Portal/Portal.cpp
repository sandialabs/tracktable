/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// Portal.cpp
//
// C++ routines for portal manipulation
//
//
// Created by Danny Rintoul
//

#include <algorithm>
#include <iterator>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/geometry/arithmetic/arithmetic.hpp>
#include <boost/geometry/algorithms/intersects.hpp>
#include <boost/geometry/algorithms/intersection.hpp>
#include <boost/geometry/algorithms/distance.hpp>
#include <boost/geometry/algorithms/convert.hpp>
#include <boost/geometry/geometries/box.hpp>
#include <boost/geometry/geometries/polygon.hpp>
#include <my_stl.h>
#include "Portal.h"
#include "KmlOut.h"

void SubDividePortal(PP &parent, unsigned int interval_x,
 unsigned int interval_y)
{
  trajectory_point_type orig_ll = parent->min_corner();
  double orig_x = orig_ll.get<0>();
  double orig_y = orig_ll.get<1>();

  trajectory_point_type delta = parent->max_corner();;
  boost::geometry::subtract_point(delta,orig_ll);
  double delta_x = delta.get<0>()/static_cast<double>(interval_x);
  double delta_y = delta.get<1>()/static_cast<double>(interval_y);

  for (unsigned int i = 0; i < interval_x; ++i)
    for (unsigned int j = 0; j < interval_y; ++j) {
      double temp[2];
      temp[0] = orig_x + i*delta_x;
      temp[1] = orig_y + j*delta_y;
      trajectory_point_type ll = trajectory_point_type(temp);
      temp[0] = orig_x + (i+1)*delta_x;
      temp[1] = orig_y + (j+1)*delta_y;
      trajectory_point_type ur = trajectory_point_type(temp);
      PP p(new Portal(boost::geometry::model::box<trajectory_point_type>(ll,ur)));
      p->level = parent->level+1;
      parent->children.push_back(p);
    }

  // Now, go through all of the trajectories associated with the parent portal
  // and assign them to the child portals by testing intersection.
  // This is potentially inefficient.

  for (fp_itr itr = parent->trajectories.begin();
   itr != parent->trajectories.end(); ++itr)
    for (pp_itr itr2 = parent->children.begin();
     itr2 != parent->children.end(); ++itr2)
      if (FPIntersects(*itr,*itr2))
        (*itr2)->trajectories.insert(*itr);

  // Now that we've created the children, remove the empty ones

  parent->children.remove_if(boost::bind(&std::set<trajectory_type*>::empty,
   boost::bind(&Portal::trajectories,_1)));

  return;
}

int RefinePairs(Pair_heap &pairs,
 const unsigned int depth, const unsigned int interval_x,
 const unsigned int interval_y)
{
  if (!pairs.empty() && ((pairs.top().p1->level < depth) ||
   (pairs.top().p2->level < depth))) {
    RefineTopPair(pairs,depth,interval_x,interval_y);
    return 1;
  } else
    return 0;
}

void RefineTopPair(Pair_heap &pairs,
 const unsigned int depth, const unsigned int interval_x,
 const unsigned int interval_y)
{

  // Decompose the first portal by default (it's the largest), or
  // do the second if the first is already small enough

  PP shrink, keep;
  if (pairs.top().p1->level < depth) {
    shrink = pairs.top().p1;
    keep = pairs.top().p2;
  } else {
    shrink = pairs.top().p2;
    keep = pairs.top().p1;
  }
  pairs.pop();

  // If we haven't already created the children in the decomposition, do so

  if (shrink->children.empty())
    SubDividePortal(shrink,interval_x,interval_y);

  // Now reassign the pairs

  for (pp_itr itr = shrink->children.begin(); itr
   != shrink->children.end(); ++itr) {
    if (PortalDist(*itr,keep) < pairs.min_sep /* degrees */)
      continue;
    MakeNewPair(pairs,*itr,keep);
    pp_itr itr2 = itr;
    for (++itr2; itr2 != shrink->children.end(); ++itr2) {
      if (PortalDist(*itr,*itr2) < pairs.min_sep)
        continue;
      MakeNewPair(pairs,*itr,*itr2);
    }
  }
}

void MakeNewPair(Pair_heap &pairs, PP &p1, PP &p2)
{
  Portal_pair pp;
  if (p1->trajectories.size() > p2->trajectories.size()) {
    pp.p1 = p1;
    pp.p2 = p2;
  } else {
    pp.p1 = p2;
    pp.p2 = p1;
  }

  UpdatePairVal(pp);
  UpdatePairSep(pp);

  // Have minimum threshold

  if (pp.val >= pairs.min_val)
    pairs.push(pp);

  return;
}

void RemoveTopPair(Pair_heap &pairs, Trajectories &trajectories, PP &US)
{

  std::vector<trajectory_type*> to_remove;
  std::set_intersection(pairs.top().p1->trajectories.begin(),
                        pairs.top().p1->trajectories.end(),
                        pairs.top().p2->trajectories.begin(),
                        pairs.top().p2->trajectories.end(),
                        std::back_inserter(to_remove));

  RemoveTrajectories(US,trajectories,to_remove);

  pairs.pop();  // Finally remove the top one

  // Now that the trajectories are removed, we have to go through and redo the
  // Portal_pairs.  We need to recalculate their overlap and re-heap them.

  std::for_each(pairs.impl().begin(),pairs.impl().end(),UpdatePairVal);
  pairs.impl().erase(std::remove_if(pairs.impl().begin(),pairs.impl().end(),
   boost::bind(std::less<unsigned int>(),
   boost::bind(&Portal_pair::val,_1),pairs.min_val)),pairs.impl().end());
  pairs.make_heap();

  return;
}

void RemoveTopPairClipped(Pair_heap &pairs, Trajectories &trajectories, PP &US)
{

  std::vector<trajectory_type*> to_remove;
  std::set_intersection(pairs.top().p1->trajectories.begin(),
                        pairs.top().p1->trajectories.end(),
                        pairs.top().p2->trajectories.begin(),
                        pairs.top().p2->trajectories.end(),
                        std::back_inserter(to_remove));

  RemoveClippedTrajectories(US,trajectories,to_remove,pairs.top());

  pairs.pop();  // Finally remove the top one

  // Now that the trajectories are removed and added,
  // we have to go through and redo the
  // Portal_pairs.  We need to recalculate their overlap and re-heap them.

  std::for_each(pairs.impl().begin(),pairs.impl().end(),UpdatePairVal);
  pairs.impl().erase(std::remove_if(pairs.impl().begin(),pairs.impl().end(),
   boost::bind(std::less<unsigned int>(),
   boost::bind(&Portal_pair::val,_1),pairs.min_val)),pairs.impl().end());
  pairs.make_heap();

  return;
}

void RemoveTopPortal(my_pq<PP,std::vector<PP>,PPCompare> &portals, PP &US)
{
  for (fp_itr itr = portals.top()->trajectories.begin();
   itr != portals.top()->trajectories.end(); ++itr)
    PortalRemoveTrajectory(US,*itr);

  portals.pop();
  portals.make_heap();

  return;
}
void RemoveTrajectories(PP &portal, Trajectories &trajectories,
 std::vector<trajectory_type*> &to_remove)
{

  std::vector<trajectory_type*>::iterator itr = to_remove.begin();
  for(; itr != to_remove.end(); ++itr) {
    PortalRemoveTrajectory(portal,*itr);
    ListRemoveTrajectory(trajectories,*itr);
  }
  return;
}

void RemoveClippedTrajectories(PP &portal, Trajectories &trajectories,
 std::vector<trajectory_type*> &to_remove, const Portal_pair &pp)
{
  for (std::vector<trajectory_type*>::iterator itr = to_remove.begin();
   itr != to_remove.end(); ++itr) {
    T_itr first_pt, last_pt;
    GetTwoPortalSegment(pp,*itr,first_pt,last_pt);
    ClipTrajectory(portal,trajectories,*itr,first_pt,last_pt);

    PortalRemoveTrajectory(portal,*itr);
    ListRemoveTrajectory(trajectories,*itr);
  }

  return;
}
void UpdatePairVal(Portal_pair &pp)
{
  pp.val = 0;
  fp_itr itr1 = pp.p1->trajectories.begin();
  fp_itr itr2 = pp.p2->trajectories.begin();
  while (itr1 != pp.p1->trajectories.end() && itr2 != pp.p2->trajectories.end()) {
    if (*itr1 < *itr2) ++itr1;
    else if (*itr2 < *itr1) ++itr2;
    else {
      if (WithinPortalEllipse(pp,*itr1,1.01))
        ++pp.val;
      ++itr1; ++itr2;
    }
  }

  return;
}

void UpdatePairSep(Portal_pair &pp)
{
  pp.sep = PortalDist(pp.p1,pp.p2);
}

int RefineSingles(my_pq<PP,std::vector<PP>,PPCompare> &portals,
 const unsigned int depth, const unsigned int interval_x,
 const unsigned int interval_y)
{
  if (portals.top()->level < depth) {
    RefineTopSingle(portals,depth,interval_x,interval_y);
    return 1;
  } else
    return 0;
}

void RefineTopSingle(my_pq<PP,std::vector<PP>,PPCompare> &portals,
 const unsigned int depth, const unsigned int interval_x,
 const unsigned int interval_y)
{
  PP shrink = portals.top();
  portals.pop();

  SubDividePortal(shrink,interval_x,interval_y);
  for (pp_itr itr = shrink->children.begin();
   itr != shrink->children.end(); ++itr)
    portals.push(*itr);
}

std::ostream& operator<< (std::ostream &out, Portal &p)
{
  out << "Level :" << p.level << std::endl;
  out << boost::geometry::wkt(p) << std::endl;
  out << "trajectories.size() = " << p.trajectories.size() << std::endl;
  out << "children.size() = " << p.children.size();

  return out;
}

bool FPIntersects(const trajectory_type* fp, const PP &pp)
{
  return boost::geometry::intersects(*fp,*pp);
}
/*
std::vector<trajectory_point_type> FPIntersection(const trajectory_type* fp, const PP &pp)
{
  boost::geometry::model::polygon<trajectory_point_type> poly;
  boost::geometry::convert(*pp,poly);

  std::vector<trajectory_point_type> points;
  boost::geometry::intersection(*fp,poly,points);

  return points;
}
*/
double PortalDist(const PP &p1, const PP &p2)
{
  return boost::geometry::distance(*p1,*p2);
}

void GetTwoPortalSegment(const Portal_pair &pp, trajectory_type *trajectory,
T_itr &first_pt, T_itr &last_pt)
{
  unsigned int prev = 0;
   boost::geometry::model::segment<trajectory_point_type> temp;
  T_itr cur_box1, cur_box2;

  if (trajectory->size() < 2)
    std::cout << "Warning, trajectory->size() = " << trajectory->size() << std::endl;

  for (T_itr itr = trajectory->begin(); itr != trajectory->end()-1; ++itr) {
    temp =
     boost::geometry::model::segment<trajectory_point_type>(*itr,*(itr+1));
    if (boost::geometry::intersects(temp,*pp.p1)) {
      cur_box1 = itr;
      if (prev == 2) {
        last_pt = ++cur_box1;
        first_pt = cur_box2;
      }
      prev = 1;
    }
    if (boost::geometry::intersects(temp,*pp.p2)) {
      cur_box2 = itr;
      if (prev == 1) {
        first_pt = cur_box1;
        last_pt = ++cur_box2;
      }
      prev = 2;
    }
  }

  if (!prev) {
    std::cout << "Something is very wrong!" << std::endl;
  }

  return;
}

bool WithinPortalEllipse(const Portal_pair &pp, trajectory_type *trajectory,
 const double &ecc)
{

  trajectory_type::iterator first_pt, last_pt;
  GetTwoPortalSegment(pp,trajectory,first_pt,last_pt);
  trajectory_type trajectory_portion(first_pt,last_pt);

  if (!trajectory_portion.empty() &&
   (boost::geometry::length(trajectory_portion) <
   ecc*boost::geometry::distance(trajectory_portion.front(),
   trajectory_portion.back()))) {
    return true;
  }

  return false;
}

void ClipTrajectory(PP &portal,
 Trajectories &trajectories, trajectory_type *trajectory,
 T_itr &first_pt, T_itr &last_pt)
{
  trajectory_type part1(trajectory->begin(),first_pt);
  trajectory_type part2(last_pt,trajectory->end());

  if (part1.size() > 4) {
    trajectories.push_back(part1);
    AddTrajectory(portal,&(trajectories.back()));
  }

  if (part2.size() > 4) {
    trajectories.push_back(part2);
    AddTrajectory(portal,&(trajectories.back()));
  }

//  PortalRemoveTrajectory(portal,trajectory);
//  ListRemoveTrajectory(trajectories,trajectory);

  return;
}

void PortalRemoveTrajectory(PP &portal, trajectory_type *to_remove)
{
  if (portal->trajectories.erase(to_remove))
    for (pp_itr itr = portal->children.begin();
     itr != portal->children.end(); ++itr)
      PortalRemoveTrajectory(*itr,to_remove);

  return;
}

void ListRemoveTrajectory(Trajectories &trajectories, trajectory_type *t)
{
  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr) {
    if (&(*itr) == t) {
      trajectories.erase(itr);
      break;
    }
  }

  return;
}

void AddTrajectory(PP &portal, trajectory_type *to_add)
{

  portal->trajectories.insert(to_add);

  // Note, this assumes that the child portal exists.  Right now that
  // assumption is true, but it won't always be.  Basically, sub-dividing is
  // a separate operation.

  for (pp_itr itr = portal->children.begin();
   itr != portal->children.end(); ++itr)
    if (FPIntersects(to_add,*itr))
      AddTrajectory(*itr,to_add);


  return;
}
