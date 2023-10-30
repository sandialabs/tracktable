#!/bin/sh

# Exit immediately on error.
set -e


DEFAULT_CMAKE_VERSION=3.22.2

###
### Build and install CMake in our container that has all the Python 
### interpreters and Boost libraries.
###
### This script takes the desired CMake version from an environment 
### variable CMAKE_VERSION.
###

if [ -z ${CMAKE_VERSION+x} ]; then
    export CMAKE_VERSION=${DEFAULT_CMAKE_VERSION}
    echo "WARNING: CMAKE_VERSION is not set in the environment.  This "
    echo "         usually happens when you're running a build stage in isolation"
    echo "         (for testing or debugging) instead of from the top-level"
    echo "         build_all.sh script.  Defaulting to CMake ${CMAKE_VERSION}."
else
    echo "INFO: CMake version ${CMAKE_VERSION} requested in environment variables."
fi


if [ -z ${CI_REGISTRY+x} ]; then
    export SOURCE_IMAGE=boost_multipython:latest
else
    export SOURCE_IMAGE=${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
fi

###
### Download CMake source code if we don't have it already.
###

CMAKE_SOURCE_FILENAME=cmake-${CMAKE_VERSION}.tar.gz

if [ ! -f ${CMAKE_SOURCE_FILENAME} ]; then
    echo "INFO: Downloading CMake source code."
    curl \
        --location \
        -o ${CMAKE_SOURCE_FILENAME} \
        https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz
else
    echo "INFO: CMake source code already downloaded."
fi

echo "INFO: Building CMake."

docker build \
       --build-arg CMAKE_VERSION=${CMAKE_VERSION} \
       --build-arg SOURCE_IMAGE=${SOURCE_IMAGE} \
       --build-arg CI_REGISTRY=${CI_REGISTRY} \
       -t boost_multipython_cmake:latest \
       .

###
### If we're running from a CI job we can save this container for later re-use.
###

if [ ! -z ${CI_REGISTRY:x} ]; then
    echo "INFO: Uploading Boost.Python+CMake container to registry"
    docker tag boost_multipython_cmake:latest ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
    docker push ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
fi

###
### Cleanup: we no longer need the source code 
###

rm ${CMAKE_SOURCE_FILENAME}