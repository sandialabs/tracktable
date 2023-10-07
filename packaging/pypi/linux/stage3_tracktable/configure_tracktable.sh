#!/bin/sh

# Exit immediately on error
set -e

PYTHON_IMPLEMENTATION=$1
PYTHON_HOME=/opt/python/${PYTHON_IMPLEMENTATION}

# This should exist: we put the symlink into place if needed back in 
# Stage 1 when we built Boost.
PYTHON_INCLUDE_DIR_NAME=$(${PYTHON_HOME}/bin/python -c 'from __future__ import print_function; import sys; print("python{}.{}".format(sys.version_info.major, sys.version_info.minor))')
PYTHON_INCLUDE_DIR=${PYTHON_HOME}/include/${PYTHON_INCLUDE_DIR_NAME}

if [ ! -d ${PYTHON_INCLUDE_DIR} ]; then
    echo "WARNING: Python include directory not found at expected path ${PYTHON_INCLUDE_DIR}."
    PYTHON_INCLUDE_DIR="${PYTHON_INCLUDE_DIR}m"
    if [ ! -d ${PYTHON_INCLUDE_DIR} ]; then
        echo "ERROR: Python include directory not found at fallback path ${PYTHON_INCLUDE_DIR} either."
        echo "       Build cannot continue."
        exit 1
    fi
fi

# We need Jupyter as part of the build
${PYTHON_HOME}/bin/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org jupyter
export PATH="${PYTHON_HOME}/bin:${PATH}"

echo "INFO: Configuring Tracktable for CPython version ${PYTHON_IMPLEMENTATION}."
cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/src/tracktable/install \
        -DBoost_INCLUDE_DIR=/usr/local/include \
        -DPython3_EXECUTABLE=${PYTHON_HOME}/bin/python \
        -DPython3_INCLUDE_DIR=${PYTHON_INCLUDE_DIR} \
        -DBUILD_TESTING=OFF \
        -DBUILD_EXAMPLES=OFF \
        ../src