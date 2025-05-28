#!/usr/bin/env bash

###
### stage0_base_image/build_all.sh
###
### Configure the base image that all of our later builds will use
### as an environment.
###
### Parameters are supplied using environment variables.  Here's
### what we look for:
###
### BASE_IMAGE: Defaults to quay.io/pypa/manylinux2014_x86_64.
###
### PIP_PYTHON_INTERPRETER:
###    No default.  If set, this will be used inside the base image
###    to configure PyPI mirror settings with pip.
###
### PIP_INDEX:
###    No default.  If set, this will be used inside the base image
###    to configure PyPI mirror settings with pip.
###
### PIP_INDEX_URL:
###    No default.  If set, this will be used inside the base image
###    to configure PyPI mirror settings with pip.
###
### SNL_HTTP_PROXY, SNL_HTTPS_PROXY, SNL_NO_PROXY:
###    If set, these variables will provide the values for http_proxy,
###    https_proxy, and no_proxy inside the Docker build.  If not set,
###    we will use the current shell's values for http_proxy, https_proxy,
###    and no_proxy.
###
### CUSTOM_SSL_CERT:
###    This is a certificate to add to the OS list of authorities.
###    You will need this if you're building in an organization that
###    does HTTPS interception at the firewall.  You can either include
###    the certificate itself in this variable (as an ASCII string) or
###    provide a filename containing the cert.  No default.
###



### ---------------------------------------------------------------------
###
### Housekeeping: load parsing functions
###
### ---------------------------------------------------------------------

# Utility function: where is this script?  We need this to get to our
# function library.
#
# Sets the variable HERE.
#
# From https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script

find_script_directory() {
    local _source="${BASH_SOURCE[0]}"
    while [ -L "${_source}" ]; do
        # Resolve _source until the file is no longer a symlink.
        _dir=$( cd -P "$(dirname "${_source}" )" >/dev/null 2>&1 && pwd )
        _source=$(readlink "$_source")
    done
    export HERE=$( cd -P "$(dirname "${_source}")" >/dev/null 2>&1 && pwd )
}

# This sets $HERE
find_script_directory
source ${HERE}/../functions/parsing.sh
source ${HERE}/../defaults.sh



### ---------------------------------------------------------------------
###
### Argument parsing
###
### ---------------------------------------------------------------------

###
### Get the name of the Docker image that will be the base for
### our entire build environment
###

if [ -z ${BASE_IMAGE+x} ]; then
    echo "INFO: BASE_IMAGE not specified.  Defaulting to "
    echo "      ${DEFAULT_BASE_IMAGE} for build container."
    BASE_IMAGE=${DEFAULT_BASE_IMAGE}
else
    echo "INFO: Using ${BASE_IMAGE} as build container."
fi

###
### Get SSL and proxy parameters from more environment variables.  These
### do not have default values.
###

# The variables SNL_*_PROXY and CUSTOM_SSL_CERT should be set by the CI
# runner configuration.  If they're missing, try to pull them
# from the local environemnt as a reasonable backup.
#
# The idiom "-z ${VARNAME:x}" is Bash for "if this variable is not set
# at all".

if [ -z "${CUSTOM_SSL_CERT:x}" ]; then
    echo "INFO: No custom SSL certificate found. Using OS defaults."
else
    echo "INFO: Custom SSL certificate provided by build host."
    if [ "${#CUSTOM_SSL_CERT}" -le 500 ]; then
        echo "INFO: Custom SSL certificate is very short.  Interpreting as filename."
        export CUSTOM_SSL_CERT=$(cat ${CUSTOM_SSL_CERT})
    else
        echo "INFO: Custom SSL certificate in environment variable may be the text of the certificate itself."
    fi
fi

# The proxy variables should be all lower case.  We'll check those first.
# It's still common to have upper-case versions, though, so we'll just
# deal with it if they're all we have.

