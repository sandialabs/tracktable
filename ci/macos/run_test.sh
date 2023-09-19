#!/usr/bin/env bash

# Run CMake to set up the build

# This script uses the following functions:
#
# common.sh:
#   check_for_program
#
# conda.sh:
#   enable_anaconda
#   activate_anaconda_environment
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

    list_conda_environments

    if conda_environment_exists ${__py_version} list_conda_environments_OUTPUT
    then
        find_conda_environment_path ${__py_version}
        __CONDA_ENVIRONMENT_PATH=${find_conda_environment_path_OUTPUT}
        activate_conda_environment ${__py_version}
    else 
        msg_error "Anaconda environment for Python ${__py_version} not found."
        exit 1
    fi


    ### ---------------------------------------------------------------
    ### Step N: Make sure we have CMake.

    if ! check_for_program ctest
    then
        msg_error "Tracktable testing require CTest."
        exit 2
    fi

    ### ---------------------------------------------------------------
    ### Step 4: Have CMake invoke the native build tool.

    BUILD_DIRECTORY="${__HERE}/${BUILD_DIRECTORY_NAME}"

    if [[ -z ${EXCLUDED_TESTS+x} ]]
    then
        msg_debug "--- No EXCLUDED_TESTS variable in environment"
        cmake_run_ctest ${__BUILD_DIRECTORY}
    else
        msg_debug "--- Running with test exclusions: ${EXCLUDED_TESTS}"
        cmake_run_ctest ${__BUILD_DIRECTORY} ${EXCLUDED_TESTS}
    fi

    ctest_result=$?

    if [[ ${ctest_result} -ne 0 ]]
    then
        msg_error "CMake test stage failed."
        return 20
    fi
}

main "$@"
