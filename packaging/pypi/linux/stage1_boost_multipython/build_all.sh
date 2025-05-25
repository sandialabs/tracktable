#!/usr/bin/env bash

# Exit on error.
set -e

###
### STARTUP
###
### We get all of our arguments from environment variables rather than on
### the command line.  Check to see what's there and what's not.
###
### Parameters are supplied with environment variables.  Here are
### the ones we look for:
###
### BOOST_VERSION: Defaults to 1.82.0.
###

### ---------------------------------------------------------------------
###
### Housekeeping: load parsing functions
###
### ---------------------------------------------------------------------

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


find_script_directory
source ${HERE}/../functions/parsing.sh
source ${HERE}/../functions/find_interpreters.sh
source ${HERE}/../defaults.sh


### ---------------------------------------------------------------------
###
### Argument Parsing
###
### Get all of our settings from user-provided environment variables if
### available or built-ind efaults (from defaults.sh) if not.
###
### Note to future visitors: You are welcome to refactor all of this to
### use command line arguments and getopt if you'd like.
###
### ---------------------------------------------------------------------

if [ -z ${PYTHON_VERSIONS+x} ]; then
    echo "INFO: PYTHON_VERSIONS is not set.  Defaulting to versions: "
    echo "      ${DEFAULT_PYTHON_VERSIONS}"
    PYTHON_VERSIONS=${DEFAULT_PYTHON_VERSIONS}
fi

if [ -z ${BOOST_VERSION+x} ]; then
    echo "WARNING: BOOST_VERSION is not set.  Defaulting to version ${DEFAULT_BOOST_VERSION}."
    BOOST_VERSION=${DEFAULT_BOOST_VERSION}
fi

# This sets BOOST_VERSION_DOTS and BOOST_VERSION_UNDERSCORES
parse_boost_version ${BOOST_VERSION}


### ---------------------------------------------------------------------
###
### Download Boost and unpack in /opt/src
###
### ---------------------------------------------------------------------


echo "INFO: Building Boost.Python from Boost ${BOOST_VERSION_DOTS} for all supported Python versions."

###
### Download Boost source if we don't have it already
###

BOOST_FILENAME=boost_${BOOST_VERSION_UNDERSCORES}.tar.gz
if [ ! -f ${BOOST_FILENAME} ]; then
    echo "INFO: Downloading Boost ${BOOST_VERSION_DOTS}"
    curl \
       --location \
       -o ${BOOST_FILENAME} \
       https://archives.boost.io/release/${BOOST_VERSION_DOTS}/source/boost_${BOOST_VERSION_UNDERSCORES}.tar.gz
else
    echo "INFO: Boost source already downloaded."
fi

###
### Save source code in a container along with the SSL/proxy environment.
### We'll clean up this image when we're done.
###

BOOST_DOWNLOADED_CONTAINER=boost_downloaded:${BOOST_VERSION_DOTS}

docker build \
       -t ${BOOST_DOWNLOADED_CONTAINER} \
       -f Dockerfile.download_boost \
       --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
       --build-arg BOOST_VERSION_UNDERSCORES=${BOOST_VERSION_UNDERSCORES} \
       .



### ---------------------------------------------------------------------
###
### Build Boost for all of our Python versions
###
### ---------------------------------------------------------------------

###
### Find all of the CPython implementations in our container that
### match the versions in PYTHON_VERSIONS.
###

# This sets INTERPRETER_DIRECTORIES
find_interpreters "${PYTHON_VERSIONS}" ${BOOST_DOWNLOADED_CONTAINER}

# This image will be used as the basis for the final output of this stage.
# They're all the same except for the selected Python interpreter
# that was used to build libboost_python.so, so there's no need to do anything
# more complex than just selecting the first one.
BASE_MULTIPYTHON_IMAGE=not_yet_defined

