#!/usr/bin/env bash

###
### Build wheels for all of the Tracktable builds that succeeded.
###

# Utility function: where is this script?  We need this to get to our
# function library.
#
# Sets the variable HERE.
#
# From https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script

find_script_directory() {
    local _source="${BASH_SOURCE[0]}"
    while [ -L "${_source}" ]; do 
        # Resolve _source until the file is no longer a symlink.
        _dir=$( cd -P "$(dirname "${_source}" )" >/dev/null 2>&1 && pwd )
        _source=$(readlink "$_source")
    done
    export HERE=$( cd -P "$(dirname "${_source}")" >/dev/null 2>&1 && pwd )
}

# Load parsing functions from external library
find_script_directory
source ${HERE}/../functions/parsing.sh


# Housekeeping: make a place to put the wheels

if [ ! -d ../finished_wheels ]; then
    mkdir ../finished_wheels
fi

# Start by getting the name of one successful build.  Just one.  We'll
# use that to get the names of all the CPython implementations and look
# for successful builds.
TEMP_BUILD_CONTAINER=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep "tracktable:cp" | head -1)
if [ -z "${TEMP_BUILD_CONTAINER}" ]; then
    echo "ERROR: Couldn't find any successful Tracktable builds."
    exit 1
fi

echo "INFO: Retrieving list of CPython versions in build container."
AVAILABLE_PYTHON_IMPLEMENTATIONS=$(docker run -ti --rm ${TEMP_BUILD_CONTAINER} '/bin/ls /opt/python | grep cp | grep -v cp36')


# # Trim leading and trailing whitespace.
# #
# # From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
# #
# # Output variable: _trimmed_string
# trim() {
#     local var="$*"
#     # remove leading whitespace
#     var="${var#"${var%%[![:space:]]*}"}"
#     # remove trailing whitespace
#     var="${var%"${var##*[![:space:]]}"}"
#     export _trimmed_string="${var}"
# }

# # Parse Python implementation into version and options.
# # For example, 'cp37-cp37m' -> 'cp37' and 'cp37m'.
# #
# # Output variables:
# # _python_version, _python_abi

# parse_python_version() {
#     local _full_version="$*"
#     trim "${_full_version}"
#     _full_version=${_trimmed_string}

#     if [[ ${_full_version} =~ ^(cp[[:digit:]]+[m]?)-(cp[[:digit:]]+[m]?) ]]; then
#         export _python_version=${BASH_REMATCH[1]}
#         export _python_abi=${BASH_REMATCH[2]}
#     else
#         echo "ERROR: Couldn't parse Python implementation name: ${_full_version}"
#         exit 3
#     fi
# }


### 
### Loop through each implementation.  Check to see if the build succeeded,
### indicated by the presence of a tracktable:cpXY container.  If so, 
### make the wheel, copy it out, and clean up.
###


for PYTHON_IMPLEMENTATION in ${AVAILABLE_PYTHON_IMPLEMENTATIONS}; do
    trim ${PYTHON_IMPLEMENTATION}
    PYTHON_IMPLEMENTATION=${_trimmed_string}

    parse_python_version ${PYTHON_IMPLEMENTATION}
    PYTHON_VERSION=${_python_version}
    PYTHON_ABI=${_python_abi}
    
    TRACKTABLE_BUILD_CONTAINER="tracktable:${PYTHON_VERSION}"
    
    # Does that image exist?
    docker images --format '{{.Repository}}:{{.Tag}}' | grep "${TRACKTABLE_BUILD_CONTAINER}" > /dev/null
    if [ ! $? -eq 0 ]; then
        echo "WARNING: No Docker container for Tracktable build for ${PYTHON_VERSION}."
        echo "         Did that build fail?"
    else
        # Yes, it exists; let's build the wheel
        echo "INFO: Building wheel for CPython version ${PYTHON_IMPLEMENTATION}"
        WHEEL_BUILD_CONTAINER="tracktable-wheel:${PYTHON_VERSION}"
        docker build \
           -t ${WHEEL_BUILD_CONTAINER} \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
           --build-arg TRACKTABLE_BUILD_CONTAINER=${TRACKTABLE_BUILD_CONTAINER} \
           --build-arg CI_JOB_TOKEN=${CI_JOB_TOKEN} \
           --build-arg CI_API_V4_URL=${CI_API_V4_URL} \
           --build-arg CI_PROJECT_ID=${CI_PROJECT_ID} \
           --build-arg NIGHTLY=${NIGHTLY} \
           --build-arg DEVELOPMENT=${DEVELOPMENT} \
           --build-arg DEV_NUMBER=${DEV_NUMBER} \
           .
    
        # Pull the wheel out of the container's filesystem
        echo "INFO: Retrieving finished wheel for CPython version ${PYTHON_IMPLEMENTATION}"
        mkdir ../finished_wheels/${PYTHON_IMPLEMENTATION}
        export CREATED_NAME=$(docker create ${WHEEL_BUILD_CONTAINER})
        docker cp ${CREATED_NAME}:/finished_wheels ../finished_wheels/${PYTHON_IMPLEMENTATION}
        docker rm ${CREATED_NAME}

        # We've got the wheel files out of the container; move them into place
        mv ../finished_wheels/${PYTHON_IMPLEMENTATION}/finished_wheels/*.whl ../finished_wheels
        rmdir ../finished_wheels/${PYTHON_IMPLEMENTATION}/finished_wheels
        rmdir ../finished_wheels/${PYTHON_IMPLEMENTATION}

        # Clean up after ourselves
        echo "INFO: Cleaning up build containers for CPython version ${PYTHON_IMPLEMENTATION}"
        #docker rmi ${WHEEL_BUILD_CONTAINER}
        #docker rmi ${TRACKTABLE_BUILD_CONTAINER}
    fi
done
