#!/bin/bash

# This script will build OSX wheels for Tracktable from the currently 
# checked-out repository.  By default it will build for Python versions 
# 3.5, 3.6, 3.7, 3.8, and 3.9.  
#
# To request just one version, use the '--python-version 3.x' argument.  
# To set the output directory for wheels, use the '--output-directory /path' argument.
# To set the parent directory for the build, use the '--build-root /path' argument.

# TO DO:
# 
# Verify presence of cmake
# Verify presence of getopt
# Make temporary directory for build/install
# Make directory for wheel output
# Clean up build/install directory
# Write function to build for single version
# Check for existence of Conda build environments
# Create Conda build environments if necessary
# Check for initialized Anaconda environment
# Check CMake version
# Check Conda environment contents
#
# OUT OF SCOPE:
#
# I don't think we want to install Anaconda ourselves.


set -o pipefail
set -o nounset
set -o errexit


# Set these values to be 0 to inhibit categories of output
DEBUG=1
ERROR=1
INFO=1


### -------------------------------------------------------------------
### Utility functions
###


function _msg_error() {
	[[ "${ERROR}" == "1" ]] && echo -e "[ERROR]: $*"
}

function _msg_debug() {
	[[ "${DEBUG}" == "1" ]] && echo -e "[DEBUG]: $*" 
}

function _msg_info() {
	[[ "${INFO}" == "1" ]] && echo -e "[INFO]: $*"
}

function _check_for_program () {
	local __program_to_find=$1
	_msg_debug "Checking for program $1"
	if [ -x "$(command -v ${__program_to_find})" ]
		then
		 	_msg_debug "Program ${__program_to_find} found"
			_check_result="FOUND"
		else
			_msg_debug "Program ${__program_to_find} not found"
			_check_result="NOTFOUND"
	fi
}


### -------------------------------------------------------------------
### Setup - check for prerequisites
###

_check_for_program getopt
if [ "${_check_result}" == "NOTFOUND" ]; then
	echo "This script requires GNU getopt."
	exit 1
fi

_check_for_program cmake
if [ "${_check_result}" == "NOTFOUND" ]; then
	echo "This script requires CMake."
	exit 1
fi

_check_for_program conda
if [ "${_check_result}" == "NOTFOUND" ]; then
	echo "This script requires either Anaconda or Miniconda to be installed and active."
	exit 1
fi

_msg_info "All prerequisite utilities found."


### -------------------------------------------------------------------
### Parse command line options
### 
### This section sets the following variables:
###
### _tmpdir_root - Where to make our temporary directory
### _python_versions - Which versions of Python need Tracktable wheels?
### _wheel_directory - Where should the wheels go?

PARSED_ARGUMENTS=$(getopt -a -n alphabet \
	--options b:p:w: \
	--longoptions build-root:,python-version:,wheel-directory: \
	-- "$@"
	)

_msg_debug "Past PARSED_ARGUMENTS getopt call"

if [ $? != 0 ]
	then 
		echo "Failure while parsing command-line options.  Terminating."
		exit 2
fi

_msg_debug "Past exit test"

_msg_debug "Parsed arguments: ${PARSED_ARGUMENTS}"

eval set -- "$PARSED_ARGUMENTS"

_msg_debug "Past eval statement"

_build_tree_root=unset
_python_versions=unset
_wheel_directory=unset

while true; do
	case "$1" in
		-b | --build-root ) _build_tree_root="$2"; shift 2 ;;
		-p | --python-version ) if [ "${_python_versions}" == "unset" ]; 
								then _python_versions=("$2"); 
								else _python_versions+=("$2");
								fi; shift 2 ;;
		-w | --wheel-directory ) _wheel_directory="$2"; shift 2 ;; 
	-- ) shift; break ;;
	* ) break ;;
	esac
done

_msg_debug "Build tree root: ${_build_tree_root}"
_msg_debug "Python versions: ${_python_versions[*]}"
_msg_debug "Wheel directory: ${_wheel_directory}"

# # Set default values for anything that wasn't specified
# if [ "${_build_tree_root}" == "unset" ]
# then
# 	_msg_debug "Build tree root not supplied."
# 	if [ -z "${TMPDIR_x}" ]
# 	then
# 		_msg_debug "TMPDIR is not set.  Defaulting to /tmp."
# 		_build_tree_root=/tmp
# 	else
# 		_msg_debug "Defaulting to ${TMPDIR}."
# 		_build_tree_root=${TMPDIR}
# 	fi
# fi

# if [ "${_wheel_directory}" == "unset" ]
# then
# 	_msg_debug "Wheel output directory not set.  Defaulting to current directory."
# 	_wheel_directory=$(pwd)
# fi

# if [ "${#_python_versions[@]}" == "0" ]
# then
# 	_msg_debug "No Python versions requested.  Defaulting to 3.5 - 3.9."
# 	_python_versions=(py35 py36 py37 py38 py39)
# fi
