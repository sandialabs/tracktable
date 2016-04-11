//
// AirDataRoutines
//
// Just reads in a file full of the air data records.  Doesn't do a 
// lot of error checking.  So far, the files have all had 17 columns
// as advertised. The problem is that some of the columns are empty.
//
// Created by Danny Rintoul.
// Copyright (c) 2013 Sandia Corporation.  All rights reserved.

#include "AirDataRoutines.h"
//#include <boost/geometry.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/geometry/algorithms/length.hpp>
#include <boost/geometry/strategies/spherical/distance_haversine.hpp>
#include <boost/geometry/algorithms/for_each.hpp>
#include <boost/bind.hpp>

int readAirDataFile(std::string &input_file, std::string& sep_char, 
 Flights& flights)
{
  Flight_map flight_map;

  std::ifstream in(input_file.c_str());
  if (!in.is_open()) return 1;

/*  const unsigned int id_col = 0;
  const unsigned int time_col = 1;
  const unsigned int lat_col = 12;
  const unsigned int lon_col = 13;
  const unsigned int alt_col = 14;
  const unsigned int spd_col = 15;
  const unsigned int hed_col = 16; */

  const unsigned int id_col = 0;
  const unsigned int time_col = 1;
  const unsigned int lat_col = 3;
  const unsigned int lon_col = 2;
  const unsigned int alt_col = 6;
  const unsigned int spd_col = 4;
  const unsigned int hed_col = 5;

  std::string line;

  while (std::getline(in,line))
  {
    if (line[0] == '#') continue;

    boost::char_separator<char> 
     sep(sep_char.c_str(),"",boost::keep_empty_tokens);
    boost::tokenizer<boost::char_separator<char> > tok(line,sep);
    std::vector<std::string> tok_vector(tok.begin(),tok.end());

    FlightPoint fp;

  // Fill the records.  Filling heterogeneous structures involves a
  // little ugliness at some point.  Here it is.  One has to also check
  // for empty strings and process them properly.  Do you want zeros, or do
  // you want to bail?  It depends on the situation.

    fp.set_id(tok_vector[id_col]);

  // If we don't have an update time, we can't really use it.

    if (tok_vector[time_col].empty()) continue;
    boost::algorithm::trim(tok_vector[time_col]);
    boost::posix_time::ptime time = 
     boost::posix_time::time_from_string(tok_vector[time_col]);
    fp.set_time(time);

  // Gotta have lat/lon.  And, for the sake of testing, we'll require
  // altitude, speed and heading.  Again, we can change that if we want, but
  // then we have to decided how to handle missing values.  In this case,
  // zeroes are probably not the right answer.

    if (tok_vector[lat_col].empty()) continue;
    double lat = boost::lexical_cast<double>(tok_vector[lat_col]);
    fp.set_latitude(lat);

    if (tok_vector[lon_col].empty()) continue;
    double lon = boost::lexical_cast<double>(tok_vector[lon_col]);
    fp.set_longitude(lon);


    if (tok_vector[alt_col].empty()) continue;
    int altitude = boost::lexical_cast<int>(tok_vector[alt_col]);
    fp.set_altitude(altitude);

  // Speed is a funny thing.  I have adapted the routine to store ints as
  // that is how the data is generally given in nm/hr.  But the following
  // line also allows us to read doubles.

    if (tok_vector[spd_col].empty()) continue;
    int speed = 
     static_cast<int>(boost::lexical_cast<double>(tok_vector[spd_col]));
    fp.set_speed(speed);

    if (tok_vector[hed_col].empty()) continue;
    int heading = boost::lexical_cast<int>(tok_vector[hed_col]);
    fp.set_heading(heading); 

    flight_map[fp.get_id()].push_back(fp);
  }

  // Turn the map into the flights format (vector of flights)
  separateMapFlights(flight_map,flights);

  return 0;
}

