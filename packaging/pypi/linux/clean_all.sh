#!/bin/sh

# This script removes absolutely all the images and auxiliary
# files created by this project with one exception: the
# original, unaltered manylinux image.

pushd stage0_base_image
./clean_all.sh
popd

pushd stage1_boost_multipython
./clean_all.sh
popd

pushd stage2_cmake
./clean_all.sh
popd

pushd stage3_tracktable
./clean_all.sh
popd

pushd stage4_wheel
./clean_all.sh
popd
