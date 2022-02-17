#!/bin/sh

PYTHON_IMPLEMENTATION=$1
PYTHON_BASE=/opt/python/${PYTHON_IMPLEMENTATION}-${PYTHON_IMPLEMENTATION}
if [ -e ${PYTHON_BASE}m ]; then
    PYTHON_HOME=${PYTHON_BASE}m
else
    PYTHON_HOME=${PYTHON_BASE}
fi

${PYTHON_HOME}/bin/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy
