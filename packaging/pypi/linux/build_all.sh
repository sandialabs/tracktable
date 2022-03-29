#!/bin/sh

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
