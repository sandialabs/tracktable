#!/bin/sh

if [ ! -d ../finished_wheels ]; then
    mkdir ../finished_wheels
fi

for PYTHON_IMPLEMENTATION in cp36 cp37 cp38 cp39 cp310; do
    docker build \
           -t tracktable-wheel:${PYTHON_IMPLEMENTATION} \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
           --build-arg CI_JOB_TOKEN=${CI_JOB_TOKEN} \
           --build-arg CI_API_V4_URL=${CI_API_V4_URL} \
           --build-arg CI_PROJECT_ID=${CI_PROJECT_ID} \
           --build-arg HTTPS_PROXY=${SNL_HTTPS_PROXY} \
           --build-arg HTTP_PROXY=${SNL_HTTP_PROXY} \
           --build-arg NO_PROXY=${SNL_NO_PROXY} \
           --build-arg NIGHTLY=${NIGHTLY} \
           --build-arg DEVELOPMENT=${DEVELOPMENT} \
           --build-arg DEV_NUMBER=${DEV_NUMBER} \
           . && \
    docker run \
           --rm \
           --mount type=bind,source="$(pwd)"/../finished_wheels,target=/finished_wheels \
           tracktable-wheel:${PYTHON_IMPLEMENTATION}

done

