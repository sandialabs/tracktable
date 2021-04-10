# This is a multi-stage docker build. The intent of this is to minimize the
# size of the final docker image to contain only those components absolutely
# necessary to the compilation and testing of Tracktable.
#
# To that end, the first stage will perform all the builds, which will
# generate .o files and other byproducts of the build process. The end result
# will be a set of wheels and rpms that can be carried forward to the final
# image, without carrying forward the unnecessary build artifacts of projects
# that are not Tracktable. This could also be accomplished with a more diligent
# cleaning process after each build, but the docker multi-stage approach
# allows you to start with a clean slate in a much simpler fashion.

##########################################################################
### BUILD STAGE
##########################################################################
# We'll start from a basic Ubuntu 20.04 image.
FROM cee-gitlab.sandia.gov:4567/innersource/docker/ubuntu:focal as build
WORKDIR /root

ADD scripts /root/scripts
ADD requirements.txt /root/requirements.txt

# Our primary goal is to install as many core packages as we can.
# We want to try and stay as close as we can to the Ubuntu releases.

RUN sh /root/scripts/apt-install-build-dependencies.sh

RUN sh /root/scripts/pip-build-dependencies.sh


##########################################################################
### FINAL STAGE
##########################################################################

FROM cee-gitlab.sandia.gov:4567/innersource/docker/ubuntu:focal

WORKDIR /root

COPY --from=build /wheels /wheels
ADD kitware-archive-latest.asc /root/kitware-archive-latest.asc
ADD scripts /root/scripts
ADD requirements.txt /root/requirements.txt

RUN sh /root/scripts/apt-install-runtime-dependencies.sh
RUN sh /root/scripts/pip-install-dependencies.sh

# Finally, when we're done with our image let's go ahead and clean up all our
# intermediate work that doesn't need to hang around. This will make our
# gitlab-ci docker image a bit smaller.

RUN sh /root/scripts/cleanup.sh

