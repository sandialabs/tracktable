#!/usr/bin/env bash

# Set up the Anaconda environment to build and test Tracktable

# This script uses the following functions:
#
# common.sh:
#   check_for_program
#
# conda.sh:
#   create_anaconda_environment
#   enable_anaconda
#   list_conda_environments

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

###
###
### STATE VARIABLES
###
###


###
###
### FUNCTIONS INTERNAL TO THIS SCRIPT
###
###

function _check_for_anaconda () {
    if ! check_for_program conda; then
        return 1
    fi
    return 0
}

function _load_helper_functions () {
    pushd .
    cd "${BASH_SOURCE%/*}" || exit 3
    source ./functions/common.sh
    source ./functions/conda.sh
    popd
}


### 
###
### PROGRAM LOGIC STARTS HERE
###
###


function main () {

    # We need Bash version 4 or greater for associative arrays
    if [[ "${BASH_VERSINFO:-0}" -lt 4 ]]
    then
        echo "This script requires Bash version 4 or greater.  The Gitlab runner is using ${BASH_VERSION}."
        exit 5
    fi

    ### ---------------------------------------------------------------
    ### Step 1: Load in the helper functions we need
    ###
    _load_helper_functions;

    disable_debug_log

    ### ---------------------------------------------------------------
    ### Step 2: Activate Anaconda.  
    ###
    if ! _check_for_anaconda
    then
        echo "The Gitlab runner must execute in an environment with Anaconda (conda) on the path."
        exit 1
    fi

    enable_anaconda

    ### ---------------------------------------------------------------
    ### Step 3: Grab the list of virtual environments.  We will need
    ###         this to determine whether or not we need to create
    ###         the environment we need.

    list_conda_environments

    ### ---------------------------------------------------------------
    ### Step 4: Check to see whether we've got a conda environment for
    ###         the version of Python we want to build for.
    ###
    ### TODO: Allow customization of Python version via shell variable.

    __py_version=${DEFAULT_PYTHON_VERSION}

    if ! conda_environment_exists ${__py_version} list_conda_environments_OUTPUT
    then
        msg_info "Creating Anaconda environment for Python ${__py_version}."
        create_conda_environment ${__py_version}
    else
        msg_info "Using existing Anaconda environment for Python ${__py_version}."
    fi

    msg_info "Done configuring Anaconda environment."
}

main "$@"
