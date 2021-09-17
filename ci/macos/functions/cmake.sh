### CMAKE UTILITY LIBRARY
#
# This file contains functions for manipulating a build with CMake.  It
# is intended to be included in other scripts with the Bash 'source' 
# builtin.  

###
### STATE VARIABLES
###

# Set this to an integer to use multiple processes during the build.
PARALLEL_JOBS=4

# Run CMake to configure the TT build for a specific Python version.
#
# Arguments:
#    $1: Path to build directory
#    $2: Path to source code
#    $3: Path to Conda environment for this build
#
# Returns:
#    0 on success, 1 on failure

function cmake_configure () {
    local __build_directory="$1"
    local __src_directory="$2"
    local __conda_env_path="$3"

    cmake \
        -B ${__build_directory} \
        -DBOOST_ROOT:PATH=${__conda_env_path} \
        -DCMAKE_BUILD_TYPE:STRING=Release \
        -DCMAKE_INSTALL_PREFIX:PATH=${__build_directory}/install \
        -DPython3_EXECUTABLE:FILEPATH=${__conda_env_path}/bin/python \
        -DPython3_ROOT_DIR:PATH=${__conda_env_path} \
        ${__src_directory}
}


# Have CMake invoke 'make wheel'.
#
# This calls CMake to invoke the build target since we might not always
# be using GNU make.  
#
# Arguments:
#     $1: Build directory
#
# Returns:
#     0 on success, 1 on error

function cmake_build_wheel () {
    local __build_directory="$1"

    cmake --build ${__build_directory} --target wheel
}


# Go forth and build!
#
# This calls CMake to invoke the build instead of running the build tool
# directly since we might not always be using GNU make.
#
# Arguments:
#     $1: Build directory
#
# Returns:
#     0 on success, 1 on error
#
# Note:
#     This function can be parameterized to include parallelization options
#     for build tools that support it.  

function cmake_run_build () {
    local __build_directory="$1"

    if [[ ${PARALLEL_JOBS} == "unset" ]]; then
        cmake --build ${__build_directory}
    else
        cmake --build ${__build_directory} --parallel ${PARALLEL_JOBS}
    fi
}


# Install after building.
#
# This calls CMake to invoke the install step instead of running the build tool
# directly since we might not always be using GNU make.  According to CMake's
# documentation, this might not even use the underlying build tool directly.
#
# Arguments:
#     $1: Build directory
#
# Returns:
#     0 on success, 1 on error

function cmake_run_install () {
    local __build_directory="$1"

    cmake --install ${__build_directory}
}

# Run CTest after building.
#
# This calls CTest to run all the tests.  
#
# Arguments:
#     $1: build directory (required)
#     $2: tests to exclude (optional)

function cmake_run_ctest () {
    local __build_directory="$1"
    pushd ${__build_directory}
    if [[ "$#" -eq 2 ]]
    then
        local __exclusions="$2"
        ctest --exclude-regex ${__exclusions} --output-on-failure
    else 
        ctest --output-on-failure
    fi
}

# Copy a finished wheel from a build directory to some output directory.
#
# This will actually grab all the wheels from that directory.  Because of
# the way we've set up the rest of the build, there should only be one.
#
# Arguments:
#     $1: build directory (wheel is in $1/wheel/*.whl)
#     $2: destination directory
#
# Returns:
#     0 on success, 1 on failure 

function copy_wheel_to_output () {
    local __build_directory="$1"
    local __output_directory="$2"

    cp ${__build_directory}/wheel/*.whl ${__output_directory}
}


function scratchspace () {
        if ! cmake_configure ${__build_directory} ${SOURCE_DIRECTORY} ${__conda_environment_path}
            then
                msg_error "CMake configure stage failed.  Exiting."
                return 10
            fi


} # end of main()

