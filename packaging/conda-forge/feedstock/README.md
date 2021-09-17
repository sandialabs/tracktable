# Conda-Forge Tracktable Package

The original conda-forge PR can be found here: https://github.com/conda-forge/staged-recipes/pull/14690

The conda-forge variant of our tracktable recipe is copied in this folder
as a reference against our locally maintained recipe as there are differences
between them due to how conda-forge performs build and maintenance; Because of this we
can't run the same recipe both locally and on conda-forge meaning we have two
functional recipes out in the wild.

The differences are subtle (for the most part) and as such are listed below:

## conda_build_config.yaml
* The conda-forge recipe is missing `conda_build_config.yaml` as the variant builds are
  handled globally on conda-forge, i.e. builds for different `python`, `boost` and `numpy` versions
    - Accordingly the `meta.yaml` is missing the `{{package}}` syntax for `python` and `boost` and
      the version constraint of `numpy` is removed for the same reason listed above

## meta.yaml
* All comments and unused section have been removed for a clean file
* `Build number` Jinja syntax has been removed i.e. `build number` is no longer set by a variable
* License file location is pointing at a different location

## bld.bat
* Removed debug commands for displaying environment and cmake vars

## build.sh
* Removed debug commands for displaying environment and cmake vars
* Removed Linux and Darwin specific build commands as conda-forge correctly handles the
  `${CMAKE_ARGS}` variable and will set the appropriate `sysroot`