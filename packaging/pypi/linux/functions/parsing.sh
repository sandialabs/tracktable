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

    if [[ ${_full_version} =~ ^(cp[[:digit:]]+[m]?)-(cp[[:digit:]]+[m]?) ]]; then
        export _python_version=${BASH_REMATCH[1]}
        export _python_abi=${BASH_REMATCH[2]}
    else
        echo "ERROR: Couldn't parse Python implementation name: ${_full_version}"
        exit 3
    fi
}
