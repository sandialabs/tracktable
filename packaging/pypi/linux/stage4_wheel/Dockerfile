ARG PYTHON_IMPLEMENTATION
FROM tracktable:${PYTHON_IMPLEMENTATION}

ENV PYTHON_IMPLEMENTATION=${PYTHON_IMPLEMENTATION}
ARG TRACKTABLE_VERSION=1.6.0
ENV TRACKTABLE_VERSION=${TRACKTABLE_VERSION}

ARG NIGHTLY
ENV NIGHTLY=${NIGHTLY}

ARG CI_JOB_TOKEN
ARG CI_API_V4_URL
ARG CI_PROJECT_ID
ENV CI_JOB_TOKEN=${CI_JOB_TOKEN}
ENV CI_API_V4_URL=${CI_API_V4_URL}
ENV CI_PROJECT_ID=${CI_PROJECT_ID}

ARG HTTPS_PROXY
ARG HTTP_PROXY
ARG NO_PROXY
ENV https_proxy=${HTTPS_PROXY}
ENV http_proxy=${HTTP_PROXY}
ENV no_proxy=${NO_PROXY}

WORKDIR /opt/src/tracktable/build
RUN /opt/python/${PYTHON_IMPLEMENTATION}-${PYTHON_IMPLEMENTATION}*/bin/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org packaging \
&& make install \
&& make wheel

ENTRYPOINT ["/bin/sh", "-c"]
CMD [ "/bin/cp /opt/src/tracktable/build/wheel/wheelhouse/*.whl /finished_wheels" ]




