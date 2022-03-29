#!/bin/bash
source ./docker.config

docker run -it -v ${LOCAL_SOURCE_PATH}:${IMAGE_SOURCE_MOUNT} ${IMAGE_NAME}:${IMAGE_TAG}
