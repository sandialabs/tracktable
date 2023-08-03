#!/bin/sh

echo "Building wheels for all supported Python versions."

# if [ ! -d /tmp/finished_wheels ]; then
#     mkdir /tmp/finished_wheels
#     chmod 777 /tmp/finished_wheels
# fi

if [ ! -d ../finished_wheels ]; then
    mkdir ../finished_wheels
fi

for PYTHON_IMPLEMENTATION in cp36 cp37 cp38 cp39 cp310; do
    echo "INFO: Saving wheel for Python version ${PYTHON_IMPLEMENTATION}."
    export CONTAINER_NAME=tracktable-wheel:${PYTHON_IMPLEMENTATION}
    docker build \
           -t ${CONTAINER_NAME} \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
           --build-arg CI_JOB_TOKEN=${CI_JOB_TOKEN} \
           --build-arg CI_API_V4_URL=${CI_API_V4_URL} \
           --build-arg CI_PROJECT_ID=${CI_PROJECT_ID} \
           --build-arg NIGHTLY=${NIGHTLY} \
           --build-arg DEVELOPMENT=${DEVELOPMENT} \
           --build-arg DEV_NUMBER=${DEV_NUMBER} \
           .
    export CREATED_NAME=$(docker create ${CONTAINER_NAME})
    docker cp ${CREATED_NAME}:/finished_wheels ../finished_wheels/${PYTHON_IMPLEMENTATION}
    docker rm ${CREATED_NAME}
    mv ../finished_wheels/${PYTHON_IMPLEMENTATION}/*.whl ../finished_wheels
    rmdir ../finished_wheels/${PYTHON_IMPLEMENTATION}

    # docker run \
    #        --rm \
    #        --mount type=bind,source=/tmp/finished_wheels,target=/finished_wheels \
    #        tracktable-wheel:${PYTHON_IMPLEMENTATION}

done

#cp /tmp/finished_wheels/*.whl ../finished_wheels && rm -rf /tmp/finished_wheels
