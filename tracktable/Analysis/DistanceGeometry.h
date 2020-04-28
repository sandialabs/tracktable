#ifndef _DG_h
#define _DG_h

#include <vector>
#include <utility> // for std::pair
#include <tracktable/Core/Trajectory.h>


template<typename TrajectoryT>
double ControlPointDistance(TrajectoryT trajectory,
 std::pair<double,double> control_point) {
  return tracktable::distance(
    tracktable::point_at_length_fraction(trajectory,control_point.first),
    tracktable::point_at_length_fraction(trajectory,control_point.second));
}

// This routine returns a vector of distance geometries of length 
// depth * (depth+1)/2 for each trajectory.  The are all normalized to be 
// between 0 and 1.
template<typename TrajectoryT>
void GetDistanceGeometries(std::vector<TrajectoryT> &trajectories, 
 std::vector<std::vector<double> > &dgs, unsigned int depth)
{

  if (depth < 1)
    return;

  // This builds the different fractional intervals
  std::vector<std::pair<double,double> > control_points;
  for (unsigned int i = 1; i <= depth; ++i)
    for (unsigned int j = 0; j < i; ++j) {
      double start = static_cast<double>(j)/static_cast<double>(i);
      double stop = static_cast<double>(j+1)/static_cast<double>(i);
      control_points.push_back(std::make_pair(start,stop));
    }

  for (unsigned int i = 0; i < trajectories.size(); ++i) {
    std::vector<double> dists;
    double length = tracktable::length(trajectories[i]);

    // Build the distances for all of the control points
    for (unsigned int j = 0; j < control_points.size(); ++j)
      dists.push_back(ControlPointDistance(trajectories[i],control_points[j]));

    // Normalize them all with respect to fraction of total length
    // If it is a zero length trajectory, in theory we could just ignore it
    // but this could cause some misalignment with the trajectory vector that
    // the user may want.  So, so just give it a default value.  Really, the
    // user should be filtering for zero length trajectories
    unsigned int cur = 0;
    for (unsigned int j = 1; j <= depth; ++j)
      for (unsigned int k = 0; k < j; ++k)
        if (length == 0.0)
          dists[cur++] = 1.0;  // Need a default behavior, either this or 0.0
        else
          dists[cur++] /= length/static_cast<double>(j);

    dgs.push_back(dists);
  }
  
  return;
}
#endif
