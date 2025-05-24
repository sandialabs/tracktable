#!/usr/bin/env bash

# Exit immediately on error.
set -e

# These will override the defaults in defaults.sh.
export BOOST_VERSION=1.82.0
export CMAKE_VERSION=4.02
export PYTHON_VERSIONS="3.9 3.10 3.11 3.12 3.13"
export MANYLINUX_TAG=manylinux2014_x86_64
export KEEP_CONTAINERS_AFTER_BUILD=0

pushd stage1_boost_multipython
./build_all.sh
popd

pushd stage2_cmake
./build_all.sh
popd

pushd stage3_tracktable
./build_all.sh
popd

pushd stage4_wheel
./build_all.sh
popd