void separateMapFlights(Flight_map& flight_map, Flights& flights, 
 const int min_flight_size)
{

  // Take the vectors from the flight_map, separate them, and put them into
  // the fector of flights.

  Flight_map::iterator map_itr;

  for (map_itr = flight_map.begin(); map_itr != flight_map.end(); ++map_itr) {
  // Can technically remove next line if points start out time sorted...
    std::sort(map_itr->second.begin(),map_itr->second.end(),timeSort);
    separateFlights(map_itr->second,flights);
  }
  
  return;
}
void separateFlights(std::vector<FlightPoint> &fps, Flights &flights,
 const int min_flight_size)
{
  // Simple for loop to separate the individual flights.  There is an
  // awkwardness to doing this with a for loop that has to do with how
  // std::adjacent_find works.  Basically, when you hit the end, you still
  // have one more record to do, so a do-while is better.  The constant
  // in the pointer comparison is the minimum data points we need to define
  // a flight.

  Flight::iterator ptr1 = fps.begin();
  Flight::iterator ptr2;
  do {
    ptr2 = std::adjacent_find(ptr1,fps.end(),apartInTime);
    if (ptr2 != fps.end()) ++ptr2;
    if ((ptr2 - ptr1) >= min_flight_size)
      flights.push_back(Flight(FlightTrajectory(ptr1,ptr2)));
    ptr1 = ptr2;
  } while (ptr2 != fps.end());

  return;
}

  // Sometimes we want to write out a single file corresponding to a flight.
  // This allows us to take a particularly interesting flight (or one
  // that causes problems) and write it out for future use as an input file.
  // This routine currently has some hard-coded stuff in it that will
  // eventually have to go.

void writeKmlSepFlights(Flights &flights, const std::string &output_dir)
{
  for (Flights::iterator itr = flights.begin(); itr != flights.end(); ++itr) {
    std::string s = output_dir + itr->get_flight_id_long() + ".kml";
    std::ofstream outfile(s.c_str());
    std::string color = getColorString();
    writeKmlFlight(*itr,outfile,color.c_str(),6.0);
    outfile.clear();
    outfile.close();
  }

  return;
}
    
void writecsvFlights(Flights &flights, const std::string &output_dir)
{
  for (Flights::iterator itr = flights.begin(); itr != flights.end(); ++itr) {
    std::string s = output_dir + itr->begin()->get_id_long() + ".csv";
    std::ofstream outfile(s.c_str());
    itr->writecsvFlight(outfile);
    outfile.clear();
    outfile.close();
  }

  return;
}

  // Kind of silly to replace a one-line command with another, isn't it?
  // The reason this is here is that boost uses extremely convoluted 
  // "strategies" with its geometries that don't work in an obvious manner
  // with STL things and bind.  This encapsulates the distance command to
  // work fine with latlon points in STL commands.

double latLonDistance(const point_2d &x, const point_2d &y) 
{
  return boost::geometry::distance(x,y);
}

  // The following routine cleans up spurious data points based on the
  // badPoint routine in AirDataRecord.cpp.  It contains the definitions
  // on what makes something a bad point relative to its predecessor.
  // There is a weakness in this logic that if the first point has
  // problems, you'll be left with garbage or no points.
  //
  // Should the badPoints definition be in this file?  Maybe.

void cleanFlights(Flights &flights)
{
  for_each(flights.begin(),flights.end(),
   boost::bind(&Flight::cleanFlight,_1));

  // Sometimes, when flights get cleaned, they then get too short.  So
  // we remove the ones that are too short.

  flights.erase(std::remove_if(flights.begin(),flights.end(),
   boost::bind(std::less<int>(),boost::bind(&Flight::size,_1),10)),
   flights.end());

  return;
}
double distFromTrack(const point_2d &point, const ls_xy &track)
{
  return boost::geometry::distance(point,track);
}

int timeDiffSeconds(const boost::posix_time::ptime &t2,
 const boost::posix_time::ptime &t1)
{

  // Could just do this in-line, but my policy is that if it looks a little
  // messy, write a function.  It makes things easier in the main part of
  // the code.  Basically, my policy is bury your messes.

    boost::posix_time::time_duration delta = t2 - t1;
    return delta.total_seconds();
}

int timeDiffSeconds(const FlightPoint &fp2, const FlightPoint &fp1)
{
    boost::posix_time::time_duration delta = 
      fp2.get_time() - fp1.get_time();
    return delta.total_seconds();
}

