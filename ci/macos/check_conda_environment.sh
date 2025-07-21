#!/usr/bin/env bash

# Check to make sure the Conda environment we'll use for the build
# is up to date -- that is, it was last updated more recently than
# the last commit to its definition file

# This script uses the following functions:
#
# common.sh:
#   check_for_program
#
# conda.sh:
#   enable_anaconda
#
# ci/common/is_conda_environment_up_to_date.sh

# Note: This script will probably be invoked from the repository
# root directory.

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

# Trace execution
# set -x

###
###
### STATE VARIABLES
###
###

__HERE="__here_path_NOT_SET__"
__BUILD_DIRECTORY="__build_directory_NOT_SET__"
__CONDA_ENVIRONMENT_PATH="__conda_environment_path_NOT_SET__"

###
###
### FUNCTIONS INTERNAL TO THIS SCRIPT
###
###

function _load_helper_functions () {
    pushd .
    cd "${BASH_SOURCE%/*}" || exit 3
    source ./functions/common.sh
    source ./functions/cmake.sh
    source ./functions/conda.sh
    popd
}


###
###
### PROGRAM LOGIC STARTS HERE
###
###


function main () {
    __HERE="$(pwd)"

    # This one-liner works as long as the last component of the path is not a
    # symbolic link.
    __SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

    # We need Bash version 4 or greater for associative arrays
    if [[ "${BASH_VERSINFO:-0}" -lt 4 ]]
    then
        echo "This script requires Bash version 4 or greater.  The Gitlab runner is using ${BASH_VERSION}."
        exit 5
    fi

    ### ---------------------------------------------------------------
    ### Step 1: Load in the helper functions we need
    ###
    _load_helper_functions
    __BUILD_DIRECTORY=${__HERE}/${BUILD_DIRECTORY_NAME}

    disable_debug_log

    ### ---------------------------------------------------------------
    ### Step 2: Activate Anaconda.  We already know it's available
    ###         because we checked for it in the setup stage.
    ###

    enable_anaconda

    ### ---------------------------------------------------------------
    ### Step 3: Activate the Anaconda environment for our Python
    ###         version.  Make sure it exists first.
    ###
    ### TODO: Allow customization of Python version via shell variable.

    __py_version=${DEFAULT_PYTHON_VERSION}
    __conda_def_file=macos_ci_environment_python${__py_version}.yml

    ${__SCRIPT_DIR}/../common/is_conda_environment_up_to_date.sh ${__SCRIPT_DIR}/${__conda_def_file}
    status=$?

    exit $status
}

main "$@"
