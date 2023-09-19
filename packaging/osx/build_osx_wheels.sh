#!/usr/bin/env bash

# This script will build OSX wheels for Tracktable from the currently 
# checked-out repository.  By default it will build for Python versions 
# 3.5, 3.6, 3.7, 3.8, and 3.9.  
#
# To request just one version, use the '--python-version 3.x' argument.  
# To set the output directory for wheels, use the '--output-directory /path' argument.
# To set the parent directory for the build, use the '--build-root /path' argument.

### -------------------------------------------------------------------
###
### ORGANIZATION
###
### 1. To-Do List
### 2. Bash Configuration (exit on errors)
### 3. State Variable Initialization
### 4. Useful Functions
### 5. Program Logic
###
### -------------------------------------------------------------------

# TO DO:
# 
# Check CMake version
# Check Conda environment contents
# Copy wheel to output directory
# Add command-line option for build version (e.g. 1.4.1-2)
#
# Package up default-setting into a function


# OUT OF SCOPE:
#
# I don't think we want to install Anaconda ourselves.


### -------------------------------------------------------------------
### Bash configuration
###
### These are the error conditions we want to treat as fatal.

# Exit if any command in a pipe fails
set -o pipefail

# Exit when we try to use an undeclared variable
set -o nounset

# Exit when a command fails
set -o errexit

# Enable trace output
#set -x

# We need to run Conda functions with debugging off because there are some
# bugs in their own scripts that we can't reach from here.

function disable_debug () {
	set +o pipefail
	set +o nounset
}

function enable_debug () { 
	set -o pipefail
	set -o nounset
}

### -------------------------------------------------------------------
### State variable initialization
###

# Set these values to be 0 to inhibit categories of output
DEBUG=1
ERROR=1
INFO=1

# These will keep track of what we're building and where.
WORKDIR_LOCATION=unset
PYTHON_VERSIONS=unset
WHEEL_DIRECTORY=unset
KEEP_BUILD_TREES=unset
PARALLEL_JOBS=unset

# We will need these other variables.

# Actual temporary directory that we create under WORKDIR_LOCATION
BUILD_ROOT=unset

# Where is the source code to build?
SOURCE_DIRECTORY=unset


### -------------------------------------------------------------------
### Useful functions
###

function usage() {
	cat <<EOF
usage: build_osx_wheels.sh [--python-version X.Y] [--build-root <dir>] [--wheel-directory <dir>] path_to_source

Build Tracktable wheels for the specified Python versions.

Required Arguments:

    path_to_source: Directory that contains the Tracktable source to
        build.  This is the directory that contains the top-level
        CMakeLists.txt and RELEASE_NOTES.md.

Options:
    -p,--python-version X.Y: Build for Python version X.Y.  This can be 
        specified multiple times to build for multiple versions.  By
        default, wheels will be built for Python 3.5, 3.6, 3.7, 3.8,
        and 3.9.

    -b,--build-root <path>: Build trees will be created under the
        specified directory.  This defaults to the value of the
        environment variable TMPDIR, which is often /tmp on Unix-like
        systems.  This directory needs to have about 1 gigabyte free
        for each version of Python in the build list.  

        Note that the build trees will be collected in a temporary
        subdirectory of the build root named 'tracktable-build.XXXXXX'
        where XXXXXX will be replaced with a random string.

    -w,--wheel-directory <path>: Generated wheels will be written
        into this directory.  Defaults to the current directory.

    -k,--keep-build-trees: Do not delete the Tracktable build trees after
        we're done.  This option is for debugging.

    -j,--parallel <jobs>: Run <jobs> parallel build jobs.  The default
        is controlled by the native build tool.  For GNU Make, the default
        is one.  

Notes:
    At present, this script does not allow the specification of patch 
    levels for Python versions (e.g. 3.8.2), only major and minor versions.  
    It also does not check whether requested Python versions actually exist 
    until build time.

    This script will be enhanced to allow specification of a post-build
    number (for example, 5 in 'tracktable-1.2.3-5') for multiple releases
    of the same version.
EOF
}


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
	build_directory_name_OUTPUT="tt-python${python_version}"
}


# Activate a Conda virtual environment for a given Python version.
#
# This uses conda_environment_name to get the name of the environment
# we want.
#
# Arguments:
#     Argument 1: Python version (for example, 3.5)
#
# Returns:
#     0 on success, 1 on error