int degreeHeading(const point_2d &p2, const point_2d &p1)
{

  // This is the formula for heading from true north from two lat/lon points.
  // It's interesting to work this out yourself, but the formula is also
  // well-known and oft-used.  It returns a heading between 0 and 360

    double lat1 = M_PI*p1.get<1>()/180.0;
    double lat2 = M_PI*p2.get<1>()/180.0;
    double lon1 = M_PI*p1.get<0>()/180.0;
    double lon2 = M_PI*p2.get<0>()/180.0;
    double dlon = lon2 - lon1;
    double y = sin(dlon)*cos(lat2);
    double x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dlon);
    return (int((atan2(y,x)*180.0/M_PI))+360)%360;
}

double radianHeading(const point_2d &p2, const point_2d &p1)
{

  // This is the formula for heading from true north from two lat/lon points.
  // It's interesting to work this out yourself, but the formula is also
  // well-known and oft-used.  It returns between -pi and pi.

    if ((p2.get<0>() == p1.get<0>()) && (p2.get<1>() == p1.get<1>()))
      return 0.0;

    double lat1 = M_PI*p1.get<1>()/180.0;
    double lat2 = M_PI*p2.get<1>()/180.0;
    double lon1 = M_PI*p1.get<0>()/180.0;
    double lon2 = M_PI*p2.get<0>()/180.0;
    double dlon = lon2 - lon1;
    double y = sin(dlon)*cos(lat2);
    double x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dlon);
    return atan2(y,x);
}

int headingDifference(const int h2, const int h1)
{

  // This gives the heading difference between two headings such that the
  // answer lies between -180 and 180.  And it's done without ugly if
  // statements.

  return (h2 - h1) - 360 * ((h2 - h1)/180);
}

int headingDifference(const FlightPoint &h2, const FlightPoint &h1)
{
  return headingDifference(h2.get_calc_heading(),h1.get_calc_heading());
}

void Flight::calculateFlightValues()
{
// Fills in the calculated distances.  The quantities between two points are
// // based on the heading/speed/distance between that point and the previous.
//
  if (this->size() < 2) return;

  Flight::iterator itr1 = this->begin(), itr2;

  for (itr2 = itr1+1; itr2 != this->end(); ++itr1, ++itr2) {
    itr2->set_calc_distance(latLonDistance(*itr1,*itr2));
    double time_delta = static_cast<double>(timeDiffSeconds(*itr2,*itr1));
    itr2->set_calc_speed(itr2->get_calc_distance()/time_delta);
    itr2->set_calc_heading(degreeHeading(*itr2,*itr1));
    if (itr1 != this->begin()) {
      itr1->set_avg_distance((itr1->get_calc_distance() + 
       itr2->get_calc_distance())/2.0);
      itr1->set_curvature((M_PI/180.0)*
       headingDifference(*itr2,*itr1)/(itr1->get_avg_distance()));
    }
  }
  this->front().set_curvature(0.0);
  this->back().set_curvature(0.0);
  this->front().set_avg_distance((this->begin()+1)->get_calc_distance()/2.0);
  this->back().set_avg_distance(this->back().get_calc_distance()/2.0);
  this->begin()->set_calc_speed((this->begin()+1)->get_calc_speed());
  this->begin()->set_calc_heading((this->begin()+1)->get_calc_heading());
  this->begin()->set_calc_distance(0.0);

  this->set_start_time(this->front().get_time());
  this->set_end_time(this->back().get_time());
  this->set_flight_id(this->front().get_id());
  this->set_end_to_end_distance(boost::geometry::distance(
   this->front(),this->back()));
  this->set_max_altitude(
   std::max_element(this->begin(),this->end(),boost::bind(
   &FlightPoint::get_altitude,_2) > 
   boost::bind(&FlightPoint::get_altitude,_1))->get_altitude());
  this->set_max_speed(
   static_cast<int>(std::max_element(this->begin(),this->end(),boost::bind(
   &FlightPoint::get_calc_speed,_2) > 
   boost::bind(&FlightPoint::get_calc_speed,_1))->get_calc_speed()));
  this->set_total_distance(boost::geometry::length(FlightTrajectory(*this)));

  return;
}

