#!/bin/sh

echo "Getting a copy of the current build's source code"
cp -r ../../../../../tracktable ../../../../../tracktable-copy
mv ../../../../../tracktable-copy .
mv tracktable-copy tracktable

echo "Building tracktable for all of the python implementations"
for PYTHON_IMPLEMENTATION in cp36 cp37 cp38 cp39 cp310; do
   docker build -t tracktable:${PYTHON_IMPLEMENTATION} \
         -f Dockerfile.build_tracktable \
         --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
         --build-arg NIGHTLY=${NIGHTLY} \
         --build-arg DEVELOPMENT=${DEVELOPMENT} \
         --build-arg DEV_NUMBER=${DEV_NUMBER} \
         --build-arg CI_REGISTRY=${CI_REGISTRY} \
         .
done

