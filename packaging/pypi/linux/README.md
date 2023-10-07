# Tracktable Linux Wheels

This repository contains the infrastructure to create
[wheels](https://packaging.python.org/discussions/wheel-vs-egg/)
(Python binary install packages) for Tracktable running under Linux.

### How do I use it?

1.  Clone this repository.

2.  Install Docker on your computer.  Make sure to configure the web proxies inside Docker's preferences to match Sandia's proxy infrastructure.

3.  ```cd /path/to/tracktable-linux-wheels```

4. ```./build_all.sh```

### What about Windows and OS X?

Those are a lot simpler.  On Windows and OS X it should be sufficient
to build Tracktable, run 'make install', and then run 'make wheel'
from the build directory.  Note judicious use of the word 'should'.

### How do I use the resulting wheel files?

Copy the wheel file onto a computer where you want to install it.
That computer should be running Linux and Anaconda (Python
distribution).  Install the ```basemap-data-hires``` package in
Anaconda.  That will pull in some necessary dependencies.

Make sure the Python version in the wheel file
(indicated by the -cp37- tag for Python 3.7, for example) matches the
version of Anaconda installed.  Then type ```pip install
tracktable-1.1.0-cp37-none-manylinux2010_x86_64.whl```.

### What all does this thing do?

The _what_ will make more sense if I start with the _why_.  In order
to distribute wheels for Linux Python packages that include
non-trivial binary components, we have to adhere to a standard called
(manylinux)[https://www.python.org/dev/peps/pep-0513/], recently
updated to ```manylinux2010```.  This dictates what libraries one is
permitted to link to that are not included in the wheel itself as well
as acceptable versions of those libraries.  The easiest way to meet
that requirement is to build your package inside a Docker image that
contains only the permissible libraries.  Everything else, you have to
bring on your own and bundle if necessary.

With that in mind, here's what we do:

1.  Start with the latest ```manylinux2014``` image.
2.  Download, build and install Boost for all of the CPython versions 
    in that image.  
3.  Collect all of the binaries for the Boost.Python library.
4.  Make an image that has Boost.Python binaries for all of those CPython
    versions.  THIS ENDS STAGE 1.
4.  Download, build, and install the latest version of 
    (CMake)[https://www.cmake.org].  THIS IS STAGE 2.
5.  Build and install Tracktable for all of the above versions of Python.
7.  Use a custom CMake module (```BuildWheel.cmake```) to drive a
    standard Python setup script to create the wheel.
8.  Use the ```auditwheel``` tool to find and bundle libraries that we link against.
9.  Copy the resulting wheels back out of the Docker containers so that you can use them.

### Okay, what do I do with the .whl files?

Find the one that corresponds to your Python installation and say
```pip install tracktable-1.1.0-whatever.whl```.  That should do the
trick.

### What Python interpreters can I use?

Alas, we're restricted to the CPython interpreter (the one distributed
from python.org).  We don't currently interoperate with Pypy or
Jython.

### What if it breaks?

Write to Andy (atwilso@sandia.gov) about the problem.  Alternately,
fork the repository, fix it, and send him a pull request.