if [ -z ${SNL_HTTP_PROXY:x} ]; then
    if [ ! -z ${http_proxy:x} ]; then
        export SNL_HTTP_PROXY=${http_proxy}
    elif [ ! -z ${HTTP_PROXY:x} ]; then
        export SNL_HTTP_PROXY=${HTTP_PROXY}
    else
        echo "INFO: No HTTP proxy environment variable set."
        if [ ! -z ${SNL_HTTP_PROXY+x} ]; then
            echo "Using current shell's http_proxy variable ('${SNL_HTTP_PROXY}')."
        fi
    fi
else
    echo "INFO: HTTP proxy provided by build host."
fi

if [ -z ${SNL_HTTPS_PROXY:x} ]; then
    if [ ! -z ${https_proxy:x} ]; then
        export SNL_HTTPS_PROXY=${https_proxy}
    elif [ ! -z ${HTTPS_PROXY:x} ]; then
        export SNL_HTTPS_PROXY=${HTTPS_PROXY}
    else
        echo "INFO: No HTTPS proxy environment variable set."
        if [ ! -z ${SNL_HTTPS_PROXY+x} ]; then
           echo "INFO: Using current shell's https_proxy variable ('${SNL_HTTPS_PROXY}')."
        fi
    fi
else
    echo "INFO: HTTPS proxy provided by build host."
fi

if [ -z ${SNL_NO_PROXY:x} ]; then
    if [ ! -z ${no_proxy:x} ]; then
        export SNL_NO_PROXY=${no_proxy}
    elif [ ! -z ${NO_PROXY:x} ]; then
        export SNL_NO_PROXY=${NO_PROXY}
    else
        echo "INFO: No no_proxy environment variable set."
        if [ ! -z ${SNL_NO_PROXY+x} ]; then
            echo "INFO: Using current shell's no_proxy variable ('${SNL_NO_PROXY}')."
        fi
    fi
else
    echo "INFO: Proxy exceptions provided by build host."
fi

###
### Get settings for PyPI mirror (if any)
###

if [ ! -z ${PIP_INDEX+x} ]; then
    if [ -z ${PIP_INDEX_URL+x} ]; then
        echo "ERROR: You must specify both PIP_INDEX and PIP_INDEX_URL"
        echo "       in order to set a PyPI mirror."
        exit 5
    fi
    if [ -z ${PIP_PYTHON_INTERPRETER+x} ]; then
        if [[ ${BASE_IMAGE} == *manylinux* ]]; then
            echo "ERROR: If you are using a PyPI mirror with a Manylinux"
            echo "       image you MUST specify PIP_PYTHON_INTERPRETER."
            echo "       The Python in /usr/bin does not have pip installed."
            exit 6
        fi

        echo "INFO: PIP_PYTHON_INTERPRETER was not defined in the"
        echo "      environment.  Defaulting to /usr/bin/python."
        PIP_PYTHON_INTERPRETER=${DEFAULT_PIP_PYTHON_INTERPRETER}
    fi

    echo "INFO: Configuring PyPI index URL for base image."
    echo "INFO: Index will be set to ${PIP_INDEX}"
    echo "INFO: Index URL will be set to ${PIP_INDEX_URL}"
else
    echo "INFO: Build container will fetch packages from pypi.org."
    PIP_INDEX=${DEFAULT_PIP_INDEX}
    PIP_INDEX_URL=${DEFAULT_PIP_INDEX_URL}
fi


### ---------------------------------------------------------------------
###
### Build and go
###
### ---------------------------------------------------------------------

echo "INFO: Building base container with Pip and SSL settings."

docker build \
       -t tracktable_build_base \
       -f Dockerfile.configure_pip_and_ssl \
       --build-arg BASE_IMAGE="${BASE_IMAGE}" \
       --build-arg SSL_CERT="${CUSTOM_SSL_CERT}" \
       --build-arg HTTPS_PROXY=${SNL_HTTPS_PROXY} \
       --build-arg HTTP_PROXY=${SNL_HTTP_PROXY} \
       --build-arg NO_PROXY=${SNL_NO_PROXY} \
       --build-arg PIP_PYTHON_INTERPRETER=${PIP_PYTHON_INTERPRETER} \
       --build-arg PIP_INDEX=${PIP_INDEX} \
       --build-arg PIP_INDEX_URL=${PIP_INDEX_URL} \
       .
