#!/bin/sh

echo "Building Tracktable for all supported Python versions."
if [ -d tracktable-copy ]; then
    echo "INFO: Cleaning up after previous run of script."
    rm -rf tracktable-copy
fi

if [ -d tracktable ]; then
    echo "INFO: Removing old copy of Tracktable source."
    rm -rf tracktable
fi


echo "INFO: Copying Tracktable source from current tree."
cp -r ../../../../../tracktable ../../../../../tracktable-copy
mv ../../../../../tracktable-copy ./tracktable

if [ -z ${CI_REGISTRY+x} ]; then
    export SOURCE_IMAGE=boost_multipython_cmake:latest
else
    export SOURCE_IMAGE=${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython_cmake:latest
fi

for PYTHON_IMPLEMENTATION in cp36 cp37 cp38 cp39 cp310; do
   echo "INFO: Building Tracktable for Python version ${PYTHON_IMPLEMENTATION}."
   docker build -t tracktable:${PYTHON_IMPLEMENTATION} \
         -f Dockerfile.build_tracktable \
         --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
         --build-arg NIGHTLY=${NIGHTLY} \
         --build-arg DEVELOPMENT=${DEVELOPMENT} \
         --build-arg DEV_NUMBER=${DEV_NUMBER} \
         --build-arg SOURCE_IMAGE=${SOURCE_IMAGE} \
         .
done

