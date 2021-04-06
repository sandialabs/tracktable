.. Tracktable documentation homepage.

=============================================
Tracktable: Trajectory Analysis and Rendering
=============================================

Hello! Welcome to the Tracktable documentation. Here you will find
information and examples pertaining to the installation and usage of
the Tracktable library.

Tracktable's Purpose
====================

Tracktable's purpose is to load, assemble, analyze and render the
paths traced out by moving objects, which we call _trajectories_.
We combine the best tools and techniques we can find from both Python and C++ with
the intent of making all of our capabilities easily accessible from both languages.
Our goal is to make it easy to...

* Render trajectories as histograms (heatmaps), track plots and movies. In Tracktable 1.5.0, histograms
  are available as still images, track plots are available as still images and interactive maps, and movies
  can be written in any format supported by FFMPEG supports.
* Run heavy-duty analysis in C++ and manipulate the results quickly in Python, including Jupyter notebooks.
  Our core data structures and algorithms are implemented in C++ for speed.
* Couple algorithms from top to bottom:

  - Easy I/O to and from delimited text files

  - Perform filtering and cleaning techniques to assemble points into
    trajectories

  - Characterize trajectories using features derived from computational geometry

  - Find clusters and similar trajectories

  - Communicate findings with visualization


Tracktable's Target Audience
============================

The target audience of Tracktable is individuals or teams that are interested
in generating, analyzing and visualizing trajectories based on data generated
by a variety of moving objects such as ships, airplanes and cars.

Tracktable's Capabilities
=========================

Tracktable's core capabilities include these features:

* DBSCAN Clustering

* Multilevel Distance Geometry

* Data Generation

* Conversions Between Units

* Trajectory Assembly

* Trajectory Filtering

* Trajectory Prediction

* Geographic and Cartesian Coordinate Systems

* Point & Trajectory IO

  * Delimited text files (most commonly comma- and tab-separated values)

  * Keyhole Markup Language (KML) (Output Only)

* Visualization

  * Histograms (Heatmaps)

  * Track Plots

  * Movies

.. _tracktable_contacts:

Tracktable Contacts
===================

If you come across problems, please tell us about them so that we can
improve Tracktable in the future!

To reach us with questions, bug reports, suggestions and contributions, please use the `Contact Us <https://tracktable.sandia.gov/contact-us.html>`_ page on Tracktable's `web site <https://tracktable.sandia.gov>`_. For more detailed discussion, consider joining one of our mailing lists:


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
   common_errors.rst
   credits.rst
   changelog.rst
   todo.rst

Indices & Tables
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
