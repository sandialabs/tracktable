#!/usr/bin/env bash

#
# Examine the HTTP_PROXY, HTTPS_PROXY, and NO_PROXY environment
# variables.  If set, add them to /etc/bashrc so that all future
# shells will inherit them.
#

if [ ! -z ${HTTP_PROXY+x} ]; then
    echo "http_proxy=${HTTP_PROXY}" >> /etc/bashrc
    echo "HTTP_PROXY=${HTTP_PROXY}" >> /etc/bashrc
fi

if [ ! -z ${HTTPS_PROXY+x} ]; then
    echo "https_proxy=${HTTPS_PROXY}" >> /etc/bashrc
    echo "HTTPS_PROXY=${HTTPS_PROXY}" >> /etc/bashrc
fi

if [ ! -z ${NO_PROXY+x} ]; then
    echo "https_proxy=${HTTPS_PROXY}" >> /etc/bashrc
    echo "HTTPS_PROXY=${HTTPS_PROXY}" >> /etc/bashrc
fi

