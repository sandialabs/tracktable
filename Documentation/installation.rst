.. _Tracktable_Installation:

Installation
============

We currently use CMake to manage building Tracktable and running its
tests.  We hope to someday have a Python-centric install as simple as
'pip install tracktable'.  For now, you'll need a little bit more
expertise.

Step 0: Audience
----------------

We assume that you are familiar with downloading, compiling and
installing software from source as well as with your operating
system's package manager (if any).  You will need to know how to set
or modify environment variables, run the compiler and find libraries
or header files on your system.


Step 1: Dependencies
--------------------


Tracktable has the following required dependencies:

Python
^^^^^^

* Python 2.7 - http://python.org
* numpy 1.7+ - http://numpy.org
* Matplotlib 1.2.1+ - http://matplotlib.org
* Basemap - http://matplotlib.org/basemap
* PyTZ - https://pypi.python.org/pypi/pytz/
* Shapely - https://pypi.python.org/pypi/Shapely

C++
^^^

* Compiler - GCC 4.4.7 or newer (http://gcc.gnu.org), clang 3.5 or newer (http://clang.llvm.org)
* Boost 1.57 or newer - http://www.boost.org
* GEOS library - http://geos.osgeo.org

  - You must build Boost with Boost.Python enabled using the headers
    from the same Python installation you will use to run Tracktable.

  - We rely on the r-tree and distance computation code available in
    recent versions of Boost.  These appeared in version 1.55 but have
    serious compile bugs in versions 1.55 and 1.56.  Please use 1.57.0
    or newer.

Other
^^^^^

* CMake 2.8+ - http://www.cmake.org

If you want to build documentation you will also need the following packages:

* Sphinx - http://sphinx-doc.org
* napoleon - https://sphinxcontrib-napoleon.readthedocs.org/en/latest
* Breathe - http://breathe.readthedocs.org/en/latest/

If you want to render movies you will need FFMPEG:

* FFMPEG - https://www.ffmpeg.org
  - If you build from source please be sure to include the MPEG4 and
  FFV1 codecs.  Both of these are included with the standard FFMPEG
  download.  Tracktable can use other codecs but does not require
  them.

Build Notes for Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you can possibly help it, install all the dependencies using
package managers like ``pip`` (comes with Python), ``yum``,
``apt-get`` (both of these are common in Linux environments), MacPorts
(http://macports.org) or Homebrew (http://brew.sh).  The notes in this
section are for cases when you have no choice but to build external
packages from source.

Building Python
***************

The option we care about the most if you build your own Python is
``--enabled-shared``.  This will leave you with a shared library
version of the Python C API.  Tracktable will need to link against
this.

Building Boost
**************

We need several of Boost's compiled libraries including chrono,
date_time, iostreams, log, random, timer and especially Boost.Python.
As with other dependencies, check your operating system's package
manager first.  It's possible that you can install Boost with all its
optional components from there.

If you already have a recent Boost installation you can check for
Boost.Python by looking for files named
``(prefix)boost_python.(suffix)`` where (prefix) is ``lib`` on
Unix-like systems and (suffix) is ``.so`` on Unix systems, ``.so`` or
``.dylib`` on Mac OSX and ``.dll`` (and ``.lib``) on Windows.

If you really do have to build Boost from source -- for example, if
you had to build your own Python installation -- then make sure to
configure it to use the proper Python installation.  Information about
how to do this can be found in the Boost.Python documentation at
http://www.boost.org/doc/libs/1_57_0/libs/python/doc/building.html

One final note: We know that it's often a pain to try to keep up with
recent versions of a library as big as Boost.  We will not require a
newer version unless absolutely necessary.

Building FFMPEG
***************

For up-to-date instructions on building FFMPEG please refer to
https://trac.ffmpeg.org/wiki/CompilationGuide and choose your OS.  We
recommend that you compile in support for H264 video (via libx264).
While this is not required, it is widely supported by current devices
such as iPads, iPhones and Android systems.


You are now ready to configure and build the C++ part of Tracktable.
Install the Python dependencies whenever convenient.

Step 2: Configuration
---------------------

CMake enforces what we call "out-of-source" builds: that is, you
cannot build object files alongside source code files.  This makes it
much easier to manage multiple build configurations.  It also means
that the first thing you must do is create a build directory.  In the
rest of this section we will use ``TRACKTABLE_HOME`` to refer to the
directory where you unpacked the Tracktable source.::

    $ cd TRACKTABLE_HOME
    $ mkdir build
    $ cd build

(You can also put your build directory anywhere else you please.)

Next, use CMake's configuration utility ``ccmake`` (or its GUI tool if
you prefer) to configure compile settings:

If you made your build directory inside the source directory::

    $ ccmake ..

If you made it someplace else::

    $ ccmake TRACKTABLE_HOME/


Once CMake starts you will see a mostly empty screen with the message
``EMPTY CACHE``.  Press 'c' (if you use ``ccmake``) or click
'Configure' (if you use the CMake GUI) to start configuration.  After
a moment, several new options will appear including
``BUILD_PYTHON_WRAPPING`` and ``BUILD_SHARED_LIBS``.  Leave these set
to ON -- without them you will not be able to use any of Tracktable's
Python components.  Set the value of ``CMAKE_INSTALL_PREFIX`` to the
directory where you want to install the software.  Press 'c' or click
the 'Configure' button again to incorporate your choice.

Now you need to set options that are normally hidden.  Press 't' or
select the Show Advanced Options checkbox.  Here are the variables you
need to check:

1.  ``Boost_INCLUDE_DIR`` and ``Boost_LIBRARY_DIR``.

    These should point to your Boost 1.57 install with Boost.Python.
    Filenames for the ``boost_date_time`` and ``boost_python``
    libraries should appear automatically.

    If you change either of these directories in CMake, press 'c' or
    click 'Configure' to make your changes take effect.

2.  ``PYTHON_EXECUTABLE``, ``PYTHON_LIBRARY``, ``PYTHON_INCLUDE_DIR``

    Make sure that all three of these point to the same installation.
    On Mac OSX with MacPorts in particular, CMake has a habit of using
    whatever Python executable is first in your path, the include
    directory from ``/System/Library/Frameworks/Python.framework`` and
    the library from ``/usr/lib/``.  MacPorts installs its Python
    library in
    ``/opt/local/Library/Frameworks/Python.framework/Versions/2.7``
    with headers in ``Headers/`` and the Python library in
    ``lib/libpython2.7.dylib``.  If you have installed your own Python
    interpreter then use whatever path you chose for its installation.

    Note: You must make sure that all three components (interpreter,
    library and headers) correspond to one another or else the Python
    code will crash on startup with an unhelpful error message about
    thread state.

    If you change any of these variables, press 'c' or click
    Configure' to make your changes take effect.

Now press 'g' or click 'Generate' to confirm all of your choices and
generate Makefiles, Visual Studio project files or your chosen
equivalent.

Note
^^^^

Some older CMake installations have an odd bug that shows up with
certain Linux installations.  You may see ``Boost_DIR`` set to
something like ``/usr/lib64`` no matter what value you try to set for
``Boost_INCLUDE_DIR`` and ``Boost_LIBRARY_DIR``.  If you experience
this, try adding the line::

    set(Boost_NO_BOOST_CMAKE ON)

to ``TRACKTABLE_HOME/tracktable/CMakeLists.txt`` and then rerun CMake as described above.


Step 3: Build and Test
----------------------

On Unix-like systems, type ``make``.  For Visual Studio, run ``nmake``
or open up the project files in your IDE (as appropriate).

Once the build process has finished go to your build directory and run
``ctest`` (part of CMake) to run all the tests.  They should all
succeed.  Some of the later Python tests such as P_Mapmaker may take a
minute or two.

If you have multiple cores or processors and your build system
supports it, by all means build in parallel.  GNU Make will do this
when you say ``make -j <n>`` where <n> is the number of compilers
you're willing to run.  A bare ``make -j`` will cause it to run as
many compiler instances as it believes you have cores or processors.

.. warning::

   The Python wrappers, especially the wrappers for DBSCAN, feature
   vectors and the R-tree, take between 1GB and 1.5GB of memory to
   compile.  Keep this in mind when you run parallel builds.  A good
   rule of thumb is to run no more than 1 process for every 1.5-2GB of
   main memory in your computer.

Common Problems
^^^^^^^^^^^^^^^

1.  Python tests crashing

    If the tests whose names begin with ``P_`` crash, you probably
    have a mismatch between ``PYTHON_EXECUTABLE`` and
    ``PYTHON_LIBRARY``.  Check their values in ``ccmake`` / CMake GUI.
    If your Python executable is in (for example)
    ``/usr/local/python/bin/python`` then its corresponding library
    will usually be in ``/usr/local/python/lib/libpython2.7.so``
    instead of halfway across the system.

2.  Python tests running but failing

    * Cause #1: One or more required Python packages missing.

      Check to make sure you have installed everything listed in the
      Dependencies section.

    * Cause #2: Couldn't load one or more C++ libraries.

      Make sure that the directories containing the libraries in
      question are in your LD_LIBRARY_PATH (DYLD_LIBRARY_PATH for Mac
      OSX) environment variable.

    * Cause #3: The wrong Python interpreter is being invoked.

      This really shouldn't happen: we use the same Python interpreter
      that you specify in ``PYTHON_EXECUTABLE`` and set ``PYTHONPATH``
      ourselves while running tests.

3.  Nearby stars go nova

    * We're afraid you're on your own if this happens.


Step 4: Install
---------------

You can use Tracktable as-is from its build directory or install it
elsewhere on your system.  To install it, type ``make install`` in the
build directory (or, again, your IDE's equivalent).

You will also need to add Tracktable to your system's Python search
path, usually stored in an environment variable named ``PYTHONPATH``.

* If you  are going  to run  Tracktable from  the directory  where you
  unpacked it  then add  the directory  ``TRACKTABLE_HOME/tracktable/Python/`` to
  your ``PYTHONPATH``.
* If you installed Tracktable via ``make install`` then you will need
  to add ``INSTALL_DIR/Python/`` to your ``PYTHONPATH``. Here
  ``INSTALL_DIR`` is the directory you specified for installation when
  running CMake.

Finally, you will need to tell your system where to find the
Tracktable C++ libraries.

* If you are running from your build tree (common during development) then the libraries will be in ``BUILD/lib`` and ``BUILD/bin`` (XXX Check where Windows puts its DLLs).
* If you are running from an installed location the libraries will be in ``INSTALL_DIR/lib`` and ``INSTALL_DIR/bin`` (XXX same check).

* On Windows, add the library directory to your ``PATH`` environment variable.
* On Linux and most Unix-like systems, add the library directory to your ``LD_LIBRARY_PATH`` environment variable.
* On Mac OSX, add the library directory to your ``DYLD_LIBRARY_PATH`` variable.

On Unix-like systems you can also add the library directory to your system-wide ld.so.conf file.  You will need root permissions in order to do so.  That is beyond the scope of this document.