function activate_conda_environment () {
	local __python_version="$1"
	local __envname

	conda_environment_name ${__python_version}
	__envname=${conda_environment_name_OUTPUT}

	msg_debug "Activating Conda environment ${__envname}"

	disable_debug;
	conda activate ${__envname}
	enable_debug;
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
	[[ -x "$(command -v ${__program_to_find})" ]]
}


# Run CMake to configure the TT build for a specific Python version.
#
# Arguments:
#    $1: Path to build directory
#    $2: Path to source code
#	 $3: Path to Conda environment for this build
#
# Returns:
#    0 on success, 1 on failure

function cmake_configure () {
	local __build_directory="$1"
	local __src_directory="$2"
	local __conda_env_path="$3"

	cmake \
		-B ${__build_directory} \
		-DBOOST_ROOT:PATH=${__conda_env_path} \
		-DCMAKE_BUILD_TYPE:STRING=Release \
		-DCMAKE_INSTALL_PREFIX:PATH=${__build_directory}/install \
		-DPython3_EXECUTABLE:FILEPATH=${__conda_env_path}/bin/python \
		-DPython3_ROOT_DIR:PATH=${__conda_env_path} \
		${__src_directory}
}


# Have CMake invoke 'make wheel'.
#
# This calls CMake to invoke the build target since we might not always
# be using GNU make.  
#
# Arguments:
#     $1: Build directory
#
# Returns:
#     0 on success, 1 on error

function cmake_build_wheel () {
	local __build_directory="$1"

	cmake --build ${__build_directory} --target wheel
}


# Go forth and build!
#
# This calls CMake to invoke the build instead of running the build tool
# directly since we might not always be using GNU make.
#
# Arguments:
#     $1: Build directory
#
# Returns:
#     0 on success, 1 on error
#
# Note:
#     This function can be parameterized to include parallelization options
#     for build tools that support it.  

function cmake_run_build () {
	local __build_directory="$1"

	if [[ ${PARALLEL_JOBS} == "unset" ]]; then
		cmake --build ${__build_directory}
	else
		cmake --build ${__build_directory} --parallel ${PARALLEL_JOBS}
	fi
}


# Install after building.
#
# This calls CMake to invoke the install step instead of running the build tool
# directly since we might not always be using GNU make.  According to CMake's
# documentation, this might not even use the underlying build tool directly.
#
# Arguments:
#     $1: Build directory
#
# Returns:
#     0 on success, 1 on error

function cmake_run_install () {
	local __build_directory="$1"

	cmake --install ${__build_directory}
}

# Make the Conda build environment name for a Python version.
#
# Like build_directory_name, this is here for consistency.
#
# Arguments:
#     Argument 1: Python version (for example, 3.5)
#
# Output Variables:
#     conda_environment_name_OUTPUT: String name of environment

function conda_environment_name () {
	local __py_version="$1"
    conda_environment_name_OUTPUT="tracktable-build-python${__py_version}"
    return 0
}

# Check to see if a Conda environment exists for a Python version.
#
# Arguments:
#    Argument 1: Python version (for example, 3.5)
#    Argument 2: Name of associative array of Conda environments (retrieve
#        with list_conda_environments)
#
# Return Value:
#    0 if environment exists, 1 otherwise
#
# NOTE:
#    Bash can't pass associative arrays by value, only by reference.  This
#    is why you must supply the NAME of the array.

function conda_environment_exists () {
	local __python_version="$1"
	
	msg_debug "Checking for Conda environment for Python ${__python_version}"

	conda_environment_name ${__python_version}
	local __envname="${conda_environment_name_OUTPUT}"

	if map_has_key "${__envname}" "$2"; then
		msg_debug "Environment found: ${__envname}"
		return 0
	else
		msg_debug "Environment not found: ${__envname}"
		return 1
	fi
}


# Copy a finished wheel from a build directory to some output directory.
#
# This will actually grab all the wheels from that directory.  Because of
# the way we've set up the rest of the build, there should only be one.
#
# Arguments:
#     $1: build directory (wheel is in $1/wheel/*.whl)
#     $2: destination directory
#
# Returns:
#     0 on success, 1 on failure 