# This is where we'll save libboost binaries as we build them
if [ -d libboost_python_tmp ]; then
    echo "INFO: Deleting existing libboost_python binaries."
    rm -rf libboost_python_tmp
fi
mkdir libboost_python_tmp


###
### Loop through all of the available CPython implementations in this container and
### build Boost for each one.
###
### We could also push this into a shell script inside the container and
### run all the builds in a single container.
###
for PYTHON_IMPLEMENTATION in ${INTERPRETER_DIRECTORIES}; do
    trim "${PYTHON_IMPLEMENTATION}"
    PYTHON_IMPLEMENTATION="${_trimmed_string}"

    parse_python_version "${PYTHON_IMPLEMENTATION}"
    PYTHON_VERSION=${_python_platform}${_python_version}${_python_abi}

    DESTINATION_IMAGE_NAME=boost-${BOOST_VERSION_DOTS}:${PYTHON_VERSION}

    if [ "${BASE_MULTIPYTHON_IMAGE}" = "not_yet_defined" ]; then
        BASE_MULTIPYTHON_IMAGE=${DESTINATION_IMAGE_NAME}
    fi

    echo "INFO: Building Boost.Python for interpreter version ${PYTHON_VERSION}."
    docker build \
           -t ${DESTINATION_IMAGE_NAME} \
           -f Dockerfile.build_boost \
           --build-arg BOOST_DOWNLOADED_CONTAINER=${BOOST_DOWNLOADED_CONTAINER} \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
           --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
           --build-arg BOOST_VERSION_UNDERSCORES=${BOOST_VERSION_UNDERSCORES} \
           .

    echo "INFO: Copying Boost.Python libraries for ${PYTHON_VERSION} to temporary directory."
    # Start an instance of the container so we can extract things from its filesystem
    CREATED_NAME=$(docker create ${DESTINATION_IMAGE_NAME})
    docker cp ${CREATED_NAME}:/boost_python/boost_python_libraries.tar ./libboost_python_tmp
    # OK, done, delete the container
    docker rm ${CREATED_NAME}

    pushd libboost_python_tmp
    tar xf boost_python_libraries.tar && rm boost_python_libraries.tar
    popd
done


###
### Collect all of the compiled libboost_python libraries into a single image.
###

echo "INFO: Collecting all Boost Python compiled libraries for final image."
pushd libboost_python_tmp
tar cf ../collected_boost_python.tar .
popd

docker build \
    -t boost_multipython:${BOOST_VERSION_DOTS} \
    --build-arg BASE_MULTIPYTHON_IMAGE=${BASE_MULTIPYTHON_IMAGE} \
    -f Dockerfile.collect_boost_python \
    .
docker tag boost_multipython:${BOOST_VERSION_DOTS} boost_multipython:latest



### ---------------------------------------------------------------------
###
### Cleanup: we no longer need the individual builds or the Boost source
### code.
###
### ---------------------------------------------------------------------

rm collected_boost_python.tar
rm -rf libboost_python_tmp

for PYTHON_IMPLEMENTATION in ${INTERPRETER_DIRECTORIES}; do
    parse_python_version "${PYTHON_IMPLEMENTATION}"
    PYTHON_VERSION=${_python_platform}${_python_version}${_python_abi}

    DESTINATION_IMAGE_NAME=boost-${BOOST_VERSION_DOTS}:${PYTHON_VERSION}
    echo "CLEANUP: Removing Docker image ${DESTINATION_IMAGE_NAME} after build"
    docker rmi ${DESTINATION_IMAGE_NAME}
done

docker rmi boost_downloaded:${BOOST_VERSION_DOTS}
rm ${BOOST_FILENAME}

###
### Finally, if we're being called from a CI job, we may have a registry URL
### to which we can upload our shiny new container.
###

if [ ! -z ${CI_REGISTRY:x} ]; then
    echo "INFO: Uploading boost multipython container to container registry"
    docker tag boost_multipython:latest ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython:latest
    docker push ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython:latest
fi
