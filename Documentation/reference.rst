.. _tracktable_reference_label:

Reference Documentation
=======================

.. todo:: In a future release there will be a detailed explanation of
          the differences between the C++ and Python interfaces and
          how to go back and forth between them.

Python Interface
----------------

Right now Tracktable's functions are accessible principally via the
Python interface.  We prefer to implement things in Python first for
ease, speed and malleability, then choose parts to re-implement in C++
based on speed, memory usage and algorithmic needs.

.. toctree::
   :maxdepth: 10

   python/tracktable.rst
   python/tracktable.analysis
   python/tracktable.core.rst
   python/tracktable.core.geomath.rst
   python/tracktable.core.log.rst
   python/tracktable.core.simple_timezone.rst
   python/tracktable.core.timestamp.rst
   python/tracktable.feature.rst
   python/tracktable.filter.rst
   python/tracktable.info.rst
   python/tracktable.render.rst
   python/tracktable.script_helpers.rst


C++ Interface
-------------

In this release there is minimal functionality available directly in
C++.  We have the point hierarchy ending in ``TrajectoryPoint`` (a 2D
point on a globe) and ``PointBaseCartesian`` (an N-dimensional point
-- bring your own dimension) as well as the Trajectory class.  All of
these have the necessary typedefs and traits to be used with the
``boost::geometry`` library.  We also have
``DelimitedTextPointReader`` in the ``TracktableIO`` library.

Our first release is focused on getting enough capability out there to
start rendering maps and movies.

.. toctree::
   :maxdepth: 2

   cpp/tracktable.core.rst
   cpp/tracktable.domain.rst
   cpp/tracktable.io.rst
   cpp/tracktable.analysis.rst

.. todo:: Clean up table of contents.  Look at tracktable.render.rst
          for an example.

.. todo:: Write an explanatory page for the Python domain module.
