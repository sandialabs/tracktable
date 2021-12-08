#!/bin/sh
source ./docker.config

docker push ${IMAGE_NAME}:${IMAGE_TAG}

if [ "${TAG_IMAGE_LATEST}" = true ] ; then
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
    docker push ${IMAGE_NAME}:latest
fi
