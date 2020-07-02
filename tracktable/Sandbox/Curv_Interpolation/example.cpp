#include <string>
#include <iostream>
#include <sstream>
#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Core/Trajectory.h>
#include <tracktable/Core/TrajectoryPoint.h>
#include <tracktable/IO/PointReader.h>
#include <tracktable/Analysis/AssembleTrajectories.h>

#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <boost/bind.hpp>

#include "KmlOut.h"

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

void get_flight(std::string &s)
{
  s =
		"CHQ6369	2013-07-10 20:23:00	-84.1181	35.7786\n"
		"CHQ6369	2013-07-10 20:24:00	-84.2053	35.785\n"
		"CHQ6369	2013-07-10 20:25:00	-84.2922	35.7931\n"
		"CHQ6369	2013-07-10 20:26:00	-84.3894	35.8011\n"
		"CHQ6369	2013-07-10 20:27:00	-84.4844	35.8092\n"
		"CHQ6369	2013-07-10 20:28:00	-84.5867	35.815\n"
		"CHQ6369	2013-07-10 20:29:00	-84.6944	35.8231\n"
		"CHQ6369	2013-07-10 20:30:00	-84.8019	35.8369\n"
		"CHQ6369	2013-07-10 20:31:00	-84.9175	35.8508\n"
		"CHQ6369	2013-07-10 20:31:50	-85.0103	35.8431\n"
		"CHQ6369	2013-07-10 20:32:50	-85.1219	35.8186\n"
		"CHQ6369	2013-07-10 20:33:50	-85.2333	35.7961\n"
		"CHQ6369	2013-07-10 20:34:50	-85.3447	35.7736\n"
		"CHQ6369	2013-07-10 20:35:50	-85.4561	35.7511\n"
		"CHQ6369	2013-07-10 20:36:50	-85.5672	35.7283\n"
		"CHQ6369	2013-07-10 20:37:50	-85.6761	35.7053\n"
		"CHQ6369	2013-07-10 20:38:50	-85.7894	35.6867\n"
		"CHQ6369	2013-07-10 20:39:50	-85.9156	35.6725\n"
		"CHQ6369	2013-07-10 20:40:50	-86.0464	35.6625\n"
		"CHQ6369	2013-07-10 20:41:50	-86.1847	35.6589\n"
		"CHQ6369	2013-07-10 20:42:50	-86.3247	35.6656\n"
		"CHQ6369	2013-07-10 20:43:50	-86.4647	35.6803\n"
		"CHQ6369	2013-07-10 20:44:30	-86.4647	35.6803\n"
		"CHQ6369	2013-07-10 20:45:11	-86.635	35.7475\n"
		"CHQ6369	2013-07-10 20:45:50	-86.7108	35.7775\n"
		"CHQ6369	2013-07-10 20:47:15	-86.8592	35.8969\n"
		"CHQ6369	2013-07-10 20:48:17	-86.9622	35.9839\n"
		"CHQ6369	2013-07-10 20:48:50	-87.0256	36.0303\n"
		"CHQ6369	2013-07-10 20:49:19	-87.0661	36.0689\n"
		"CHQ6369	2013-07-10 20:49:50	-87.1325	36.1186\n"
		"CHQ6369	2013-07-10 20:50:21	-87.1919	36.1728\n"
		"CHQ6369	2013-07-10 20:50:50	-87.2444	36.2133\n"
		"CHQ6369	2013-07-10 20:51:23	-87.2956	36.2583\n"
		"CHQ6369	2013-07-10 20:51:50	-87.3492	36.2992\n"
		"CHQ6369	2013-07-10 20:52:25	-87.4	36.345\n"
		"CHQ6369	2013-07-10 20:53:27	-87.5003	36.4264\n"
		"CHQ6369	2013-07-10 20:53:50	-87.5469	36.4664\n"
		"CHQ6369	2013-07-10 20:54:50	-87.6342	36.5539\n"
		"CHQ6369	2013-07-10 20:55:50	-87.7244	36.6414\n"
		"CHQ6369	2013-07-10 20:56:50	-87.8022	36.7181\n"
		"CHQ6369	2013-07-10 20:57:35	-87.8706	36.7839\n"
		"CHQ6369	2013-07-10 20:57:50	-87.8878	36.7989\n"
		"CHQ6369	2013-07-10 20:58:37	-87.9553	36.8636\n"
		"CHQ6369	2013-07-10 20:58:50	-87.9733	36.8797\n"
		"CHQ6369	2013-07-10 20:59:50	-88.0542	36.9606\n"
		"CHQ6369	2013-07-10 21:00:50	-88.1425	37.0475\n"
		"CHQ6369	2013-07-10 21:01:50	-88.2364	37.1344\n"
		"CHQ6369	2013-07-10 21:02:50	-88.3306	37.2133\n"
		"CHQ6369	2013-07-10 21:03:50	-88.4275	37.2919\n"
		"CHQ6369	2013-07-10 21:04:13	-88.4275	37.2919\n"
		"CHQ6369	2013-07-10 21:04:50	-88.5206	37.3667\n"
		"CHQ6369	2013-07-10 21:05:52	-88.6103	37.4433\n"
		"CHQ6369	2013-07-10 21:07:56	-88.825	37.6217\n"
		"CHQ6369	2013-07-10 21:08:58	-88.9267	37.7058\n"
		"CHQ6369	2013-07-10 21:10:00	-89.0394	37.7858\n"
		"CHQ6369	2013-07-10 21:11:02	-89.1592	37.8717\n"
		"CHQ6369	2013-07-10 21:11:41	-89.1592	37.8717\n"
		"CHQ6369	2013-07-10 21:12:04	-89.2442	37.9819\n"
		"CHQ6369	2013-07-10 21:13:06	-89.2731	38.1056\n"
		"CHQ6369	2013-07-10 21:14:08	-89.3058	38.2378\n"
		"CHQ6369	2013-07-10 21:15:10	-89.3261	38.3636\n"
		"CHQ6369	2013-07-10 21:16:12	-89.3411	38.4906\n"
		"CHQ6369	2013-07-10 21:17:14	-89.3658	38.6264\n"
		"CHQ6369	2013-07-10 21:18:16	-89.3889	38.7525\n"
		"CHQ6369	2013-07-10 21:19:18	-89.4133	38.8875\n"
		"CHQ6369	2013-07-10 21:20:20	-89.4353	39.0133\n"
		"CHQ6369	2013-07-10 21:21:22	-89.4578	39.1489\n"
		"CHQ6369	2013-07-10 21:21:42	-89.4667	39.1767\n"
		"CHQ6369	2013-07-10 21:22:24	-89.4811	39.2806\n"
		"CHQ6369	2013-07-10 21:22:44	-89.4889	39.3033\n"
		"CHQ6369	2013-07-10 21:23:46	-89.5128	39.4294\n"
		"CHQ6369	2013-07-10 21:24:48	-89.5414	39.5808\n"
		"CHQ6369	2013-07-10 21:25:50	-89.5647	39.7078\n"
		"CHQ6369	2013-07-10 21:26:52	-89.5919	39.8347\n"
		"CHQ6369	2013-07-10 21:27:35	-89.6064	39.9097\n"
		"CHQ6369	2013-07-10 21:27:54	-89.6189	39.9614\n"
		"CHQ6369	2013-07-10 21:28:37	-89.6422	40.0611\n"
		"CHQ6369	2013-07-10 21:29:13	-89.6483	40.0867\n"
		"CHQ6369	2013-07-10 21:29:36	-89.6756	40.1872\n"
		"CHQ6369	2013-07-10 21:29:58	-89.6842	40.2114\n"
		"CHQ6369	2013-07-10 21:30:41	-89.6558	40.3136\n"
		"CHQ6369	2013-07-10 21:31:00	-89.6286	40.3594\n"
		"CHQ6369	2013-07-10 21:31:43	-89.5856	40.4311\n"
		"CHQ6369	2013-07-10 21:32:02	-89.5642	40.4703\n"
		"CHQ6369	2013-07-10 21:32:45	-89.5119	40.5522\n"
		"CHQ6369	2013-07-10 21:33:04	-89.4822	40.6008\n"
		"CHQ6369	2013-07-10 21:34:06	-89.4092	40.7231\n"
		"CHQ6369	2013-07-10 21:35:08	-89.3342	40.8458\n"
		"CHQ6369	2013-07-10 21:36:10	-89.2458	40.9936\n"
		"CHQ6369	2013-07-10 21:37:12	-89.1767	41.1094\n"
		"CHQ6369	2013-07-10 21:38:14	-89.1039	41.235\n"
		"CHQ6369	2013-07-10 21:39:16	-89.0364	41.3592\n"
		"CHQ6369	2013-07-10 21:40:18	-88.9522	41.5128\n"
		"CHQ6369	2013-07-10 21:41:20	-88.8861	41.6419\n"
		"CHQ6369	2013-07-10 21:42:22	-88.8186	41.7697\n"
		"CHQ6369	2013-07-10 21:43:24	-88.7547	41.8967\n"
		"CHQ6369	2013-07-10 21:44:01	-88.7547	41.8967\n"
		"CHQ6369	2013-07-10 21:44:26	-88.6922	42.0194\n"
		"CHQ6369	2013-07-10 21:45:31	-88.6028	42.1325\n"
		"CHQ6369	2013-07-10 21:46:31	-88.4878	42.2644\n"
		"CHQ6369	2013-07-10 21:47:33	-88.3861	42.3572\n"
		"CHQ6369	2013-07-10 21:48:35	-88.2578	42.4406\n"
		"CHQ6369	2013-07-10 21:49:37	-88.1122	42.5339\n"
		"CHQ6369	2013-07-10 21:50:39	-87.9872	42.6164\n"
		"CHQ6369	2013-07-10 21:51:12	-87.9872	42.6164\n"
		"CHQ6369	2013-07-10 21:51:41	-87.8683	42.7089\n"
		"CHQ6369	2013-07-10 21:52:43	-87.7433	42.8044\n"
		"CHQ6369	2013-07-10 21:53:45	-87.6369	42.9058\n"
		"CHQ6369	2013-07-10 21:54:47	-87.5572	43.0342\n"
		"CHQ6369	2013-07-10 21:55:49	-87.4928	43.1425\n"
		"CHQ6369	2013-07-10 21:56:51	-87.3919	43.2411\n"
		"CHQ6369	2013-07-10 21:57:53	-87.2283	43.2811\n"
		"CHQ6369	2013-07-10 21:58:54	-87.0472	43.3003\n"
		"CHQ6369	2013-07-10 21:59:57	-86.8281	43.3214\n"
		"CHQ6369	2013-07-10 22:00:59	-86.6439	43.3469\n"
		"CHQ6369	2013-07-10 22:02:01	-86.4611	43.3739\n"
		"CHQ6369	2013-07-10 22:02:55	-86.4611	43.3739\n"
		"CHQ6369	2013-07-10 22:04:04	-86.0939	43.4225\n"
		"CHQ6369	2013-07-10 22:05:06	-85.9178	43.3792\n"
		"CHQ6369	2013-07-10 22:06:08	-85.7583	43.3314\n"
		"CHQ6369	2013-07-10 22:07:10	-85.6056	43.2839\n"
		"CHQ6369	2013-07-10 22:08:12	-85.45	43.2378\n"
		"CHQ6369	2013-07-10 22:08:36	-85.37	43.2175\n"
		"CHQ6369	2013-07-10 22:09:36	-85.1906	43.1811\n"
		"CHQ6369	2013-07-10 22:10:36	-85.0169	43.1461\n"
		"CHQ6369	2013-07-10 22:11:18	-84.8844	43.1256\n"
		"CHQ6369	2013-07-10 22:11:36	-84.8411	43.1153\n"
		"CHQ6369	2013-07-10 22:12:36	-84.6686	43.0881\n"
		"CHQ6369	2013-07-10 22:13:22	-84.5442	43.075\n"
		"CHQ6369	2013-07-10 22:13:36	-84.505	43.0647\n"
		"CHQ6369	2013-07-10 22:14:36	-84.3506	43.0469\n"
		"CHQ6369	2013-07-10 22:15:09	-84.3506	43.0469\n"
		"CHQ6369	2013-07-10 22:15:25	-84.2378	43.0333\n"
		"CHQ6369	2013-07-10 22:16:27	-84.0756	42.9769\n"
		"CHQ6369	2013-07-10 22:17:36	-83.9336	42.9056\n"
		"CHQ6369	2013-07-10 22:18:07	-83.8611	42.8722\n"
		"CHQ6369	2013-07-10 22:19:07	-83.7583	42.8\n"
		"CHQ6369	2013-07-10 22:19:36	-83.7089	42.7742\n"
		"CHQ6369	2013-07-10 22:20:08	-83.6519	42.7675\n"
		"CHQ6369	2013-07-10 22:21:09	-83.6286	42.6972\n"
		"CHQ6369	2013-07-10 22:21:36	-83.6325	42.6617\n"
		"CHQ6369	2013-07-10 22:22:10	-83.6083	42.6247\n"
		"CHQ6369	2013-07-10 22:22:36	-83.5708	42.6111\n"
		"CHQ6369	2013-07-10 22:23:17	-83.5081	42.5939\n"
		"CHQ6369	2013-07-10 22:23:36	-83.4794	42.5842\n"
		"CHQ6369	2013-07-10 22:24:18	-83.4164	42.565\n"
		"CHQ6369	2013-07-10 22:24:36	-83.3906	42.5553\n"
		"CHQ6369	2013-07-10 22:25:36	-83.3322	42.5086\n"
		"CHQ6369	2013-07-10 22:26:21	-83.3106	42.4611\n"
		"CHQ6369	2013-07-10 22:27:27	-83.2961	42.3864\n"
		"CHQ6369	2013-07-10 22:27:51	-83.2961	42.3864\n"
		"CHQ6369	2013-07-10 22:28:22	-83.2967	42.3344\n"
		"CHQ6369	2013-07-10 22:29:17	-83.3197	42.2881\n"
		"CHQ6369	2013-07-10 22:30:18	-83.3492	42.2497\n";

  return;
}

