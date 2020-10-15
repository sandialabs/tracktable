/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 */

//
// GeoLifeIO
//
// Just reads in a file full of the GeoLife records.  Doesn't do a
// lot of error checking.
//
// Created by Danny Rintoul.

#include "GeoLifeIO.h"
#include <boost/algorithm/string.hpp>

int readGeoLifeFile(std::string &input_file, std::string& sep_char,
 Flights& flights)
{
  Flight_map flight_map;

  std::ifstream in(input_file.c_str());
  if (!in.is_open()) return 1;

  const unsigned int id_col = 0;
  const unsigned int time_col = 4;
  const unsigned int lat_col = 1;
  const unsigned int lon_col = 2;
  const unsigned int alt_col = 3;

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
    int altitude = static_cast<int>(boost::lexical_cast<double>(tok_vector[alt_col]));
    fp.set_altitude(altitude);

    flight_map[fp.get_id()].push_back(fp);
  }

  // Turn the map into the flights format (vector of flights)
  separateGeoLife(flight_map,flights);

  return 0;
}

void separateGeoLife(Flight_map& flight_map, Flights& flights)
{

  // Take the vectors from the flight_map, separate them, and put them into
  // the fector of flights.

  Flight_map::iterator map_itr;

  for (map_itr = flight_map.begin(); map_itr != flight_map.end(); ++map_itr) {
  // Can technically remove next line if points start out time sorted...
  // std::sort(map_itr->second.begin(),map_itr->second.end(),timeSort);
  //  separateFlights(map_itr->second,flights);
    flights.push_back(Flight(FlightTrajectory(map_itr->second.begin(),map_itr->second.end())));
  }

  return;
}
