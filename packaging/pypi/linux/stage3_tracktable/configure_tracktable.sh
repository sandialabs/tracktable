#!/bin/sh

PYTHON_IMPLEMENTATION=$1
PYTHON_BASE=/opt/python/${PYTHON_IMPLEMENTATION}-${PYTHON_IMPLEMENTATION}
if [ -e ${PYTHON_BASE}m ]; then
    PYTHON_HOME=${PYTHON_BASE}m
else
    PYTHON_HOME=${PYTHON_BASE}
fi

PYTHON_VERSION=`${PYTHON_HOME}/bin/python -c 'from __future__ import print_function; import sys; print("{}.{}".format(sys.version_info.major,sys.version_info.minor))'`
PYTHON_VERSION_MICRO=`${PYTHON_HOME}/bin/python -c 'from __future__ import print_function; import sys; print("{}".format(sys.version_info.micro))'`

if [ -d ${PYTHON_HOME}/include/python${PYTHON_VERSION}m ]; then
    PYTHON_INCLUDE_DIR=${PYTHON_HOME}/include/python${PYTHON_VERSION}m
else
    PYTHON_INCLUDE_DIR=${PYTHON_HOME}/include/python${PYTHON_VERSION}
fi

${PYTHON_HOME}/bin/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org jupyter
export PATH="/opt/_internal/cpython-${PYTHON_VERSION}.${PYTHON_VERSION_MICRO}/bin:$PATH"

cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/src/tracktable/install \
        -DBoost_INCLUDE_DIR=/usr/local/include \
        -DPython3_EXECUTABLE=${PYTHON_HOME}/bin/python \
        -DPython3_INCLUDE_DIR=${PYTHON_INCLUDE_DIR} \
        -DBUILD_TESTING=OFF \
        -DBUILD_EXAMPLES=OFF \
        ../src