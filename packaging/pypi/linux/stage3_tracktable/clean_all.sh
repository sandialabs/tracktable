#!/usr/bin/env bash

# Utility function: where is this script?  We need this to get to our
# function library.
#
# Sets the variable HERE.
#
# From https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script

find_script_directory() {
    local _source="${BASH_SOURCE[0]}"
    while [ -L "${_source}" ]; do
        # Resolve _source until the file is no longer a symlink.
        _dir=$( cd -P "$(dirname "${_source}" )" >/dev/null 2>&1 && pwd )
        _source=$(readlink "$_source")
    done
    export HERE=$( cd -P "$(dirname "${_source}")" >/dev/null 2>&1 && pwd )
}


###
### Remove all the images that could have been created by this stage
###

_image_format='{{.Repository}}:{{.Tag}}'

ALL_IMAGES=$(docker images --format "${_image_format}")

TRACKTABLE_BUILD_IMAGES=$(docker images --format "${_image_format}" | grep "tracktable:cp")
if [ $? -eq 0 ]; then
    echo "Removing image with Tracktable build trees."
    for _image in "${TRACKTABLE_BUILD_IMAGES}"; do
        docker image remove $_image
    done
fi

###
### Remove the Tracktable source code if it's still there
###

# It is vitally important that we only remove the source code
# in the directory containing this script.
find_script_directory
pushd $HERE
if [ -d tracktable ]; then
    echo "Removing Tracktable source code."
    rm -rf tracktable
fi

