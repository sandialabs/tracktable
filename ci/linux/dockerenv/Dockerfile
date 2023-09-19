# We'll start from a preconfigured debian based miniconda image.
ARG CI_REGISTRY
FROM ${CI_REGISTRY}/innersource/docker/miniconda:debian
WORKDIR /root

SHELL ["/bin/bash", "--login", "-c"]

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install curl

RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc
RUN /opt/conda/condabin/conda init bash
RUN /opt/conda/condabin/conda config --add channels conda-forge
ADD linux_ci_environment.yml /root/linux_ci_environment.yml
RUN /opt/conda/condabin/conda env create -f /root/linux_ci_environment.yml
RUN echo "conda activate tracktable-linux-ci" >> /root/.bashrc

# Finally, when we're done with our image let's go ahead and clean up all our
# intermediate work that doesn't need to hang around. This will make our
# gitlab-ci docker image a bit smaller.

ADD build-tracktable-ubuntu2004.sh /root/bin/build-tracktable-ubuntu2004.sh
RUN echo "PATH=\"/root/bin:\${PATH}\"" >> /root/.bashrc
RUN rm -rf /tmp/* /var/tmp/*

SHELL ["/bin/bash", "--login", "-c"]
CMD ["/bin/bash", "-l"]

