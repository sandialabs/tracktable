## What's In This Directory

This is `tracktable/Documentation`.  This directory tree contains the
source code for Tracktable documentation.

Tracktable's C++ documentation is built by Doxygen (https://www.doxygen.nl).
It it recommended that you also have Graphviz (https://www.graphviz.org)
installed to build graphical interactive class inheritance diagrams.

Tracktable's Python documentation is built by Sphinx (http://sphinx-doc.org),
Doxygen (https://www.doxygen.nl), Breathe (https://breathe.readthedocs.org),
Napoleon (bundled with Sphinx 1.3 and newer; otherwise available from
https://pypi.python.org/pypi/sphinxcontrib-napoleon) and the Sphinx
Read-the-Docs theme (https://pypi.python.org/pypi/sphinx_rtd_theme) in
order to compile the documents into HTML pages.

Turn on the `BUILD_DOCUMENTATION` or `BUILD_DOCUMENTATION_CXX_ONLY`
options in CMake once you have the respective tools installed.

There is no option to only build the Python documentation since the Python
documentation build process depends upon the C++ documentation.
