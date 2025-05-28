# Useful Bash functions that we use in building wheels


# Trim leading and trailing whitespace.
#
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
#
# Output variable: _trimmed_string
trim() {
    local var="$*"
    # remove leading whitespace
    var="${var#"${var%%[![:space:]]*}"}"
    # remove trailing whitespace
    var="${var%"${var##*[![:space:]]}"}"
    export _trimmed_string="${var}"
}

# Parse Python implementation into version and options.
# For example, 'cp37-cp37m' -> 'cp37' and 'cp37m'.
#
# Output variables:
# _python_version, _python_abi

parse_python_version() {
    local _full_version="$*"
    trim "${_full_version}"
    _full_version=${_trimmed_string}

    python_version_re='^([[:alpha:]]+)([[:digit:]]+)([[:alpha:]]*)-([[:alpha:]]+)([[:digit:]]+)([[:alpha:]]*)$'
    if [[ ${_full_version} =~ $python_version_re ]]; then
        export _python_platform=${BASH_REMATCH[4]}
        export _python_version=${BASH_REMATCH[5]}
        export _python_abi=${BASH_REMATCH[6]}
    else
        echo "ERROR: Couldn't parse Python implementation name: ${_full_version}"
        exit 3
    fi
}

parse_boost_version() {
    local _full_version="$*"
    trim "${_full_version}"
    _full_version=${_trimmed_string}

    _boost_version_major_minor_re='^([[:digit:]])\.([[:digit:]]+)$'
    _boost_version_major_minor_patch_re='^([[:digit:]])\.([[:digit:]]+)\.([[:digit:]]+)$'

    if [[ ${_full_version} =~ $_boost_version_major_minor_re ]]; then
        _boost_major_version=${BASH_REMATCH[1]}
        _boost_minor_version=${BASH_REMATCH[2]}
        _boost_patch_version=0
    elif [[ ${_full_version} =~ $_boost_version_major_minor_patch_re ]]; then
        _boost_major_version=${BASH_REMATCH[1]}
        _boost_minor_version=${BASH_REMATCH[2]}
        _boost_patch_version=${BASH_REMATCH[3]}
    else
        echo "ERROR: Couldn't parse Boost version: ${_full_version}"
        exit 4
    fi

    export BOOST_VERSION_DOTS=${_boost_major_version}.${_boost_minor_version}.${_boost_patch_version}
    export BOOST_VERSION_UNDERSCORES=${_boost_major_version}_${_boost_minor_version}_${_boost_patch_version}
}