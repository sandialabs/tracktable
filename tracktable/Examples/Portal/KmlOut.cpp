/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "KmlOut.h"
#include <boost/geometry/algorithms/length.hpp>

  // Gotta write the KML junk.  Could store this in a file somewhere,
  // but this reduces the associated files needed for compiling.

void writeKmlHeader(std::ostream& outfile)
{
  outfile << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" << std::endl;
  outfile << "<kml xmlns=\"http://www.opengis.net/kml/2.2\" ";
  outfile << "xmlns:gx=\"http://www.google.com/kml/ext/2.2\" ";
  outfile << "xmlns:kml=\"http://www.opengis.net/kml/2.2\">" << std::endl;
  outfile << "<Document>" << std::endl;

  return;
}

void writeKmlTrailer(std::ostream& outfile)
{
  outfile << "</Document>" << std::endl;
  outfile << "</kml>" << std::endl;

  return;
}

  // This does what it looks like.  The KML line that represents a flight
  // needs to be a color.  The writeKmlFlight requires you to specify a
  // color, and in lieu of making up a new one every time, you can grab
  // a random one with the routine below.  The rand() function is a bit
  // depricated, but this ain't rocket science.  Basically, you get a random
  // byte capital hex for R, G, and B, and then you get a full 255 for
  // the transparency.
  //
  // Be sure to seed the random number generator, or you'll get bored.

std::string getColorString(void)
{
  std::stringstream s;
  s << std::hex << std::setfill('0') << std::uppercase;
  // Stupid setw isn't sticky...
  s << "FF" << std::setw(2) << rand() % 255 << std::setw(2) 
   << rand() % 255 << std::setw(2) << rand() % 255;

  return s.str();
}

  // The two routines below write out a KML file to an ostream that
  // you send it.  The first takes in a flight, the second just takes in
  // a linestring of points.  I *think* linestring derives from vector
  // or something like that, so it could possibly be done more generically.
  // Someone should look into that.  It uses the flight info for the name
  // in the KML file if it has it.  Otherwise, it uses a generic name.

void writeKmlFlight(trajectory_type &trajectory, std::ostream &outfile,
 const std::string &ColorString, const double &width)
{
//  writeKmlHeader(outfile);
  std::string style = trajectory.object_id();
  std::string start_time =
    boost::posix_time::to_iso_extended_string(trajectory.start_time());
  std::string end_time =
    boost::posix_time::to_iso_extended_string(trajectory.end_time());
	std::string s = 
    boost::gregorian::to_simple_string(trajectory.start_time().date());
  outfile << "<Style id=\"" << style << "\">" << std::endl;
  outfile << "  <LineStyle>" << std::endl;
  outfile << "    <gx:labelVisibility>1</gx:labelVisibility>" << std::endl;
  outfile << "    <width>" << width << "</width>" << std::endl;
  outfile << "    <color>" << ColorString << "</color>" << std::endl;
  outfile << "  </LineStyle>" << std::endl;
  outfile << "</Style>" << std::endl;
  outfile << "<Placemark>" << std::endl;
  outfile << "  <name>" << style + "-" + s << "</name>" << std::endl;
  outfile << "  <TimeSpan> <begin>" << start_time << "</begin>" << std::endl;
  outfile << "             <end>" << end_time << "</end> </TimeSpan>" << 
   std::endl;
  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
  outfile << "  <LineString>" << std::endl;
  outfile << "    <coordinates>" << std::endl;
  for (T_itr itr = trajectory.begin();
   itr != trajectory.end(); ++itr)
    outfile << "    " << (*itr)[0] << "," << (*itr)[1] <<
     "," << itr->real_property("altitude")/3.3 << std::endl;
  outfile << "    </coordinates>" << std::endl;
  outfile << "  </LineString>" << std::endl;
  outfile << "</Placemark>" << std::endl;
//  writeKmlTrailer(outfile);

  return;
}

