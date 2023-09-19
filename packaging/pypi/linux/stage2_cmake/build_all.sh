#!/bin/sh

if [ -z ${CMAKE_VERSION+x} ]; then
    export CMAKE_VERSION=3.22.2
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

curl \
       --location \
       -o cmake-${CMAKE_VERSION}.tar.gz \
       https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz

echo "INFO: Building CMake."

docker build \
       --build-arg CMAKE_VERSION=${CMAKE_VERSION} \
       --build-arg SOURCE_IMAGE=${SOURCE_IMAGE} \
       --build-arg CI_REGISTRY=${CI_REGISTRY} \
       -t boost_multipython_cmake:latest \
       .

if [ ! -z ${CI_REGISTRY:x} ]; then
    echo "INFO: Uploading Boost.Python+CMake container to registry"
    docker tag boost_multipython_cmake:latest ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
    docker push ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
fi