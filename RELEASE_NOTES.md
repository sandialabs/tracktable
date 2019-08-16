Tracktable Release Notes

VERSION 1.1.1, August 2019
==========================

This version includes two bugfixes since 1.1.0:

* The Python module ```tracktable.analysis``` was not being installed
  during ```make install```.
  
* The ```current_length``` property was not exposed on TrajectoryPoint
  instances.

VERSION 1.1.0, May 2019
=======================

This version is the last in which we will actively support Python 2.7.
Python 2 is scheduled to stop support on January 1, 2020
(https://www.python.org/dev/peps/pep-0373/).  Many packages
(TensorFlow, Pandas, iPython, Matplotlib, NumPy, SciPy... see
https://python3statement.org/ for the full list) have already dropped
support for Python 2.

We also expect that this will be the last version of Tracktable that
uses Basemap for its back-end rendering layer.  Basemap's maintainer
has stated that there will be one final release at the end of 2019
followed by honorable retirement.  We thank the entire Basemap team,
past and present, for their many years of service.


NEW FEATURES
------------

* Tracktable now has mailing lists!  Send a blank email to
  <listname>-join@software.sandia.gov to request membership.  The
  available lists are:

  * tracktable-announce - Very low volume.  New releases of Tracktable
    will be announced here.
    
  * tracktable-develop - Discussions of new features and changes to
    the library will be conducted here.
    
  * tracktable-commit - Commit messages will be forwarded to this list.
  
* We are moving the repository to GitHub.  Starting with this release,
  the canonical URL will be https://github.com/sandialabs/tracktable
  with documentation at ReadTheDocs.

* As of Version 1.1, we require Boost 1.61 or newer.

* Functions ``tracktable.core.current_memory_use()`` and
  ``tracktable.core.peak_memory_use()`` are now available.
  
* Functions on trajectories:

  * ``time_at_fraction()`` will give you a point along a trajectory at any
    fraction between beginning and end.
  
* Functions on points:

  * ``extrapolate()`` is like ``interpolate()`` in that it takes two
    points and a floating-point number and interpolates between the
    start and end points according to that float.  Unlike
    interpolate(), it doesn't do any bounds checking: it is perfectly
    legitimate to ask for extrapolate(hither, yon, -1.0).
  
  * ``distance()`` now computes distance between any combination of
    points and trajectories.

* Clustering with DBSCAN:

  * The DBSCAN interface has been cleaned up.  You will no longer
    instantiate tracktable::DBSCAN.  Instead, call
    tracktable::cluster_with_dbscan().
    
  * You can decorate the points you feed to DBSCAN.  For example, if
    you want to store your own index, you can pass in a
    ``std::pair<PointType, int>``.
    
* Trajectory I/O using JSON:

  * We now support reading and writing trajectories to JSON in Python.
    Check out the functions ``json_from_trajectory`` and
    ``trajectory_from_json`` in the ``tracktable.io.read_write_json``
    module.  Look for JSON support in C++ in an upcoming version.

* The example scripts in the Python directory now have their own page
  in the documentation.
  

NOTABLE FIXES
-------------

* We can now use Boost versions up to 1.69.  As of Boost 1.67, the
  name of the Python shared library changed in a way that broke our
  build process.  Fixed.  Note, however, that we cannot yet deal with
  CMake-ified versions of Boost.

* We detect Anaconda's Python interpreter on OS X and modify the link
  flags so that loading Tracktable in Python code does not instantly
  generate a segmentation fault.

* Many spurious compilation warnings in Boost have been disabled.  

* Distances in the terrestrial domain are now returned properly in
  kilometers.
  
* We use ``sphinx.autodoc_mock_imports`` in our documentation so that you do not
  need to build the entire toolkit just to create the documentation.
  This still needs a little work to remove the need for CMake.


OUTSTANDING ISSUES
------------------

* The C++ examples need to be cleaned up and documented.  

* There are several useful scripts in
  ``tracktable/Python/tracktable/examples/work_in_progress`` that need
  minor fixes to run with the latest API.


COMING SOON
-----------

* We are experimenting with various replacements for Basemap.  As of
  May 2019 the leading contenders are Cartopy
  (https://scitools.org.uk/cartopy/docs/latest/) for offline rendering
  and either Folium/Leaflet
  (https://python-visualization.github.io/folium/) or Plotly
  (https://plot.ly/) for interactive rendering.  We welcome suggestions
  and discussion!  Please join the tracktable-develop mailing list if
  you're interested.

* We are almost ready to move our documentation to ReadTheDocs.  Look
  for an announcement on the ``tracktable-announce`` mailing list.
  
* C++11 features will be permitted in new contributions to the library.



----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 1.0.5, March 2018
=========================

This is a bug-fix release.

NEW FEATURES
------------

* No new features.


NOTABLE FIXES
-------------

* Writing to files or to file-like objects in Python caused a
  segfault.  See the commit on Feb 21 2018 whose hash begins with
  8db2248d for details.

* C++ headers for convex hulls were not being installed with 'make
  install'.


OUTSTANDING ISSUES
------------------

* Link errors / segfaults under certain OSX configurations, especially
  the Anaconda Python environment.  



----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 1.0.4, November 2017
============================

NEW FEATURES
------------

* Trajectories can be written to and read from JSON and Python
  dictionaries.  At the moment this is only present in Python.  Check
  out tracktable.io.read_write_dictionary and
  tracktable.io.read_write_json.  
  
NOTABLE FIXES
-------------

* References to ``std::cout`` are still in Boost's geometry library.  This
  causes compile problems if I don't work around it.

* ``tracktable.core.Timestamp.from_string()`` should now honor ``%z``
  in Python 3.  Support for the ``%z`` directive is missing in Python
  2.

----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 1.0.3, October 2017
---------------------------

Cleanup release.  We've removed the old Python point writers.  These
were made obsolete by the introduction of point domains.

We've also fixed some tests that were failing because of numeric
imprecision.

Copyright notices on all files updated after NTESS replaced Sandia
Corporation (Lockheed Martin) as the operator of Sandia National Labs.

----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 1.0.2
-------------

There is no Version 1.0.2.


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 1.0.1, April 2016
=========================

NEW FEATURES
------------

* Convex hull measures for 2D spaces (Cartesian and geographic)
* Support Python 3
* Property values can now be null

NOTABLE FIXES
-------------

* Minimize calls to ``std::imbue``.  This was 90% or more of the time
  it took to read trajectories.


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 1.0, January 2016
=========================

NEW FEATURES
------------

* DBSCAN clustering exposed to Python
* RTree spatial index exposed to Python
* Point writers in C++ exposed to Python
* Trajectory writer added to C++
* Named property values can now be integers

NOTABLE FIXES
-------------

* Python wrappers for feature vectors no longer need quite as much memory at compile time
* Guard against NaN results for math on the sphere
* Timestamps are now interpolated with microsecond resolution


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 0.9, September 2015
===========================

First public alpha release.

NEW FEATURES
------------

* Boost r-tree exposed to C++ and Python for all point types along with common query functions.
* Convenience method ``tracktable.core.geomath.recompute_speed`` added since we have to do this so often
* Configurable timestamp input format
* Point writer generalized to work with all domains, output to stream instead of requiring filename
* Add "feature vector" point types (undecorated vectors of doubles) for clustering

NOTABLE FIXES
-------------

* Length of terrestrial trajectories now returned in kilometers instead of radians


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 0.3, March 2015
=======================

Internal release only.

NEW FEATURES
------------

* Tracktable now builds with Visual Studio!
* Automatic bounding box computation (used for culling during rendering)
* Tests of image generating code now compare against ground truth image

NOTABLE FIXES
-------------

* Avoid compiler-specific definitions of ``size_t`` in favor of ``std::size_t``


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------


VERSION 0.2, December 2014
==========================

Internal release only.

NEW FEATURES
------------

* Allow points in 2D and 3D Cartesian space as well as geographic space
* ``tracktable.render.mapmaker`` - convenience calls for many common map use cases
* Delimited text point writer added to Python
* Delimited text point reader added to C++, exposed to Python
* Named properties added to ``tracktable::Trajectory``
* Code in ``tracktable.examples`` can now be used as a module
* ``tracktable::Trajectory`` can now be used with ``boost::geometry`` functions
* Header files install into ``${INSTALL}/include/tracktable``
* Add DBSCAN clustering code to C++

NOTABLE FIXES
-------------

* ``PYTHONPATH`` was not being set for regression tests.
* CMake install path was not being propagated to all modules.


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------

VERSION 0.1, September 2014
===========================

Internal release only: not released to public.

NEW FEATURES
------------

* Movie-making script can now run in parallel
* Example scripts all use common command-line arguments, including reading arguments from files
* Added timezone support for clock rendering
* Doxygen documentation present but incomplete
* Overall documentation now builds using Sphinx
* Decree: distances shall be specified in kilometers

NOTABLE FIXES
-------------

* Histogram buckets have reasonable sizes on both small and large maps
* City labels were not rendering near cities
* Radius of the Earth was wrong
* Copyright notice adjusted to use proper Sandia language
* License file for external data cleaned up


----------------------------------------------------------------------
----------------------------------------------------------------------
----------------------------------------------------------------------

VERSION 0, July 2014
----------------------

Initial milestone: not released to public.

NEW FEATURES
------------

* Points and trajectories in geographic domain implemented in C++ and exposed to Python.
* Math on points and trajectories implemented in C++ and exposed to Python.
* Python script added for movie making on geographic maps.
* Python script added for still images on geographic maps.
* Python scripts for all rendering methods added to examples directory.
