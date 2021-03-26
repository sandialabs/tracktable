.. _common_issues_errors:

======================
Common Issues & Errors
======================

.. important:: This list will be updated as issues and errors are
   discovered or fixed.

.. note:: If the information on this page fails to resolve the
   roadblocks that you are experiencing, please contact us using the
   contact information listed under the
   :ref:`Tracktable Contacts <tracktable_contacts>` section. Include a
   description of your problem, the OS and version you're using, details
   of your Python/Anaconda environment, and any screenshots and error
   messages you can capture.

.. _common_issues_errors_installation:

Installation
============

* Pip fails to install Tracktable

   Look carefully at the error message. It is most
   likely an error while trying to install `Cartopy
   <https://scitools.org.uk/cartopy/docs/latest/>`_, a map rendering
   toolkit that tracktable uses to render images. This will show up as a
   complaint about a ``GEOS`` version or a request for ``Proj 4.9.0``.

   The solution is to install Cartopy and its dependencies yourself
   before you try to install Tracktable.

      * If you're using Anaconda:

         The command ``conda install --channel conda-forge cartopy`` should resolve the issue.

      * If you're using ``pip``:

         .. tip:: We **highly recommend** using Anaconda
            to install and manage Tracktable and its dependencies.

         * Install the Cartopy `required dependencies <https://scitools.org.uk/cartopy/docs/latest/installing.html#required-dependencies>`_
         * Once the dependencies are in place, the command
           ``pip install cartopy`` should succeed.

      * If neither of the above worked, then please refer to the
        `Cartopy installation instructions <https://scitools.org.uk/cartopy/docs/latest/installing.html#installing-cartopy>`_
        for additional ways to install Cartopy.

   After you have installed Cartopy, retry ``pip install tracktable``.

* Python reports ``"Error importing core types.  Path information follows."``
  or ``"NameError: name '_core_types' is not defined"``.

    * This is an OS-specific shared library issue. See the second bullet in the ``Runtime`` section below.

* Errors about client certificates, certificate validation, or connections timing
  out while trying to install anything with Conda or Pip.

    * This is a proxy/SSL issue and outside the scope of this document.

* Pip tries and fails to build Cartopy

    * If at all possible, please use Anaconda. The developers of
      Cartopy provide binary packages for Anaconda.

    * If you absolutely can't use Anaconda and your operating system's
      package manager does not include Cartopy, refer to "Pip fails to
      install Tracktable" above.

.. _common_issues_errors_build:

Build Time
==========

.. note:: For more information about building Tracktable from source,
   please refer to the
   :ref:`Installing Tracktable From Source <installing_from_source_guide>`
   guide. These issues and others are covered there.

* Boost import targets not found

    * This happens when your installed version of CMake is too old for your
      installed version of Boost. Please upgrade CMake to at least 3.19.

* Anaconda CMake package doesn't include ccmake

    * This is a known bug that has been fixed in ``conda-forge`` but has not
      yet propagated to the main distribution. Install ``cmake`` from the
      ``conda-forge`` channel as follows:

      ``$ conda install --channel conda-forge cmake``

* Old Boost version found in /usr/lib or /usr/lib64

    * Set the ``Boost_INCLUDE_DIR`` variable in CMake to point to the location of the include
      files for your preferred Boost installation.
      The filenames for the compiled libraries will be updated
      the next time you press ``c`` or ``Configure``.

.. _common_issues_errors_run:

Runtime
=======

* Python throwing an error similar to
  ``“ModuleNotFoundError: No module named ‘tracktable’”``

    * If you installed Tracktable using ``pip``, this error indicates that
      the Python interpreter you just started is probably not the one for
      which you installed Tracktable. If you are using virtual environments,
      make sure the correct one is active.

    * If you installed Tracktable from source, add Tracktable's installation
      directory (for example, ``/usr/local/Python``) to the front of your
      ``PYTHONPATH`` environment variable.

* Python throwing an error similar to
  ``“ModuleNotFoundError: No module named ‘<package name>’”`` that is
  unrelated to Tracktable

    * If Python can't find a package that isn't ``tracktable`` it's possible
      that the package isn't installed in the environment. If you are using
      virtual environments, make sure the correct one is active. If the problem
      persists, use one of the following commands to install the missing package:

       .. code-block:: console

         conda install --channel conda-forge <package name>

       .. code-block:: console

         conda install <package name>

       .. code-block:: console

         pip3 install <package name>

       .. tip:: We **highly recommend** using Anaconda
          to install and manage tracktable and it's dependencies.

* Python throwing an ``import`` or ``name`` error referring to the ``_core_types`` library when trying to import tracktable

    * This error occurs when the Python interpreter is unable to find
      a shared library used by Tracktable or one of the libraries it
      depends upon. Here are the most common remedies:

        #. Microsoft Windows: The C++ runtime library may be missing. It can be
           downloaded from
           `Microsoft's Visual C++ downloads page <https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0>`_.

        #. MacOS:  The ICU library may be too recent. Tracktable 1.5 was built using
           ICU version 64. If you are using Anaconda, run the following command to install
           the correct version:

           .. code-block:: console

              conda install --channel conda-forge icu=64

           .. note:: If Anaconda reports a conflict from that command, you may need
              to remove and recreate the environment. Conda can often resolve version
              conflicts when an environment is created. Specify ``icu=64`` as one of
              the arguments to ``conda create``. Refer to :ref:`Anaconda Virtual Environment <create_conda_environment>`
              for instructions.

        #. If you built one or more dependencies from source, they may
           need to be added to your environment. On Windows, add the
           directory containing the package's libraries to your ``PATH``
           environment variable. On Linux, add the package's library
           directory to the ``LD_LIBRARY_PATH`` environment variable.
           On MacOS, add the package's library directory to the
           ``DYLD_LIBRARY_PATH`` environment variable.