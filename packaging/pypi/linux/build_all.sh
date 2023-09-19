#!/bin/sh

# Change these if you want to update the Boost version.  The default below
# is Boost 1.82.0.  Remember to update clean_all.sh when you change this.
export BOOST_MAJOR_VERSION=1
export BOOST_MINOR_VERSION=82
export BOOST_PATCH_VERSION=0

# Change this if you want to update the CMake version.
export CMAKE_VERSION=3.22.2

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
