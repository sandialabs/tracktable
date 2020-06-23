#include "curv_interpolation.h"
#include <boost/bind.hpp>

trajectory_point_type curve_interpolate(
 trajectory_type &traj, double val, unsigned int level)
{

  // This holds all of the intermediate steps, and the final value is the
  // answer.  If you take the final value at any point at the end of the
  // inner loop, that is a valid lower order answer.

  std::vector<trajectory_point_type> ans;

  // This is a highly stylized version of a very simple algorithm known
  // as Neville's algorithm.  Neville's algorithm is just an interpolation
  // algorithm that builds up a series of linear interpolations to give
  // a higher order polynomial interpolation.  We've just substituted the 
  // normal cartesian linear interpolation for a spherical great-circle
  // interpolation.
  //
  // And, for the sake of computer science elegance, we don't go through
  // the traditional order of doing all of the points first, and then doing
  // all of the resulting points, etc.  We do it by adding one point at a time
  // and then producing the resulting interpolation.  It's a little harder
  // to grok, but it is the right way to do this for a lot of reasons.
  //
  // Note that all we are doing is calling tracktable's linear interpolation
  // function over and over.  

  std::vector<trajectory_point_type> point_list;

  get_ordered_neighbors(traj,point_list,val,level);

  for (unsigned int i = 0; i < level; ++i) {
    ans.push_back(point_list[i]);
    for (unsigned int j = 1; j <= i; ++j)
      ans.push_back(tracktable::extrapolate(
       *(ans.rbegin()), *(ans.rbegin() + i),
       (point_list[i].current_length() - val) / 
        (point_list[i].current_length() - point_list[i-j].current_length())));
  }

  return ans.back();
}

void get_ordered_neighbors(const trajectory_type &traj, 
 std::vector<trajectory_point_type> &point_list, 
 double val, unsigned int level)
{

  // Okay, what is this mess?  It's the logic required to grab the nearest
  // k (= level) points from a value in a sorted list, whether or not the
  // list contains the value.
  //
  // Note that this is essentially logarithmic in time.  I could do this in
  // a couple of lines of code (via sort) if people didn't mind N log N time 
  // instead of log N time.  

  if (!level) 
    return;

  // Here are the easy cases where it's either before the beginning or
  // after the end.  If we had reverse iterators, it would be prettier but
  // not more correct.

  typedef trajectory_type::const_iterator c_itr;

  if (val <= traj.front().current_length()) {
    // all are bigger, go through and add them
    for (c_itr itr = traj.begin(); (itr != traj.end()) && level--;)
      point_list.push_back(*itr++);
    return;
  } else if (val >= traj.back().current_length()) {
    // all are small, go backwards and add them
    for (c_itr itr = traj.end(); (itr-- != traj.begin()) && level--;)
      point_list.push_back(*itr);
    return;
  }

  // Okay, we are somewhere in the middle.  Let's find the points around us.
  trajectory_point_type p;
  p.set_current_length(val);

  std::pair<c_itr,c_itr> itrs = std::equal_range(traj.begin(),traj.end(),
   p,boost::bind(&trajectory_point_type::current_length,_1) <
   boost::bind(&trajectory_point_type::current_length,_2));

  c_itr lower = itrs.first;
  c_itr upper = itrs.second;

  // Case of exact match:  We know that lower is exactly right
  if (lower != upper) { // Exact match
    point_list.push_back(*lower);  // Because of earlier check, it's safe
    level--;
  }

  // If exact match, we have used lower and need to move it down.  If not
  // exact match, lower = upper, and we need them different.
  lower--;

  // You can guess what is going on here.  We take the nearest point from 
  // upper and lower.  If we hit either end, we know we just have to finish
  // off in the other direction.  Again, prettier if we had reverse iterators
  // because it woud be symmetrical.  But in the end, it's correct.  

  while (level) {
    --level;
    if ((val - lower->current_length()) < (upper->current_length() - val)) {
      point_list.push_back(*lower);
      if (lower-- == traj.begin()) {  // Finish off the uppers
        for (; level-- && (upper != traj.end());)
          point_list.push_back(*upper++);
        return;
      }
    } else {
      point_list.push_back(*upper);
      if ((++upper == traj.end()) && (level)) {  // Finish off lowers
        for (point_list.push_back(*lower); --level && (lower != traj.begin());)
          point_list.push_back(*--lower);
        return;
      }
    }
  }

  return;
}

