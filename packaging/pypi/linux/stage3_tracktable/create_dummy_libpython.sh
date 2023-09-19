#!/bin/sh

# CMake insists on finding libpython.so before it will go look for
# headers.  It isn't there if the interpreter has been statically
# linked.  This script creates a dummy file just to make it happy.

IMPLEMENTATION=$1
PYTHON_BASE=/opt/python/${IMPLEMENTATION}-${IMPLEMENTATION}

if [ -e ${PYTHON_BASE}m ]; then
    PYTHON_HOME=${PYTHON_BASE}m
else
    PYTHON_HOME=${PYTHON_BASE}
fi

PYTHON=${PYTHON_HOME}/bin/python
PYTHON_VERSION=`$PYTHON -c 'from __future__ import print_function; import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))'`

if [ ! -e ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}m.so ]; then
    touch ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}m.so
fi

if [ ! -e ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}.so ]; then
    touch ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}.so
fi
