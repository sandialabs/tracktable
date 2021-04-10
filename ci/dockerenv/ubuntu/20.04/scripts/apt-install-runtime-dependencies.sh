#!/bin/sh

apt-get update
apt-get -y upgrade

ln -fs /usr/share/zoneinfo/America/Denver /etc/localtime
DEBIAN_FRONTEND=noninteractive apt-get -y install \
    tzdata
dpkg-reconfigure --frontend noninteractive tzdata

# Add the kitware repository to obtain the latest cmake version
# We need software-properties-common to get the apt-add-repository command
apt-get -y install software-properties-common
gpg --output /etc/apt/trusted.gpg.d/kitware.gpg --dearmor kitware-archive-latest.asc
rm kitware-archive-latest.asc
apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main'
apt-get update

apt-get -y install \
    libboost-all-dev \
    build-essential \
    libssl-dev \
    wget \
    cmake \
    curl \
    doxygen \
    libgeos-dev \
    graphviz \
    libtool \
    ninja-build \
    pkgconf \
    libproj-dev \
    python3-breathe \
    python3-certifi \
    python3-jupyter-sphinx \
    python3-matplotlib \
    python3-nbsphinx \
    python3-numpy-dev \
    python3-pip \
    python3-pyelftools \
    python3-pykdtree \
    python3-requests \
    python3-scipy \
    python3-shapely \
    python3-six \
    python3-sphinx \
    python3-sphinx-rtd-theme \
    unzip
