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

BOOST_DOWNLOADED_IMAGE=$(docker images --format "${_image_format}" | grep "boost_downloaded")
if [ $? -eq 0 ]; then
    echo "Removing image with downloaded Boost source code."
    for _image in "${BOOST_DOWNLOADED_IMAGE}"; do
        docker image remove $_image
    done
fi

SINGLE_BUILD_BOOST_IMAGES=$(docker images --format "${_image_format}" | grep "boost-")
if [ $? -eq 0 ]; then
    echo "Removing images containing Boost build trees."
    for _image in "${SINGLE_BUILD_BOOST_IMAGES}"; do
        docker image remove $_image
    done
fi

MULTIPYTHON_IMAGES=$(docker images --format "${_image_format}" | grep "boost_multipython" | grep -v cmake)
if [ $? -eq 0 ]; then
    echo "Removing boost_multipython images."
    for _image in "${MULTIPYTHON_IMAGES}"; do
        docker image remove $_image
    done
fi

###
### Remove the Boost source code if it's still there
###

find_script_directory
rm -f ${HERE}/boost*.tar.gz

