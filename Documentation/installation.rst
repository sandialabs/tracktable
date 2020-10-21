.. _Tracktable_Installation:

Installing Pre-Built Packages
=============================

As of Version 1.2, Tracktable is available on the Python Package Index
(PyPI, https://pypi.org) and can be installed with ``pip`` as long as
you're running Python 3.5 or newer.  Use the following command:

``pip install tracktable``

If this fails, look carefully at the error message.  It is most
probably an error while trying to install `Cartopy
<https://scitools.org.uk/cartopy/docs/latest/>`_, a map rendering
toolkit that Tracktable uses to render images.  This will show up as a
complaint about a GEOS version or a request for Proj 4.9.0.

The solution is to install Cartopy yourself before you try to install
Tracktable.  If you are using `Anaconda
<https://www.anaconda.com/distribution/>`_, the command ``conda install
cartopy`` should do it.

After you have installed Cartopy, retry ``pip install tracktable``.

Anaconda Virtual Environment
----------------------------
If Anaconda is installed then the Anaconda virtual environment command
below will create and configure a virtual environment that is ready to use Tracktable.
Enter the following commands in a command/terminal/Anaconda prompt.

* Create the Anaconda virtual environment:
    * ::

        conda create --name tracktable --channel defaults --channel conda-forge --yes python pip folium pyshp pytz cartopy pip[tracktable]
* Verify that the ``tracktable`` virtual environment was created:
    * ``conda env list``
* Activate the virtual environment:
    * ``conda activate tracktable``
* Deactivate the virtual environment:
    * ``conda deactivate``
* If the virtual environment is no longer needed then it can be removed by running:
    * ``conda remove --name tracktable --all``

Note for Windows Users
----------------------

If you are using Tracktable under Windows, you might also need to install
the C++ runtime library.  This is a necessary component for any program
compiled with Microsoft's Visual C++ suite.  You can get it from the following
URL:

<https://aka.ms/vs/16/release/vc_redist.x64.exe>

The most common indication that you're missing this library is an import
error referring to the "_core_types" library when you try to import Tracktable
in a Python interpreter.

Installing from Source
======================

There are a few cases where you might want to build from source.  For
example:

- You might need access to features on the development branch.
- You might be running a version of Python for which we do not build wheels (binary packages).
- You might be on an unsupported platform.
- You might not have permission to use binary packages on your system.

In that case, this section is for you.


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

* Python 3.5, 3.6, or 3.7 - http://python.org
    * NOTE: Tracktable 1.1 was the last version to officially support Python 2.7.
* NumPy 1.7+ - http://numpy.org
* Matplotlib 2.0+ - http://matplotlib.org
* Cartopy - https://scitools.org.uk/cartopy/docs/latest/
    * NOTE: Tracktable 1.1 and earlier used Basemap (http://matplotlib.org/basemap) for rendering.
    * NOTE: On Ubuntu ``libproj-dev`` and ``proj-bin`` need to be installed prior to installing Cartopy
* PyTZ - https://pypi.python.org/pypi/pytz/
* Shapely - https://pypi.python.org/pypi/Shapely
    * When installing on Ubuntu, Shapely needs to be installed with no binaries i.e. ``pip install --no-binary shapely shapely``
* Six - https://pypi.org/project/six/
* PyProj - https://pypi.org/project/pyproj/
* Folium - https://pypi.org/project/folium/
* Scipy - https://pypi.org/project/scipy/
    * NOTE: This package only needs to be installed manually on Linux

C++
^^^

* Compiler - GCC 4.4.7 or newer (http://gcc.gnu.org), clang 3.5 or newer (http://clang.llvm.org),
  Visual Studio 14 2015 or newer (https://visualstudio.microsoft.com)
* Boost 1.67 or newer - http://www.boost.org
* GEOS library - http://geos.osgeo.org

  - You must build Boost with Boost.Python enabled using the headers
    from the same Python installation you will use to run Tracktable.

  - We rely on the r-tree and distance computation code available in
    recent versions of Boost.  Use 1.67 or newer.

  - With respect to C++11: if you want to call Tracktable from code
    built with C++11 turned on, you must also build Tracktable with
    C++11 turned on.  The implementation of ``boost::variant`` (which we
    use for ``tracktable::PropertyValueT``) is entirely different between the two
    language versions.  This causes link errors if you try to mix
    versions.

  - We do not yet use any C++11 features in Tracktable in order to
    maintain compatibility with a few environments that are still
    stranded in the age of C++03.  We look forward to their arrival in
    the modern age.


Other
^^^^^

* CMake 3.12+ - http://www.cmake.org

If you want to build documentation you will also need the following packages:

* Sphinx - http://sphinx-doc.org
* Sphinx Read the Docs theme - https://sphinx-rtd-theme.readthedocs.io/en/latest
* nbsphinx - https://nbsphinx.readthedocs.io/en/latest/index.html
* nbsphinx-link - https://nbsphinx-link.readthedocs.io/en/latest/index.html
* napoleon - https://sphinxcontrib-napoleon.readthedocs.org/en/latest
   * This is bundled with Sphinx as of version 1.3.
* Pandoc - https://pandoc.org/index.html
* Breathe - http://breathe.readthedocs.org/en/latest/
* Doxygen - http://www.doxygen.nl/index.html
* Graphviz (for dot executable)- https://www.graphviz.org/

If you want to render movies you will need FFMPEG:

* FFMPEG - https://www.ffmpeg.org
  - If you build from source please be sure to include the MPEG4 and
  FFV1 codecs.  Both of these are included with the standard FFMPEG
  download.  Tracktable can use other codecs but does not require
  them.
  - Windows users can obtain the ffmpeg executable by installing
  Image Magick (https://www.imagemagick.org)

Build Notes for Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you can possibly help it, install all the dependencies using
package managers like ``conda`` (Anaconda's built-in package manager),
``pip`` (comes with Python), ``yum``, ``apt-get`` (both of these are
common in Linux environments), MacPorts (http://macports.org) or
Homebrew (http://brew.sh).  The notes in this section are for cases
when you have no choice but to build external packages from source.

Building Boost
**************

We need several of Boost's compiled libraries including ``chrono``,
``date_time``, ``iostreams``, ``log``, ``random``, ``timer`` and
especially Boost.Python.  As with other dependencies, check your
operating system's package manager first.  It's possible that you can
install Boost with all its optional components from there.

If you already have a recent Boost installation you can check for
Boost.Python by looking for files named
``(prefix)boost_python.(suffix)`` where (prefix) is ``lib`` on
Unix-like systems and (suffix) is ``.so`` on Unix systems, ``.so`` or
``.dylib`` on Mac OSX and ``.dll`` (and ``.lib``) on Windows.

If you really do have to build Boost from source -- for example, if
you had to build your own Python installation -- then make sure to
configure it to use the proper Python installation.  Information about
how to do this can be found in the Boost.Python documentation at
http://www.boost.org/doc/libs/1_67_0/libs/python/doc/building.html

One final note: We know that it's a pain to try to keep up with recent
versions of a library as big as Boost.  We will not require a newer
version unless absolutely necessary.

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
you prefer) to configure compile settings.

If you made your build directory inside the source directory::

    $ ccmake ..

If you made it someplace else::

    $ ccmake TRACKTABLE_HOME/


Once CMake starts you will see a mostly empty screen with the message
``EMPTY CACHE``.  Press 'c' (if you use ``ccmake``) or click
'Configure' (if you use the CMake GUI) to start configuration.  After
a moment, several new options will appear including
``BUILD_PYTHON_WRAPPING`` and ``BUILD_SHARED_LIBS``.  Leave these set
to ``ON``. Without these options you will not be able to use any of
Tracktable's Python components.  Set the value of
``CMAKE_INSTALL_PREFIX`` to the directory where you want to install
the software.  To build the documentation set the ``BUILD_DOCUMENTATION``
or ``BUILD_DOCUMENTATION_CXX_ONLY`` options to ``ON`` once you have the
respective tools installed. There is no option to only build the Python
documentation since the Python documentation build process depends upon
the C++ documentation.Press 'c' or click the 'Configure' button again to
incorporate your choice.

Now you need to set options that are normally hidden.  Press 't' or
select the Show Advanced Options checkbox.  Here are the variables you
need to check:

1.  ``Boost_INCLUDE_DIR`` and ``Boost_LIBRARY_DIR``.

    These should point to your Boost install with Boost.Python.
    Filenames for the ``boost_date_time`` and ``boost_python``
    libraries should appear automatically.

    If you change either of these directories in CMake, press 'c' or
    click 'Configure' to make your changes take effect.

2.  ``Python3_EXECUTABLE``, ``Python3_LIBRARIES``, ``Python3_INCLUDE_DIRS``

    Make sure that all three of these point to the same installation.
    On Mac OSX with MacPorts in particular, CMake has a habit of using
    whatever Python executable is first in your path, the include
    directory from ``/System/Library/Frameworks/Python.framework`` and
    the library from ``/usr/lib/``.  MacPorts installs its Python
    library in
    ``/opt/local/Library/Frameworks/Python.framework/Versions/3.7``
    with headers in ``Headers/`` and the Python library in
    ``lib/libpython3.7.dylib``.  Substitute whatever version you have
    installed in place of 3.7.  If you have installed your own Python
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

Gotcha: Boost import targets not found
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This happens when your installed version of CMake is too old for your
installed version of Boost.  Please upgrade CMake to at least 3.12.

Gotcha: Anaconda does not install ccmake
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a known bug that has been fixed in ``conda-forge`` but has not
yet propagated to the main distribution.  Install ``cmake`` from the
``conda-forge`` channel as follows:

``$ conda install -c conda-forge cmake``

Gotcha: python3 Boost library not found but I'm using Python 2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check your Python CMake variables as listed in #2 above.  They are
probably pointing to a Python 3 interpreter.

Gotcha: Old version of Boost found in /usr/lib or /usr/lib64
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set the ``Boost_INCLUDE_DIR`` variable in CMake to point to the location of the include files for your preferred Boost installation.  The filenames for the compiled libraries will be updated the next time you press 'c' or 'Configure'.

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

On Unix-like systems, type ``make``.  For Visual Studio, run ``nmake``, run ``msbuild`` on
a project file, or open up the project files in your IDE (as appropriate).

Once the build process has finished go to your build directory and run
``ctest`` (part of CMake) to run all the tests.  Optionally, Windows users can run the
test project but this is just a fancy wrapper for ctest in this case. They should all
succeed.  Some of the later Python tests such as P_Mapmaker may take a minute or two.

If you have multiple cores or processors and your build system
supports it, by all means build in parallel.  GNU Make will do this
when you say ``make -j <n>`` where <n> is the number of compilers
you're willing to run.  A bare ``make -j`` will cause it to run as
many compiler instances as it believes you have cores or processors.
Windows users using msbuild, can use the ``/m:<n>`` option from the
command line.

.. warning::

   The Python wrappers, especially the wrappers for DBSCAN, feature
   vectors and the R-tree, take between 1GB and 1.5GB of memory to
   compile.  Keep this in mind when you run parallel builds.  A good
   rule of thumb is to run no more than 1 process for every 1.5-2GB of
   main memory in your computer.

Common Problems
^^^^^^^^^^^^^^^

1.  CMake error: "cannot find numpy"

    This usually arises when CMake detects a different Python
    installation than the one you actually use.  Take a look at the
    ``Python3_EXECUTABLE`` field in CMake.  If it says something like
    ``/usr/bin/python`` and you use a Python distribution like
    Anaconda or Enthought's Canopy, that's the problem.

    To fix, change ``Python3_EXECUTABLE`` to point to the Python
    interpreter in your environment.  For Anaconda under Linux and OS
    X, this is usually either ``~/anaconda3/bin/python`` or
    ``~/anaconda3/envs/<environment name>/bin/python``.  Remember to
    also change ``Python3_LIBRARIES`` and ``Python3_INCLUDE_DIRS`` to the
    files inside your Anaconda (or Enthought) directory.

2.  Python tests crashing

    If the tests whose names begin with ``P_`` crash, you probably
    have a mismatch between ``Python3_EXECUTABLE`` and
    ``Python3_LIBRARIES``.  Check their values in ``ccmake`` / CMake GUI.
    If your Python executable is in (for example)
    ``/usr/local/python/bin/python`` then its corresponding library
    will usually be in ``/usr/local/python/lib/libpython3.6.so``
    instead of halfway across the system.

3.  Python tests running but failing

    * Cause #1: One or more required Python packages missing.

      Check to make sure you have installed everything listed in the
      Dependencies section.

    * Cause #2: Couldn't load one or more C++ libraries.

      Make sure that the directories containing the libraries in
      question are in your LD_LIBRARY_PATH (DYLD_LIBRARY_PATH for Mac
      OSX) environment variable.

    * Cause #3: The wrong Python interpreter is being invoked.

      This really shouldn't happen: we use the same Python interpreter
      that you specify in ``Python3_EXECUTABLE`` and set ``PYTHONPATH``
      ourselves while running tests.

4.  Nearby stars go nova

    * We're afraid you're on your own if this happens.


Step 4: Install
---------------

You can use Tracktable as-is from its build directory or install it
elsewhere on your system.  To install it, type ``make install`` in the
build directory (or, again, your IDE's equivalent).  You can choose
the install destination by changing the ``CMAKE_INSTALL_PREFIX``
variable in CMake.

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
* If you are running from an installed location the libraries will be in ``INSTALL_DIR/lib`` and ``INSTALL_DIR/bin``.

* On Windows, add the library directory to your ``PATH`` environment variable.
* On Linux and most Unix-like systems, add the library directory to your ``LD_LIBRARY_PATH`` environment variable.
* On Mac OSX, add the library directory to your ``DYLD_LIBRARY_PATH`` variable.

On Unix-like systems you can also add the library directory to your
system-wide ld.so.conf file.  You will need root permissions in order
to do so.  That is beyond the scope of this document.
