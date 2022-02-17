#!/bin/sh

# Change this line if you want to build against some version of Boost other than 1.76.0
BOOST_MINOR_VERSION=76
BOOST_VERSION=1.${BOOST_MINOR_VERSION}.0

echo "Downloading boost ${BOOST_VERSION}"
curl \
       --location \
       -o boost_1_${BOOST_MINOR_VERSION}_0.tar.gz \
       https://boostorg.jfrog.io/artifactory/main/release/1.${BOOST_MINOR_VERSION}.0/source/boost_1_${BOOST_MINOR_VERSION}_0.tar.gz

echo "Building boost container"
docker build \
       -t boost_downloaded:${BOOST_VERSION} \
       -f Dockerfile.download_boost \
       --build-arg BOOST_MINOR_VERSION=${BOOST_MINOR_VERSION} \
       --build-arg HTTPS_INTERCEPTION="${HTTPS_INTERCEPTION}" \
       --build-arg SSL_CERT="${SSL_CERT}" \
       --build-arg HTTPS_PROXY=${SNL_HTTPS_PROXY} \
       --build-arg HTTP_PROXY=${SNL_HTTP_PROXY} \
       --build-arg NO_PROXY=${SNL_NO_PROXY} \
       .

echo "Building python containers"
for PYTHON_VERSION in cp36m cp37m cp38 cp39 cp310; do
    if [ $PYTHON_VERSION = cp310 ]; then
       PYTHON_VERSION_WITHOUT_M=`echo $PYTHON_VERSION | cut -c 1-5`
    else
       PYTHON_VERSION_WITHOUT_M=`echo $PYTHON_VERSION | cut -c 1-4`
    fi
    docker build -t \
           boost-${BOOST_VERSION}:${PYTHON_VERSION_WITHOUT_M} \
           -f Dockerfile.build_boost \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_VERSION_WITHOUT_M}-${PYTHON_VERSION} \
           --build-arg BOOST_MINOR_VERSION=${BOOST_MINOR_VERSION} \
           .
done

echo "Building boost multipython container"
docker build \
       -t boost_multipython:latest \
       -f Dockerfile.collect_boost_python \
       .

echo "Uploading boost multipython container to container registry"
docker tag boost_multipython:latest cee-gitlab.sandia.gov:4567/trajectory/tracktable/linux/boost_multipython:latest
docker push cee-gitlab.sandia.gov:4567/trajectory/tracktable/linux/boost_multipython:latest