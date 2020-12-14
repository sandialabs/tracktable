.. Tracktable documentation homepage.

=============================================
Tracktable: Trajectory Analysis and Rendering
=============================================

Hello! Welcome to the Tracktable documentation. Here you will find
information and examples pretaining to the installation and usage of
the Tracktable library.

Tracktable's Purpose
====================

Tracktable's purpose is to load, assemble, analyze and render the
paths traced out by moving objects. We combine the best tools and
techniques we can find from both Python and C++ with the intent of
making all of our capabilities easily accessible from both languages.
Our goal is to make it easy to...

* Render trajectories as histograms (heatmaps), track
  plots and movies.
* Run heavy-duty analysis in C++ and manipulate the results quickly in
  Python.
* Couple algorithms from top to bottom:

  - Databases to store raw data

  - Perform filtering and cleaning techniques to assemble points into
    trajectories

  - Perform computational geometry to characterize trajectories

  - Clustering and spatial data structures to find groups

  - Visualization to help communicate findings

* Have fun!

Tracktable's Target Audience
============================

The target audience of Tracktable is individuals or teams that are interested
in generating, analyzing and visualizing trajectories based on data generated
by a variety of moving objects such as ships, airplanes and cars.

Tracktable's Capabilities
=========================

Tracktable's core capabilities consist of the following functionality:

* DBSCAN Clustering
* Multilevel Distance Geometry
* Data Generation
* Mathematic Conversions
* Trajectory Assembly
* Trajectory Filtering
* Trajectory Predictions (RTree)
* Point & Trajectory Domains

  * Terrestrial (Longitude, Latitude)
  * Cartesian
  * Feature Vectors
* Point & Trajectory IO

  * CSV
  * TSV
  * Keyhole Markup Language (Output Only)
* Visualization

  * Histograms (Heatmaps)
  * Track Plots
  * Movies

Tracktable Contacts
===================

If you come across problems, please tell us about them so that we can
improve Tracktable in the future!

For questions, bug reports or contributions contact:

* **Andrew T. Wilson** | atwilso@sandia.gov

We maintain the following mailing lists for Tracktable:

.. csv-table::
   :header: "Mailing List", "Join Address", "Post Address", "Purpose", "Traffic"
   :widths: auto

   "Tracktable Announcements", "tracktable-announce-join@software.sandia.gov", "tracktable-announce@software.sandia.gov", "Announcements of new Tracktable versions", "Low"
   "Tracktable Development", "tracktable-develop-join@software.sandia.gov", "tracktable-develop@software.sandia.gov", "Ongoing conversations about development for the toolkit", "Medium"
   "Tracktable Repository Commits", "tracktable-commit-join@software.sandia.gov", "tracktable-commit@software.sandia.gov", "Messages every time someone pushes to our main repository", "High"


Documentation
=============

.. toctree::
   :maxdepth: 3

   /installation/installation.rst
   conventions.rst
   /data/data.rst
   /user_guides/user_guides.rst
   /examples/examples.rst
   /api/api.rst
   credits.rst
   todo.rst

Indices & Tables
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
