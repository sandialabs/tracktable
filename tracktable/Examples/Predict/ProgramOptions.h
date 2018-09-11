/*
 * Copyright (c) 2012-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

//
//  ProgramOptions.h
//  GeoGraphy
//
//  Created by Ojas Parekh on 6/27/12.
//

#ifndef _ProgramOptions_h
#define _ProgramOptions_h

#include <iostream>
#include <string>

// Boost includes
#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/ShadowedDeclaration.h>
#include <boost/program_options.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

namespace po = boost::program_options;

// ProgramOptions is command line options-parsing wrapper class for 
// Boost's program_options module
class ProgramOptions
{
public:
	// initialization
	ProgramOptions():options_(USAGE_TITLE)
	{
	  // add help option

	  options_.add_options()(HELP_FULL_FLAG.c_str(), HELP_MESSAGE.c_str());
	}
	
	// public interface
	
	// add a switch (an option with no parameters)

	void addSwitch(std::string const & name, std::string const & description)
	{
	  options_.add_options()(name.c_str(), description.c_str());
	}
	
	// add an option without specifying a default value 
	// sample usage: addOption<int>("intflag", "this is an int parameter")

	template <typename ValueT>
	void addOption(std::string const & name, std::string const & description)
	{
	  options_.add_options()(name.c_str(), po::value<ValueT>(), 
     description.c_str());
	}

	// add an option with specifying a default value 
	// sample usage: addOption<int>("intflag", "this is an int parameter 
	// with default value 0", 0)

	template <typename ValueT>
	void addOption(std::string const & name, std::string const & description, 
   ValueT defaultValue)
	{
	  options_.add_options()(name.c_str(), 
     po::value<ValueT>()->default_value(defaultValue), description.c_str());
	}

	// get the parsed value for an option 
	// sample usage: getValue<int>("intflag")

	template <typename ValueT>
	ValueT getValue(std::string const & name) const
	{
	  return variables_[name].as<ValueT>();
	}
	
	// determines whether a given option was specified on the command line
	// sample usage: hasValue("intflag")

	bool hasValue(std::string const & optionName) const
	{
	  return variables_.count(optionName) > 0;
	}
	
	// prints usage information to a specified ostream

	void printUsage(std::ostream & stream) const
	{
	  stream << options_;
	}
	
	// performs the actual parsing of the command line
	// return: false iff the "help" flag was specified, 
	// in which case the help message will be printed

	bool parseOptions(int argc, char * const argv[]);
	
private:
	// private constants
	static std::string const USAGE_TITLE;
	static std::string const HELP_SHORT_FLAG;
	static std::string const HELP_LONG_FLAG;
	static std::string const HELP_FULL_FLAG;
	static std::string const HELP_MESSAGE;
	
	po::options_description options_;
	po::variables_map variables_;
};

#endif // _ProgramOptions_h
