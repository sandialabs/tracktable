#!/usr/bin/env bash

# Regenerate all of the Conda environments in the source
# tree using the files in
# tracktable/conda_environments/components.  This will
# create the following files:
#
# conda_environments/tracktable_dev_{windows,linux,macos} -
# Environment suitable for regular builds or CI runs using
# the oldest supported version of Python
#
# conda_environments/versioned/{windows,linux,macos}/tracktable_dev_python3.{9,10,11,12,13}.yml -
# Development environments with specific versions of Python for
# each platform.
#

# Exit on error
set -e

# Note: This is not a universal solution.  There are corner cases such as
# the last component of the path having newlines or being a symbolic link
# that it will not catch.  However, for this applicatin inside a Git
# repository, it works just fine.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

COMPONENT_DIR=${SCRIPT_DIR}/components
declare -a ALL_PYTHON_VERSIONS=(3.9 3.10 3.11 3.12 3.13)

# Although Python 3.9 doesn't go end-of-life until October 2025, we're
# migrating to 3.10 now (end of July 2025) because 3.9 isn't working
# properly on Windows.
MINIMUM_PYTHON_VERSION=3.10
declare -a PLATFORMS=("linux" "windows" "macos")

TMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t "tracktable_scratch")

echo "Creating per-platform and per-Python-version environments."
echo ""

for _platform in ${PLATFORMS[@]}; do
  for _python_version in ${ALL_PYTHON_VERSIONS[@]}; do
    echo "Creating versioned/${_platform}/tracktable-dev-python${_python_version}.yml"
    conda-merge \
      ${COMPONENT_DIR}/common.yml \
      ${COMPONENT_DIR}/${_platform}.yml \
      ${COMPONENT_DIR}/python${_python_version}.yml \
      > ${TMPDIR}/body.yml
    cat ${COMPONENT_DIR}/header.yml ${TMPDIR}/body.yml \
      > ${SCRIPT_DIR}/versioned/${_platform}/tracktable-dev-python${_python_version}.yml
    rm ${TMPDIR}/body.yml
  done
done

echo ""
echo "Done creating versioned environment files."
echo "Creating top-level dev environment files."
echo ""

for _platform in ${PLATFORMS[@]}; do
  _src_environment_name=tracktable-dev-python${MINIMUM_PYTHON_VERSION}
  _dst_environment_name=tracktable-dev
  _srcfile=versioned/${_platform}/${_src_environment_name}.yml
  _dstfile=${SCRIPT_DIR}/tracktable-dev-${_platform}.yml

  echo "Creating ${_dstfile}"
  cp ${_srcfile} ${_dstfile}
  sed -i .backup -e "s/name: ${_src_environment_name}/name: ${_dst_environment_name}/g" ${_dstfile}
  rm ${_dstfile}.backup
done

echo ""
echo "All done.  Remember to commit any environment files that were changed."
