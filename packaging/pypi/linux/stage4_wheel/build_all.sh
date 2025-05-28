#!/usr/bin/env bash

###
### Build wheels for all of the Tracktable builds that succeeded.
###

# Exit immediately if something goes wrong.

set -e


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

# Get the names of all the images that look like they contain
# successful builds.

PROBABLE_BUILD_CONTAINERS=$(\
    docker images --format '{{.Repository}}:{{.Tag}}' \
    | grep "tracktable:cp" \
    )

if [ -z "${PROBABLE_BUILD_CONTAINERS}" ]; then
    echo "ERROR: Couldn't find any successful Tracktable builds."
    exit 1
fi

###
### Loop through each container.  Make the wheel, copy it out, and
### clean up.
###

for TRACKTABLE_BUILD_CONTAINER in ${PROBABLE_BUILD_CONTAINERS}; do

    trim ${TRACKTABLE_BUILD_CONTAINER}
    TRACKTABLE_BUILD_CONTAINER=${_trimmed_string}

    # Grab the Python interpreter tag from the build container name
    interpreter_tag_re='tracktable:([[:alpha:]]+)([[:digit:]]+)([[:alpha:]]*)'
    if [[ ${TRACKTABLE_BUILD_CONTAINER} =~ $interpreter_tag_re ]]; then
        _python_platform=${BASH_REMATCH[1]}
        _python_version=${BASH_REMATCH[2]}
        _python_abi=${BASH_REMATCH[3]}
        export PYTHON_IMPLEMENTATION=${_python_platform}${_python_version}${_python_abi}
    else
        echo "ERROR: Couldn't parse Python implementation from image name: ${TRACKTABLE_BUILD_CONTAINER}"
        exit 3
    fi

    # Yes, it exists; let's build the wheel
    echo "INFO: Building wheel for CPython version ${PYTHON_IMPLEMENTATION}"
    WHEEL_BUILD_CONTAINER="tracktable-wheel:${PYTHON_IMPLEMENTATION}"

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

    if [ ! ${KEEP_CONTAINERS_AFTER_BUILD} ]; then
        if [ -f ../finished_wheels/tracktable-*-${PYTHON_IMPLEMENTATION}-*.whl ]; then
            echo "INFO: Cleaning up build containers for CPython version ${PYTHON_IMPLEMENTATION}"
            docker rmi ${WHEEL_BUILD_CONTAINER}
            docker rmi ${TRACKTABLE_BUILD_CONTAINER}
        fi
    fi
done
