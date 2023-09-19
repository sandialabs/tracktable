#!/bin/bash
source ./docker.config

# We have to copy this, otherwise it is not inside
# our docker build context
cp ../linux_ci_environment.yml .

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} \
    --build-arg CI_REGISTRY=${CI_REGISTRY} \
    .

if [[ "${TAG_IMAGE_LATEST}" == "true" ]]; then
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
fi

rm linux_ci_environment.yml