void writeKmlFlights(Trajectories &trajectories, const std::string &file_name)
{
  std::ofstream outfile(file_name.c_str());
  outfile.precision(15);
  writeKmlHeader(outfile);
  double width = 0.1;
  std::string color = getColorString();
//  std::string color("FFFFFFFF");

  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr) {
	  std::string style = itr->object_id();
	  std::string start_time =
	    boost::posix_time::to_iso_extended_string(itr->start_time());
	  std::string end_time =
	    boost::posix_time::to_iso_extended_string(itr->end_time());
		std::string s = 
	    boost::gregorian::to_simple_string(itr->start_time().date());
	  outfile << "<Style id=\"" << style << "\">" << std::endl;
	  outfile << "  <LineStyle>" << std::endl;
//	  outfile << "    <gx:labelVisibility>1</gx:labelVisibility>" << std::endl;
	  outfile << "    <width>" << width << "</width>" << std::endl;
//	  outfile << "    <color>" << getColorString() << "</color>" << std::endl;
	  outfile << "    <color>" << color << "</color>" << std::endl;
	  outfile << "  </LineStyle>" << std::endl;
	  outfile << "</Style>" << std::endl;
	  outfile << "<Placemark>" << std::endl;
//	  outfile << "  <name>" << style + "-" + s << "</name>" << std::endl;
	  outfile << "  <TimeSpan> <begin>" << start_time << "</begin>" << std::endl;
	  outfile << "             <end>" << end_time << "</end> </TimeSpan>" << 
	   std::endl;
	  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
	  outfile << "  <LineString>" << std::endl;
	  outfile << "    <coordinates>" << std::endl;
	  for (T_itr itr2 = itr->begin();
	   itr2 != itr->end(); ++itr2)
	    outfile << "    " << (*itr2)[0] << "," << (*itr2)[1] <<
	     "," << itr2->real_property("altitude")/3.3 << std::endl;
	  outfile << "    </coordinates>" << std::endl;
	  outfile << "  </LineString>" << std::endl;
	  outfile << "</Placemark>" << std::endl;
  }
  writeKmlTrailer(outfile);
  outfile.clear();
  outfile.close();

}
/*
void writeKmlFlight(const Ls &trajectory, std::ostream &outfile, 
 const std::string &ColorString, const double &width)
{
//  writeKmlHeader(outfile);
  std::string style = "Flight";
	std::string s = "Bounding Box";
  outfile << "<Style id=\"" << style << "\">" << std::endl;
  outfile << "  <LineStyle>" << std::endl;
  outfile << "    <gx:labelVisibility>1</gx:labelVisibility>" << std::endl;
  outfile << "    <width>" << width << "</width>" << std::endl;
  outfile << "    <color>" << ColorString << "</color>" << std::endl;
  outfile << "  </LineStyle>" << std::endl;
  outfile << "</Style>" << std::endl;
  outfile << "<Placemark>" << std::endl;
  outfile << "  <name>" << style + "-" + s << "</name>" << std::endl;
  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
  outfile << "  <LineString>" << std::endl;
  outfile << "    <coordinates>" << std::endl;
  for (Ls::const_iterator itr = trajectory.begin(); 
   itr != trajectory.end(); ++itr)
    outfile << "    " << itr->get<0>() << "," << itr->get<1>() <<
     "," <<  0.0  << std::endl;
  outfile << "    </coordinates>" << std::endl;
  outfile << "  </LineString>" << std::endl;
  outfile << "</Placemark>" << std::endl;
//  writeKmlTrailer(outfile);

  return;
}
*/
void writeKmlPortals(std::list<PP> &portals, const std::string &file_name)
{
  std::ofstream outfile(file_name.c_str());
  outfile.precision(15);
  writeKmlHeader(outfile);
//  double width = 3.0;
//  std::string color = getColorString();
//  std::string color("FFFFFFFF");

  for (pp_itr itr = portals.begin(); itr != portals.end(); ++itr) {
    writeSingleKmlPortal(*itr,outfile);
  }
  writeKmlTrailer(outfile);
  outfile.clear();
  outfile.close();

}

void writeKmlPortalPair(const Portal_pair &pp, const std::string &file_name)
{
  Trajectories trajectories;

  std::set<trajectory_type*>::iterator itr1 = pp.p1->trajectories.begin();
  std::set<trajectory_type*>::iterator itr2 = pp.p2->trajectories.begin();
  while (itr1 != pp.p1->trajectories.end() && itr2 != pp.p2->trajectories.end()) {
    if (*itr1 < *itr2) ++itr1;
    else if (*itr2 < *itr1) ++itr2;
    else {trajectories.push_back(**itr1); ++itr1; ++itr2;}
  }

  std::ofstream outfile(file_name.c_str());
  outfile.precision(15);
  writeKmlHeader(outfile);
  double width = 0.1;
  std::string color = getColorString();
//  std::string color("FFFFFFFF");

  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr) {
	  std::string style = itr->object_id();
	  std::string start_time =
	    boost::posix_time::to_iso_extended_string(itr->start_time());
	  std::string end_time =
	    boost::posix_time::to_iso_extended_string(itr->end_time());
		std::string s = 
	    boost::gregorian::to_simple_string(itr->start_time().date());
	  outfile << "<Style id=\"" << style << "\">" << std::endl;
	  outfile << "  <LineStyle>" << std::endl;
//	  outfile << "    <gx:labelVisibility>1</gx:labelVisibility>" << std::endl;
	  outfile << "    <width>" << width << "</width>" << std::endl;
//	  outfile << "    <color>" << getColorString() << "</color>" << std::endl;
	  outfile << "    <color>" << color << "</color>" << std::endl;
	  outfile << "  </LineStyle>" << std::endl;
	  outfile << "</Style>" << std::endl;
	  outfile << "<Placemark>" << std::endl;
//	  outfile << "  <name>" << style + "-" + s << "</name>" << std::endl;
	  outfile << "  <TimeSpan> <begin>" << start_time << "</begin>" << std::endl;
	  outfile << "             <end>" << end_time << "</end> </TimeSpan>" << 
	   std::endl;
	  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
	  outfile << "  <LineString>" << std::endl;
	  outfile << "    <coordinates>" << std::endl;
	  for (T_itr itr2 = itr->begin();
	   itr2 != itr->end(); ++itr2)
	    outfile << "    " << (*itr2)[0] << "," << (*itr2)[1] <<
	     "," << itr2->real_property("altitude")/3.3 << std::endl;
	  outfile << "    </coordinates>" << std::endl;
	  outfile << "  </LineString>" << std::endl;
	  outfile << "</Placemark>" << std::endl;
  }
  writeSingleKmlPortal(pp.p1,outfile);
  writeSingleKmlPortal(pp.p2,outfile);
  writeKmlTrailer(outfile);
  outfile.clear();
  outfile.close();
}

