#!/bin/sh

# The Python include directory is often called 'python3.7m'.  The
# Boost build process expects to see just 'python3.7'.  Make a symlink
# if needed.  In fact, just make symlinks to ensure that both
# directories exist.


FULL_IMPLEMENTATION=$1

PYTHON_HOME=/opt/python/${FULL_IMPLEMENTATION}
PYTHON=${PYTHON_HOME}/bin/python

PYTHON_VERSION=`${PYTHON} -c 'from __future__ import print_function; import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))'`

DIRECTORY_WITH_M=${PYTHON_HOME}/include/python${PYTHON_VERSION}m
DIRECTORY_WITHOUT_M=${PYTHON_HOME}/include/python${PYTHON_VERSION}

if [ -d ${DIRECTORY_WITH_M} -a ! -d ${DIRECTORY_WITHOUT_M} ]; then
    echo "Creating symlink: ${DIRECTORY_WITH_M} -> ${DIRECTORY_WITHOUT_M}"
    ln -s ${DIRECTORY_WITH_M} ${DIRECTORY_WITHOUT_M}
elif [ -d ${DIRECTORY_WITHOUT_M} -a ! -d ${DIRECTORY_WITH_M} ]; then
    echo "Creating symlink: ${DIRECTORY_WITHOUT_M} -> ${DIRECTORY_WITH_M}"
    ln -s ${DIRECTORY_WITHOUT_M} ${DIRECTORY_WITH_M}
fi

