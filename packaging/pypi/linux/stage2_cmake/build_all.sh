#!/bin/sh

CMAKE_VERSION=3.22.2

curl \
       --location \
       -o cmake-${CMAKE_VERSION}.tar.gz \
       https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz

echo "Building boost multipython cmake container"
docker build \
       -t boost_multipython_cmake:latest \
       .

echo "Uploading boost multipython cmake container to container registry"
docker tag boost_multipython_cmake:latest cee-gitlab.sandia.gov:4567/trajectory/tracktable/linux/boost_multipython_cmake:latest
docker push cee-gitlab.sandia.gov:4567/trajectory/tracktable/linux/boost_multipython_cmake:latest