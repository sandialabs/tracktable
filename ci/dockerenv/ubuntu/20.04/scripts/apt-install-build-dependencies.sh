#!/bin/sh

apt-get update
apt-get -y upgrade

ln -fs /usr/share/zoneinfo/America/Denver /etc/localtime
DEBIAN_FRONTEND=noninteractive apt-get -y install \
    tzdata
dpkg-reconfigure --frontend noninteractive tzdata

apt-get -y install \
    build-essential \
    wget \
    doxygen \
    libgeos-dev \
    libtool \
    pkgconf \
    libproj-dev \
    lcov \
    python3-breathe \
    python3-certifi \
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
