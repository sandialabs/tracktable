#!/bin/sh

# Change these lines whenever you want to build against a different version
# of Boost
if [ -z ${BOOST_MAJOR_VERSION+x} ]; then
    echo "WARNING: BOOST_MAJOR_VERSION is not set in the environment.  This "
    echo "         usually happens when you're running a build stage in isolation"
    echo "         (for testing or debugging) instead of from the top-level"
    echo "         build_all.sh script.  Defaulting to Boost 1.82.0."

    export BOOST_MAJOR_VERSION=1
    export BOOST_MINOR_VERSION=82
    export BOOST_PATCH_VERSION=0
else
    echo "INFO: Boost version present in environment variables."
fi

BOOST_VERSION_DOTS=${BOOST_MAJOR_VERSION}.${BOOST_MINOR_VERSION}.${BOOST_PATCH_VERSION}
BOOST_VERSION_UNDERSCORES=${BOOST_MAJOR_VERSION}_${BOOST_MINOR_VERSION}_${BOOST_PATCH_VERSION}

BOOST_FILENAME=boost_${BOOST_VERSION_UNDERSCORES}.tar.gz

echo "INFO: Building Boost.Python from Boost ${BOOST_VERSION_DOTS} for all supported Python versions."

echo "INFO: Downloading Boost ${BOOST_VERSION_DOTS}"
curl \
--location \
-o ${BOOST_FILENAME} \
https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION_DOTS}/source/${BOOST_FILENAME}

# The variables SNL_*_PROXY and CUSTOM_SSL_CERT should be set by the CI
# runner configuration.  If they're missing, try to pull them
# from the local environemnt as a reasonable backup.
#
# The idiom "-z ${VARNAME:x}" is Bash for "if this variable is not set
# at all".

if [ -z ${CUSTOM_SSL_CERT:x} ]; then
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

docker build \
       -t boost_downloaded:${BOOST_VERSION_DOTS} \
       -f Dockerfile.download_boost \
       --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
       --build-arg BOOST_VERSION_UNDERSCORES=${BOOST_VERSION_UNDERSCORES} \
       --build-arg SSL_CERT="${CUSTOM_SSL_CERT}" \
       --build-arg HTTPS_PROXY=${SNL_HTTPS_PROXY} \
       --build-arg HTTP_PROXY=${SNL_HTTP_PROXY} \
       --build-arg NO_PROXY=${SNL_NO_PROXY} \
       .


export BOOST_DOWNLOADED_CONTAINER=boost_downloaded:${BOOST_VERSION_DOTS}

for PYTHON_VERSION in cp36m cp37m cp38 cp39 cp310; do
    if [ $PYTHON_VERSION = cp310 ]; then
       PYTHON_VERSION_WITHOUT_M=`echo $PYTHON_VERSION | cut -c 1-5`
    else
       PYTHON_VERSION_WITHOUT_M=`echo $PYTHON_VERSION | cut -c 1-4`
    fi

    echo "INFO: Building Boost.Python for interpreter version ${PYTHON_VERSION}."
    docker build -t \
           boost-${BOOST_VERSION_DOTS}:${PYTHON_VERSION_WITHOUT_M} \
           -f Dockerfile.build_boost \
           --build-arg BOOST_DOWNLOADED_CONTAINER=${BOOST_DOWNLOADED_CONTAINER} \
           --build-arg PYTHON_IMPLEMENTATION=${PYTHON_VERSION_WITHOUT_M}-${PYTHON_VERSION} \
           --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
           --build-arg BOOST_VERSION_UNDERSCORES=${BOOST_VERSION_UNDERSCORES} \
           .
done


echo "INFO: Collecting version-specific Boost.Python libraries into boost_multipython."
docker build \
       -t boost_multipython:latest \
       -f Dockerfile.collect_boost_python \
       --build-arg BOOST_VERSION_DOTS=${BOOST_VERSION_DOTS} \
       --build-arg SOURCE_CONTAINER_NAME=boost-${BOOST_VERSION_DOTS} \
       .

if [ ! -z ${CI_REGISTRY:x} ]; then
    echo "INFO: Uploading boost multipython container to container registry"
    docker tag boost_multipython:latest ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython:latest
    docker push ${CI_REGISTRY}/trajectory/tracktable/linux/boost_multipython:latest
fi

echo "INFO: Done building multi-version Boost.Python container."