## What's In This Directory

This is `tracktable/Documentation`.  This directory tree contains the
source code for Tracktable documentation.  You will need Sphinx
(http://sphinx-doc.org), Breathe (https://breathe.readthedocs.org),
Napoleon (bundled with Sphinx 1.3 and newer; otherwise available from
https://pypi.python.org/pypi/sphinxcontrib-napoleon) and the Sphinx
Read-the-Docs theme (https://pypi.python.org/pypi/sphinx_rtd_theme) in
order to compile the documents into HTML pages.

Turn on the `BUILD_DOCUMENTATION` option in CMake once you have those
installed.  The documentation is never built by default: you must say
`make doc` (or your platform's appropriate equivalent) to invoke it.
