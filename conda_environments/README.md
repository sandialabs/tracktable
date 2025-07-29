# Conda Environment Definitions

The files in this directory replace the old environments we had scattered
all across the repository.  We now use the same environment for development,
CI/CD builds, and packaging.

If all you want is a Tracktable development environment, pick the YAML file
in this directory corresponding to your platform (Windows, MacOS, or Linux)
and run the following command.  Replace `myplatform` with the name of your
platform.

```bash
conda env create --file tracktable-dev-myplatform.yml
```

This will create a Conda environment named `tracktable-dev`.

If you need an environment with a particular version of Python, use the
files in the `versioned/<platform>` directory.  You might do this if you
are working on an issue that only appears on certain platforms and certain
versions of Python.  For example, to create a Tracktable development
environment under MacOS for Python 3.12, run the following command:

```bash
conda env create --file versioned/macos/tracktable-dev-python3.12.yml
```

This will create the environment `tracktable-dev-python3.12`.

## Adding Packages

When you want to add packages to the environment for future use, add them
to the appropriate file in `components/` and then run `regenerate-all.sh`.
Please do not modify the `tracktable-dev` YML files directly.  Those files
are auto-generated and your changes will be overwritten by
`regenerate-all.sh`.

If your package will be used on all platforms, add it to `common.yml`.
If it will only be used on some platforms, add it to `windows.yml`,
`linux.yml`, or `macos.yml` as appropriate.  If it will only be used with
certain Python versions, add it to the `pythonX.Y` files corresponding
to the versions where the package is needed.

After you have done this, commit your changes and run `regenerate_all.sh`.
This will rebuild all of the files under `conda_environments/versioned/`
and the three environment files in this directory.  Commit anything that
changed.

Note that this only changes the environment definition files.  Our
continuous integration scripts do not yet have the ability to add new
packages on the fly.

