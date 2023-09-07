#!/usr/bin/env bash


### -------------------------------------------------------------------
### State variable initialization
###

# This is for use in all scripts -- unlike build_osx_wheels, we don't
# create a different directory name for each Python version
BUILD_DIRECTORY_NAME=build_macos
DEFAULT_PYTHON_VERSION=3.8

__COMMON_DEBUG_ENABLED=1
__COMMON_ERROR_ENABLED=1
__COMMON_INFO_ENABLED=1


# Construct the directory name for a particular Python version.
#
# This function is here so that we can just call it to get the 
# directory name instead of having to make sure we type the
# same thing everywhere.
#
# Arguments:
#    Argument 1: Python version (e.g. 3.5, 3.8)
#
# Variables Set:
#    build_directory_name_OUTPUT: requested directory name

function build_directory_name () {
	local python_version="$1"
	build_directory_name_OUTPUT="${BUILD_DIRECTORY_NAME}"
}


# Check for GNU Getopt, CMake, and Conda
#
# Arguments:
#     None.
#
# Return Value:
#     0 if all prerequisites found, 1 otherwise
function check_for_build_prerequisites () {
	local __ok=0

	# We need GNU Getopt to parse long arguments
	if ! check_for_program getopt; then
		echo "This script requires GNU getopt.  Please install it and try again."
		__ok=1
	fi

	if ! check_for_program cmake; then
		echo "Tracktable builds require CMake."
		__ok=1
	fi

	if ! check_for_program conda; then
		echo "Tracktable builds require Anaconda to be installed and active."
		__ok=1
	fi

	return ${__ok}
}


# Check to see if a specified command is on the user's PATH
# and is executable.
#
# This takes one argument (the program to check for).
#
# Returns:
#    0 if program found, 1 otherwise

function check_for_program () {
	local __program_to_find=$1
	msg_debug "Checking for program $1"
	echo "type of conda: $(type -t conda)"
	[[ -x "$(command -v ${__program_to_find})" ]]
}


# Delete the Tracktable build tree for a particular Python version.
#
# This function checks to see that the Python version is kosher and
# that the build directory actually exists.
#
# Arguments:
#     Argument #1: Python version (for example, 3.5)
#
# Returns:
#     0 on success, 1 on error

function delete_build_directory () {
	local __py_version="$1"
	local __dirname

	if ! parse_python_version ${__py_version}; then
		msg_error "delete_build_tree: Declining to delete build tree for malformed Python version ${__py_version}"
		return 1
	fi

	build_directory_name ${__py_version}
	__dirname=${build_directory_name_OUTPUT}

	local __full_build_path=${BUILD_ROOT}/${__dirname}

	if [[ ! -d ${__full_build_path} ]]; then
		msg_error "delete_build_directory: Directory ${__full_build_path} doesn't exist."
		return 1
	else
		rm -r ${__full_build_path}
	fi
}

# Delete the working directory where we keep our build trees.
#
# This function checks the global variable KEEP_BUILD_TREES to determine
# whether or not the user wants to keep the trees around.  If not,
# remove the work directory.
#
# Note: It is the responsibility of the build loop to clean up the tree
# for each individual build!
#
# Arguments:
#     None.
#
# Return value:
#     0 if rmdir succeeds or KEEP_BUILD_TREES is set, 1 if rmdir fails

function delete_workdir () {
	if [[ ${KEEP_BUILD_TREES} == 1 ]]; then
		exit 0
	else
		if [[ ! -z ${BUILD_ROOT+x} ]]; then
			if [[ ${BUILD_ROOT} != "unset" ]]; then
				msg_info "Removing work directory ${BUILD_ROOT}."
				rmdir ${BUILD_ROOT}
			fi
		else
			msg_error "Unexpected: BUILD_ROOT is not set in delete_workdir."
			exit 1
		fi
	fi
}


# Check to see if an array contains a certain value
#
# Usage:
#
# if element_in "value_to_find" "${myArray[@]}"
# then
#     do something;
# else
#     do something else;
# done
#
# Arguments:
#    Argument 1: value_to_find (quote as string)
#    Argument 2: array_to_search
#        NOTE: this must be quoted as "${array_to_search[@]}"
#
# Returns:
#    0 on success (element found), 1 otherwise

