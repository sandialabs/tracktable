/*
 * Copyright (c) 2012-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//  ProgramOptions.cpp
//  GeoGraphy
//
//  Created by Ojas Parekh on 6/27/12.
//

#include "ProgramOptions.h"

// constants
std::string const ProgramOptions::USAGE_TITLE     = "Usage";        
std::string const ProgramOptions::HELP_SHORT_FLAG = "h";    
std::string const ProgramOptions::HELP_LONG_FLAG  = "help";
std::string const ProgramOptions::HELP_FULL_FLAG  = HELP_LONG_FLAG + "," 
 + HELP_SHORT_FLAG;
std::string const ProgramOptions::HELP_MESSAGE    = "Display usage information";

bool ProgramOptions::parseOptions(int argc, char * const argv[])
{
	bool retVal = true;
	
	try {
//	  po::store(po::parse_command_line(argc, argv, options_), variables_);
	  po::store(po::parse_command_line(argc, argv, options_), variables_);
	  po::notify(variables_);
	}
	catch (const boost::program_options::error& e) {
	  retVal = false;
	  std::cerr << "Options parsing error: " << e.what() << "." << std::endl;
	  std::cerr << options_;
	}
	
	// process help option
	if (hasValue(HELP_LONG_FLAG)) {
	  std::cout << options_;
	  retVal = false;
	}        
	return retVal;
}
