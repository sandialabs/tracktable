/*
 * Copyright (c) 2014-2020 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
// KmlOut.h
//
// Created by Danny Rintoul.

#ifndef __KmlOut
#define __KmlOut
#include <iostream>
#include "Common.h"
#include "Portal.h"

void writeKmlHeader(std::ostream &outfile);

void writeKmlTrailer(std::ostream &outfile);

// void writeKmlFlight(const Ls &flight, std::ostream &outfile,
// const std::string &ColorString, const double &width);

void writeKmlFlight(trajectory_type &trajectory, std::ostream &outfile,
 const std::string &ColorString, const double &width);

void writeKmlFlights(Trajectories &trajectories,
 const std::string &file_name);

std::string getColorString(void);

void writeKmlPortals(std::list<PP> &portals, const std::string &file_name);
void writeKmlPortalPair(const Portal_pair &portals,
 const std::string &file_name);
void writeKmlPortalPairClipped(const Portal_pair &pp,
 const std::string &file_name);
void writeSingleKmlPortal(const PP &portal, std::ofstream &outfile);

#endif
