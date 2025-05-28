#!/usr/bin/env bash


###
### Remove all the images that could have been created by this stage
###

_image_format='{{.Repository}}:{{.Tag}}'

WHEEL_BUILD_IMAGES=$(docker images --format "${_image_format}" | grep "tracktable-wheel:cp")
if [ $? -eq 0 ]; then
    echo "Removing image with Tracktable wheels."
    for _image in "${WHEEL_BUILD_IMAGES}"; do
        docker image remove $_image
    done
fi
