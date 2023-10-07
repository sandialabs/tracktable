#!/usr/bin/env bash

# Exit immediately on error.
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



echo "Building Tracktable for all supported Python versions."
if [ -d tracktable-copy ]; then
    echo "INFO: Cleaning up after previous run of script."
    rm -rf tracktable-copy
fi

if [ -d tracktable ]; then
    echo "INFO: Removing old copy of Tracktable source."
    rm -rf tracktable
fi


echo "INFO: Copying Tracktable source from current tree."
cp -r ../../../../../tracktable ../../../../../tracktable-copy
mv ../../../../../tracktable-copy ./tracktable



if [ -z "${CI_REGISTRY+x}" ]; then
    export BOOST_CMAKE_IMAGE=boost_multipython_cmake:latest
else
    export BOOST_CMAKE_IMAGE=${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
fi


# We're going to build Tracktable for all available CPython versions.
# Get a list of those versions from the container.
echo "INFO: Retrieving list of CPython versions in build container."
AVAILABLE_PYTHON_IMPLEMENTATIONS=$(docker run -ti --rm ${BOOST_CMAKE_IMAGE} '/bin/ls /opt/python | grep cp')


###
### Loop through all of the available CPython implementations in this container and
### build Boost for each one.
###

for PYTHON_IMPLEMENTATION in ${AVAILABLE_PYTHON_IMPLEMENTATIONS}; do
    trim ${PYTHON_IMPLEMENTATION}
    PYTHON_IMPLEMENTATION=${_trimmed_string}
    
    parse_python_version ${PYTHON_IMPLEMENTATION}
    PYTHON_VERSION=${_python_version}
    PYTHON_ABI=${_python_abi}
    
    DESTINATION_IMAGE=tracktable:${PYTHON_VERSION}
    
   echo "INFO: Building Tracktable for Python version ${PYTHON_IMPLEMENTATION}."
   echo "DEBUG: destination image is ${DESTINATION_IMAGE}"

   docker build -t ${DESTINATION_IMAGE} \
         -f Dockerfile.build_tracktable \
         --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
         --build-arg NIGHTLY=${NIGHTLY} \
         --build-arg DEVELOPMENT=${DEVELOPMENT} \
         --build-arg DEV_NUMBER=${DEV_NUMBER} \
         --build-arg SOURCE_IMAGE=${BOOST_CMAKE_IMAGE} \
         .
done

### Cleanup: we no longer need the Tracktable source in this directory
rm -rf ./tracktable

