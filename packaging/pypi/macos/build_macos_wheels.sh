#!/usr/bin/env bash

# This script will build MacOS wheels for Tracktable from the currently 
# checked-out repository.  By default it will build for Python versions 
# 3.8 - 3.11 (3.9 - 3.11 on ARM64)
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


# These will keep track of what we're building and where.
TRACKTABLE_HOME=unset
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
usage: build_macos_wheels.sh [--python-version X.Y] [--build-root <dir>] [--wheel-directory <dir>] path_to_source

Build Tracktable wheels for the specified Python versions.

Required Arguments:

    path_to_source: Directory that contains the Tracktable source to
        build.  This is the directory that contains the top-level
        CMakeLists.txt and RELEASE_NOTES.md.

Options:
    -p,--python-version X.Y: Build for Python version X.Y.  This can be 
        specified multiple times to build for multiple versions.  By
        default, wheels will be built for Python 3.8 - 3.11 (3.9 - 3.11
		on Apple Silicon).

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

# This will load our script libraries.  Since we have to call it before
# we have those libraries, it has to be in this file by definition.
# So it goes.
#
# Arguments:
#    None.
#
# Returns:
#    No return value.  Exits if shell cannot cd to the directory 
#    containing this script (which would be very weird).
#
# Output variables:
#    Sets TRACKTABLE_HOME to the root of the directory tree containing
#    this script.

function _load_helper_functions () {
    pushd .
    cd "${BASH_SOURCE%/*}" || exit 3
	# at this point we're in tracktable/packaging/pypi/macos
	cd ../../..
	TRACKTABLE_HOME="$(pwd)"
    source ./ci/macos/functions/common.sh
    source ./ci/macos/functions/cmake.sh
    source ./ci/macos/functions/conda.sh
    popd
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

	# Load our function libraries and set TRACKTABLE_HOME
	_load_helper_functions
	

	### -------------------------------------------------------------------
	### Parse command line options
	### 
	### This section sets the following variables:
	###
	### _tmpdir_root - Where to make our temporary directory
	### PYTHON_VERSIONS - Which versions of Python need Tracktable wheels?
	### WHEEL_DIRECTORY - Where should the wheels go?

	PARSED_ARGUMENTS=$(getopt -a -n build_macos_wheels \
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


	# Find the root of our source tree

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
		msg_debug "No Python versions requested."
		ARCH="$(uname -m)"
		if [[ "${ARCH}" == "arm64" ]]
		then
			msg_debug "Defaulting to Python 3.9 - 3.11 on arm64."
			PYTHON_VERSIONS=(3.9 3.10 3.11)
		else
			msg_debug "Defaulting to Python 3.8 - 3.11."
			PYTHON_VERSIONS=(3.8 3.9 3.10 3.11)
		fi
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
		else
			msg_debug "Conda environment already exists for this version"
		fi

		activate_conda_environment ${py_version}

		# We check for build prerequisites after activating the Conda environment
		# because some of them may be installed in the Conda environment
		# instead of at system level.
		if ! check_for_build_prerequisites; then
			msg_error "One or more build requirements not satisfied."
			exit 1
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

