#!/bin/sh

# CMake insists on finding libpython.so before it will go look for
# headers.  It isn't there if the interpreter has been statically
# linked.  This script creates a dummy file just to make it happy.

# Exit immediately on error
set -e

IMPLEMENTATION=$1
PYTHON_HOME=/opt/python/${IMPLEMENTATION}

if [ ! -d ${PYTHON_HOME}/lib ]; then
    echo "ERROR: create_dummy_libpython.sh: Python library directory not found at expected path ${PYTHON_HOME}/lib"
    exit 1
fi

PYTHON=${PYTHON_HOME}/bin/python
PYTHON_VERSION=`$PYTHON -c 'from __future__ import print_function; import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))'`

# Just to cover all bases -- create both libpythonX.Y.so
# and libpythonX.Ym.so

if [ ! -e ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}m.so ]; then
    echo "INFO: create_dummy_libpython.sh: Creating dummy file for libpython${PYTHON_VERSION}m.so"
    touch ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}m.so
fi

if [ ! -e ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}.so ]; then
    echo "INFO: create_dummy_libpython.sh: Creating dummy file for libpython${PYTHON_VERSION}.so"
    touch ${PYTHON_HOME}/lib/libpython${PYTHON_VERSION}.so
fi