int Flight::totalTurning()
{

  // Unlike the winding calculation, this just sums up the absolute values
  // of the heading changes.  A perfectly straight flight would have a value
  // of 0.  Because of latlon imperfection, headings tend to have a
  // variability associated with them.  

  return std::inner_product(++this->begin(),this->end(),this->begin(),0,
   std::plus<int>(),boost::bind(abs,boost::bind(static_cast<int (*) 
   (const FlightPoint&, const FlightPoint&)>(headingDifference),_1,_2)));
}

int Flight::totalWinding()
{
  return std::inner_product(++this->begin(),this->end(),this->begin(),0,
   std::plus<int>(),boost::bind(static_cast<int (*) 
   (const FlightPoint&, const FlightPoint&)>(headingDifference),_1,_2));
}

void Flight::cleanFlight()
{
  this->erase(std::unique(this->begin(),this->end(),
   boost::bind(static_cast<bool(*) 
   (const FlightPoint &, const FlightPoint &)>(badPoint),_1,_2)),
   this->end());

  return;
}

void Flight::writecsvFlight(std::ostream &outfile)
{
  std::for_each(this->begin(),this->end(),
   boost::bind(&FlightPoint::csvWrite,_1,boost::ref(outfile)));

  return;
}

double Flight::longStraightFraction()
{
  int sum = 0;
  int min_straight_size = 8;
  Flight::iterator ptr1 = this->begin();
  Flight::iterator ptr2;
  do {
    ptr2 = std::adjacent_find(ptr1,this->end(),
     !boost::bind(std::less<int>(),
     boost::bind(abs,(boost::bind(static_cast<int(*)
     (const FlightPoint &, const FlightPoint &)>(headingDifference),_1,_2))),4));
    if (ptr2 != this->end()) ++ptr2;
    if ((ptr2 - ptr1) >= min_straight_size)
      sum += (ptr2 - ptr1);
    ptr1 = ptr2;
  } while (ptr2 != this->end());

  return static_cast<double>(sum)/static_cast<double>(this->size());
}

bool Flight::isTailNumber()
{
  std::string s = this->get_flight_id();
  if ((s[0] != 'N') || (s[1] < '0') || (s[1] > '9'))
    return false;

  return true;
}

bool Flight::isDelta()
{
  std::string s = this->get_flight_id();
  if ((s[0] != 'D') || (s[1] != 'A') || (s[2] != 'L'))
    return false;

  return true;
}

bool Flight::idContains(const std::string& s_arg)
{
  std::string s = this->get_flight_id();
  return s.find(s_arg) != std::string::npos;
}

int Flight::numTurnArounds()
{
  const int window = 5;
  double sum = 0.0;
  int ctr = 0;

  for (Flight::iterator itr = this->begin(); itr != this->begin()+window; ++itr)
    sum += itr->get_curvature()*itr->get_avg_distance();

  Flight::iterator itr1 = this->begin()+window;
  Flight::iterator itr2 = this->begin();

  do {
    if (((sum*(180/M_PI) > 178.0) && (sum*(180/M_PI) < 182.0)) ||
     ((sum*(180/M_PI) > -182.0) && (sum*(180/M_PI) < -178.0)))
      ctr++;
    sum += (itr1->get_curvature()*itr1->get_avg_distance() -
     itr2->get_curvature()*itr2->get_avg_distance());
    ++itr1; ++itr2;
  } while (itr1 != this->end());

  return ctr;
}

    // If we need all fields to have values...
    // if (std::find_if(tok.begin(),tok.end(),
    // boost::bind(&std::string::empty,_1)) != tok.end()) continue;

  // Okay.  Here is where the boost::posix_time routines are a lifesaver.  
  // They seem to correcly process all date/time info we get.  The following
  // try/catch routines also give the right behavior for empty strings.
  // Even better, by using the built-in "not_a_date_time" behavior, we can
  // design I/O for such that the program can input its own output.

/*    try {adr.sched_dep_time = boost::posix_time::time_from_string(*tok_itr++);}
      catch (...) { 
       adr.sched_dep_time = boost::posix_time::not_a_date_time;} */