int main()
{ 

  boost::log::core::get()->set_filter(
   boost::log::trivial::severity >= boost::log::trivial::error);

  // Read in the flight from the data file above.  This is just a way to
  // mimic reading it off of disk

  std::string s;
  get_flight(s);
  std::istringstream infile(s);

  typedef tracktable::PointReader<trajectory_point_type> point_reader_type;
  typedef tracktable::AssembleTrajectories<trajectory_type, 
   typename point_reader_type::iterator> assembler_type;

  point_reader_type point_reader;
  point_reader.set_input(infile);
  point_reader.set_field_delimiter("\t");
  assembler_type trajectory_assembler(point_reader.begin(), point_reader.end());

  // Grab the first (and only) flight

  trajectory_type traj = *trajectory_assembler.begin();

  // Grab 4 points from the middle of it as an example

  trajectory_type small_traj(traj.begin()+137,traj.begin()+141);

  // We need somewhere to keep the temporary points

  trajectory_type temp;

  // Go through, distance-wise, from 10% before the first point to 110%
  // after the last, demonstrating both interpolation and extrapolation.
  //
  // We'll put these into a new trajectory, and because of the way we are
  // doing it, they will be in the right order (otherwise, we have to sort
  // by time).  We just have to do the compute_current_length calculation to
  // make sure it is a legitimate trajectory, even though we don't use it.
  // I'd hate to see someone copy this code and then need it.

  for (int i = -10; i < 110; ++i) {
    double val = i*(small_traj.back().current_length())/100.0;
    temp.insert(temp.end(),curve_interpolate(small_traj,val,4));
  }
  temp.compute_current_length(0);

  std::ofstream outfile("New_CHQ.kml");
  writeKmlTrajectory(temp,outfile,"FFFF55FF",4.0);
  outfile.clear();
  outfile.close();

  return 0;
}

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

