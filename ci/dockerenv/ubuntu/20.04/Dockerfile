# We'll start from a basic Ubuntu 20.04 image.
FROM cee-gitlab.sandia.gov:4567/innersource/docker/ubuntu:focal as build
WORKDIR /root

ARG MINICONDA_VERSION=latest
ENV MINICONDA_URL=https://repo.continuum.io/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh

SHELL ["/bin/bash", "--login", "-c"]

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install curl

RUN curl -L -\# ${MINICONDA_URL} -o /root/miniconda.sh
RUN /bin/bash /root/miniconda.sh -b
RUN rm /root/miniconda.sh
RUN echo "source /root/miniconda3/etc/profile.d/conda.sh" >> /root/.bashrc
RUN /root/miniconda3/condabin/conda init bash
RUN /root/miniconda3/condabin/conda config --set proxy_servers.http http://proxy.sandia.gov:80
RUN /root/miniconda3/condabin/conda config --set proxy_servers.https http://proxy.sandia.gov:80
RUN /root/miniconda3/condabin/conda config --set ssl_verify /etc/ssl/certs/ca-certificates.crt
RUN /root/miniconda3/condabin/conda config --add channels conda-forge
RUN /root/miniconda3/condabin/conda update -qy conda
ADD tracktable_dev_environment.yml /root/tracktable_dev_environment.yml
RUN /root/miniconda3/condabin/conda env create -f /root/tracktable_dev_environment.yml
RUN echo "conda activate tracktable-dev" >> /root/.bashrc

# Finally, when we're done with our image let's go ahead and clean up all our
# intermediate work that doesn't need to hang around. This will make our
# gitlab-ci docker image a bit smaller.

ADD build-tracktable-ubuntu2004 /root/bin/build-tracktable-ubuntu2004
RUN echo "PATH=\"/root/bin:\${PATH}\"" >> /root/.bashrc
RUN apt-get autoclean
RUN apt-get --purge -y autoremove
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

SHELL ["/bin/bash", "--login", "-c"]
CMD ["/bin/bash", "-l"]

