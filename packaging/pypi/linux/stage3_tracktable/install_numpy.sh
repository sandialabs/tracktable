#!/bin/sh

IMPLEMENTATION=$1
PYTHON_HOME=/opt/python/${IMPLEMENTATION}

if [ ! -f ${PYTHON_HOME}/bin/pip ]; then
    echo "ERROR: install_numpy.sh: Pip not found at expected path ${PYTHON_HOME}/bin/pip"
    exit 1
fi

echo "INFO: Installing NumPy for Python implementation ${IMPLEMENTATION}"
${PYTHON_HOME}/bin/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy
