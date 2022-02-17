# Manylinux1-derived image for building and packaging Tracktable
# for use on Linux.

# Download base image
FROM cee-gitlab.sandia.gov:4567/trajectory/tracktable/linux/boost_multipython:latest

ENV CMAKE_VERSION 3.22.2

### ----------------------------------------------------------------------
###
### Step 1: Delete the old CMake since it's too old to be useful
###

# RUN yum -y erase cmake

### ----------------------------------------------------------------------
###
### Step 2: Download and build CMake
###

WORKDIR /opt/src

# This curl command works but due to some proxy issues we're downloading
# boost outside of the container for now and just copying it in
# RUN curl \
#          --location \
#          -o cmake-${CMAKE_VERSION}.tar.gz \
#          https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz

COPY cmake-${CMAKE_VERSION}.tar.gz .

# Build and install CMake and clean up behind ourselves
RUN tar xzf cmake-${CMAKE_VERSION}.tar.gz
WORKDIR /opt/src/cmake-${CMAKE_VERSION}
RUN ./bootstrap --prefix=/usr/local \
&& make -j 8 \
&& make -j 8 install
WORKDIR /opt/src
RUN rm -rf cmake-${CMAKE_VERSION}

ENTRYPOINT [ "/bin/bash" ]

