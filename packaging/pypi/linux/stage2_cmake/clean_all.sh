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

BOOST_MULTIPYTHON_CMAKE_IMAGES=$(docker images --format "${_image_format}" | grep "boost_multipython_cmake")
if [ $? -eq 0 ]; then
    echo "Removing images with Boost and CMake."
    for _image in "${BOOST_MULTIPYTHON_CMAKE_IMAGES}"; do
        docker image remove $_image
    done
fi

# Remove the CMake source code if it's here
find_script_directory
rm -f ${HERE}/cmake-*.tar.gz

