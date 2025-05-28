#!/bin/sh

# The Python include directory is usually named 'python{major}.{minor}{abi_flag}'.
# Boost expects it to be named 'python{major}.{minor}'.  This script
# checks for that and makes a symlink if necessary.



FULL_IMPLEMENTATION=$1

PYTHON_HOME=/opt/python/${FULL_IMPLEMENTATION}
PYTHON=${PYTHON_HOME}/bin/python

MAJOR_DOT_MINOR=$(${PYTHON} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor})')
MAJOR_DOT_MINOR_ABI=$(${PYTHON} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}{sys.abiflags}")')

DESIRED_INCLUDE_DIR="${PYTHON_HOME}/include/python${MAJOR_DOT_MINOR}"
EXPECTED_INCLUDE_DIR="${PYTHON_HOME}/include/python${MAJOR_DOT_MINOR_ABI}"

if [ -d ${DESIRED_INCLUDE_DIR} ]; then
    echo "INFO: Python include directly already exists at expected path.  No repair necessary."
elif [ -d ${EXPECTED_INCLUDE_DIR} ]; then
    echo "INFO: Making Python include directory symlink from ${EXPECTED_INCLUDE_DIR} to ${DESIRED_INCLUDE_DIR} so Boost can find it."
    ln -s ${EXPECTED_INCLUDE_DIR} ${DESIRED_INCLUDE_DIR}
else
    echo "ERROR: Include directory for Python implementation ${FULL_IMPLEMENTATION} is not where we expect it (${EXPECTED_INCLUDE_DIR} or ${DESIRED_INCLUDE_DIR})."
    exit 1
fi
