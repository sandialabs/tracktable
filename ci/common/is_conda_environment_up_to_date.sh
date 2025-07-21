#!/bin/sh

# This script checks to see whether the conda environment named in a
# YML file exists and was last created/updated more recently than
# the last commit to the YML file.
#
# We do this in case dependencies have been added/changed to the YML
# file.  Running `conda env update` is an expensive operation --
# just as expensive as constructing the environment from scratch --
# but this is a pretty good approximation.

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <conda_environment_def.yml>"
    exit 1
fi

FILE_PATH=$1

CONDA_ENV_NAME=$(\
   grep "name: " $FILE_PATH \
   | cut -f 2 -d ':' \
   | sed -e 's/^[[:space:]]*//g' \
   )


# Check to make sure the conda environment exists

if ! conda env list | grep -w "$CONDA_ENV_NAME" > /dev/null; then
    echo "Error: Conda environment '$CONDA_ENV_NAME' does not exist."
    exit 1
fi

echo "Checking to see if Conda environment $CONDA_ENV_NAME is up to date."

# If we grep the output of `conda env list` for our environment
# name, we will get one of three results:
#
# 1. Nothing: environment doesn't exist.  We already checked for that.
#
# 2. <name_of_environment> <whitespace> <path_to_environment>
#    Environment exists but is not active.
#
# 3. <name_of_environment> * <path_to_environment>
#    Environment exists and is active.
#
# By running the output of `grep` through `rev` before `cut`
# and then back again, we can ask for the first field before
# any whitespace and get the *last* field (which `cut` otherwise
# can't name) after all whitespace from our original string.

CONDA_ENV_DIRECTORY=$(\
   conda env list \
   | grep ${CONDA_ENV_NAME} \
   | rev \
   | cut -f 1 -d ' ' \
   | rev)

# Check if the Conda environment exists
if [ ! -d "$CONDA_ENV_DIRECTORY/conda-meta" ]; then
    echo "Error: Conda environment '$CONDA_ENV_NAME' does not have a conda-meta directory."
    exit 3
fi

# Get the last modification time of the Conda environment
LAST_ENV_UPDATE=$(grep '^==>' "$CONDA_ENV_DIRECTORY/conda-meta/history" | tail -n 1 | sed 's/^==> //; s/ <==.*//')
if [ -z "$LAST_ENV_UPDATE" ]; then
    echo "Error: Could not find any update timestamps in the Conda environment history."
    exit 1
fi

# Convert the last environment update time to epoch.  This one is in
# YYYY-MM-DD HH:MM:SS format.
LAST_ENV_UPDATE_EPOCH=$(\
   python -c \
   "import time; print(int(time.mktime(time.strptime('$LAST_ENV_UPDATE', '%Y-%m-%d %H:%M:%S'))))"\
)

# Get the last commit time of the specified file.  We can get this
# directly in Unix timestamp format with '%ct'.
LAST_COMMIT_TIME_EPOCH=$(git log -1 --format=%ct -- "$FILE_PATH")
if [ -z "$LAST_COMMIT_TIME_EPOCH" ]; then
    echo "Error: Could not find any commits for the file '$FILE_PATH'."
    exit 1
fi

# Compare the timestamps
if [ "$LAST_ENV_UPDATE_EPOCH" -lt "$LAST_COMMIT_TIME_EPOCH" ]; then
    echo "ERROR: The definition file ${FILE_PATH} was modified more recently than its Conda environment.  Please update the Conda environment for the runner."
    exit 1
else
    echo "Success: Conda environment ${CONDA_ENV_NAME} is newer than the last updates to definition file ${FILE_PATH}."
    exit 0
fi