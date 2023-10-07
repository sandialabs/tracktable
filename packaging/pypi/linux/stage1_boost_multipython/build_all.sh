#!/usr/bin/env bash

# Exit on error.
set -e

### 
### STARTUP
###
### We get all of our arguments from environment variables rather than on 
### the command line.  Check to see what's there and what's not.
###
### Here's what we look for:
###
### BOOST_MAJOR_VERSION, BOOST_MINOR_VERSION, BOOST_PATCH_VERSION: 
###    What version of Boost should we build?  Defaults to 1.82.0.
###
### SNL_HTTP_PROXY, SNL_HTTPS_PROXY, SNL_NO_PROXY:
###    If set, these variables will provide the values for http_proxy,
###    https_proxy, and no_proxy inside the Docker build.  If not set,
###    we will use the current shell's values for those variables.
###
### CUSTOM_SSL_CERT:
###    This is a certificate to add to the OS list of authorities. 
###    You will need this if you're building in an organization that 
###    does HTTPS interception at the firewall.  You can either include
###    the certificate itself in this variable (as an ASCII string) or
###    provide a filename containing the cert.  No default.
###

DEFAULT_BOOST_MAJOR_VERSION=1
DEFAULT_BOOST_MINOR_VERSION=82
DEFAULT_BOOST_PATCH_VERSION=0

# Change these lines whenever you want to build against a different version
# of Boost
if [ -z ${BOOST_MAJOR_VERSION+x} ]; then
    echo "WARNING: BOOST_MAJOR_VERSION is not set in the environment.  This "
    echo "         usually happens when you're running a build stage in isolation"
    echo "         (for testing or debugging) instead of from the top-level"
    echo "         build_all.sh script.  Defaulting to Boost ${DEFAULT_BOOST_MAJOR_VERSION}.${DEFAULT_BOOST_MINOR_VERSION}.${DEFAULT_BOOST_PATCH_VERSION}."

    BOOST_MAJOR_VERSION=${DEFAULT_BOOST_MAJOR_VERSION}
    BOOST_MINOR_VERSION=${DEFAULT_BOOST_MINOR_VERSION}
    BOOST_PATCH_VERSION=${DEFAULT_BOOST_PATCH_VERSION}
else
    echo "INFO: Boost version present in environment variables."
fi

BOOST_VERSION_DOTS=${BOOST_MAJOR_VERSION}.${BOOST_MINOR_VERSION}.${BOOST_PATCH_VERSION}
BOOST_VERSION_UNDERSCORES=${BOOST_MAJOR_VERSION}_${BOOST_MINOR_VERSION}_${BOOST_PATCH_VERSION}

# The variables SNL_*_PROXY and CUSTOM_SSL_CERT should be set by the CI
# runner configuration.  If they're missing, try to pull them
# from the local environemnt as a reasonable backup.
#
# The idiom "-z ${VARNAME:x}" is Bash for "if this variable is not set
# at all".

if [ -z "${CUSTOM_SSL_CERT:x}" ]; then
    echo "INFO: No custom SSL certificate found. Using OS default."
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
       echo "INFO: No HTTP proxy environment variable set.  Using OS default."
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
       echo "INFO: No HTTPS proxy environment variable set.  Using OS default."
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
       echo "INFO: Proxy exception environment variable is not set.  Using OS default."
    fi
else
    echo "INFO: Proxy exceptions provided by build host."
fi

###
### Housekeeping: load parsing functions
###

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

# Load parsing functions from external library
find_script_directory
source ${HERE}/../functions/parsing.sh

echo "INFO: Building Boost.Python from Boost ${BOOST_VERSION_DOTS} for all supported Python versions."

### 
### Download Boost source if we don't have it already
###

BOOST_FILENAME=boost_${BOOST_VERSION_UNDERSCORES}.tar.gz
if [ ! -f ${BOOST_FILENAME} ]; then
    echo "INFO: Downloading Boost ${BOOST_VERSION_DOTS}"
    curl \
       --location \
       -o ${BOOST_FILENAME} \
       https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION_DOTS}/source/${BOOST_FILENAME}
else
    echo "INFO: Boost source already downloaded."
fi

###
### Save source code in a container along with the SSL/proxy environment.
### We'll clean up this image when we're done.
###
BOOST_DOWNLOADED_CONTAINER=boost_downloaded:${BOOST_VERSION_DOTS}

