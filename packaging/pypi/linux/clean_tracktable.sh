#!/bin/sh

# This script removes the Docker images containing the Tracktable
# build trees and wheels.  It makes way for a new build of a
# different version.

for version in cp35 cp36 cp37 cp38 cp39 cp310; do
    docker rmi tracktable:${version} tracktable-wheel:${version}
done

