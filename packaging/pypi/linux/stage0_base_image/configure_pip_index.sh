#!/usr/bin/env bash

# Configure global.index and global.index-url with Pip.

_python_interpreter=$1
_pip_index=$2
_pip_index_url=$3

if [ ! -z ${_pip_index+x}
     -a ${_pip_index} != "__default__"
     -a ${_pip_index_url} != "__default__" ]; then

    ${_python_interpreter} -m pip config set global.index ${_pip_index}
    ${_python_interpreter} -m pip config set global.index-url ${_pip_index_url}
    echo "INFO: Pip index and index-url set succesfully."
else
    echo "INFO: No need to set Pip index or index-url."
fi


