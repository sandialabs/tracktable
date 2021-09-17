.. _installing_pre_built_guide:

Installing Pre-Built Tracktable
===============================

.. attention:: For all installation issues and errors encountered
   in the steps below refer to the
   :ref:`Common Issues & Errors <common_issues_errors_installation>` Page.

.. attention:: We **highly recommend** using Anaconda
   to install and manage tracktable and it's dependencies.

Pip
---

As of Version 1.2, Tracktable is available on the Python Package Index
(PyPI, https://pypi.org) and can be installed with ``pip`` as long as
you're running Python 3.5 to Python 3.9. Use the following command:

.. code-block:: console

    pip install tracktable

.. _create_conda_environment:

Anaconda Virtual Environment
----------------------------

If you have `Anaconda <https://www.anaconda.com/distribution/>`_
installed then the Anaconda virtual environment commands
below will create and configure a virtual environment that is ready to use
Tracktable. Enter the following commands in a command/terminal/Anaconda prompt.

#. Create the Anaconda virtual environment

   There are two ways to create an ``tracktable`` anaconda virtual environment:

   * **Creating a virtual environment from an conda environment.yml file**

     We include a YML configuration file
     (:download:`tracktable_environment.yml <../../tracktable_environment.yml>`)
     that can be used to create an Anaconda virtual environment named
     ``tracktable``. This file will create the environment in one shot and doesn't
     require any additional package installation after the environment is activated.

     .. code-block:: console

        conda env create -f /path/to/tracktable_environment.yml

     .. important:: Be sure to substitute the location where you saved tracktable_environment.yml in the command above.

   * **Creating a virtual environment from listed packages**

     .. code-block:: console

        conda create --name tracktable --channel conda-forge python tracktable

#. Verify that the ``tracktable`` virtual environment was created

   .. code-block:: console

      conda env list

#. Activate the virtual environment

   .. code-block:: console

      conda activate tracktable

#. Deactivate the virtual environment (optional)

   .. code-block:: console

      conda deactivate

#. Delete the virtual environment when it is no longer needed

  .. code-block:: console

      conda remove --name tracktable --all

Note for Windows Users
----------------------

If you are using Tracktable under Windows, you might also need to install
the C++ runtime library. This is a necessary component for any program
compiled with Microsoft's Visual C++ suite. You can get it from the following
URL:

https://aka.ms/vs/16/release/vc_redist.x64.exe

The most common indication that you're missing this library is an import
error, ``Error importing Tracktable's core types library.``, when you try to import Tracktable
in a Python interpreter.