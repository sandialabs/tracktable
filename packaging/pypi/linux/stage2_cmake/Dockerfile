# Manylinux1-derived image for building and packaging Tracktable
# for use on Linux.

# Download base image
ARG CMAKE_VERSION
ARG SOURCE_IMAGE

FROM ${SOURCE_IMAGE}

ARG CMAKE_VERSION
ENV cmake_version=${CMAKE_VERSION}

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

COPY cmake-${cmake_version}.tar.gz .

# Build and install CMake and clean up behind ourselves
RUN tar xzf cmake-${cmake_version}.tar.gz
WORKDIR /opt/src/cmake-${cmake_version}
RUN ./bootstrap --prefix=/usr/local \
&& make -j 4 \
&& make install
WORKDIR /opt/src
RUN rm -rf cmake-${cmake_version}

# The "-c -l" is necessary to get an actual login shell. If you
# skip it, you will often get an error from Docker like
# "cannot execute binary file".

ENTRYPOINT [ "/bin/bash", "-c", "-l" ]

