#!/bin/sh

# The Python include directory is often called 'python3.7m'.  The
# Boost build process expects to see just 'python3.7'.  Make a symlink
# if needed.  In fact, just make symlinks to ensure that both
# directories exist.


FULL_IMPLEMENTATION=$1

PYTHON_HOME=/opt/python/${FULL_IMPLEMENTATION}
PYTHON=${PYTHON_HOME}/bin/python

EXPECTED_INCLUDE_DIR_NAME=$(${PYTHON} -c 'from __future__ import print_function; import sys; print("python{}.{}".format(sys.version_info.major, sys.version_info.minor))')

DIRECTORY_WITHOUT_M=${PYTHON_HOME}/include/${EXPECTED_INCLUDE_DIR_NAME}
DIRECTORY_WITH_M=${DIRECTORY_WITHOUT_M}m

if [ -d ${DIRECTORY_WITHOUT_M} ]; then
    echo "INFO: Python include directly already exists at expected path.  No repair necessary."
elif [ -d ${DIRECTORY_WITH_M} ]; then
    echo "INFO: Making Python include directory symlink from ${DIRECTORY_WITH_M} to ${DIRECTORY_WITHOUT_M} so Boost can find it."
    ln -s ${DIRECTORY_WITH_M} ${DIRECTORY_WITHOUT_M}
else
    echo "ERROR: Include directory for Python implementation ${FULL_IMPLEMENTATION} is not where we expect it (${DIRECTORY_WITH_M} or ${DIRECTORY_WITHOUT_M})."
    exit 1
fi
