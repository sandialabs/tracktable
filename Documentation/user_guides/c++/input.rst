
.. _userguide-cpp-input:

=====
Input
=====

There are three ways to get point data into Tracktable in version
1.2.4. We can instantiate and populate TrajectoryPoint objects by
hand, load points from a delimited text file, or create them
algorithmically.

If we choose to create points algorithmically we will need to supply
(at a minimum) coordinates, a timestamp and an ID.

.. todo:: Example of creating points algorithmically

.. _loading-cpp-points:

----------------------------------
Loading Points from Delimited Text
----------------------------------

Tracktable has a flexible point reader for delimited text files. The
bare class is the templated PointReader in the IO directory. Each
point domain provides two versions of it, one for loading base points
(coordinates only) and one for loading trajectory points.

^^^^^^^
Example
^^^^^^^

.. todo:: Add an example

.. _c-point-sources:
.. _c-trajectory-source:

-------------
Point Sources
-------------

.. todo:: This section is out of date

There are algorithmic point generators in the
``tracktable.source.path_point_source`` module that are suitable for
trajectory-building. The ones most likely to be useful are
:py:class:`GreatCircleTrajectoryPointSource <tracktable.source.path_point_source.GreatCircleTrajectoryPointSource>`
and :py:class:`LinearTrajectoryPointSource <tracktable.source.path_point_source.LinearTrajectoryPointSource>`.
Give them start and end points, start and end times, a number of
points to generate and an object ID and you should be ready to go.

.. todo:: Code example

.. _c-trajectory-assembly:

-----------------------------------
Assembling Points into Trajectories
-----------------------------------

.. todo:: This section is out of date

Creating trajectories from a set of points is simple conceptually but
logistically annoying when we write the code ourselves. The overall
idea is as follows:

1. Group points together by object ID and increasing timestamp.

2. For each object ID, connect one point to the next to form
   trajectories.

3. Break the sequence to create a new trajectory whenever it doesn't
   make sense to connect two neighboring points.

This is common enough that Tracktable includes a filter
(:py:class:`tracktable.source.trajectory.AssembleTrajectoryFromPoints`)
to perform the assembly starting from a Python iterable of points
sorted by non-decreasing timestamp. We can specify two parameters to
control part 3 (when to start a new trajectory):

* ``separation_time``: A :py:class:`datetime.timedelta` specifying the
  longest permissible gap between points in the same trajectory. Any
  gap longer than this will start a new trajectory.

* ``separation_distance``: Maximum permissible distance (in
  kilometers) between two points in the same trajectory. Any gap
  longer than this will start a new trajectory.

We can also specify a ``minimum_length``. Trajectories with fewer than
this many points will be silently discarded.

^^^^^^^
Example
^^^^^^^

.. todo:: Add an example

-----------
Annotations
-----------

Once we have points or trajectories in memory we may want to
annotate them with derived quantities for analysis or rendering. For
example, we might want to color an airplane's trajectory using its
climb rate to indicate takeoff, landing, ascent and descent. we
might want to use acceleration, deceleration and rates of turning to
help classify moving objects.

The module ``tracktable.feature.annotations`` contains functions to do
this. Every feature defined in that package has two functions
associated with it: a *calculator* and an *accessor*. The calculator
computes the values for a feature and stores them in the trajectory.
The accessor takes an already-annotated trajectory and returns a
1-dimensional array containing the values of the already-computed
feature. This allows us to attach as many annotations to a
trajectory as we like and then select which one to use (and how) at
render time.

.. todo:: Code example for annotations

--------
Analysis
--------
Once the points or trajectories have been generated and annotated we may need
to perform analysis to determine information about the points or trajectories
such as clustering, distance geometry or nearest neighbors.

The ``tracktable.analysis`` module contains the submodules necessary to
to perform these types of analyses on points or trajectories. The
``tracktable.analysis.dbscan`` submodule will perform the density-based spatial
clustering of applications with noise analysis to determine the clustering of the
feature vector points. The ``tracktable.analysis.distance_geometry`` submodule will
compute the multilevel distance geometry for a trajectory based on either ``length``
or ``time``. The ``tracktable.analysis.rtree`` submodule will generate an rtree that
will compute the nearest neighbors based on provided points within a clustering box.

.. todo:: Code examples for Analysis modules
.. todo:: Find the best location for this section
.. todo:: Add additional/clarifying language
