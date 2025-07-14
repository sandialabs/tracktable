# Tracktable's Linux CI environment

This document is about how our Linux CI environment works and how you can change the contents (Python version and packages) installed in it.

We assume that you are logged into a machine where you can pull, build, run, and push Docker images that will run on Intel processors.

## The Context

We run continuous integration jobs under Linux using Gitlab's Docker runner.  This has some implications for how we set things up:

- We have to specify a Docker image to be used as a base.  This can either be an image we build ourselves or one located somewhere else.

- Every stage in the CI job (configure, build, test) runs separately and loses all state from previous stages except what we preserve with Gitlab's Artifacts mechanism.

- Like any security-conscious organization, we want to avoid leaking details about our internal network environment.  This includes hostnames for things like Docker registries and web proxies as well as details of our edge infrastructure.

### Building the Image

We build our own Docker image starting from a Miniconda image customized for our local environment.  The scripts in `tracktable/ci/linux/dockerenv` do this:

- `docker-build.sh` builds the image using the specifications in `docker.config` and `Dockerfile`
- `docker-push.sh` pushes the image to its proper home
- `docker-run.sh` calls `docker run -it` on the image
- `docker-run-dev.sh` calls `docker run -it -v` on the image

You will need to set the CI_REGISTRY environment variable before you run any of these scripts.

### Gitlab CI variables

We provide the name of the image to Gitlab using a CI variable `LINUX_CI_DOCKER_IMAGE`.  To change this, go to the Tracktable repository on Gitlab, then Settings > CI/CD on the sidebar, then find "Variables" and click Expand.  (You will need Maintainer access to the repository to do this.).  Make sure the value of `LINUX_CI_DOCKER_IMAGE` matches the full name of the image, including the registry.  You can see that full name by running `docker images`.

It's smartest to have the CI variable point to the `latest` tag on the image so that you can
pick up new versions of the environment without changing the CI variable.

### Conda Environment

The Conda environment is in `tracktable/ci/linux/linux_ci_environment.yml`.

## Adding New Packages

Here's how you update the environment, including adding new packages or updating versions of existing packages.

0. Create an issue in the Tracktable repository for the changes you want to make and a corresponding merge request.

1. Change the conda environment specification in `tracktable/ci/linux/linux_ci_environment.yml`.

2. Update the build number in `tracktable/ci/linux/dockerenv/docker.config`.

3. Set the `CI_REGISTRY` environment variable to the location where the image will live (hostname:port).

4. Run `docker-build.sh`.

5. If that succeeds, run `docker-push.sh`.

6. Commit your changes to `linux_ci_environment.yml` and `docker.config` and push them to the repository.  This will trigger a CI pipeline.

7. If that pipeline fails, debug your environment (including pushing the updated image) until it works.

8. Once the pipeline succeeds, submit the merge request as usual.

## Changing the Base Image

0. Create an issue in the Tracktable repository for the changes you want to make and a corresponding merge request.

1. Change `linux_ci_environment.yml` and `dockerenv/Dockerfile` as needed.

2. Update the build number and, if appropriate, `OS_TYPE` and `OS_VERSION` in `docker.config`.   If you're changing OS type or version or something else on that level, it's best to reset the build number to zero.

3. Set the `CI_REGISTRY` environment variable to the location where the image will live (hostname:port).

4. Run `docker-build.sh`.

5. If that succeeds, run `docker-push.sh`.

6. Change the `LINUX_CI_DOCKER_IMAGE` variable as described above.

7. Commit your changes and push them to the repository.  This will trigger a CI pipeline that should use the new image.

8. If the pipeline fails, debug your environment (including pushing the updated image) until it works.

9.  Once the pipeline succeeds, submit the merge request as usual.

### If the Docker push fails

If `docker-push.sh` fails, you will probably need to run `docker login $CI_REGISTRY`.  Use your Kerberos credentials.  If you're logged into a Mac over SSH, you may have to run `security unlock-keychain` before this will work or else run from a local terminal window.


