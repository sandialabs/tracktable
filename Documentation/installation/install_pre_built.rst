Installing Pre-Built Tracktable
===============================

Pip
---

As of Version 1.2, Tracktable is available on the Python Package Index
(PyPI, https://pypi.org) and can be installed with ``pip`` as long as
you're running Python 3.5 or newer. Use the following command:

``pip install tracktable``

.. note:: If this fails, look carefully at the error message. It is most
    likely an error while trying to install `Cartopy
    <https://scitools.org.uk/cartopy/docs/latest/>`_, a map rendering
    toolkit that Tracktable uses to render images. This will show up as a
    complaint about a ``GEOS`` version or a request for ``Proj 4.9.0``.

    The solution is to install Cartopy yourself before you try to install
    Tracktable.

      * If you're using Anaconda,
        the command ``conda install -c conda-forge cartopy`` should do it.
      * If you're using pip and the Cartopy `required dependencies
        <https://scitools.org.uk/cartopy/docs/latest/installing.html#required-dependencies>`_ have been
        installed then the command ``pip install cartopy`` should do it.
      * If neither of the aboved worked then please refer to the `Cartopy installation instructions
        <https://scitools.org.uk/cartopy/docs/latest/installing.html#installing-cartopy>`_
        for additional ways to install Cartopy.

    After you have installed Cartopy, retry ``pip install tracktable``.

Anaconda Virtual Environment
----------------------------
If you have `Anaconda <https://www.anaconda.com/distribution/>`_
installed then the Anaconda virtual environment command
below will create and configure a virtual environment that is ready to use Tracktable.
Enter the following commands in a command/terminal/Anaconda prompt.

- Create the Anaconda virtual environment

  * .. code-block:: console

      conda create --name tracktable --channel defaults --channel conda-forge --yes python pip folium pyshp pytz cartopy pip[tracktable]
- Verify that the ``tracktable`` virtual environment was created

  * ``conda env list``
- Activate the virtual environment

  * ``conda activate tracktable``
- Deactivate the virtual environment

  * ``conda deactivate``
- If the virtual environment is no longer needed then it can be removed

  * ``conda remove --name tracktable --all``

Note for Windows Users
----------------------

If you are using Tracktable under Windows, you might also need to install
the C++ runtime library. This is a necessary component for any program
compiled with Microsoft's Visual C++ suite. You can get it from the following
URL:

https://aka.ms/vs/16/release/vc_redist.x64.exe

The most common indication that you're missing this library is an import
error referring to the "_core_types" library when you try to import Tracktable
in a Python interpreter.