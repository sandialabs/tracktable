#!/bin/sh
source ./docker.config

docker run -it ${IMAGE_NAME}:${IMAGE_TAG}
