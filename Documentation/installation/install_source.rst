.. _installing_from_source_guide:

Installing Tracktable From Source
=================================

.. attention:: For all build/installation issues and errors encountered
   in the steps below refer to the
   :ref:`Common Issues & Errors <common_issues_errors_installation>` Page.

There are a few cases where you might want to build from source. For
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
system's package manager (if any). You will need to know how to set
or modify environment variables, run the compiler and find libraries
or header files on your system.


Step 1: Dependencies
--------------------

Wherever possible, install the dependencies using
package managers such as

  - Windows, Mac, Linux:

    - ``conda`` (Anaconda's built-in package manager),
    - ``pip`` (comes with Python),

  - Windows:

    While Windows specific package managers are available the Tracktable
    team cannot guarantee they have the required dependencies needed to
    build tracktable from source

  - Linux:

    - ``yum``
    - ``apt-get``

  - Mac:

    - MacPorts (https://www.macports.org/)
    - Homebrew (https://brew.sh/)

Instructions on using Anaconda to configure a fully functional development environment are located in
the :ref:`Anaconda Virtual Environment <create_conda_environment_source>` section below.

Tracktable has the following required dependencies:

Python
^^^^^^

* Python 3.5 through 3.9 - https://www.python.org/

  .. note:: Tracktable 1.1 was the last version to officially support Python 2.7.

* NumPy 1.7 or newer - https://numpy.org/
* Matplotlib 3.0 or newer - https://matplotlib.org/
* Cartopy 0.18.0 or newer - https://scitools.org.uk/cartopy/docs/latest/

  .. important:: On Linux, ``libproj-dev`` and ``proj-bin`` need to be installed prior to installing Cartopy
* PyTZ 2020.1 or newer - https://pypi.python.org/pypi/pytz/
* Shapely 1.7.1 or newer - https://pypi.python.org/pypi/Shapely

  .. note:: When installing on Linux, Shapely needs to be installed with no binaries i.e. ``pip install --no-binary shapely shapely``
* PyProj 2.6.1 or newer - https://pypi.org/project/pyproj/
* Folium 0.11.0 or newer - https://pypi.org/project/folium/
* Scipy 1.5.2 or newer - https://pypi.org/project/scipy/

  .. note:: This package only needs to be installed manually on Linux

C++
^^^

Tracktable requires a C++14-capable compiler as of release 1.5.

* Compiler Options

  * GCC 5.2 or newer (https://gcc.gnu.org/)
  * Clang 3.5 or newer (http://clang.llvm.org)
  * Visual Studio (15) 2017 or newer (https://visualstudio.microsoft.com)
* GEOS library 3.8.1 or newer - https://trac.osgeo.org/geos
* Boost 1.74 or newer - https://www.boost.org/

  .. tip:: Windows users can find pre-built Boost binaries at https://sourceforge.net/projects/boost/files/boost-binaries/
  .. hint:: Windows users should remember to add the path of the Boost installation
     to the systems ``PATH`` environment variable.

  - We need several of Boost's compiled libraries including ``chrono``,
    ``date_time``, ``iostreams``, ``log``, ``random``, ``timer`` and
    especially ``Boost.Python``. As with other dependencies, check your
    operating system's package manager first. It's possible that you can
    install Boost with all its optional components from there.

    - If you already have a recent Boost installation you can check for
      ``Boost.Python`` by looking for files named
      ``(prefix)boost_python.(suffix)`` where (prefix) is ``lib`` on
      Unix-like systems and (suffix) is ``.so`` on Unix systems, ``.so`` or
      ``.dylib`` on Mac OSX and ``.dll`` (and ``.lib``) on Windows.

  - You must build Boost with Boost.Python enabled using the headers
    from the same Python installation you will use to run Tracktable.

  - Tracktable requires a C++14-capable compiler as of version 1.5.

  .. note:: We know that it is inconvenient to try to keep up with recent
     versions of a library as big as Boost. We only change the required version
     when absolutely necessary.


Documentation
^^^^^^^^^^^^^

If you want to build documentation you will also need the following packages:

* Sphinx 3.4.3 or newer - https://www.sphinx-doc.org/en/master/
* Sphinx Read the Docs theme 0.5.0 or newer - https://sphinx-rtd-theme.readthedocs.io/en/latest
* nbsphinx 0.7.1 or newer - https://nbsphinx.readthedocs.io/en/latest/index.html
* nbsphinx-link 1.3.0 or newer - https://nbsphinx-link.readthedocs.io/en/latest/index.html
* Pandoc 2.5 or newer - https://pandoc.org/index.html
* Breathe 4.26.1 or newer - https://breathe.readthedocs.io/en/latest/
* Doxygen 1.8.17 or newer - https://www.doxygen.nl/index.html
* Graphviz (for dot executable) 2.42.2 or newer - https://www.graphviz.org/

Movies
^^^^^^

If you want to render movies you will need FFMPEG:

* FFMPEG 4.2.4 or newer - https://www.ffmpeg.org

  - If you build from source please be sure to include the MPEG4 and
    FFV1 codecs. Both of these are included with the standard FFMPEG
    download. Tracktable can use other codecs but does not require
    them.

  .. tip:: Windows users can obtain the ffmpeg executable by installing
    Image Magick (https://www.imagemagick.org)


Other
^^^^^

* CMake 3.19.5 or newer - https://cmake.org/
* TQDM (Optional for enabling progress bars in Python) 4.51.0 or newer - https://tqdm.github.io/

Build Notes for Dependencies Built from Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The notes in this section are for cases when you have *absolutely* no
choice but to build external packages from source.

Building Boost
**************

.. tip:: You must build Boost with Boost.Python enabled using the headers
   from the same Python installation you will use to run Tracktable.

The instructions to build Boost from source can be found at
https://www.boost.org/doc/libs/1_75_0/more/getting_started/index.html

The specific instructions for building ``Boost.Python`` can be found at
https://www.boost.org/doc/libs/1_75_0/libs/python/doc/html/building/


Building FFMPEG
***************

For up-to-date instructions on building FFMPEG please refer to
https://trac.ffmpeg.org/wiki/CompilationGuide and choose your OS.
We recommend that you compile in support for H264 video (via ``libx264``).


.. _create_conda_environment_source:

Anaconda Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. attention:: The tracktable development anaconda environment that is created in this section
    is plug and play on Linux and MacOS and will build the Tracktable source code with no additional
    configuration. For Windows, there are additional steps required to configure cmake and an IDE
    to recognize the anaconda environment. These additional steps are dependent on the existing
    Windows environment, compiler and IDE being used and are outside the scope of the troubleshooting
    provided in this documentation.

If you have `Anaconda <https://www.anaconda.com/distribution/>`_
installed then the Anaconda virtual environment commands
below will create and configure a virtual environment that is ready to use
to build Tracktable from source. Enter the following commands in a command/terminal/Anaconda prompt.


#. Create the Anaconda virtual environment

    We include a YML configuration file
    (:download:`tracktable_dev_environment.yml <../../tracktable_dev_environment.yml>`)
    that can be used to create an Anaconda virtual environment named
    ``tracktable-dev``. This file will create the environment in one shot and doesn't
    require any additional package installation after the environment is activated.

    .. code-block:: console

      conda env create -f /path/to/tracktable_dev_environment.yml

    .. important:: Be sure to substitute the location where you saved tracktable_dev_environment.yml in the command above.

#. Verify that the ``tracktable-dev`` virtual environment was created

    .. code-block:: console

      conda env list

#. Activate the virtual environment

    .. code-block:: console

      conda activate tracktable-dev

#. Deactivate the virtual environment (optional)

    .. code-block:: console

      conda deactivate

#. Delete the virtual environment when it is no longer needed

  .. code-block:: console

      conda remove --name tracktable-dev --all

Step 2: Configuration
---------------------

CMake enforces what we call "out-of-source" builds: that is, you
cannot build object files alongside source code files. This makes it
much easier to manage multiple build configurations. It also means
that the first thing you must do is create a build directory.

.. important:: In the rest of this guide we will use
   ``TRACKTABLE_HOME`` to refer to the
   directory where you unpacked the Tracktable source.

.. code-block:: console

    $ cd TRACKTABLE_HOME
    $ mkdir build
    $ cd build

.. tip:: You can also put your build directory anywhere else you please.

Next, use CMake's configuration utility ``ccmake`` (or it’s command line
version ‘cmake’ if you prefer) to configure compile settings.

If you made your build directory inside the source directory

.. code-block:: console

    $ ccmake ..

Or, if you made the build directory elsewhere

.. code-block:: console

    $ ccmake TRACKTABLE_HOME/


Once CMake starts you will see a mostly empty screen with the message ``EMPTY CACHE``.

  * Press ``c`` (if you use ``ccmake``) or click
    ``Configure`` (if you use the CMake GUI) to start configuration.

  * After a moment, several new options will appear including
    ``BUILD_PYTHON_WRAPPING`` and ``BUILD_SHARED_LIBS``. Leave these set to
    ``ON``.

      .. Warning:: Without these options you will not be able to use
        any of Tracktable's Python components.

  * Set the value of
    ``CMAKE_INSTALL_PREFIX`` to the directory where you want to install
    the software.

  * To build the documentation set the ``BUILD_DOCUMENTATION``
    or ``BUILD_DOCUMENTATION_CXX_ONLY`` options to ``ON`` once you have the
    respective tools installed.

      .. note:: There is no option to only build the Python
        documentation since the Python documentation build process depends upon
        the C++ documentation.

  * Press ``c`` or click the ``Configure`` button again to incorporate your choices.

Now you need to set options that are normally hidden. Press ``t`` or
select the ``Show Advanced Options`` checkbox.

Here are the variables you need to check:

1. ``Boost_INCLUDE_DIR`` and ``Boost_LIBRARY_DIR``.

    These should point to your Boost install with Boost.Python.
    Filenames for the ``boost_date_time`` and ``boost_python``
    libraries should appear automatically.

    If you change either of these directories in CMake, press ``c`` or
    click ``Configure`` to make your changes take effect.

.. _python_cmake_vars:

_`2`. ``Python3_EXECUTABLE``, ``Python3_LIBRARIES``, ``Python3_INCLUDE_DIRS``

    Make sure that all three of these point to the same installation. If you change any
    of these variables, press ``c`` or click ``Configure`` to make your changes take effect.

    .. important:: You must make sure that all three components (interpreter,
      library and headers) correspond to one another or else the Python
      code will crash on startup with an unhelpful error message about
      thread state.

    .. note:: On Mac OSX with MacPorts in particular, CMake has a habit of using
      whatever Python executable is first in your path, the include
      directory from ``/System/Library/Frameworks/Python.framework`` and
      the library from ``/usr/lib/``. MacPorts installs its Python
      library in
      ``/opt/local/Library/Frameworks/Python.framework/Versions/3.7``
      with headers in ``Headers/`` and the Python library in
      ``lib/libpython3.7.dylib``. Substitute whatever version you have
      installed in place of 3.7. If you have installed your own Python
      interpreter then use whatever path you chose for its installation.


Now press ``g`` or click ``Generate`` to confirm all of your choices and
generate Makefiles, Visual Studio project files or your chosen
equivalent.

.. note:: Some older CMake installations have an odd bug that shows up with
  certain Linux installations. You may see ``Boost_DIR`` set to
  something like ``/usr/lib64`` no matter what value you try to set for
  ``Boost_INCLUDE_DIR`` and ``Boost_LIBRARY_DIR``. If you experience
  this, try adding the line

  .. code-block:: cmake

      set(Boost_NO_BOOST_CMAKE ON)

  to ``TRACKTABLE_HOME/tracktable/CMakeLists.txt`` and then rerun CMake as described above.

.. _installation_common_gotchas:

Common Gotchas
^^^^^^^^^^^^^^

Boost import targets not found
******************************

This happens when your installed version of CMake is too old for your
installed version of Boost. Please upgrade CMake to at least 3.12.
If the problem persists, the Boost imports can be manually entered into
your cmake configuration.

Anaconda does not install ccmake
********************************

This is a known bug that has been fixed in ``conda-forge`` but has not
yet propagated to the main distribution. Install ``cmake`` from the
``conda-forge`` channel as follows:

``$ conda install -c conda-forge cmake``

Old version of Boost found in /usr/lib or /usr/lib64
****************************************************

Set the ``Boost_INCLUDE_DIR`` variable in CMake to point to the location of the include
files for your preferred Boost installation.
The filenames for the compiled libraries will be updated
the next time you press ``c`` or ``Configure``.

Windows: import error referring to the "_core_types" library
******************************************************************

If you are using Tracktable under Windows, you might also need to install
the C++ runtime library. This is a necessary component for any program
compiled with Microsoft's Visual C++ suite. You can get it from the following
URL:

https://aka.ms/vs/16/release/vc_redist.x64.exe

The most common indication that you're missing this library is an import
error, ``NameError: name '_core_types' is not defined``, when you try to import Tracktable
in a Python interpreter.


Step 3: Build and Test
----------------------

* On Unix-like systems, type ``make``.
* For Visual Studio, run ``nmake``, run ``msbuild`` on
  a project file, or open up the project files in your IDE (as appropriate).
  ``msbuild ALL_BUILD.vcxproj /t:Rebuild /p:Configuration=Release``

Once the build process has finished go to your build directory and run
``ctest`` (part of CMake) to run all the tests. They should all succeed.

.. note:: Some of the later Python tests such as P_Mapmaker may take a minute or two.

.. tip::  Windows users who chose Visual Studio project files during configuration
   can run the "test" project to run all the tests. This is a thin wrapper that
   calls CTest.

If you have multiple cores or processors and your build system
supports it, by all means build in parallel. GNU Make will do this
when you say ``make -j <n>`` where ``<n>`` is the number of compilers
you're willing to run. A bare ``make -j`` will cause it to run as
many compiler instances as it believes you have cores or processors.
Windows users using msbuild, can use the ``/m:<n>`` option from the
command line.

.. warning::

   The Python wrappers, especially the wrappers for DBSCAN, feature
   vectors and the R-tree, take between 1GB and 1.5GB of memory to
   compile. Keep this in mind when you run parallel builds. A good
   rule of thumb is to run no more than 1 process for every 1.5-2GB of
   main memory in your computer.

Common Problems
^^^^^^^^^^^^^^^

CMake error: "cannot find numpy"
********************************

This usually arises when CMake detects a different Python
installation than the one you actually use. Take a look at the
``Python3_EXECUTABLE`` field in CMake. If it says something like
``/usr/bin/python`` and you use a Python distribution like
Anaconda.

To fix, change ``Python3_EXECUTABLE`` to point to the Python
interpreter in your environment. For Anaconda under Linux and OS
X, this is usually either ``~/anaconda3/bin/python`` or
``~/anaconda3/envs/<environment name>/bin/python``. Remember to
also change ``Python3_LIBRARIES`` and ``Python3_INCLUDE_DIRS`` to the
files inside your Anaconda directory.

Python tests crashing
*********************

If the tests whose names begin with ``P_`` crash, you probably
have a mismatch between ``Python3_EXECUTABLE`` and
``Python3_LIBRARIES``. Check their values in ``ccmake`` / CMake GUI.
If your Python executable is in (for example)
``/usr/local/python/bin/python`` then its corresponding library
will usually be somewhere in ``/usr/local/python`` -- for example,
``/usr/local/python/lib/libpython3.6.so`` -- instead of in some directory
outside ``/usr/local/python``.

Python tests running but failing
********************************

* Cause #1: One or more required Python packages missing.

  Check to make sure you have installed everything listed in the
  Dependencies section.

* Cause #2: Couldn't load one or more C++ libraries.

  Make sure that the directories containing the libraries in
  question are in your ``LD_LIBRARY_PATH`` (``DYLD_LIBRARY_PATH`` for
  MacOS) environment variable.

* Cause #3: The wrong Python interpreter is being invoked.

  This really shouldn't happen: we use the same Python interpreter
  that you specify in ``Python3_EXECUTABLE`` and set ``PYTHONPATH``
  ourselves while running tests.

Windows VS/MSBuild Debug Build Fails
************************************

When creating a debug build in a Visual Studio based environment,
it maybe necessary to add the the ``\bigobj`` flag to the
``CMAKE_CXX_FLAGS_DEBUG`` field.


Nearby Stars Go Nova
********************
We're afraid you're on your own if this happens.


Step 4: Install
---------------

You can use Tracktable as-is from its build directory or install it
elsewhere on your system. To install it, type ``make install`` in the
build directory (or, again, your IDE's equivalent). You can choose
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

.. hint:: On Windows, unless modified any Tracktable DLLs generated by Visual Studio
   will be located in ``tracktable\out\build\<build config>\bin``. When installing
   Tracktable from Visual Studio on Windows the DLLs located in
   ``tracktable/out/install/<build config>/bin/TracktableCore.dll`` will be used for
   installation. ``build config`` is referring to the selected build configuration
   in Visual Studio i.e. x64-Release, x64-Debug, etc.

* If you are running from your build tree (common during development) then the libraries will be in ``BUILD/lib`` and ``BUILD/bin``

* If you are running from an installed location the libraries will be in ``INSTALL_DIR/lib`` and ``INSTALL_DIR/bin``.

* On Windows, add the library directory to your ``PATH`` environment variable.
* On Linux and most Unix-like systems, add the library directory to your ``LD_LIBRARY_PATH`` environment variable.
* On Mac OSX, add the library directory to your ``DYLD_LIBRARY_PATH`` variable.

On Unix-like systems you can also add the library directory to your
system-wide ``ld.so.conf`` file. You will need root permissions in order
to do so. That is beyond the scope of this document.
