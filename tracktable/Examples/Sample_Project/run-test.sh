#!/usr/bin/bash
if [ -d build ]; then
  echo "Removing previous build with command:"
  echo "     rm -rf build"
  rm -rf build
fi

if [ ! -d build ]; then
  echo "Creating new build directory with command:"
  echo "     mkdir build"
  mkdir build
fi

echo "Changing into the build directory with command:"
echo "     cd build"
cd build

echo "Running cmake to create Makefiles with command:"
echo "     cmake .."
cmake ..

echo "Building cool program with command (we'll use 4 cores): "
echo "     make -j 4"
make -j 4

echo "Program is built"
echo "Now we'll run it with command: "
echo "     ./coolprogram"
echo
echo "Here's our output:"
echo "--- BEGIN OUTPUT ---"
./coolprogram
echo "--- END OUTPUT ---"
echo

echo "And... we're done."
echo
echo "Things to try:"
echo
echo "Look around in the build directory:"
echo "     cd build"
echo "     ls"
echo
echo "Clean and rebuild the program:"
echo "     make clean; make"
echo

