#ifndef  __curv_interpolation_h
#define  __curv_interpolation_h
#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>

typedef tracktable::domain::terrestrial::trajectory_point_type 
 trajectory_point_type;
typedef tracktable::domain::terrestrial::trajectory_type trajectory_type;

trajectory_point_type curve_interpolate(
 trajectory_type &point_list, double val, unsigned int level);

trajectory_point_type my_extrapolate(double val1, trajectory_point_type &p1, 
 double val2, trajectory_point_type &p2, double val);

void get_ordered_neighbors(const trajectory_type &traj, 
 std::vector<trajectory_point_type> &point_list, 
 double val, unsigned int level);
#endif