void writeKmlPortalPairClipped(const Portal_pair &pp, 
 const std::string &file_name)
{
  std::vector<trajectory_type> trajectories;

  std::set<trajectory_type*>::iterator itr1 = pp.p1->trajectories.begin();
  std::set<trajectory_type*>::iterator itr2 = pp.p2->trajectories.begin();
  while (itr1 != pp.p1->trajectories.end() && 
   itr2 != pp.p2->trajectories.end()) {
    if (*itr1 < *itr2) ++itr1;
    else if (*itr2 < *itr1) ++itr2;
    else { 
      trajectory_type::iterator first_pt, last_pt;
      GetTwoPortalSegment(pp,*itr1,first_pt,last_pt);
      trajectory_type clipped(first_pt,last_pt);

//      Ls clipped;
//      GetTwoBoxLS(pp,*itr1,clipped);
      if (!clipped.empty() &&
       (boost::geometry::length(clipped) <
       1.01*boost::geometry::distance(clipped.front(),clipped.back())))
        trajectories.push_back(clipped);
      ++itr1; ++itr2;
    }
  }

  std::ofstream outfile(file_name.c_str());
  outfile.precision(15);
  writeKmlHeader(outfile);
  double width = 0.1;
  std::string color = getColorString();
  std::string style = "LineString";
//  std::string color("FFFFFFFF");

  for (std::vector<trajectory_type>::iterator itr = trajectories.begin(); 
   itr != trajectories.end(); ++itr) {
	  outfile << "<Style id=\"" << style << "\">" << std::endl;
	  outfile << "  <LineStyle>" << std::endl;
//	  outfile << "    <gx:labelVisibility>1</gx:labelVisibility>" << std::endl;
	  outfile << "    <width>" << width << "</width>" << std::endl;
//	  outfile << "    <color>" << getColorString() << "</color>" << std::endl;
	  outfile << "    <color>" << color << "</color>" << std::endl;
	  outfile << "  </LineStyle>" << std::endl;
	  outfile << "</Style>" << std::endl;
	  outfile << "<Placemark>" << std::endl;
	  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
	  outfile << "  <LineString>" << std::endl;
	  outfile << "    <coordinates>" << std::endl;
	  for (trajectory_type::iterator itr2 = itr->begin();
	   itr2 != itr->end(); ++itr2)
	    outfile << "    " << itr2->get<0>() << "," << itr2->get<1>() <<
	     "," << 0.0 << std::endl;
	  outfile << "    </coordinates>" << std::endl;
	  outfile << "  </LineString>" << std::endl;
	  outfile << "</Placemark>" << std::endl;
  }
  writeSingleKmlPortal(pp.p1,outfile);
  writeSingleKmlPortal(pp.p2,outfile);
  writeKmlTrailer(outfile);
  outfile.clear();
  outfile.close();
}

void writeSingleKmlPortal(const PP &portal, std::ofstream &outfile)
{
  double width = 3.0;
//  std::string color = getColorString();
  std::string color("FFFFFFFF");

  std::string style = boost::lexical_cast<std::string>(portal->level);
  outfile << "<Style id=\"" << style << "\">" << std::endl;
  outfile << "  <LineStyle>" << std::endl;
//	  outfile << "    <gx:labelVisibility>1</gx:labelVisibility>" << std::endl;
  outfile << "    <width>" << width << "</width>" << std::endl;
//	  outfile << "    <color>" << getColorString() << "</color>" << std::endl;
  outfile << "    <color>" << color << "</color>" << std::endl;
  outfile << "  </LineStyle>" << std::endl;
  outfile << "</Style>" << std::endl;
  outfile << "<Placemark>" << std::endl;
  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
  outfile << "  <LineString>" << std::endl;
  outfile << "    <coordinates>" << std::endl;
   outfile << "    " << portal->min_corner().get<0>() << "," << portal->min_corner().get<1>() <<
     "," << 0.0 << std::endl;
   outfile << "    " << portal->min_corner().get<0>() << "," << portal->max_corner().get<1>() <<
     "," << 0.0 << std::endl;
   outfile << "    " << portal->max_corner().get<0>() << "," << portal->max_corner().get<1>() <<
     "," << 0.0 << std::endl;
   outfile << "    " << portal->max_corner().get<0>() << "," << portal->min_corner().get<1>() <<
     "," << 0.0 << std::endl;
   outfile << "    " << portal->min_corner().get<0>() << "," << portal->min_corner().get<1>() <<
     "," << 0.0 << std::endl;
  outfile << "    </coordinates>" << std::endl;
  outfile << "  </LineString>" << std::endl;
  outfile << "</Placemark>" << std::endl;

  return;
}
