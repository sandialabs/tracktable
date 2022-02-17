
# This file uses the following functions from elsewhere:

# msg_debug
# msg_info
# enable_debug
# disable_debug

###
### INTERNAL-ONLY FUNCTIONS
###

# We need to run Conda functions with debugging off because there are some
# bugs in their own scripts that we can't reach from here.

function _disable_debug () {
	set +o pipefail
	set +o nounset
}

function _enable_debug () {
	set -o pipefail
	set -o nounset
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

	_disable_debug
	conda activate ${__envname}
	_enable_debug
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
    conda_environment_name_OUTPUT="tracktable-ci-python${__py_version}"
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

	msg_debug "Creating Conda build environment ${__envname}"

	_disable_debug

	conda create \
		--name ${__envname} \
		--yes \
		--channel conda-forge \
		python_abi=${__python_version}=*_cp* \
		boost=1.75 \
		cartopy \
		cmake \
		compilers \
		doxygen \
		folium \
		graphviz \
		jupyter \
		nbsphinx \
		nbsphinx-link \
		numpy \
		pandoc \
		pip \
		pytz \
		sphinx \
		sphinx_rtd_theme \
		tracktable-data \
		tqdm

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

	_enable_debug

	# These utilities aren't in conda main or conda-forge
	pip install \
		delocate \
		breathe
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
	_disable_debug;
	eval "$(command conda 'shell.bash' 'hook' 2>/dev/null)"
	_enable_debug;
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
	_disable_debug;
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
				msg_debug "Line didn't match (this is not an error)"
			fi
		done < <( \
		conda env list \
		| grep -v \# \
		)
	_enable_debug;
}
