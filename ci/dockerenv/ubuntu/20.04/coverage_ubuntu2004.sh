#!/bin/sh
rm -rf build_coverage
mkdir build_coverage
cd build_coverage
cmake -DCMAKE_BUILD_TYPE=Coverage ..
make
make cov_unit
make cov_genhtml
