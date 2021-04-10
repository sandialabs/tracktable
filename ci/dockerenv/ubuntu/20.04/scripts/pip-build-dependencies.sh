#!/bin/sh

# Several Tracktable depedencies aren't available or sufficient in Ubuntu
# so we will pip install them.

python3 -m pip wheel \
    --wheel-dir /wheels \
    --find-links /wheels \
    -r requirements.txt