function copy_wheel_to_output () {
	local __build_directory="$1"
	local __output_directory="$2"

	cp ${__build_directory}/wheel/*.whl ${__output_directory}
}


# Create a Conda virtual environment for a given Python version.
#
# Arguments:
#     Argument 1: Python version (for example, 3.5)
#
# Return Value:
#     1 on success, 0 on failure
#
# NOTE: 
#     This function could be enhanced to parameterize on Boost
#     version as well. 
#
# NOTE:
#     Channel names and package contents are hard-coded.  Further
#     work will be needed to use different channels, contents, or
#     Nexus proxies.
#
# NOTE:
#     Package contents are currently specific to MacOS.

function create_conda_environment () {
	local __python_version=$1
	local __envname
	
	conda_environment_name ${__python_version}
	__envname=${conda_environment_name_OUTPUT}

	msg_info "Creating Conda build environment ${__envname}"
	conda create \
		--name ${__envname} \
		--yes \
		--channel conda-forge \
		python=${__python_version} \
		boost \
		cartopy \
		doxygen \
		folium \
		graphviz \
		jupyter \
		numpy \
		pip \
		pytz \
		sphinx \
		sphinx_rtd_theme

	# Refresh the list of environments -- we just added one
	list_conda_environments;

	if [[ "$?" != 0 ]]; then
		msg_error "Failed to create Conda environment ${__envname} -- cannot continue."
		exit 6
	fi

	if ! activate_conda_environment ${__python_version}; then
		msg_error "Failed to activate Conda environment ${__envname} -- cannot continue."
		exit 6
	fi

	# These utilities aren't in conda main or conda-forge
	pip install \
		delocate \
		breathe
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


# Enable Anaconda commands in the current shell
#
# Conda relies on a few shell variables and functions being set
# in the shell.  This script, running in a non-interactive shell,
# does not get those by default.  This function should fix that.
#
# Arguments:
#     None.
#
# Return Value:
#     0 on success, 1 on error.

function enable_anaconda () {
	msg_info "Enabling Anaconda commands."
	export PS1=
	disable_debug;
	eval "$(command conda 'shell.bash' 'hook' 2>/dev/null)"
	enable_debug;
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


# Retrieve the path containing the Conda environment for a given 
# Python version
#
# Arguments:
#     $1: Python version (for example, 3.5)
#
# Returns:
#     0 if the environment exists, 1 otherwise
#
# Output Variables: 
#     find_conda_environment_path_OUTPUT: Path to environment
#
# Global Variables:
#     Uses list_conda_environments_OUTPUT.

function find_conda_environment_path ()
{
	local __py_version="$1"
	local __env_name

	unset find_conda_environment_path_OUTPUT

	conda_environment_name ${__py_version}
	__env_name=${conda_environment_name_OUTPUT}

	if ! map_has_key ${__env_name} list_conda_environments_OUTPUT; then
		msg_error "find_conda_environment_path: Environment ${__env_name} not in map!"
		return 1
	else
		find_conda_environment_path_OUTPUT="${list_conda_environments_OUTPUT[${__env_name}]}"
		msg_debug "find_conda_environment_path: Environment ${__env_name} is at ${find_conda_environment_path_OUTPUT}"
		return 0
	fi
}


# Retrieve a list of the Anaconda environments visible to the user by
# running the command 'conda env list'.
#
# Arguments:
#     No arguments.
#
# Variables Set:
#     list_conda_environments_OUTPUT: Associative array
#         mapping environment names to paths on disk
#
# TODO: Possible bug: This function should clear the output array
# every time it runs

function list_conda_environments () {
	msg_info "Retrieving list of Anaconda environments."
    declare -gA list_conda_environments_OUTPUT
	local __env_regex="^([a-zA-Z0-9._-]+)[ *]+(\/.+)\$"
	while IFS= read -r __line; do
		#msg_debug "Processing line ${__line}"
		if [[ ${__line} =~ ${__env_regex} ]]
			then
				local __env_name="${BASH_REMATCH[1]}"
				local __env_path="${BASH_REMATCH[2]}"
				#msg_debug "Found Conda environment '${__env_name}' at '${__env_path}'"
				#list_conda_environments_OUTPUT["${__env_name}"]="${__env_path}"
				list_conda_environments_OUTPUT["${BASH_REMATCH[1]}"]+="${BASH_REMATCH[2]}"
			else
				msg_debug "Line didn't match"
			fi
		done < <( \
		conda env list \
		| grep -v \# \
		)
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
	[[ "${ERROR}" == "1" ]] && echo -e "[ERROR]: $*" >&2 
}

# Write a debug message.  This will only produce output if the 
# variable DEBUG is set to 1.
#
# No return values.

function msg_debug() {
	[[ "${DEBUG}" == "1" ]] && echo -e "[DEBUG]: $*" 
}

# Write an informational message.  This will only produce output
# if the variable INFO is set to 1.
#
# No return values.

function msg_info() {
	[[ "${INFO}" == "1" ]] && echo -e "[INFO]: $*"
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


### -------------------------------------------------------------------
### -------------------------------------------------------------------
###
###
### PROGRAM LOGIC BEGINS HERE
###
###
### -------------------------------------------------------------------
### -------------------------------------------------------------------


function main () {

	# We need Bash version 4 or greater for associative arrays
	if [[ "${BASH_VERSINFO:-0}" -lt 4 ]]; then
		msg_error "This script requires Bash version 4 or greater.  You are running ${BASH_VERSION}."
		exit 5
	fi

	if ! check_for_build_prerequisites; then
		msg_error "One or more build requirements not satisfied."
		exit 1
	fi


	### -------------------------------------------------------------------
	### Parse command line options
	### 
	### This section sets the following variables:
	###
	### _tmpdir_root - Where to make our temporary directory
	### PYTHON_VERSIONS - Which versions of Python need Tracktable wheels?
	### WHEEL_DIRECTORY - Where should the wheels go?

	PARSED_ARGUMENTS=$(getopt -a -n build_osx_wheels \
		--options b:p:w:j:hk \
		--longoptions build-root:,python-version:,wheel-directory:,parallel:,help,keep-build-trees \
		-- "$@" )

	if [[ "$?" != 0 ]]; then
		msg_error "Failure while parsing command-line options.  Terminating."
		exit 2
	fi

	eval set -- "$PARSED_ARGUMENTS"

	while true; do
		case "$1" in
			-b | --build-root ) WORKDIR_LOCATION="$2"; shift 2 ;;
			-p | --python-version ) if [ "${PYTHON_VERSIONS}" == "unset" ]; 
									then PYTHON_VERSIONS=("$2"); 
									else PYTHON_VERSIONS+=("$2");
									fi; shift 2 ;;
			-w | --wheel-directory ) WHEEL_DIRECTORY="$2"; shift 2 ;; 
			-j | --parallel ) PARALLEL_JOBS="$2"; shift 2 ;;
	        -k | --keep-build-trees ) KEEP_BUILD_TREES=1; shift ;;
			-h | --help ) usage; exit 3 ;;
			-- ) shift; break ;; ## everything after here is not a swiutch
		* ) break ;;
		esac
	done

	### Now that optional arguments have been parsed, we have to check for
	### one last thing: the path to the source code!

	if [[ "$#" == "0" ]]; then
		msg_error "No path to source code supplied."
		usage
		exit 5
	else
		SOURCE_DIRECTORY="$1"
		msg_info "Tracktable source code is in ${SOURCE_DIRECTORY}."
	fi

	### -------------------------------------------------------------------
	### Set default values for any parameters not specified
	###

	# Set default value for the build root
	if [[ "${WORKDIR_LOCATION}" == "unset" ]]
	then
		msg_debug "Build tree root not supplied.  Using system default."
		if [ -z "${TMPDIR+x}" ]
		then
			msg_debug "TMPDIR is not set.  Defaulting to /tmp."
			WORKDIR_LOCATION=/tmp
		else
			msg_debug "Defaulting to TMPDIR: ${TMPDIR}"
			WORKDIR_LOCATION=${TMPDIR}
		fi
	else
		# Make sure we have an absolute path for the work directory
		ABS_PATH=$(cd "${WORKDIR_LOCATION}" && pwd)
		WORKDIR_LOCATION=${ABS_PATH}
	fi

	# By default, don't keep build trees
	if [[ "${KEEP_BUILD_TREES}" == "unset" ]]; then
		KEEP_BUILD_TREES=0
	fi

	# Set default value for the output directory
	if [[ "${WHEEL_DIRECTORY}" == "unset" ]]
	then
		msg_debug "Wheel output directory not set.  Defaulting to current directory."
		WHEEL_DIRECTORY=$(pwd)
	fi

	# Set default value for Python versions
	if [[ "${PYTHON_VERSIONS}" == "unset" ]]
	then
		msg_debug "No Python versions requested.  Defaulting to 3.5 - 3.9."
		PYTHON_VERSIONS=(3.5 3.6 3.7 3.8 3.9)
	fi

	# Check the syntax of all the Python versions
	for _version in "${PYTHON_VERSIONS[@]}"
	do
		msg_debug "About to try parsing alleged Python version ${_version}"
		#parse_python_version "${_version}"
		#result="$?"
		#msg_debug "Result code from parsing alleged Python version ${_version}: ${result}"
		if ! parse_python_version "${_version}" ; then
			msg_debug "test: ${parse_python_version_OUTPUT_major_version}.${parse_python_version_OUTPUT_minor_version}"
			msg_error "Python versions must be specified as X.Y.  You supplied $_version, which doesn't fit this syntax."
			exit 4
		fi
	done


	msg_info "Build trees will be created under ${WORKDIR_LOCATION}."
	msg_info "Wheels will be written to '${WHEEL_DIRECTORY}'."
	msg_info "Python versions to be used: ${PYTHON_VERSIONS[*]}"
	msg_info "Arguments after parse_args: $@"

	enable_anaconda

	### --------------------------------------------------------------------
	### Grab Conda environments for future reference
	### This will populate the variable list_conda_environments_OUTPUT
	list_conda_environments 

	### --------------------------------------------------------------------
	### Make sure we have a place for our builds
	###
	### TODO: mktemp has different behavior on MacOS and Linux.  Abstract this
	### into its own function.
	#msg_debug "About to run mktemp -d -t ${WORKDIR_LOCATION}/tracktable-build.XXXXXXXXXX"
	BUILD_ROOT=$(mktemp -d ${WORKDIR_LOCATION}/tracktable-build.XXXXXXXXXX)

	msg_info "Build trees will go under ${BUILD_ROOT}."

	### --------------------------------------------------------------------
	### Make sure we have a place to save wheels
	###

	if [ -d "${WHEEL_DIRECTORY}" ]
	then
		msg_info "Destination directory ${WHEEL_DIRECTORY} already exists -- no need to create."
	else
		msg_info "Creating output directory ${WHEEL_DIRECTORY}."
		mkdir ${_wheel_directory}
	fi

	### --------------------------------------------------------------------
	### Main loop is here: loop over requested Python versions
	###


	for py_version in "${PYTHON_VERSIONS[@]}"
	do
		msg_info "Beginning Tracktable build for Python ${py_version}."

		if ! conda_environment_exists ${py_version} list_conda_environments_OUTPUT
		then
			create_conda_environment ${py_version}
			activate_conda_environment ${py_version}
		else
			msg_debug "Conda environment already exists for this version"
		fi

		make_build_directory ${py_version}

		# Get the build directory for convenience
		build_directory_name ${py_version}
		local __build_directory=${BUILD_ROOT}/${build_directory_name_OUTPUT}

		find_conda_environment_path ${py_version}
		local __conda_environment_path=${find_conda_environment_path_OUTPUT}

		if ! cmake_configure ${__build_directory} ${SOURCE_DIRECTORY} ${__conda_environment_path}
			then
				msg_error "CMake configure stage failed.  Exiting."
				return 10
			fi

		if ! cmake_run_build ${__build_directory}; then
			msg_error "CMake build stage failed.  Exiting."
			return 20
		fi


		if ! cmake_run_install ${__build_directory}; then 
			msg_error "CMake install stage failed.  Exiting."
			return 30
		fi

		if ! cmake_build_wheel ${__build_directory}; then
			msg_error "Wheel build stage failed.  Exiting."
			return 40
		fi

		if ! copy_wheel_to_output ${__build_directory} ${WHEEL_DIRECTORY}; then
			msg_error "Wheel copy stage failed.  Exiting."
			return 50
		fi

		msg_info "Done building wheel for Python ${py_version}."

	    if [[ ${KEEP_BUILD_TREES} == 0 ]]; then
	    	delete_build_directory ${py_version}
	    fi

	done

} # end of main()



trap exit_cleanup EXIT

main "$@"

