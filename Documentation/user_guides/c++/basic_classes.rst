
=============
Basic Classes
=============

.. _userguide-cpp-domain:

-------
Domains
-------

Tracktable operates on points, timestamps and trajectories. Since
points and trajectories are meaningless without a coordinate system,
we instantiate points and trajectories from a *domain*. Each domain
provides several different data types and a standard set of units. By
design, it is difficult to mix points and trajectories from different
domains. While we cannot prevent you entirely from mixing up (for
example) kilometers and miles when computing distances, we can at
least try to make it difficult.

Tracktable 1.3 includes the following domains:

.. csv-table:: Available Point Domains
   :header: "C++ Namespace", "Description"
   :widths: 30, 30

   "tracktable::domain::terrestrial", "Points in longitude/latitude space"
   "tracktable::domain::cartesian2d", "Points in flat 2D space"
   "tracktable::doamin::cartesian3d", "Points in flat 3D space"

Each domain defines several data types:

.. csv-table:: Domain Data Types
   :header: "C++ Class", "Description"
   :widths: 10, 40

   "base_point_type", "Bare point - just coordinates."
   "trajectory_point_type", "Point with coordinates, object ID, timestamp and used-defined properties."
   "linestring_type", "Vector of un-decorated points (base points)."
   "trajectory_type", "Vector of trajectory points. Trajectories have their own user-defined properties."
   "base_point_reader_type", "Read BasePoints from a delimited text file."
   "trajectory_point_reader_type", "Read TrajectoryPoints from a delimited text file."
   "box_type", "Axis-aligned bounding box."


We provide rendering support for the terrestrial and 2D Cartesian
domains via Matplotlib and Basemap. Rendering support for 3D points
and trajectories is still an open issue. Given the limited support
for 3D data in Matplotlib we may delegate this job to another library.
Exactly which library we might choose is open for discussion.

NOTE: In this guide we will assume you are working with
TrajectoryPoint data rather than BasePoint data and that you are in
the terrestrial domain.


.. _userguide-cpp-timestamp:

---------
Timestamp
---------


There is a single timestamp class that is common across all point
domains. In C++ this is ``tracktable::Timestamp``, a thinly disguised
``boost::posix_time::ptime``. In Python this is a timezone-aware
:py:class:`datetime.datetime`. As is the case elsewhere in
Tracktable, we convert automatically between the two data types when
Python code calls C++ and vice versa.

.. todo:: Add documentation for C++ methods for manipulating timestamps

.. _userguide-cpp-base-point:

-----------
Base Points
-----------

.. todo:: Add documentation for C++ methods for manipulating base points

Within a domain, Tracktable uses the ``BasePoint`` class to store a bare set of coordinates.
These behave like vectors or sequences in that we use square brackets to set and get coordinates.
Access a point's coordinates as if the point were an array using
``[]``.

In C++::

   TBD

Longitude is always coordinate 0 and latitude is always coordinate 1.
We choose this ordering for consistency with the 2D Cartesian domain
where the X coordinate is always at position 0 and the Y coordinate is
at position 1.

.. _userguide-cpp-trajectory-point:

-----------------
Trajectory Points
-----------------

The things that make a point part of a trajectory are: (1) its
coordinates, already covered by BasePoint; (2) an identifier for the
moving object; (3) a timestamp recording when the object was
observed. These are the main differences between BasePoint and TrajectoryPoint.

In C++::

   my_point = tracktable::domain::terrestrial::trajectory_point

   float longitude = 50, latitude = 40;
   my_point[0] = longitude;
   my_point[1] = latitude;

   my_point.set_object_id("FlightId");
   my_point.set_timestamp(tracktable::time_from_string("2014-04-05 13:25:00");

Note that the timestamp and object ID properties are specific to trajectory points.

--------------------
Operations On Points
--------------------

The module :py:mod:`tracktable.core.geomath` has most of the
operations we want to perform on two or more points. Here are a few
common ones. These work with both BasePoint and TrajectoryPoint
unless otherwise noted.

* ``distance(A, B)``: Compute distance between A and B
* ``bearing(origin, destination)``: Compute the bearing from the origin to the destination
* ``speed_between(here, there)``: Compute speed between two TrajectoryPoints
* ``signed_turn_angle(A, B, C)``: Angle between vectors AB and BC
* ``unsigned_turn_angle(A, B, C)``: Absolute value of angle between vectors AB and BC

.. _userguide-cpp-trajectories:

------------
Trajectories
------------

Just as each domain has ``BasePoint`` and ``TrajectoryPoint`` classes,
we include ``LineString`` and ``Trajectory`` for ordered sequences of
points.

``LineString`` is analogous to ``BasePoint`` in that it has no
decoration at all. It is just a sequence of points. ``Trajectory``
has its own ID (``trajectory_id``) as well as its own properties
array.

As with point classes above, each domain in Tracktable defines a
trajectory class. A trajectory is just a vector of points with a few
extra properties attached. In C++, a trajectory behaves just like a
``std::vector`` and can be used with the C++ Standard Library as such.

Here is an example of creating a trajectory.

C++::

  // Assume this array has been populated already
  trajectory_point_type my_points[100];


  // Initialize with iterators
  trajectory_type my_trajectory(my_points, my_points+100);

  trajectory_type my_trajectory2;
  for (int i = 0; i < 100; ++i) {
     my_trajectory2.push_back(my_points[i]);
  }

Tracktable expects that all points in a given trajectory will have the
same object ID. Timestamps must not decrease from one point to the
next.

There are several free functions defined on trajectories that do
useful things. We expect that the following will be used most often:

* ``point_at_time(trajectory: Trajectory, when: Timestamp)``: Given a
  timestamp, interpolate between points on the trajectory to find the
  point at exactly the specified time. Timestamps before the
  beginning or after the end of the trajectory will return the start
  and end points, respectively. Tracktable will try to interpolate
  all properties that are defined on the trajectory points.

* ``subset_in_window(trajectory: Trajectory, start, end: Timestamp)``:
  Given a start and end timestamp, extract the subset of the
  trajectory between those two times. The start and end points will
  be at exactly the start and end times you specify. These will be
  interpolated if there are no points in the trajectory at precisely
  the right time. Points in between the start and end times will be
  copied from the trajectory without modification.

* ``recompute_speed``, ``recompute_heading``: Compute new values for
  the ``speed`` and ``heading`` numeric properties at each point given
  the position and timestamp attributes. These are convenient if our
  original data set lacks speed/heading information or if the original
  values are corrupt.

.. todo:: Make sure recompute_speed and recompute_heading are there where appropriate
