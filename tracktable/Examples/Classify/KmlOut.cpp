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


void writeKmlSepTrajectories(Trajectories &trajectories, const std::string &output_dir)
{
  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr) {
    std::string s = output_dir + itr->object_id() + "-" +
     boost::gregorian::to_simple_string(itr->start_time().date()) + ".kml";
    std::ofstream outfile(s.c_str());
    std::string color = getColorString();
    writeKmlTrajectory(*itr,outfile,color.c_str(),3.0);
    outfile.clear();
    outfile.close();
  }

  return;
}

  // The two routines below write out a KML file to an ostream that
  // you send it.  The first takes in a flight, the second just takes in
  // a linestring of points.  I *think* linestring derives from vector
  // or something like that, so it could possibly be done more generically.
  // Someone should look into that.  It uses the flight info for the name
  // in the KML file if it has it.  Otherwise, it uses a generic name.

void writeKmlTrajectory(trajectory_type &trajectory, 
 std::ostream &outfile, const std::string &ColorString, const double &width)
{
  writeKmlHeader(outfile);
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
  for (T_itr itr = trajectory.begin(); itr != trajectory.end(); ++itr) {
    outfile << "    " << itr->longitude() << "," << itr->latitude() <<
    std::endl;
  }
  outfile << "    </coordinates>" << std::endl;
  outfile << "  </LineString>" << std::endl;
  outfile << "</Placemark>" << std::endl;
  writeKmlTrailer(outfile);

  return;
}

void writeKmlTrajectories(Trajectories &trajectories, 
 const std::string &file_name)
{
  std::ofstream outfile(file_name.c_str());
  writeKmlHeader(outfile);
  double width = 3.0;
  std::string color("FFFFFFFF");

  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr) {
	  std::string style = itr->object_id();
	  std::string start_time =
	    boost::posix_time::to_iso_extended_string(itr->start_time());
	  std::string end_time =
	    boost::posix_time::to_iso_extended_string(itr->end_time());
//		std::string s = 
//    boost::gregorian::to_simple_string(itr->get_start_time().date());
	  outfile << "<Style id=\"" << style << "\">" << std::endl;
	  outfile << "  <LineStyle>" << std::endl;
	  outfile << "    <width>" << width << "</width>" << std::endl;
    color = getColorString();
	  outfile << "    <color>" << color << "</color>" << std::endl;
	  outfile << "  </LineStyle>" << std::endl;
	  outfile << "</Style>" << std::endl;
	  outfile << "<Placemark>" << std::endl;
	  outfile << "  <TimeSpan> <begin>" << start_time << "</begin>" << std::endl;
	  outfile << "             <end>" << end_time << "</end> </TimeSpan>" << 
	   std::endl;
	  outfile << "  <styleUrl>#" << style << "</styleUrl>" << std::endl;
	  outfile << "  <LineString>" << std::endl;
	  outfile << "    <coordinates>" << std::endl;
	  for (T_itr itr2 = itr->begin(); itr2 != itr->end(); ++itr2) {
	    outfile << "    " << itr2->longitude() << "," << itr2->latitude() << 
      std::endl;
    }
	  outfile << "    </coordinates>" << std::endl;
	  outfile << "  </LineString>" << std::endl;
	  outfile << "</Placemark>" << std::endl;
  }
  writeKmlTrailer(outfile);
  outfile.clear();
  outfile.close();

}
