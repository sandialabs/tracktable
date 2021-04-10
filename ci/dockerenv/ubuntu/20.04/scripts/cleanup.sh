#!/bin/sh

apt-get update
apt-get autoclean
apt-get --purge -y autoremove
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


