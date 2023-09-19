#!/bin/sh

# Several Tracktable depedencies aren't available or sufficient in Ubuntu
# so we will pip install them.

python3 -m pip --no-cache-dir install \
    --find-links /wheels \
    --no-index \
    -r requirements.txt
