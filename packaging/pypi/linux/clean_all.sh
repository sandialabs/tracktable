#!/bin/sh

# This script removes absolutely all the images created by
# this project.  At present it hard-codes the Boost version.

BOOST_VERSION=1.74.0

for py_version in cp35 cp36 cp37 cp38 cp39 cp310; do
    docker rmi tracktable:${py_version} \
               tracktable-wheel:${py_version} \
               boost-${BOOST_VERSION}:${py_version}
done

docker rmi boost_multipython:latest
docker rmi boost_multipython_cmake:latest
docker rmi boost_downloaded:${BOOST_VERSION}
docker rmi quay.io/pypa/manylinux2010_x86_64