function element_in () {
	local element match="$1"
    shift
    for element
    do
    	[[ "$element" == "$match" ]] && return 0
    done
    return 1
}


### Clean up in case of ^C exit

function exit_cleanup () {
	msg_info "Cleaning up working files before exit."
	if [[ ! -z ${BUILD_ROOT+x} ]]; then
		delete_workdir
	else
		msg_info "Script had not yet created work directory - nothing to delete."
	fi
}

 
# Create the build directory for a specific Python version.
#
# Relies on BUILD_ROOT being set to provide the root path for all
# of our build trees.
#
# Arguments:
#    Argument 1: Python version for this build
#
# Returns:
#    0 on success, 1 otherwise.

function make_build_directory () {
	local python_version="$1"

	build_directory_name ${python_version}
	local __build_dir="${build_directory_name_OUTPUT}"
	mkdir ${BUILD_ROOT}/${__build_dir}
}


# Check to see if an associative array contains a certain key
#
# Usage:
#
# if map_has_key "value_to_find" name_of_map
# then
#     do something
# else
#     do something else
#
# Arguments:
#     Argument 1: (quoted) key value to search for
#     Argument 2: name of map to search
#
# Returns:
#     0 on success, 1 on failure
#
# Note:
#     Associative array to search is passed by name, NOT
#     by value.  Bash cannot currently pass associative
#     arrays by value.

function map_has_key () {
	local __value="$1"
	local -n __map_to_check="$2"

	[[ ${__map_to_check[${__value}]+abc} ]]
}



# Write an error message.  This will only produce output if the 
# variable ERROR is set to 1.
#
# No return values.

function msg_error() {
	if [[ "${__COMMON_ERROR_ENABLED}" == "1" ]] 
		then
			echo -e "[ERROR]: $*" >&2 
		fi
}

# Write a debug message.  This will only produce output if the 
# variable DEBUG is set to 1.
#
# No return values.

function msg_debug() {
	if [[ "${__COMMON_DEBUG_ENABLED}" == "1" ]] 
		then
			echo -e "[DEBUG]: $*" 
		fi
}

# Write an informational message.  This will only produce output
# if the variable INFO is set to 1.
#
# No return values.

function msg_info() {
	if [[ "${__COMMON_INFO_ENABLED}" == "1" ]] 
		then
			echo -e "[INFO]: $*"
		fi
}

# Enable/disable message streams.

function disable_debug_log() {
	__COMMON_DEBUG_ENABLED=0
}

function enable_debug_log() {
	__COMMON_DEBUG_ENABLED=1
}

function disable_error_log() {
	__COMMON_ERROR_ENABLED=0
}

function enable_error_log() {
	__COMMON_ERROR_ENABLED=1
}

function disable_info_log() {
	__COMMON_INFO_ENABLED=0
}

function enable_info_log() {
	__COMMON_INFO_ENABLED=1
}

# Parse a version string to make sure it's of the format <major>.<minor>,
# where <major> is a single digit and <minor> is an integer.  
#
# Arguments:
#    Argument 1: String to be parsed
#
# Returns:
#    1 on successful parse, 0 on error
#
# Output Variables:
#
# parse_python_version_OUTPUT_major_version: the part of the version string
#     before the decimal
# parse_python_version_OUTPUT_minor_version: the part of the version string
#     after the decimal
# Takes 1 argument (the string to be parsed and sets three variables:
#

function parse_python_version () {
	__python_version_string="$1"
	msg_debug "Trying to parse Python version ${__python_version_string}"
	if [[ ${__python_version_string} =~ ^([[:digit:]])\.([[:digit:]]+)$ ]]
	then
		parse_python_version_OUTPUT_major_version=${BASH_REMATCH[1]}
		parse_python_version_OUTPUT_minor_version=${BASH_REMATCH[2]}
		msg_debug "Success: detected version ${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
		return 0
	else
		msg_debug "Parse failed"
		parse_python_version_OUTPUT_major_version=unset
		parse_python_version_OUTPUT_minor_version=unset
		return 1
	fi
}

