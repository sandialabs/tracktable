# Find desired Python interpreters in Manylinux image
#
# In Manylinux images, the Python interpreters are stored in
# /opt/python/.  There are quite a few there -- here's the
# list from manylinux2014_x86_64:
#
# cp310-cp310  cp311-cp311  cp312-cp312  cp313-cp313
# cp313-cp313t  cp36-cp36m  cp37-cp37m  cp38-cp38
# cp39-cp39  pp310-pypy310_pp73  pp311-pypy311_pp73
#
# We need a way to filter that list down to just those that
# match a list of desired versions.
#
# We assume the user has given us a list of versions they want:
#
# PYTHON_VERSIONS="3.9 3.10 3.11 3.12 3.13"
#
# We also assume that if they want a particular ABI flag
# (such as 't') they'll say so with '3.13t'.
#
# Finally, we assume that we're only building for CPython.
#
# Here's how to use the function find_interpreters in this
# file:
#
# find_interpreters "$PYTHON_VERSIONS" IMAGE_NAME
#
# The first argument MUST be a single string.
#
# It will set the variable INTERPRETER_DIRECTORY_NAMES.  If
# you pass it the list above (3.9 through 3.13), you will
# get back a list containing cp39-cp39, cp310-cp310,
# cp311-cp311, cp312-cp312, and cp313-cp313, but not cp313-cp313t.
#

_find_script_directory() {
    local _source="${BASH_SOURCE[0]}"
    while [ -L "${_source}" ]; do
        # Resolve _source until the file is no longer a symlink.
        _dir=$( cd -P "$(dirname "${_source}" )" >/dev/null 2>&1 && pwd )
        _source=$(readlink "$_source")
    done
    export HERE=$( cd -P "$(dirname "${_source}")" >/dev/null 2>&1 && pwd )
}


# Inputs:
#
# First argument: space-delimited list of desired Python versions.
#                 THIS MUST BE A SINGLE STRING.  You may need to
#                 quote it with "${PYTHON_VERSIONS}" in the caller.
# Second argument: name of Docker image to query
#
# Outputs:
#
# INTERPRETER_DIRECTORIES: Newline-delimited list (as Bash expects)
# of directories in /opt/python containing versions we think will match

function find_interpreters {
   local _desired_versions="$1"
   local _image_name="$2"

   local _interpreter_dirs_in_image=$( \
        docker run -ti --rm \
        ${_image_name} \
        "cd /opt/python && ls -1 -d cp*"
    )
    #echo "DEBUG: Interpreters in image: ${_interpreter_dirs_in_image}"

    _interpreter_dirnames=$(\
        python ${HERE}/../functions/match_versions_to_tags.py \
                                   "${_interpreter_dirs_in_image}" \
                                   "${_desired_versions}" \
    )

    #echo "DEBUG: Found interpreters: ${_interpreter_dirnames}"
    export INTERPRETER_DIRECTORIES=${_interpreter_dirnames}
}

unset -f _find_script_directory

