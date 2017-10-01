/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// AirDataRecord
//
// Supporting class for holding the flight data records we have as test data.
//
// Created by Danny Rintoul.
//

#ifndef __AirDataRecord
#define __AirDataRecord
#include "Common.h"

// First, our two kinds of coordinates.  Regular x-y (point_2d) and lat/lon
// (actually lon/lat is point_ll)

//typedef boost::geometry::model::segment<point_ll> segment_ll;

// Now, we have a class that is a point, but it also has a time stamp.

/*
class TimeStampedLatLon : public point_2d
{
  boost::posix_time::ptime time;
public:
  TimeStampedLatLon() {};
  TimeStampedLatLon(point_2d pt) : point_2d(pt) {};

  boost::posix_time::ptime get_time() const {return time;}
  int get_seconds_of_day() const {return time.time_of_day().total_seconds();}
  int get_minutes_of_day() const {return time.time_of_day().total_seconds()/60;}
  int get_seconds_of_week() const {return time.date().day_of_week().as_number()*86400 + time.time_of_day().total_seconds();}
  int get_minutes_of_week() const {return time.date().day_of_week().as_number()*1400 + time.time_of_day().total_seconds()/60;}
  int get_minutes_since(const boost::posix_time::ptime &t) const {return (time - t).total_seconds()/60;}
  const double get_longitude() const {return get<0>();}
  const double get_latitude() const {return get<1>();}
  void set_time(boost::posix_time::ptime &t) {time = t;}
  void set_longitude(const double &lon) {set<0>(lon);}
  void set_latitude(const double &lat) {set<1>(lat);}
};

// We register this homemade "point" type with Boost so that it will work
// with all of the boost point operations.

BOOST_GEOMETRY_REGISTER_POINT_2D_GET_SET(TimeStampedLatLon, double, cs::spherical_equatorial<boost::geometry::degree>, get_longitude, get_latitude, set_longitude, set_latitude)

// Okay.  Now, we derive a more complex point that has flight-like
// characteristics with things like altitude, heading and speed.

class FlightPoint : public TimeStampedLatLon
{
  std::string id;
  int altitude;
  int heading;
  int speed;

  double curvature;
  double avg_distance;
  double calc_distance;
  int calc_heading;
  double calc_speed;
public:

  FlightPoint() {};
  FlightPoint(TimeStampedLatLon tsp) : TimeStampedLatLon(tsp) {};
  FlightPoint(point_2d pt) : TimeStampedLatLon(pt) {};

  std::string get_id() const {return id;}
  std::string get_id_long() const {return id + "-" + 
    boost::gregorian::to_simple_string(get_time().date());}
  int get_altitude() const {return altitude;}
  int get_heading() const {return heading;}
  int get_speed() const {return speed;}

// Note:  curvature is defined as the difference of the incoming and outgoing 
// angles, divided by half the sum of the incoming and outgoing distances.

  double get_curvature() const {return curvature;}
  double get_avg_distance() const {return avg_distance;}
  double get_calc_distance() const {return calc_distance;}
  int get_calc_heading() const {return calc_heading;}
  double get_calc_speed() const {return calc_speed;}
  void set_id(const std::string &i) {id = i; return;}
  void set_altitude(const int &a) {altitude = a; return;}
  void set_heading(const int &h) {heading = h; return;}
  void set_speed(const int &s) {speed = s; return;}
  void set_curvature(const double &c) {curvature = c; return;}
  void set_avg_distance(const double &a) {avg_distance = a; return;}
  void set_calc_distance(const double &d) {calc_distance = d; return;}
  void set_calc_heading(const int &h) {calc_heading = h; return;}
  void set_calc_speed(const double &s) {calc_speed = s; return;}
  bool operator < (const FlightPoint& fp) const;
  void csvWrite(std::ostream& s);
};

// And we register it in boost also, so we can use it as a point.

BOOST_GEOMETRY_REGISTER_POINT_2D_GET_SET(FlightPoint, double, cs::spherical_equatorial<boost::geometry::degree>, get_longitude, get_latitude, set_longitude, set_latitude)

// We will use a boost linestring to hold a bunch of flight points, and we'll
// call it a Flight Trajectory.

typedef boost::geometry::model::linestring<FlightPoint> FlightTrajectory;

BOOST_GEOMETRY_REGISTER_LINESTRING(FlightTrajectory)

// Okay.  Everything so far has been pretty straightforward.  Now, we inherit
// from FlightTrajectory to make our flight.  The Flight has things in
// addition to the trajectory points, such as max values and characteristics
// of the points as a whole.  The difficult decision is whether or not to 
// make the class by making the FlightTrajectory a member, or whether to
// inherit FlightTrajectory.  It's more of an "is-a" relationship in my mind
// and it makes certain idioms simpler.  However, some folks consider the 
// inheritance of things like std::vector (that essentially what a linestring
// is) to be verboten.  You essentially lose their constructors, destructors
// and other things.  C11++ has nice ways of dealing with that, but our version
// does not.  

class Flight : public FlightTrajectory
{
  int max_altitude;
  double total_distance;
  double end_to_end_distance;
  int max_speed;
  boost::posix_time::ptime start_time;
  boost::posix_time::ptime end_time;
  std::string flight_id;
  double dsort_field;
public:

// Constructors, added as needed.

  Flight() {};
  Flight(FlightTrajectory ft) : FlightTrajectory(ft) {};

// Accessors...

  int get_max_altitude() const {return max_altitude;}
  int get_max_speed() const {return max_speed;}
  double get_total_distance() const {return total_distance;}
  double get_end_to_end_distance() const {return end_to_end_distance;}
  boost::posix_time::ptime get_start_time() const {return start_time;}
  boost::posix_time::ptime get_end_time() const {return end_time;}
  std::string get_flight_id() const {return flight_id;}
  std::string get_flight_id_long() const {return flight_id + "-" + 
    boost::gregorian::to_simple_string(start_time.date());}
  double get_dsort_field() const {return dsort_field;}
  void set_max_altitude(const int &a) {max_altitude = a; return;}
  void set_total_distance(const double &d) {total_distance = d; return;}
  void set_end_to_end_distance(const double &d) {end_to_end_distance = d; return;}
  void set_max_speed(const int &s) {max_speed = s; return;}
  void set_start_time(const boost::posix_time::ptime &t) 
   {start_time = t; return;}
  void set_end_time(const boost::posix_time::ptime &t) 
   {end_time = t; return;}
  void set_flight_id(const std::string &s) {flight_id = s; return;}
  void set_dsort_field(const double &d) {dsort_field = d; return;}

  void calculateFlightValues();
  int totalTurning();
  int totalWinding();
  void cleanFlight();
  void writecsvFlight(std::ostream &outfile);
  double longStraightFraction();
  bool isTailNumber();
  bool isDelta();
  bool idContains(const std::string& s_arg);
  int numTurnArounds();
};

BOOST_GEOMETRY_REGISTER_LINESTRING(Flight)

  // These typedefs exist not only to save space, but because, ultimately,
  // a "Flight" will be a more sophisticated data structure rather than
  // just a vector.


//typedef std::vector<Flight> Flights;
typedef std::list<Flight> Flights;
*/

bool timeSort(const Traj_Point &fp1, const Traj_Point &fp2);

bool sameFlight(const Traj_Point &fp1, const Traj_Point &fp2);

bool apartInTime(const Traj_Point &fp1, const Traj_Point &fp2);

bool badPoint(const Traj_Point &fp1, const Traj_Point &fp2);

#endif
