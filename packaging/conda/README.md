# Conda Packaging
There are multiple ways of getting our code into a conda package as described from the docs below:

* The best way is to obtain the source code for the software and build a conda package from the
  source and not from a wheel. This helps ensure that the new package uses other conda packages
  to satisfy its dependencies.

* The second best way is to build a conda package from the wheel file. This tells conda more
  about the files present than a pip install. It is also less likely than a pip install to
  cause errors by overwriting (or "clobbering") files. Building a conda package from the
  wheel file also has the advantage that any clobbering is more likely to happen at build
  time and not runtime.

* The third way is to use pip to install a wheel file into a conda environment. Some conda users
  have used this option safely. The first 2 ways are still the safest and most reliable.


We are using option one as it is the best way to get tracktable into a anaconda package. Previously,
we pip installed the tracktable wheel into the anaconda environment.

## meta.yaml
The meta.yaml contains all of the configuration values for the conda package. If any of the packages configuration
information, such as the package's version, build number or dependencies, needs changed this is the file to do it in.

## Conda Builder Enviroment
There are anaconda environment yaml files in the `packaging\conda` directory for building the tracktable package under
each architecture that tracktable is distributed under. While you can create the tracktable package using
the anaconda base environment it's recommended that you use one these environment files as it helps keep the
base environment clean. Pick the command below that corresponds to your OS.

**NOTE: The build environment yaml files are located in `packaging\conda` so either run the command from there
or prepend the path to the command below if you are in a different directory
i.e. `conda env create -f packaging\conda\win_conda_builder_environment.yml`**

* `conda env create -f win_conda_builder_environment.yml`
* `conda env create -f unix_conda_builder_environment.yml`

Once the environment is created be sure to activate it before proceeding with the remaining steps.

## Packaging Commands
Below are the commands to generate conda packages for the various python versions we distribute tracktable under.

**Note: You may encounter some SSL errors during the build process, refer here for a soultion:**
https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/disable-ssl-verification.html

**NOTE: These commands are assuming that you are running them from the top level of the tracktable directory,
if you want to run them from within the `conda` directory `cd` to `packaging\conda` and replace `packaging\conda`
with `.` in the commands below i.e. `conda build --python 3.6 .`**

**NOTE: If the commands below return an error referencing a URL or 404 error code replace `--channel conda-forge`
with `--channel https://conda.anaconda.org/conda-forge/`**

**NOTE: The default source code location is the lastest release in github, if you need to build from your local environment
update the meta.yaml file to pull from the local source**
### Windows Commands
* `conda build --channel conda-forge packaging\conda` | **NOTE: This will build the tracktable package against every version of Python i.e. Python 3.6-3.9**
* `conda build --channel conda-forge --python 3.6 packaging\conda`
* `conda build --channel conda-forge --python 3.7 packaging\conda`
* `conda build --channel conda-forge --python 3.8 packaging\conda`
* `conda build --channel conda-forge --python 3.9 packaging\conda`

### Linux/Mac Commands
* `conda build --channel conda-forge packaging/conda` | **NOTE: This will build the tracktable package against every version of Python i.e. Python 3.6-3.9**
* `conda build --channel conda-forge --python 3.6 packaging/conda`
* `conda build --channel conda-forge --python 3.7 packaging/conda`
* `conda build --channel conda-forge --python 3.8 packaging/conda`
* `conda build --channel conda-forge --python 3.9 packaging/conda`

## Installation Commands
To install the local generated packages into your conda enviroment using **one** of the following commands.

**NOTE: If the first command doesn't work try the second command.**

* `conda install --use-local tracktable`
* `conda install -c ${CONDA_PREFIX}/conda-bld/ tracktable`

## Conda-Build Documentation
The conda-build documentation can be found at the link below:

https://docs.conda.io/projects/conda-build/en/latest/index.html