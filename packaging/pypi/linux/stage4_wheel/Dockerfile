ARG TRACKTABLE_BUILD_CONTAINER
ARG PYTHON_IMPLEMENTATION

FROM ${TRACKTABLE_BUILD_CONTAINER}


ENV PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION}

ARG NIGHTLY
ENV NIGHTLY=${NIGHTLY}

ARG DEVELOPMENT
ENV DEVELOPMENT=${DEVELOPMENT}

ARG DEV_NUMBER
ENV DEV_NUMBER=${DEV_NUMBER}

ARG CI_JOB_TOKEN
ARG CI_API_V4_URL
ARG CI_PROJECT_ID
ENV CI_JOB_TOKEN=${CI_JOB_TOKEN}
ENV CI_API_V4_URL=${CI_API_V4_URL}
ENV CI_PROJECT_ID=${CI_PROJECT_ID}

RUN /opt/python/${PYTHON_IMPLEMENTATION}/bin/pip config set global.trusted-host "pypi.org pypi.python.org files.pythonhosted.org"

WORKDIR /opt/src/tracktable/build
RUN /opt/python/${PYTHON_IMPLEMENTATION}/bin/pip install \
         --trusted-host pypi.python.org \
         --trusted-host pypi.org \
         --trusted-host files.pythonhosted.org \
         packaging build python-build wheel \
    && VERBOSE=1 make wheel \
    && mkdir /finished_wheels \
    && cp /opt/src/tracktable/build/wheel/wheelhouse/*.whl /finished_wheels

ENTRYPOINT ["/bin/bash", "-c", "-l"]




