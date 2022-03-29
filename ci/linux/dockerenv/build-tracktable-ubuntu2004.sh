#!/bin/bash
rm -rf build_ubuntu2004
mkdir build_ubuntu2004
cd build_ubuntu2004
cmake -GNinja ..
ninja
ctest --output-on-failure