docker build \
       -t ${BOOST_DOWNLOADED_CONTAINER} \
       -f Dockerfile.download_boost \
       --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
       --build-arg BOOST_VERSION_UNDERSCORES=${BOOST_VERSION_UNDERSCORES} \
       --build-arg SSL_CERT="${CUSTOM_SSL_CERT}" \
       --build-arg HTTPS_PROXY=${SNL_HTTPS_PROXY} \
       --build-arg HTTP_PROXY=${SNL_HTTP_PROXY} \
       --build-arg NO_PROXY=${SNL_NO_PROXY} \
       .


###
### Find all of the CPython implementations in our container.
###

AVAILABLE_PYTHON_IMPLEMENTATIONS=$(docker run -ti --rm ${BOOST_DOWNLOADED_CONTAINER} '/bin/ls /opt/python | grep cp')

# This image will be used as the basis for the final output of this stage.
# They're all the same except for the selected Python interpreter
# that was used to build libboost_python.so, so there's no need to do anything
# more complex than just selecting the first one.
BASE_MULTIPYTHON_IMAGE=not_yet_defined

# This is where we'll save libboost binaries as we build them
if [ -d libboost_python_tmp ]; then
    echo "INFO: Deleting existing libboost_python binaries."
    rm -rf libboost_python_tmp
fi
mkdir libboost_python_tmp


###
### Loop through all of the available CPython implementations in this container and
### build Boost for each one.
###

for PYTHON_IMPLEMENTATION in ${AVAILABLE_PYTHON_IMPLEMENTATIONS}; do
    trim "${PYTHON_IMPLEMENTATION}"
    PYTHON_IMPLEMENTATION="${_trimmed_string}"
    
    parse_python_version "${PYTHON_IMPLEMENTATION}"
    PYTHON_VERSION=${_python_version}
    PYTHON_ABI=${_python_abi}
    
    DESTINATION_IMAGE_NAME=boost-${BOOST_VERSION_DOTS}:${PYTHON_VERSION}

    if [ "${BASE_MULTIPYTHON_IMAGE}" = "not_yet_defined" ]; then
        BASE_MULTIPYTHON_IMAGE=${DESTINATION_IMAGE_NAME}
    fi

    echo "INFO: Building Boost.Python for interpreter version ${PYTHON_VERSION}."
    docker build \
           -t ${DESTINATION_IMAGE_NAME} \
           -f Dockerfile.build_boost \
           --build-arg BOOST_DOWNLOADED_CONTAINER=${BOOST_DOWNLOADED_CONTAINER} \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION} \
           --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
           --build-arg BOOST_VERSION_UNDERSCORES=${BOOST_VERSION_UNDERSCORES} \
           .

    echo "INFO: Copying Boost.Python libraries for ${PYTHON_VERSION} to temporary directory."
    CREATED_NAME=$(docker create ${DESTINATION_IMAGE_NAME})
    docker cp ${CREATED_NAME}:/boost_python/boost_python_libraries.tar ./libboost_python_tmp
    docker rm ${CREATED_NAME}
    
    pushd libboost_python_tmp
    tar xf boost_python_libraries.tar && rm boost_python_libraries.tar
    popd
done

### 
### Collect all of the compiled libboost_python libraries into a single image.
###

echo "INFO: Collecting all Boost Python compiled libraries for final image."
docker build \
    -t boost_multipython:latest \
    --build-arg BASE_MULTIPYTHON_IMAGE=${BASE_MULTIPYTHON_IMAGE} \
    -f Dockerfile.collect_boost_python \
    .

###    
### Cleanup: we no longer need the individual builds or the Boost source code.
###
for PYTHON_IMPLEMENTATION in ${AVAILABLE_PYTHON_IMPLEMENTATIONS}; do
    parse_python_version "${PYTHON_IMPLEMENTATION}"
    PYTHON_VERSION=${_python_version}

    DESTINATION_IMAGE_NAME=boost-${BOOST_VERSION_DOTS}:${PYTHON_VERSION}
    docker rmi ${DESTINATION_IMAGE_NAME}
done

docker rmi boost_downloaded:${BOOST_VERSION_DOTS}
rm ${BOOST_FILENAME}
rm -rf libboost_python_tmp


###
### Finally, if we're being called from a CI job, we may have a registry URL
### to which we can upload our shiny new container.
###

if [ ! -z ${CI_REGISTRY:x} ]; then
    echo "INFO: Uploading boost multipython container to container registry"
    docker tag boost_multipython:latest ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython:latest
    docker push ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython:latest
fi
