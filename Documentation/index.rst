.. Tracktable documentation master file, created by
   sphinx-quickstart on Sat Aug 30 12:10:57 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Tracktable!
======================

Tracktable's purpose is to load, assemble, analyze and render the
paths traced out by moving objects.  We combine the best tools and
techniques we can find from both Python and C++ with the intent of
making all of our capabilities easily accessible from both languages.
We want to make it easy to...

* Render trajectories as histograms (heatmaps), track
  plots and movies.
* Run heavy-duty analysis in C++ and manipulate the results quickly in
  Python.
* Couple algorithms from top to bottom:

  - databases to store raw data,

  - filtering and cleaning techniques to assemble points into
    trajectories,

  - computational geometry to characterize them,

  - clustering and spatial data structures to find groups, and

  - visualization to help communicate your findings.

* Have fun!

If you come across problems, please tell us about them so that we can
improve Tracktable in the future!

Documentation
=============

.. toctree::
   :maxdepth: 3

   installation.rst
   user_guide.rst
   user_guide/example_data.rst
   examples/index.rst
   reference.rst
   conventions.rst
   contacts.rst
   credits.rst
   todo.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
